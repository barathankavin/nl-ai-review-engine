from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    pass


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_name: Mapped[str] = mapped_column(String, default="Anonymous")
    user_image: Mapped[str] = mapped_column(String, default="")
    review_date: Mapped[str] = mapped_column(String, default="")
    rating: Mapped[int] = mapped_column(Integer, default=0)
    score_text: Mapped[str] = mapped_column(String, default="")
    url: Mapped[str] = mapped_column(String, default="")
    title: Mapped[str] = mapped_column(String, default="")
    review_text: Mapped[str] = mapped_column(Text, default="")
    cleaned_text: Mapped[str] = mapped_column(Text, default="")
    reply_date: Mapped[str] = mapped_column(String, default="")
    reply_text: Mapped[str] = mapped_column(String, default="")
    app_version: Mapped[str] = mapped_column(String, default="")
    thumbs_up: Mapped[int] = mapped_column(Integer, default=0)
    criterias: Mapped[str] = mapped_column(Text, default="")
    lang: Mapped[str] = mapped_column(String, default="en")
    cluster_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    theme_id: Mapped[str | None] = mapped_column(String, ForeignKey("themes.id"), nullable=True)
    ingested_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class ReviewEmbedding(Base):
    __tablename__ = "review_embeddings"

    review_id: Mapped[str] = mapped_column(String, ForeignKey("reviews.id"), primary_key=True)
    vector: Mapped[bytes] = mapped_column(LargeBinary)


class Theme(Base):
    __tablename__ = "themes"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    cluster_id: Mapped[int] = mapped_column(Integer, index=True)
    label: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text, default="")
    sentiment_label: Mapped[str] = mapped_column(String, default="neutral")
    sentiment_score: Mapped[float] = mapped_column(Float, default=0.0)
    representative_quotes: Mapped[list] = mapped_column(JSON, default=list)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    first_seen: Mapped[str] = mapped_column(String, default="")
    last_seen: Mapped[str] = mapped_column(String, default="")
    status: Mapped[str] = mapped_column(String, default="active")
    labeled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    label_cache_key: Mapped[str] = mapped_column(String, default="")

    metrics: Mapped["ThemeMetric | None"] = relationship(back_populates="theme", uselist=False)


class ThemeMetric(Base):
    __tablename__ = "theme_metrics"

    theme_id: Mapped[str] = mapped_column(String, ForeignKey("themes.id"), primary_key=True)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    volume_pct: Mapped[float] = mapped_column(Float, default=0.0)
    avg_rating: Mapped[float] = mapped_column(Float, default=0.0)
    sentiment_avg: Mapped[float] = mapped_column(Float, default=0.0)
    trend: Mapped[str] = mapped_column(String, default="stable")
    severity_score: Mapped[float] = mapped_column(Float, default=0.0)
    current_window_count: Mapped[int] = mapped_column(Integer, default=0)
    prior_window_count: Mapped[int] = mapped_column(Integer, default=0)

    theme: Mapped["Theme"] = relationship(back_populates="metrics")


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    started_at: Mapped[datetime] = mapped_column(DateTime)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    rows_ingested: Mapped[int] = mapped_column(Integer, default=0)
    new_clusters: Mapped[int] = mapped_column(Integer, default=0)
    themes_relabeled: Mapped[int] = mapped_column(Integer, default=0)
    groq_calls: Mapped[int] = mapped_column(Integer, default=0)
    failures: Mapped[str] = mapped_column(Text, default="")
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    success: Mapped[bool] = mapped_column(Boolean, default=True)


class ChatLog(Base):
    __tablename__ = "chat_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    query: Mapped[str] = mapped_column(Text)
    intent: Mapped[str] = mapped_column(String, default="")
    answer: Mapped[str] = mapped_column(Text, default="")
    citations: Mapped[list] = mapped_column(JSON, default=list)
    citations_valid: Mapped[bool] = mapped_column(Boolean, default=False)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


def get_engine():
    settings = get_settings()
    db_path = settings.database_url.replace("sqlite:///", "")
    if db_path.startswith("./"):
        db_file = Path(db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
    connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
    return create_engine(settings.database_url, connect_args=connect_args)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def init_db() -> None:
    Base.metadata.create_all(bind=get_engine())


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
