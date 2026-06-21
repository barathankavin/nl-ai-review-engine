from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.models import ChatLog, PipelineRun, Review, Theme, ThemeMetric, get_db, init_db
from app.pipeline.orchestrator import run_pipeline
from app.rag.chat import answer_query, get_chat_status

router = APIRouter(prefix="/api/v1")


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    answer: str
    citations: list[str]
    intent: str
    citations_valid: bool
    groq_enabled: bool = False


@router.get("/health")
def health(db: Session = Depends(get_db)):
    review_count = db.query(Review).count()
    theme_count = db.query(Theme).filter(Theme.status == "active").count()
    chat_status = get_chat_status()
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "reviews": review_count,
        "themes": theme_count,
        "groq_enabled": chat_status["groq_enabled"],
        "groq_model": chat_status["groq_model"],
    }


@router.get("/chat/status")
def chat_status():
    return get_chat_status()


@router.post("/refresh")
def refresh(db: Session = Depends(get_db)):
    try:
        run = run_pipeline(db)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "run_id": run.id,
        "success": run.success,
        "rows_ingested": run.rows_ingested,
        "new_clusters": run.new_clusters,
        "themes_relabeled": run.themes_relabeled,
        "groq_calls": run.groq_calls,
        "latency_ms": run.latency_ms,
    }


@router.get("/themes")
def list_themes(db: Session = Depends(get_db)):
    rows = (
        db.query(Theme, ThemeMetric)
        .join(ThemeMetric, ThemeMetric.theme_id == Theme.id, isouter=True)
        .filter(Theme.status == "active")
        .order_by(ThemeMetric.severity_score.desc())
        .all()
    )

    return [
        {
            "id": theme.id,
            "label": theme.label,
            "description": theme.description,
            "sentiment_label": theme.sentiment_label,
            "sentiment_score": theme.sentiment_score,
            "review_count": metric.review_count if metric else theme.review_count,
            "volume_pct": metric.volume_pct if metric else 0,
            "avg_rating": metric.avg_rating if metric else 0,
            "trend": metric.trend if metric else "stable",
            "severity_score": metric.severity_score if metric else 0,
            "representative_quotes": theme.representative_quotes,
        }
        for theme, metric in rows
    ]


@router.get("/themes/{theme_id}/reviews")
def theme_reviews(theme_id: str, db: Session = Depends(get_db)):
    theme = db.get(Theme, theme_id)
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")

    reviews = (
        db.query(Review)
        .filter(Review.theme_id == theme_id)
        .order_by(Review.review_date.desc())
        .all()
    )

    return {
        "theme": {
            "id": theme.id,
            "label": theme.label,
            "description": theme.description,
        },
        "reviews": [
            {
                "id": review.id,
                "userName": review.user_name,
                "userImage": review.user_image,
                "date": review.review_date,
                "score": review.rating,
                "scoreText": review.score_text,
                "url": review.url,
                "title": review.title,
                "text": review.review_text,
                "replyDate": review.reply_date,
                "replyText": review.reply_text,
                "version": review.app_version,
                "thumbsUp": review.thumbs_up,
                "criterias": review.criterias,
            }
            for review in reviews
        ],
    }


@router.get("/reviews")
def list_reviews(db: Session = Depends(get_db)):
    reviews = db.query(Review).order_by(Review.review_date.desc()).all()
    return [
        {
            "id": review.id,
            "userName": review.user_name,
            "userImage": review.user_image,
            "date": review.review_date,
            "score": review.rating,
            "scoreText": review.score_text,
            "url": review.url,
            "title": review.title,
            "text": review.review_text,
            "replyDate": review.reply_date,
            "replyText": review.reply_text,
            "version": review.app_version,
            "thumbsUp": review.thumbs_up,
            "criterias": review.criterias,
            "theme_id": review.theme_id,
        }
        for review in reviews
    ]


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    if not payload.query.strip():
        raise HTTPException(status_code=400, detail="Query is required")
    result = answer_query(db, payload.query.strip())
    return ChatResponse(**result)


@router.get("/runs")
def list_runs(db: Session = Depends(get_db)):
    runs = db.query(PipelineRun).order_by(PipelineRun.started_at.desc()).limit(10).all()
    return [
        {
            "id": run.id,
            "started_at": run.started_at.isoformat(),
            "finished_at": run.finished_at.isoformat() if run.finished_at else None,
            "rows_ingested": run.rows_ingested,
            "new_clusters": run.new_clusters,
            "themes_relabeled": run.themes_relabeled,
            "groq_calls": run.groq_calls,
            "latency_ms": run.latency_ms,
            "success": run.success,
            "failures": run.failures,
        }
        for run in runs
    ]


@router.get("/chat/logs")
def chat_logs(db: Session = Depends(get_db)):
    logs = db.query(ChatLog).order_by(ChatLog.created_at.desc()).limit(20).all()
    return [
        {
            "id": log.id,
            "query": log.query,
            "intent": log.intent,
            "citations_valid": log.citations_valid,
            "latency_ms": log.latency_ms,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]


def create_app():
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    init_db()
    app = FastAPI(title="Review Discovery Engine API", version="1.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    return app
