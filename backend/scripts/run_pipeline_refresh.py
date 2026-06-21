#!/usr/bin/env python3
"""Run the full ingest → embed → label → quantify pipeline."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.models import SessionLocal, init_db
from app.pipeline.orchestrator import run_pipeline


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        run = run_pipeline(db)
        print(
            "Pipeline OK: "
            f"ingested={run.rows_ingested}, "
            f"clusters={run.new_clusters}, "
            f"themes={run.themes_relabeled}, "
            f"groq={run.groq_calls}, "
            f"success={run.success}"
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
