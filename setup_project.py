"""
setup_project.py
----------------
RetailLens – Phase 1 Project Bootstrap Script.

Run this script once from the project root to scaffold the full
directory structure and stage the raw data file for ingestion.

Usage:
    python setup_project.py

Author: RetailLens Analytics Team
"""

import shutil
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Directory manifest
# ---------------------------------------------------------------------------
PROJECT_ROOT: Path = Path(__file__).parent.resolve()

DIRECTORIES: list[Path] = [
    PROJECT_ROOT / "data" / "raw",
    PROJECT_ROOT / "data" / "processed",
    PROJECT_ROOT / "src",
    PROJECT_ROOT / "notebooks",
    PROJECT_ROOT / "outputs" / "charts",
    PROJECT_ROOT / "logs",
]

# Source CSV expected at the project root
SOURCE_CSV: Path = PROJECT_ROOT / "Superstore.csv"
# Destination for the raw data copy
DEST_CSV: Path = PROJECT_ROOT / "data" / "raw" / "Superstore.csv"


def create_directories(directories: list[Path]) -> None:
    """Create all required project directories.

    Creates each directory (and any necessary parent directories) using
    ``exist_ok=True`` so the script is safely idempotent. Prints a
    confirmation message for every directory processed.

    Args:
        directories: An ordered list of ``pathlib.Path`` objects representing
            the directories to create.

    Returns:
        None
    """
    print("\n" + "=" * 60)
    print("  RetailLens – Project Directory Bootstrap")
    print("=" * 60)
    print(f"\nProject root: {PROJECT_ROOT}\n")

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        # Compute a display-friendly relative path for readability
        relative = directory.relative_to(PROJECT_ROOT)
        print(f"  [OK] Created (or verified): {relative}/")

    print("\nAll directories are in place.")


def stage_raw_data(source: Path, destination: Path) -> None:
    """Copy the source CSV into the raw data directory.

    Behaviour:
        - If ``destination`` already exists, the copy is skipped silently
          to avoid overwriting a file that may already have been staged.
        - If ``source`` does not exist at the project root, a clear warning
          is printed to *stderr* and the script continues without raising;
          the user must place the file manually before running the ingestion
          pipeline.
        - On any unexpected OS-level error during the copy, the exception
          message is printed to *stderr* and the script exits with code 1.

    Args:
        source: Absolute ``Path`` to ``Superstore.csv`` at the project root.
        destination: Absolute ``Path`` for the staged copy inside
            ``data/raw/``.

    Returns:
        None
    """
    print("\n" + "-" * 60)
    print("  Staging Raw Data File")
    print("-" * 60)

    if not source.exists():
        print(
            f"\n  [WARNING] Source file not found: {source}\n"
            "  Please place 'Superstore.csv' in the project root and\n"
            "  re-run this script, or copy the file manually to:\n"
            f"  {destination}",
            file=sys.stderr,
        )
        return

    if destination.exists():
        print(
            f"\n  [SKIPPED] Destination already exists – no overwrite:\n"
            f"  {destination}"
        )
        return

    try:
        shutil.copy2(source, destination)
        print(
            f"\n  [OK] Copied '{source.name}' to:\n"
            f"  {destination}"
        )
    except OSError as exc:
        print(
            f"\n  [ERROR] Failed to copy '{source.name}':\n  {exc}",
            file=sys.stderr,
        )
        sys.exit(1)


def print_summary() -> None:
    """Print a final structured summary of the project layout.

    Walks the project root and prints the resolved directory tree so the
    user can visually confirm the scaffold is correct.

    Returns:
        None
    """
    print("\n" + "=" * 60)
    print("  RetailLens – Directory Structure Summary")
    print("=" * 60)

    for path in sorted(PROJECT_ROOT.rglob("*")):
        # Skip hidden files and __pycache__ artefacts
        if any(part.startswith(".") for part in path.parts):
            continue
        if "__pycache__" in path.parts:
            continue

        relative = path.relative_to(PROJECT_ROOT)
        depth = len(relative.parts) - 1
        indent = "    " * depth
        prefix = "├── " if path.is_file() else "└── "
        label = path.name + ("/" if path.is_dir() else "")
        print(f"  {indent}{prefix}{label}")

    print("\n  Setup complete. You may now run: python src/ingest_data.py\n")


def main() -> None:
    """Entry point for the RetailLens project bootstrap script.

    Orchestrates directory creation, raw data staging, and prints a final
    directory tree summary to confirm the scaffold is correct.

    Returns:
        None
    """
    create_directories(DIRECTORIES)
    stage_raw_data(SOURCE_CSV, DEST_CSV)
    print_summary()


if __name__ == "__main__":
    main()
