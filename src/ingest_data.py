"""
src/ingest_data.py
------------------
RetailLens – Phase 1: Core ETL Ingestion Pipeline.

This module loads the raw Superstore sales CSV, performs column
normalisation, data quality validation, numeric type enforcement,
and persists the cleaned dataset to a local SQLite database via
SQLAlchemy.

Execution:
    python src/ingest_data.py

The script is designed to be fully idempotent: re-running it will
overwrite the existing database table with the freshly cleaned data.

Author: RetailLens Analytics Team
Python: 3.10+
"""

import logging
import re
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# ---------------------------------------------------------------------------
# Constants – all configurable values live here, nowhere else in the file
# ---------------------------------------------------------------------------
PROJECT_ROOT: Path = Path(__file__).parent.parent.resolve()
RAW_DATA_DIR: Path = PROJECT_ROOT / "data" / "raw"
LOG_DIR: Path = PROJECT_ROOT / "logs"
DB_DIR: Path = PROJECT_ROOT / "data" / "processed"

CSV_FILENAME: str = "Superstore.csv"
DB_FILENAME: str = "retaillens.db"
TABLE_NAME: str = "superstore_sales"

CSV_PATH: Path = RAW_DATA_DIR / CSV_FILENAME
DB_PATH: Path = DB_DIR / DB_FILENAME

# ---------------------------------------------------------------------------
# Logging configuration – writes to both console and a rotating log file
# ---------------------------------------------------------------------------
LOG_DIR.mkdir(parents=True, exist_ok=True)
DB_DIR.mkdir(parents=True, exist_ok=True)

_log_formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(funcName)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

_console_handler = logging.StreamHandler(sys.stdout)
_console_handler.setFormatter(_log_formatter)
_console_handler.setLevel(logging.INFO)

_file_handler = logging.FileHandler(LOG_DIR / "ingest.log", mode="a", encoding="utf-8")
_file_handler.setFormatter(_log_formatter)
_file_handler.setLevel(logging.INFO)

logger = logging.getLogger("retaillens.ingest")
logger.setLevel(logging.INFO)
logger.addHandler(_console_handler)
logger.addHandler(_file_handler)
# Prevent log records from propagating to the root logger
logger.propagate = False


# ---------------------------------------------------------------------------
# ETL Functions
# ---------------------------------------------------------------------------


def load_raw_data(filepath: Path) -> pd.DataFrame:
    """Load the raw Superstore CSV from disk into a pandas DataFrame.

    Validates that the file exists before attempting to read it,
    raising a descriptive ``FileNotFoundError`` if not. Logs the
    resulting shape and full column list for auditability.

    Args:
        filepath: Absolute ``pathlib.Path`` pointing to the raw CSV file.

    Returns:
        A ``pd.DataFrame`` containing the unmodified CSV contents.

    Raises:
        FileNotFoundError: If ``filepath`` does not resolve to an existing
            file on disk.
        pd.errors.ParserError: If pandas cannot parse the CSV format.
        OSError: If an OS-level I/O error occurs while reading the file.
    """
    if not filepath.exists():
        raise FileNotFoundError(
            f"Raw data file not found at expected location: '{filepath}'. "
            "Please run setup_project.py first or ensure Superstore.csv is "
            "present in data/raw/."
        )

    logger.info("Reading CSV: %s", filepath)

    try:
        df: pd.DataFrame = pd.read_csv(filepath, encoding="windows-1252")
    except pd.errors.ParserError as exc:
        logger.error("CSV parsing failed for '%s': %s", filepath, exc)
        raise
    except OSError as exc:
        logger.error("OS error while reading '%s': %s", filepath, exc)
        raise

    logger.info(
        "Loaded DataFrame – shape: %d rows × %d columns", *df.shape
    )
    logger.info("Columns detected: %s", df.columns.tolist())

    return df


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise DataFrame column names to snake_case.

    Produces a new DataFrame with cleaned column names; the input
    DataFrame is never mutated. Transformation rules applied in order:

    1. Strip leading/trailing whitespace from each name.
    2. Convert to lowercase.
    3. Replace spaces and hyphens with underscores.
    4. Strip any remaining non-alphanumeric, non-underscore characters.
    5. Collapse consecutive underscores to a single underscore.

    Logs a before/after column mapping dictionary so the transformation
    is fully auditable.

    Args:
        df: The raw ``pd.DataFrame`` returned by ``load_raw_data``.

    Returns:
        A new ``pd.DataFrame`` with normalised snake_case column names
        and identical data.
    """

    def _to_snake(name: str) -> str:
        """Convert a single column name string to snake_case.

        Args:
            name: The original column name string.

        Returns:
            The normalised snake_case column name string.
        """
        name = name.strip().lower()
        name = re.sub(r"[\s\-]+", "_", name)
        name = re.sub(r"[^\w]", "", name)
        name = re.sub(r"_+", "_", name)
        return name.strip("_")

    original_columns: list[str] = df.columns.tolist()
    cleaned_columns: list[str] = [_to_snake(col) for col in original_columns]

    column_mapping: dict[str, str] = dict(zip(original_columns, cleaned_columns))
    logger.info("Column name mapping (original -> snake_case): %s", column_mapping)

    # Return a copy to guarantee immutability of the caller's reference
    renamed_df: pd.DataFrame = df.copy()
    renamed_df.columns = pd.Index(cleaned_columns)

    return renamed_df


def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """Apply data quality checks and enforce correct data types.

    Performs the following operations in sequence:

    1. Drop exact duplicate rows and log the count removed.
    2. Parse ``order_date`` and ``ship_date`` as proper ``datetime64``
       objects using ``pd.to_datetime`` (``dayfirst=False``,
       ``errors='coerce'``).
    3. Log null value counts per column after datetime parsing so
       coercion failures are visible.
    4. Cast ``sales``, ``profit``, ``discount`` to ``float64``.
    5. Cast ``quantity`` to ``int64``.
    6. Drop rows where ``order_id``, ``customer_id``, or ``sales`` is
       null, and log how many rows were removed.

    Args:
        df: A ``pd.DataFrame`` with snake_case column names as returned
            by ``clean_column_names``.

    Returns:
        A fully validated and type-enforced ``pd.DataFrame`` ready for
        database ingestion.

    Raises:
        KeyError: If an expected column (e.g. ``order_date``) is absent,
            indicating a schema mismatch between the CSV and the expected
            21-column Superstore schema.
        ValueError: If a numeric cast fails due to unexpected non-numeric
            data in a column declared as numeric.
    """
    working_df: pd.DataFrame = df.copy()
    initial_row_count: int = len(working_df)

    # ------------------------------------------------------------------
    # Step 1 – Deduplicate
    # ------------------------------------------------------------------
    working_df.drop_duplicates(inplace=True)
    duplicates_removed: int = initial_row_count - len(working_df)
    logger.info(
        "Duplicate rows removed: %d (remaining: %d)",
        duplicates_removed,
        len(working_df),
    )

    # ------------------------------------------------------------------
    # Step 2 – Parse date columns
    # ------------------------------------------------------------------
    for date_col in ("order_date", "ship_date"):
        if date_col not in working_df.columns:
            raise KeyError(
                f"Expected column '{date_col}' not found in DataFrame. "
                "Verify the CSV schema matches the 21-column Superstore format."
            )
        working_df[date_col] = pd.to_datetime(
            working_df[date_col],
            dayfirst=False,
            errors="coerce",
        )
        logger.info(
            "Parsed '%s' as datetime64. Coerced nulls: %d",
            date_col,
            working_df[date_col].isna().sum(),
        )

    # ------------------------------------------------------------------
    # Step 3 – Log null counts per column for full audit trail
    # ------------------------------------------------------------------
    null_counts: pd.Series = working_df.isnull().sum()
    null_report: dict[str, int] = {
        col: int(count) for col, count in null_counts.items() if count > 0
    }
    if null_report:
        logger.info("Null value counts per column (non-zero only): %s", null_report)
    else:
        logger.info("Null value audit: no nulls detected in any column.")

    # ------------------------------------------------------------------
    # Step 4 – Cast numeric columns to the declared types
    # ------------------------------------------------------------------
    float_columns: list[str] = ["sales", "profit", "discount"]
    for col in float_columns:
        if col not in working_df.columns:
            raise KeyError(
                f"Expected numeric column '{col}' not found in DataFrame."
            )
        try:
            working_df[col] = working_df[col].astype("float64")
        except ValueError as exc:
            logger.error(
                "Failed to cast column '%s' to float64: %s", col, exc
            )
            raise

    logger.info(
        "Cast to float64: %s", float_columns
    )

    if "quantity" not in working_df.columns:
        raise KeyError("Expected numeric column 'quantity' not found in DataFrame.")

    try:
        # Round before int cast to handle any residual float representation
        working_df["quantity"] = (
            working_df["quantity"].round(0).astype("int64")
        )
    except ValueError as exc:
        logger.error("Failed to cast column 'quantity' to int64: %s", exc)
        raise

    logger.info("Cast to int64: ['quantity']")

    # ------------------------------------------------------------------
    # Step 5 – Drop rows with null critical key fields
    # ------------------------------------------------------------------
    critical_columns: list[str] = ["order_id", "customer_id", "sales"]
    pre_drop_count: int = len(working_df)
    working_df.dropna(subset=critical_columns, inplace=True)
    rows_dropped: int = pre_drop_count - len(working_df)
    logger.info(
        "Rows dropped due to null in critical columns %s: %d (remaining: %d)",
        critical_columns,
        rows_dropped,
        len(working_df),
    )

    return working_df


def push_to_sqlite(
    df: pd.DataFrame,
    db_path: Path,
    table_name: str,
) -> None:
    """Persist the validated DataFrame to a SQLite database via SQLAlchemy.

    Creates (or replaces) the target table using ``df.to_sql()`` with
    ``if_exists='replace'``, ``index=False``, and ``chunksize=500``.
    The SQLAlchemy engine is used exclusively — the raw ``sqlite3``
    module is not used anywhere in this function.

    Args:
        df: The fully validated ``pd.DataFrame`` to persist.
        db_path: Absolute ``pathlib.Path`` to the ``.db`` file. The
            parent directory must already exist (created by
            ``setup_project.py`` or the module-level bootstrap above).
        table_name: The SQLite table name to write to.

    Returns:
        None

    Raises:
        SQLAlchemyError: If the engine cannot connect to the database or
            if the ``to_sql`` write operation fails.
    """
    connection_string: str = f"sqlite:///{db_path}"
    logger.info(
        "Connecting to SQLite database: %s", db_path
    )

    try:
        engine = create_engine(connection_string, echo=False)

        # Verify connectivity before attempting the bulk write
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        logger.info(
            "Writing %d rows to table '%s' (chunksize=500, if_exists='replace') …",
            len(df),
            table_name,
        )

        df.to_sql(
            name=table_name,
            con=engine,
            if_exists="replace",
            index=False,
            chunksize=500,
        )

        logger.info(
            "Successfully wrote %d rows to '%s' in database: %s",
            len(df),
            table_name,
            db_path,
        )

    except SQLAlchemyError as exc:
        logger.error(
            "SQLAlchemy error while writing to '%s': %s", db_path, exc
        )
        raise
    finally:
        # Dispose engine to release connection pool resources
        try:
            engine.dispose()
            logger.info("SQLAlchemy engine disposed cleanly.")
        except UnboundLocalError:
            # engine was never assigned (error occurred before creation)
            pass


def main() -> None:
    """Orchestrate the full RetailLens ETL ingestion pipeline.

    Calls the four pipeline stages in sequence:

    1. ``load_raw_data``   – Read the raw CSV from ``data/raw/``.
    2. ``clean_column_names`` – Normalise column names to snake_case.
    3. ``validate_data``   – Deduplicate, parse dates, enforce types.
    4. ``push_to_sqlite``  – Write the cleaned data to SQLite.

    Returns:
        None
    """
    logger.info("=" * 60)
    logger.info("  RetailLens ETL Pipeline – START")
    logger.info("  CSV  : %s", CSV_PATH)
    logger.info("  DB   : %s", DB_PATH)
    logger.info("  Table: %s", TABLE_NAME)
    logger.info("=" * 60)

    raw_df: pd.DataFrame = load_raw_data(CSV_PATH)

    clean_df: pd.DataFrame = clean_column_names(raw_df)

    validated_df: pd.DataFrame = validate_data(clean_df)

    push_to_sqlite(validated_df, DB_PATH, TABLE_NAME)

    logger.info("=" * 60)
    logger.info("  RetailLens ETL Pipeline – COMPLETE")
    logger.info("  Final row count persisted: %d", len(validated_df))
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
