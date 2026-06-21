import json

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import Review, Theme, ThemeMetric
from app.pipeline.embed_cluster import search_similar_reviews


def _query_expansions(query: str) -> list[str]:
    lowered = query.lower()
    expansions = [query]

    if any(word in lowered for word in ["discover", "new music", "find music"]):
        expansions.extend([
            "hard to discover new music find new artists",
            "cannot find new songs explore music",
        ])

    if any(word in lowered for word in ["recommendation", "recommended", "algorithm"]):
        expansions.extend([
            "bad recommendations wrong songs suggested",
            "recommendation algorithm playlist suggestions irrelevant",
        ])

    if any(word in lowered for word in ["repeat", "same content", "same song", "loop"]):
        expansions.extend([
            "same songs repeat again shuffle plays same",
            "keep hearing same music daily mix repeat",
        ])

    if any(word in lowered for word in ["behavior", "trying to achieve", "listening"]):
        expansions.extend([
            "how I use spotify listening habits daily",
            "want to listen mood workout sleep focus",
        ])

    if any(word in lowered for word in ["segment", "different users", "premium", "free"]):
        expansions.extend([
            "premium free plan india student family",
            "different experience compared to other users",
        ])

    if any(word in lowered for word in ["unmet", "need", "frustration", "struggle", "complain"]):
        expansions.extend([
            "missing feature wish need want frustrated",
            "problem issue annoying hate spotify",
        ])

    return list(dict.fromkeys(expansions))


def build_dataset_summary(db: Session) -> str:
    total = db.query(Review).count()
    if total == 0:
        return "No reviews ingested yet."

    avg_rating = db.query(func.avg(Review.rating)).scalar() or 0
    rating_counts = (
        db.query(Review.rating, func.count(Review.id))
        .group_by(Review.rating)
        .order_by(Review.rating)
        .all()
    )
    with_reply = db.query(Review).filter(Review.reply_text != "").count()
    lang_counts = (
        db.query(Review.lang, func.count(Review.id))
        .group_by(Review.lang)
        .order_by(func.count(Review.id).desc())
        .limit(5)
        .all()
    )

    lines = [
        f"total_reviews={total}",
        f"average_rating={avg_rating:.2f}",
        f"reviews_with_developer_reply={with_reply}",
        "rating_distribution=" + ", ".join(f"{rating}star:{count}" for rating, count in rating_counts),
        "languages=" + ", ".join(f"{lang}:{count}" for lang, count in lang_counts),
    ]
    return "\n".join(lines)


def build_theme_context(db: Session, limit: int | None = 10) -> tuple[str, list[str]]:
    query = (
        db.query(Theme, ThemeMetric)
        .join(ThemeMetric, ThemeMetric.theme_id == Theme.id, isouter=True)
        .filter(Theme.status == "active")
        .order_by(ThemeMetric.severity_score.desc())
    )
    if limit:
        query = query.limit(limit)
    rows = query.all()

    blocks = []
    theme_ids: list[str] = []
    for theme, metric in rows:
        theme_ids.append(theme.id)
        blocks.append(
            "\n".join(
                [
                    f"theme_id={theme.id}",
                    f"label={theme.label}",
                    f"description={theme.description}",
                    f"review_count={metric.review_count if metric else theme.review_count}",
                    f"volume_pct={metric.volume_pct if metric else 0:.1f}%",
                    f"trend={metric.trend if metric else 'stable'}",
                    f"sentiment={theme.sentiment_label} ({theme.sentiment_score:.2f})",
                    f"avg_rating={metric.avg_rating if metric else 0:.1f}",
                    f"representative_quotes={json.dumps(theme.representative_quotes[:4])}",
                ]
            )
        )
    return "\n\n".join(blocks), theme_ids


def build_review_context(reviews: list[Review]) -> tuple[str, list[str]]:
    blocks = []
    review_ids: list[str] = []
    for review in reviews:
        review_ids.append(review.id)
        blocks.append(
            "\n".join(
                [
                    f"review_id={review.id}",
                    f"rating={review.rating}",
                    f"date={review.review_date}",
                    f"version={review.app_version}",
                    f"thumbs_up={review.thumbs_up}",
                    f"text={review.review_text[:320]}",
                ]
            )
        )
    return "\n---\n".join(blocks), review_ids


def retrieve_reviews_for_query(db: Session, query: str, limit: int = 8) -> list[Review]:
    return search_similar_reviews(db, query, limit=limit)


def retrieve_multi_query_reviews(db: Session, query: str, per_query: int = 6, max_total: int = 24) -> list[Review]:
    seen: set[str] = set()
    collected: list[Review] = []

    for expansion in _query_expansions(query):
        for review in search_similar_reviews(db, expansion, limit=per_query):
            if review.id in seen:
                continue
            seen.add(review.id)
            collected.append(review)
            if len(collected) >= max_total:
                return collected

    return collected


def build_rating_segment_samples(db: Session) -> str:
    """Surface low vs high rating voices for segment-style questions."""
    segments = []
    for label, ratings in [("low_rating_1_2", [1, 2]), ("mid_rating_3", [3]), ("high_rating_4_5", [4, 5])]:
        reviews = (
            db.query(Review)
            .filter(Review.rating.in_(ratings), Review.review_text != "")
            .order_by(Review.thumbs_up.desc())
            .limit(3)
            .all()
        )
        if not reviews:
            continue
        snippets = [f"review #{r.id} ({r.rating}★): {r.review_text[:160]}" for r in reviews]
        segments.append(f"{label}:\n" + "\n".join(snippets))
    return "\n\n".join(segments)


def build_analysis_context(db: Session, query: str) -> tuple[str, list[str]]:
    summary = build_dataset_summary(db)
    themes, theme_ids = build_theme_context(db, limit=None)
    reviews = retrieve_multi_query_reviews(db, query)
    review_context, review_ids = build_review_context(reviews)
    segments = build_rating_segment_samples(db)

    context = "\n\n".join(
        [
            "=== DATASET SUMMARY ===",
            summary,
            "=== DISCOVERED THEMES ===",
            themes or "No themes available.",
            "=== RELEVANT REVIEWS (semantic retrieval) ===",
            review_context or "No matching reviews found.",
            "=== RATING SEGMENT SAMPLES ===",
            segments or "No segment samples available.",
        ]
    )
    return context, review_ids + theme_ids
