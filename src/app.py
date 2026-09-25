"""
src/app.py
----------
RetailLens – Phase 2: Streamlit Analytics Dashboard.

This is the single-file Streamlit application that serves as the
client-facing analytics front-end for the RetailLens project. It
connects to the SQLite database populated by ``ingest_data.py``,
applies interactive sidebar filters, and renders five production-grade
Plotly visualisations along with a full KPI metrics row and a raw
data explorer panel.

Execution:
    streamlit run src/app.py

Author: RetailLens Analytics Team
Python: 3.10+
"""

import logging
from pathlib import Path

import pandas as pd
import plotly.colors
import plotly.express as px
import sqlalchemy
import sqlalchemy.exc
import streamlit as st
from sqlalchemy.engine import Engine

# ---------------------------------------------------------------------------
# SECTION 1 – Page configuration (MUST be the first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="RetailLens | Executive Dashboard",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS injection
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
        /* Reduce default main block whitespace */
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 1rem;
        }

        /* KPI metric card styling */
        .stMetric {
            background-color: #f0f2f6;
            border-radius: 10px;
            padding: 15px;
            border-left: 4px solid #4A90D9;
        }

        /* Sidebar header font */
        [data-testid="stSidebar"] h1 {
            font-size: 1.2rem;
            color: #4A90D9;
        }

        /* Subtle shadow on all Plotly chart containers */
        [data-testid="stPlotlyChart"] {
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            border-radius: 8px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------
DB_PATH: Path = Path("data/processed/retaillens.db")
TABLE_NAME: str = "superstore_sales"
APP_TITLE: str = "RetailLens — Retail Analytics Dashboard"
PLOTLY_TEMPLATE: str = "plotly_white"
PRIMARY_COLOR: str = "#4A90D9"
ACCENT_COLOR: str = "#E8735A"


# ---------------------------------------------------------------------------
# SECTION 2 – Database connection and core data loading
# ---------------------------------------------------------------------------


def get_connection() -> Engine:
    """Create and return a SQLAlchemy engine connected to the RetailLens SQLite DB.

    Validates that the database file exists on disk before constructing
    the engine. If the file is absent, a descriptive ``ConnectionError``
    is raised so the caller can surface a meaningful message to the user
    rather than a raw SQLAlchemy traceback.

    Args:
        None. The database path is read from the module-level constant
        ``DB_PATH``.

    Returns:
        A ``sqlalchemy.engine.Engine`` instance connected to the SQLite
        database file at ``DB_PATH``.

    Raises:
        ConnectionError: If the ``.db`` file does not exist at ``DB_PATH``.
            Run ``python src/ingest_data.py`` first to generate the database.
    """
    if not DB_PATH.exists():
        raise ConnectionError(
            f"RetailLens database not found at '{DB_PATH}'. "
            "Please run 'python src/ingest_data.py' to generate the database "
            "before launching the dashboard."
        )
    connection_string: str = f"sqlite:///{DB_PATH}"
    engine: Engine = sqlalchemy.create_engine(connection_string, echo=False)
    return engine


@st.cache_data(ttl=3600, show_spinner="Loading RetailLens data...")
def load_full_dataset(_engine: Engine) -> pd.DataFrame:
    """Load the complete superstore_sales table and enrich it with time columns.

    Decorated with ``@st.cache_data(ttl=3600)`` so the SQL round-trip is
    executed at most once per hour per Streamlit session. The underlying
    engine is passed as ``_engine`` (leading underscore) to instruct
    Streamlit's cache to skip hashing it — SQLAlchemy engine objects are
    not hashable.

    After loading, the function:

    1. Parses ``order_date`` to ``datetime64`` using ``pd.to_datetime``
       with ``errors='coerce'`` so malformed dates become ``NaT``
       instead of raising.
    2. Extracts and appends ``order_year`` (``int``) and
       ``order_month`` (``int``) as new columns for time-series grouping
       in the dashboard charts.

    Args:
        _engine: An active ``sqlalchemy.engine.Engine`` instance as
            returned by ``get_connection()``.

    Returns:
        A fully enriched ``pd.DataFrame`` containing all rows and the
        original 21 columns plus ``order_year`` and ``order_month``.

    Raises:
        RuntimeError: If the SQL query fails for any reason, wrapping
            the original ``SQLAlchemyError`` with a human-readable
            message prefixed with ``[RetailLens DB Error]``.
    """
    query: str = f"SELECT * FROM {TABLE_NAME}"
    try:
        df: pd.DataFrame = pd.read_sql_query(query, con=_engine)
    except sqlalchemy.exc.SQLAlchemyError as exc:
        raise RuntimeError(
            f"[RetailLens DB Error] Failed to load data from table "
            f"'{TABLE_NAME}': {exc}"
        ) from exc

    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["order_year"] = df["order_date"].dt.year.astype("Int64")
    df["order_month"] = df["order_date"].dt.month.astype("Int64")

    return df


# ---------------------------------------------------------------------------
# SECTION 3 – Sidebar filter panel
# ---------------------------------------------------------------------------


def render_sidebar(df: pd.DataFrame) -> dict[str, list]:
    """Render the interactive sidebar filter panel and return selected values.

    This function constructs the full sidebar UI — logo, time period
    selector, geography selector, and product category selector — and
    returns the user's current widget selections as a plain dictionary.
    It does **not** apply any filtering logic itself; that responsibility
    belongs to ``apply_filters()``.

    Args:
        df: The full unfiltered ``pd.DataFrame`` as returned by
            ``load_full_dataset()``. Used to derive dynamic option lists
            for each multiselect widget.

    Returns:
        A ``dict[str, list]`` with the following keys:

        - ``"years"``      – List of selected year integers.
        - ``"regions"``    – List of selected region name strings.
        - ``"categories"`` – List of selected category name strings.
    """
    with st.sidebar:
        # ----------------------------------------------------------------
        # Brand / logo
        # ----------------------------------------------------------------
        try:
            st.image("assets/logo.png")
        except Exception:
            st.markdown("## 🔬 RetailLens")

        st.markdown("---")

        # ----------------------------------------------------------------
        # Time period filter
        # ----------------------------------------------------------------
        st.markdown("### 🗓️ Time Period")
        available_years: list[int] = sorted(
            df["order_year"].dropna().unique().tolist()
        )
        selected_years: list[int] = st.multiselect(
            label="Select Year(s)",
            options=available_years,
            default=available_years,
            key="filter_year",
        )

        st.markdown("---")

        # ----------------------------------------------------------------
        # Geography filter
        # ----------------------------------------------------------------
        st.markdown("### 🌎 Geography")
        available_regions: list[str] = sorted(
            df["region"].dropna().unique().tolist()
        )
        selected_regions: list[str] = st.multiselect(
            label="Select Region(s)",
            options=available_regions,
            default=available_regions,
            key="filter_region",
        )

        st.markdown("---")

        # ----------------------------------------------------------------
        # Product category filter
        # ----------------------------------------------------------------
        st.markdown("### 📦 Product")
        available_categories: list[str] = sorted(
            df["category"].dropna().unique().tolist()
        )
        selected_categories: list[str] = st.multiselect(
            label="Select Category(s)",
            options=available_categories,
            default=available_categories,
            key="filter_category",
        )

        st.markdown("---")

        # ----------------------------------------------------------------
        # Active filter summary
        # ----------------------------------------------------------------
        n_years: int = len(selected_years)
        n_regions: int = len(selected_regions)
        n_categories: int = len(selected_categories)
        st.markdown(
            f"*Filters active: {n_years} year(s), "
            f"{n_regions} region(s), "
            f"{n_categories} category(ies)*"
        )

    return {
        "years": selected_years,
        "regions": selected_regions,
        "categories": selected_categories,
    }


# ---------------------------------------------------------------------------
# SECTION 4 – Data filtering engine
# ---------------------------------------------------------------------------


def apply_filters(
    df: pd.DataFrame,
    filters: dict[str, list],
) -> pd.DataFrame:
    """Apply sidebar filter selections to the full dataset via boolean indexing.

    Chains all three filter conditions (year, region, category) in a
    single Pandas boolean index expression and returns the filtered
    subset. If the result is empty — i.e., the selected combination
    returns zero rows — a Streamlit warning is rendered and
    ``st.stop()`` is called to halt rendering gracefully so the rest
    of the dashboard does not attempt to operate on an empty DataFrame.

    Args:
        df: The full unfiltered ``pd.DataFrame`` as returned by
            ``load_full_dataset()``.
        filters: A ``dict[str, list]`` as returned by
            ``render_sidebar()``, containing keys ``"years"``,
            ``"regions"``, and ``"categories"``.

    Returns:
        A filtered ``pd.DataFrame`` containing only rows that satisfy
        all three active filter conditions simultaneously.
    """
    mask = (
        df["order_year"].isin(filters["years"])
        & df["region"].isin(filters["regions"])
        & df["category"].isin(filters["categories"])
    )
    filtered_df: pd.DataFrame = df[mask].copy()

    if filtered_df.empty:
        st.warning(
            "⚠️ No data matches the current filter selection. "
            "Please broaden your filters."
        )
        st.stop()

    logging.info(
        "apply_filters: filtered shape %d rows x %d columns",
        *filtered_df.shape,
    )
    return filtered_df


# ---------------------------------------------------------------------------
# SECTION 5 – KPI metrics row
# ---------------------------------------------------------------------------


def render_kpi_row(df: pd.DataFrame, df_full: pd.DataFrame) -> None:
    """Compute and render the top-row KPI metric cards with delta indicators.

    Computes five business KPIs from the filtered DataFrame and renders
    them as ``st.metric`` cards in a single five-column row. Each card
    includes a ``delta`` value showing the deviation of the current
    filter selection from the full (unfiltered) dataset baseline — a
    positive delta is rendered green and a negative delta is rendered
    red by Streamlit's default styling.

    Args:
        df: The filtered ``pd.DataFrame`` as returned by
            ``apply_filters()``.
        df_full: The complete unfiltered ``pd.DataFrame`` as returned by
            ``load_full_dataset()``, used as the baseline for delta
            computation.

    Returns:
        None
    """
    # ----------------------------------------------------------------
    # Filtered KPIs
    # ----------------------------------------------------------------
    total_sales: float = float(df["sales"].sum())
    total_profit: float = float(df["profit"].sum())
    profit_margin: float = (
        (total_profit / total_sales * 100) if total_sales > 0 else 0.0
    )
    total_orders: int = int(df["order_id"].nunique())
    avg_order_value: float = (
        total_sales / total_orders if total_orders > 0 else 0.0
    )

    # ----------------------------------------------------------------
    # Baseline (full dataset) KPIs for delta computation
    # ----------------------------------------------------------------
    base_sales: float = float(df_full["sales"].sum())
    base_profit: float = float(df_full["profit"].sum())
    base_margin: float = (
        (base_profit / base_sales * 100) if base_sales > 0 else 0.0
    )
    base_orders: int = int(df_full["order_id"].nunique())
    base_aov: float = base_sales / base_orders if base_orders > 0 else 0.0

    # ----------------------------------------------------------------
    # Delta values (filtered minus baseline)
    # ----------------------------------------------------------------
    delta_sales: float = round(total_sales - base_sales, 2)
    delta_profit: float = round(total_profit - base_profit, 2)
    delta_margin: float = round(profit_margin - base_margin, 2)
    delta_orders: int = total_orders - base_orders
    delta_aov: float = round(avg_order_value - base_aov, 2)

    # ----------------------------------------------------------------
    # Render section header and metric cards
    # ----------------------------------------------------------------
    st.markdown("### 📊 Key Performance Indicators")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="💰 Total Sales",
            value=f"${total_sales:,.2f}",
            delta=f"${delta_sales:,.2f}",
        )

    with col2:
        st.metric(
            label="📈 Total Profit",
            value=f"${total_profit:,.2f}",
            delta=f"${delta_profit:,.2f}",
        )

    with col3:
        st.metric(
            label="🎯 Profit Margin",
            value=f"{profit_margin:.1f}%",
            delta=f"{delta_margin:.2f}%",
        )

    with col4:
        st.metric(
            label="🛒 Total Orders",
            value=f"{total_orders:,}",
            delta=f"{delta_orders:,}",
        )

    with col5:
        st.metric(
            label="💳 Avg Order Value",
            value=f"${avg_order_value:,.2f}",
            delta=f"${delta_aov:,.2f}",
        )


# ---------------------------------------------------------------------------
# SECTION 6 – Sales Trend Over Time (Line Chart)
# ---------------------------------------------------------------------------


def render_sales_trend(df: pd.DataFrame) -> None:
    """Render a smooth monthly aggregated sales line chart using Plotly Express.

    Groups the filtered dataset by year and month, constructs a proper
    ``datetime`` period column for correct chronological ordering on the
    x-axis, and renders a spline line chart with visible data point
    markers.

    Args:
        df: The filtered ``pd.DataFrame`` as returned by
            ``apply_filters()``.

    Returns:
        None
    """
    trend_df = (
        df.groupby(["order_year", "order_month"])["sales"]
        .sum()
        .reset_index()
    )
    trend_df["period"] = pd.to_datetime(
        trend_df["order_year"].astype(str)
        + "-"
        + trend_df["order_month"].astype(str).str.zfill(2)
    )
    trend_df = trend_df.sort_values("period")

    fig = px.line(
        data_frame=trend_df,
        x="period",
        y="sales",
        title="📅 Monthly Sales Trend",
        labels={"period": "Month", "sales": "Total Sales ($)"},
        template=PLOTLY_TEMPLATE,
        color_discrete_sequence=[PRIMARY_COLOR],
    )

    fig.update_layout(
        hovermode="x unified",
        xaxis_title="Month",
        yaxis_title="Revenue ($)",
        yaxis_tickprefix="$",
        yaxis_tickformat=",.0f",
        showlegend=False,
    )

    fig.update_traces(
        mode="lines+markers",
        line_shape="spline",
    )

    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
# SECTION 7 – Profit by Region (Bar Chart)
# ---------------------------------------------------------------------------


def render_profit_by_region(df: pd.DataFrame) -> None:
    """Render a colour-scaled bar chart showing total profit by geographic region.

    Aggregates profit and sales per region, computes the profit margin
    percentage per region (surfaced on hover), and renders the bars
    sorted descending by total profit with a blue-to-red continuous
    colour scale.

    Args:
        df: The filtered ``pd.DataFrame`` as returned by
            ``apply_filters()``.

    Returns:
        None
    """
    region_df = (
        df.groupby("region")
        .agg(
            total_profit=("profit", "sum"),
            total_sales=("sales", "sum"),
        )
        .reset_index()
    )
    region_df["profit_margin_pct"] = (
        region_df["total_profit"] / region_df["total_sales"] * 100
    ).round(2)
    region_df = region_df.sort_values("total_profit", ascending=False)

    fig = px.bar(
        data_frame=region_df,
        x="region",
        y="total_profit",
        title="🗺️ Profit by Region",
        labels={"region": "Region", "total_profit": "Total Profit ($)"},
        template=PLOTLY_TEMPLATE,
        color="total_profit",
        color_continuous_scale=[ACCENT_COLOR, PRIMARY_COLOR],
        hover_data={"profit_margin_pct": ":.2f"},
    )

    fig.update_layout(
        coloraxis_showscale=False,
        xaxis_title="Region",
        yaxis_title="Profit ($)",
        yaxis_tickprefix="$",
        yaxis_tickformat=",.0f",
    )

    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
# SECTION 8 – Sales Distribution by Category (Donut Chart)
# ---------------------------------------------------------------------------


def render_category_donut(df: pd.DataFrame) -> None:
    """Render a donut pie chart showing each product category's share of sales.

    Aggregates total sales per product category and renders a Plotly
    donut chart (``hole=0.45``) with percentage and label annotations
    inside each slice and a rich custom hover template.

    Args:
        df: The filtered ``pd.DataFrame`` as returned by
            ``apply_filters()``.

    Returns:
        None
    """
    category_df = (
        df.groupby("category")["sales"]
        .sum()
        .reset_index()
        .rename(columns={"sales": "total_sales"})
    )

    fig = px.pie(
        data_frame=category_df,
        values="total_sales",
        names="category",
        title="🍩 Sales Share by Category",
        template=PLOTLY_TEMPLATE,
        color_discrete_sequence=plotly.colors.qualitative.Set2,
        hole=0.45,
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Sales: $%{value:,.2f}<br>"
            "Share: %{percent}"
            "<extra></extra>"
        ),
    )

    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5),
    )

    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
# SECTION 9 – Raw Data Explorer
# ---------------------------------------------------------------------------


def render_data_explorer(df: pd.DataFrame) -> None:
    """Render a collapsible raw data explorer panel with a CSV download button.

    Displays the filtered dataset in a scrollable ``st.dataframe`` table
    restricted to the 12 most informative columns. Also provides a
    one-click download button that exports the same column-subset as a
    UTF-8 encoded CSV file named ``retaillens_filtered_export.csv``.

    Args:
        df: The filtered ``pd.DataFrame`` as returned by
            ``apply_filters()``.

    Returns:
        None
    """
    display_columns: list[str] = [
        "order_id",
        "order_date",
        "customer_name",
        "segment",
        "region",
        "category",
        "sub_category",
        "product_name",
        "sales",
        "quantity",
        "discount",
        "profit",
    ]

    # Guard against any column being absent (defensive — schema is fixed)
    available_cols: list[str] = [
        col for col in display_columns if col in df.columns
    ]
    display_df: pd.DataFrame = df[available_cols]

    with st.expander("🔍 Raw Data Explorer", expanded=False):
        st.markdown(f"**{len(display_df):,} rows** matching current filters.")

        st.dataframe(
            display_df,
            use_container_width=True,
            height=300,
        )

        csv_bytes: bytes = display_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="⬇️ Download Filtered Data as CSV",
            data=csv_bytes,
            file_name="retaillens_filtered_export.csv",
            mime="text/csv",
        )


# ---------------------------------------------------------------------------
# SECTION 10 – main() — Full application orchestration
# ---------------------------------------------------------------------------


def main() -> None:
    """Orchestrate the full RetailLens Streamlit dashboard application.

    This is the top-level controller function. It initialises logging,
    renders the page header, establishes the database connection, loads
    and caches the dataset, applies sidebar filters, and sequentially
    renders every dashboard section in the prescribed layout order.

    The entire application body (after the page title block) is wrapped
    in a ``try/except Exception`` block. Any unhandled exception causes
    a graceful ``st.error`` message to be displayed and ``st.stop()``
    to be called rather than crashing the Streamlit process.

    Returns:
        None
    """
    # ----------------------------------------------------------------
    # Logging initialisation
    # ----------------------------------------------------------------
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s — %(levelname)s — %(message)s",
    )
    logging.info("RetailLens application starting.")

    # ----------------------------------------------------------------
    # Page header
    # ----------------------------------------------------------------
    st.title(APP_TITLE)
    st.markdown(
        "*Interactive E-Commerce Performance Overview*"
    )
    st.markdown("---")

    # ----------------------------------------------------------------
    # Application body — wrapped in a global error guard
    # ----------------------------------------------------------------
    try:
        # Step 1: Connect to the database
        engine: Engine = get_connection()

        # Step 2: Load the full dataset (cached)
        df_full: pd.DataFrame = load_full_dataset(engine)

        # Step 3: Render sidebar and collect filter selections
        filters: dict[str, list] = render_sidebar(df_full)

        # Step 4: Apply filters to get the working subset
        df_filtered: pd.DataFrame = apply_filters(df_full, filters)

        # Step 5: KPI row
        st.markdown("---")
        render_kpi_row(df_filtered, df_full)

        # Step 6: Two-column chart row — Sales Trend + Donut
        st.markdown("---")
        st.markdown("### 📉 Interactive Analytics")
        chart_col1, chart_col2 = st.columns([2, 1])

        with chart_col1:
            render_sales_trend(df_filtered)

        with chart_col2:
            render_category_donut(df_filtered)

        # Step 7: Full-width Profit by Region bar chart
        st.markdown("---")
        render_profit_by_region(df_filtered)

        # Step 8: Collapsible raw data explorer
        st.markdown("---")
        render_data_explorer(df_filtered)

        # Step 9: Footer
        st.markdown(
            "<div style='text-align: center; color: grey; font-size: 0.8rem;'>"
            "RetailLens v1.0 | Portfolio Analytics Project | "
            "Data: Superstore Sales Dataset"
            "</div>",
            unsafe_allow_html=True,
        )

    except Exception as exc:
        logging.exception("RetailLens encountered a critical application error.")
        st.error(f"🚨 Critical application error: {exc}")
        st.stop()


# ---------------------------------------------------------------------------
# Module entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
