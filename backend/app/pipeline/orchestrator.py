import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models import PipelineRun


@dataclass(frozen=True)
class PipelineRunResult:
    id: str
    success: bool
    rows_ingested: int
    new_clusters: int
    themes_relabeled: int
    groq_calls: int
    latency_ms: int
    failures: str


def run_pipeline(db: Session) -> PipelineRunResult:
    from app.pipeline.embed_cluster import embed_and_cluster
    from app.pipeline.ingest import ingest_reviews
    from app.pipeline.label import label_themes
    from app.pipeline.quantify import quantify_themes

    run_id = str(uuid.uuid4())
    started = datetime.now(timezone.utc)
    timer = time.perf_counter()
    groq_calls = 0
    failures = ""

    run = PipelineRun(id=run_id, started_at=started, success=True)
    db.add(run)
    db.commit()

    try:
        rows_ingested = ingest_reviews(db)
        _, new_clusters = embed_and_cluster(db)
        relabeled, groq_calls = label_themes(db)
        quantify_themes(db)

        run.rows_ingested = rows_ingested
        run.new_clusters = new_clusters
        run.themes_relabeled = relabeled
        run.groq_calls = groq_calls
    except Exception as exc:  # noqa: BLE001
        run.success = False
        failures = str(exc)
        run.failures = failures
        db.commit()
        raise
    finally:
        run.finished_at = datetime.now(timezone.utc)
        run.latency_ms = int((time.perf_counter() - timer) * 1000)
        run.failures = failures
        db.commit()
        db.refresh(run)

    return PipelineRunResult(
        id=run.id,
        success=run.success,
        rows_ingested=run.rows_ingested,
        new_clusters=run.new_clusters,
        themes_relabeled=run.themes_relabeled,
        groq_calls=run.groq_calls,
        latency_ms=run.latency_ms,
        failures=run.failures,
    )
