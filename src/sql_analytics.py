"""
src/sql_analytics.py
---------------------
RetailLens – Phase 1: SQL Analytics Layer.

This module connects to the local SQLite database populated by
``ingest_data.py`` and executes four advanced analytical SQL queries
against the ``superstore_sales`` table. Each query is encapsulated in
its own function, which prints a formatted section header and the full
result DataFrame to the terminal.

Execution:
    python src/sql_analytics.py

The module is intentionally stateless: it establishes a single
SQLAlchemy engine in ``main()``, passes it into each query function,
and disposes of it in a ``finally`` block.

Author: RetailLens Analytics Team
Python: 3.10+
"""

import logging
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

# ---------------------------------------------------------------------------
# Constants – must mirror the values declared in ingest_data.py
# ---------------------------------------------------------------------------
PROJECT_ROOT: Path = Path(__file__).parent.parent.resolve()
DB_PATH: Path = PROJECT_ROOT / "data" / "processed" / "retaillens.db"
TABLE_NAME: str = "superstore_sales"

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------
LOG_DIR: Path = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

_log_formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(funcName)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

_console_handler = logging.StreamHandler(sys.stdout)
_console_handler.setFormatter(_log_formatter)
_console_handler.setLevel(logging.INFO)

_file_handler = logging.FileHandler(
    LOG_DIR / "analytics.log", mode="a", encoding="utf-8"
)
_file_handler.setFormatter(_log_formatter)
_file_handler.setLevel(logging.INFO)

logger = logging.getLogger("retaillens.analytics")
logger.setLevel(logging.INFO)
logger.addHandler(_console_handler)
logger.addHandler(_file_handler)
logger.propagate = False


# ---------------------------------------------------------------------------
# Database helper
# ---------------------------------------------------------------------------


def get_db_connection() -> Engine:
    """Create and return a SQLAlchemy engine bound to the RetailLens SQLite DB.

    Validates that the database file exists on disk before constructing
    the engine. The caller is responsible for disposing the engine when
    finished (see ``main()``).

    Returns:
        A ``sqlalchemy.engine.Engine`` instance connected to the SQLite
        database at ``DB_PATH``.

    Raises:
        FileNotFoundError: If the SQLite ``.db`` file does not exist.
            Run ``python src/ingest_data.py`` first to populate it.
        SQLAlchemyError: If SQLAlchemy cannot create a valid engine from
            the constructed connection string.
    """
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database file not found: '{DB_PATH}'. "
            "Run 'python src/ingest_data.py' to generate the database before "
            "executing analytics queries."
        )

    connection_string: str = f"sqlite:///{DB_PATH}"
    logger.info("Creating SQLAlchemy engine: %s", connection_string)

    try:
        engine: Engine = create_engine(connection_string, echo=False)
    except SQLAlchemyError as exc:
        logger.error("Failed to create SQLAlchemy engine: %s", exc)
        raise

    logger.info("Engine created successfully for database: %s", DB_PATH)
    return engine


# ---------------------------------------------------------------------------
# Query functions
# ---------------------------------------------------------------------------


def query_regional_sales_and_margin(engine: Engine) -> None:
    """Execute Query 1: Regional Sales Revenue and Profit Margin Analysis.

    Aggregates total sales, total profit, and profit margin percentage
    for each geographic region, ordered by profit margin descending.
    Results are printed in full to the terminal without row index.

    SQL Logic:
        - Aggregates ``SUM(sales)`` and ``SUM(profit)`` per region.
        - Computes profit margin as ``(SUM(profit) / SUM(sales)) * 100``.
        - All monetary values rounded to 2 decimal places via ``ROUND()``.
        - Sorted by ``profit_margin_pct DESC``.

    Args:
        engine: An active ``sqlalchemy.engine.Engine`` instance as
            returned by ``get_db_connection()``.

    Returns:
        None

    Raises:
        SQLAlchemyError: If the query execution fails at the database level.
        pd.errors.DatabaseError: If pandas cannot read the query result set.
    """
    sql: str = """
        SELECT
            region,
            ROUND(SUM(sales), 2)                        AS total_sales,
            ROUND(SUM(profit), 2)                       AS total_profit,
            ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS profit_margin_pct
        FROM
            superstore_sales
        GROUP BY
            region
        ORDER BY
            profit_margin_pct DESC
    """

    print("\n" + "=" * 60)
    print("  QUERY 1: Regional Sales & Profit Margin")
    print("=" * 60)

    logger.info("Executing Query 1: Regional Sales & Profit Margin")

    try:
        result_df: pd.DataFrame = pd.read_sql_query(sql, con=engine)
    except (SQLAlchemyError, pd.errors.DatabaseError) as exc:
        logger.error("Query 1 failed: %s", exc)
        raise

    logger.info("Query 1 returned %d rows.", len(result_df))
    print(result_df.to_string(index=False))


def query_top5_profitable_subcategories(engine: Engine) -> None:
    """Execute Query 2: Top 5 Sub-Categories by Total Profit.

    Ranks the five most profitable product sub-categories, including
    their total sales revenue, total units sold, and average discount
    percentage applied. Results are printed in full to the terminal.

    SQL Logic:
        - Aggregates ``SUM(sales)``, ``SUM(profit)``, ``SUM(quantity)``,
          and ``AVG(discount) * 100`` per sub-category.
        - All computed values rounded to 2 decimal places.
        - Limited to the top 5 rows ordered by ``total_profit DESC``.

    Args:
        engine: An active ``sqlalchemy.engine.Engine`` instance as
            returned by ``get_db_connection()``.

    Returns:
        None

    Raises:
        SQLAlchemyError: If the query execution fails at the database level.
        pd.errors.DatabaseError: If pandas cannot read the query result set.
    """
    sql: str = """
        SELECT
            sub_category,
            ROUND(SUM(sales), 2)           AS total_sales,
            ROUND(SUM(profit), 2)          AS total_profit,
            ROUND(SUM(quantity), 2)        AS units_sold,
            ROUND(AVG(discount) * 100, 2)  AS avg_discount_pct
        FROM
            superstore_sales
        GROUP BY
            sub_category
        ORDER BY
            total_profit DESC
        LIMIT 5
    """

    print("\n" + "=" * 60)
    print("  QUERY 2: Top 5 Sub-Categories by Profit")
    print("=" * 60)

    logger.info("Executing Query 2: Top 5 Profitable Sub-Categories")

    try:
        result_df: pd.DataFrame = pd.read_sql_query(sql, con=engine)
    except (SQLAlchemyError, pd.errors.DatabaseError) as exc:
        logger.error("Query 2 failed: %s", exc)
        raise

    logger.info("Query 2 returned %d rows.", len(result_df))
    print(result_df.to_string(index=False))


def query_yoy_sales_growth(engine: Engine) -> None:
    """Execute Query 3: Year-over-Year (YoY) Sales Growth.

    Uses a CTE to compute annual total sales, then applies SQLite's
    ``LAG()`` window function to derive the prior year's sales figure
    and calculate the percentage growth. The first year naturally has a
    NULL growth value, which is preserved in the output as expected.

    SQL Logic:
        - CTE ``yearly_sales``: extracts year via
          ``STRFTIME('%Y', order_date)`` and aggregates ``SUM(sales)``
          per year.
        - Outer query: applies ``LAG(total_sales) OVER (ORDER BY
          order_year)`` to get the prior year's total.
        - Computes ``yoy_growth_pct`` as
          ``((total_sales - prior_year_sales) / prior_year_sales) * 100``,
          rounded to 2 decimal places.
        - Ordered by ``order_year ASC``; NULL for year one is intentional.

    Args:
        engine: An active ``sqlalchemy.engine.Engine`` instance as
            returned by ``get_db_connection()``.

    Returns:
        None

    Raises:
        SQLAlchemyError: If the query execution fails at the database level.
        pd.errors.DatabaseError: If pandas cannot read the query result set.
    """
    sql: str = """
        WITH yearly_sales AS (
            SELECT
                STRFTIME('%Y', order_date)  AS order_year,
                ROUND(SUM(sales), 2)        AS total_sales
            FROM
                superstore_sales
            GROUP BY
                order_year
        )
        SELECT
            order_year,
            total_sales,
            LAG(total_sales) OVER (ORDER BY order_year) AS prior_year_sales,
            ROUND(
                (
                    (total_sales - LAG(total_sales) OVER (ORDER BY order_year))
                    / LAG(total_sales) OVER (ORDER BY order_year)
                ) * 100,
                2
            ) AS yoy_growth_pct
        FROM
            yearly_sales
        ORDER BY
            order_year ASC
    """

    print("\n" + "=" * 60)
    print("  QUERY 3: Year-over-Year (YoY) Sales Growth")
    print("=" * 60)

    logger.info("Executing Query 3: YoY Sales Growth (CTE + LAG window function)")

    try:
        result_df: pd.DataFrame = pd.read_sql_query(sql, con=engine)
    except (SQLAlchemyError, pd.errors.DatabaseError) as exc:
        logger.error("Query 3 failed: %s", exc)
        raise

    logger.info("Query 3 returned %d rows.", len(result_df))
    print(result_df.to_string(index=False))


def query_customer_segment_analysis(engine: Engine) -> None:
    """Execute Query 4: Customer Segment KPI Analysis.

    Uses a two-level CTE aggregation to compute segment-level KPIs:
    unique customer count, total order count, average order value (AOV),
    and purchase frequency (mean orders per customer). Results are
    ordered by average order value descending.

    SQL Logic:
        - CTE ``order_level``: collapses line items to the order grain by
          grouping on ``(order_id, customer_id, segment)`` and summing
          ``sales`` as ``order_value``.
        - Outer query over the CTE:
            - ``COUNT(DISTINCT customer_id)`` → ``unique_customers``
            - ``COUNT(order_id)``              → ``total_orders``
            - ``ROUND(AVG(order_value), 2)``   → ``avg_order_value``
            - ``ROUND(CAST(COUNT(order_id) AS FLOAT)
              / COUNT(DISTINCT customer_id), 2)`` → ``purchase_frequency``
        - Grouped by ``segment``, ordered by ``avg_order_value DESC``.

    Args:
        engine: An active ``sqlalchemy.engine.Engine`` instance as
            returned by ``get_db_connection()``.

    Returns:
        None

    Raises:
        SQLAlchemyError: If the query execution fails at the database level.
        pd.errors.DatabaseError: If pandas cannot read the query result set.
    """
    sql: str = """
        WITH order_level AS (
            SELECT
                order_id,
                customer_id,
                segment,
                SUM(sales) AS order_value
            FROM
                superstore_sales
            GROUP BY
                order_id,
                customer_id,
                segment
        )
        SELECT
            segment,
            COUNT(DISTINCT customer_id)                                  AS unique_customers,
            COUNT(order_id)                                              AS total_orders,
            ROUND(AVG(order_value), 2)                                   AS avg_order_value,
            ROUND(
                CAST(COUNT(order_id) AS FLOAT) / COUNT(DISTINCT customer_id),
                2
            )                                                            AS purchase_frequency
        FROM
            order_level
        GROUP BY
            segment
        ORDER BY
            avg_order_value DESC
    """

    print("\n" + "=" * 60)
    print("  QUERY 4: Customer Segment KPI Analysis")
    print("=" * 60)

    logger.info(
        "Executing Query 4: Customer Segment Analysis (two-level CTE aggregation)"
    )

    try:
        result_df: pd.DataFrame = pd.read_sql_query(sql, con=engine)
    except (SQLAlchemyError, pd.errors.DatabaseError) as exc:
        logger.error("Query 4 failed: %s", exc)
        raise

    logger.info("Query 4 returned %d rows.", len(result_df))
    print(result_df.to_string(index=False))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Orchestrate the RetailLens SQL analytics query suite.

    Acquires a single database engine via ``get_db_connection()``, passes
    it to each of the four query functions in sequence, and guarantees
    engine disposal via a ``try/finally`` block regardless of whether any
    query raises an exception.

    Returns:
        None
    """
    logger.info("=" * 60)
    logger.info("  RetailLens SQL Analytics – START")
    logger.info("  Database: %s", DB_PATH)
    logger.info("=" * 60)

    engine: Engine = get_db_connection()

    try:
        query_regional_sales_and_margin(engine)
        query_top5_profitable_subcategories(engine)
        query_yoy_sales_growth(engine)
        query_customer_segment_analysis(engine)

        logger.info("=" * 60)
        logger.info("  RetailLens SQL Analytics – ALL QUERIES COMPLETE")
        logger.info("=" * 60)

    finally:
        engine.dispose()
        logger.info("SQLAlchemy engine disposed cleanly.")


if __name__ == "__main__":
    main()
