import json
import uuid
from datetime import datetime, timezone

from groq import Groq
from sqlalchemy.orm import Session

from app.config import get_settings, get_source_config
from app.db.models import Review, Theme


def _fallback_label(cluster_id: int, reviews: list[Review]) -> dict:
    sample = reviews[0]
    keywords = " ".join(sample.review_text.split()[:8])
    avg_rating = sum(review.rating for review in reviews) / max(len(reviews), 1)
    sentiment = "negative" if avg_rating <= 2 else "positive" if avg_rating >= 4 else "neutral"
    return {
        "theme_name": f"Theme {cluster_id}: {keywords[:48]}",
        "one_line_description": f"Cluster of {len(reviews)} reviews with average rating {avg_rating:.1f}.",
        "sentiment_label": sentiment,
        "sentiment_score": (avg_rating - 3) / 2,
        "representative_quotes": [
            {"review_id": review.id, "quote": review.review_text[:180]}
            for review in reviews[:3]
        ],
    }


def _groq_label(cluster_id: int, reviews: list[Review]) -> dict:
    settings = get_settings()
    if not settings.groq_api_key:
        return _fallback_label(cluster_id, reviews)

    config = get_source_config()
    sample_lines = []
    for review in reviews[: config["labeling"]["sample_size"]]:
        sample_lines.append(
            f"- review_id={review.id}; rating={review.rating}; date={review.review_date}; text={review.review_text[:240]}"
        )

    prompt = (
        "You label review clusters. Return strict JSON only with keys: "
        "theme_name, one_line_description, sentiment_label, sentiment_score, representative_quotes. "
        "representative_quotes is an array of objects with review_id and quote.\n\n"
        f"Cluster {cluster_id} sample reviews:\n" + "\n".join(sample_lines)
    )

    client = Groq(api_key=settings.groq_api_key)
    completion = client.chat.completions.create(
        model=settings.groq_model,
        temperature=0.1,
        messages=[
            {"role": "system", "content": "Return valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )
    content = completion.choices[0].message.content or "{}"
    return json.loads(content)


def label_themes(db: Session) -> tuple[int, int]:
    config = get_source_config()
    groq_calls = 0
    relabeled = 0

    cluster_ids = (
        db.query(Review.cluster_id)
        .filter(Review.cluster_id.isnot(None))
        .distinct()
        .all()
    )

    for (cluster_id,) in cluster_ids:
        reviews = (
            db.query(Review)
            .filter(Review.cluster_id == cluster_id)
            .order_by(Review.review_date.desc())
            .all()
        )
        if not reviews:
            continue

        cache_key = f"{cluster_id}:{len(reviews)}"
        theme = db.query(Theme).filter(Theme.cluster_id == cluster_id, Theme.status == "active").first()

        if theme and theme.label_cache_key == cache_key:
            for review in reviews:
                review.theme_id = theme.id
            continue

        if theme and theme.review_count:
            growth = (len(reviews) - theme.review_count) / theme.review_count
            if growth < config["labeling"]["relabel_growth_threshold"] and theme.label:
                theme.review_count = len(reviews)
                for review in reviews:
                    review.theme_id = theme.id
                continue

        payload = _groq_label(cluster_id, reviews)
        if get_settings().groq_api_key:
            groq_calls += 1

        theme_id = theme.id if theme else f"theme-{cluster_id}-{uuid.uuid4().hex[:8]}"
        dates = [review.review_date for review in reviews if review.review_date]
        record = theme or Theme(id=theme_id, cluster_id=cluster_id)
        record.label = payload.get("theme_name", f"Theme {cluster_id}")
        record.description = payload.get("one_line_description", "")
        record.sentiment_label = payload.get("sentiment_label", "neutral")
        record.sentiment_score = float(payload.get("sentiment_score", 0))
        record.representative_quotes = payload.get("representative_quotes", [])
        record.review_count = len(reviews)
        record.first_seen = min(dates) if dates else ""
        record.last_seen = max(dates) if dates else ""
        record.status = "active"
        record.labeled_at = datetime.now(timezone.utc)
        record.label_cache_key = cache_key

        if not theme:
            db.add(record)

        for review in reviews:
            review.theme_id = record.id

        relabeled += 1

    db.commit()
    return relabeled, groq_calls
