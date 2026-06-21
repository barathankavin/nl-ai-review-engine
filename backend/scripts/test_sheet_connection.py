#!/usr/bin/env python3
"""Phase 0: verify Google Sheet connectivity and schema."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import get_source_config
from app.pipeline.ingest import fetch_sheet_rows, validate_schema


def main() -> None:
    config = get_source_config()
    rows = fetch_sheet_rows()
    validate_schema(rows)
    print(f"Sheet OK: {config['sheet']['name']}")
    print(f"Rows fetched: {len(rows)}")
    if rows:
        print(f"Columns: {', '.join(rows[0].keys())}")


if __name__ == "__main__":
    main()
