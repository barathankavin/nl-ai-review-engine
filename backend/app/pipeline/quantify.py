from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.config import get_source_config
from app.db.models import Review, Theme, ThemeMetric


def _parse_date(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def quantify_themes(db: Session) -> int:
    config = get_source_config()
    window_days = config["quantify"]["trend_window_days"]
    now = datetime.now(timezone.utc)
    current_start = now - timedelta(days=window_days)
    prior_start = now - timedelta(days=window_days * 2)

    total_reviews = db.query(Review).count()
    all_ratings = [review.rating for review in db.query(Review).all() if review.rating]
    product_avg_rating = sum(all_ratings) / len(all_ratings) if all_ratings else 3.0

    themes = db.query(Theme).filter(Theme.status == "active").all()
    updated = 0

    for theme in themes:
        reviews = db.query(Review).filter(Review.theme_id == theme.id).all()
        if not reviews:
            continue

        ratings = [review.rating for review in reviews if review.rating]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0.0
        sentiment_avg = theme.sentiment_score

        current_count = 0
        prior_count = 0
        for review in reviews:
            review_date = _parse_date(review.review_date)
            if not review_date:
                continue
            if review_date >= current_start:
                current_count += 1
            elif prior_start <= review_date < current_start:
                prior_count += 1

        if current_count > prior_count * 1.2 and current_count >= 3:
            trend = "emerging"
        elif current_count < prior_count * 0.8 and prior_count >= 3:
            trend = "declining"
        elif current_count >= prior_count * 1.5 and current_count >= 5:
            trend = "spike"
        else:
            trend = "stable"

        negative_weight = max(0.0, (3 - avg_rating) / 2)
        rating_gap = max(0.0, product_avg_rating - avg_rating)
        severity = negative_weight * len(reviews) * (1 + rating_gap)

        metric = db.get(ThemeMetric, theme.id)
        if not metric:
            metric = ThemeMetric(theme_id=theme.id)
            db.add(metric)

        metric.review_count = len(reviews)
        metric.volume_pct = (len(reviews) / total_reviews * 100) if total_reviews else 0.0
        metric.avg_rating = avg_rating
        metric.sentiment_avg = sentiment_avg
        metric.trend = trend
        metric.severity_score = round(severity, 2)
        metric.current_window_count = current_count
        metric.prior_window_count = prior_count

        theme.review_count = len(reviews)
        updated += 1

    db.commit()
    return updated
