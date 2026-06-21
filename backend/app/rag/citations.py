import re

from sqlalchemy.orm import Session

from app.db.models import Review


def validate_citations(db: Session, answer: str, citations: list[str]) -> bool:
    if not citations:
        return True

    for citation in citations:
        review = db.get(Review, citation)
        if review:
            continue
        # Allow short-id prefixes matching full UUIDs
        matches = (
            db.query(Review)
            .filter(Review.id.like(f"{citation}%"))
            .limit(1)
            .all()
        )
        if not matches:
            return False
    return True


def extract_review_ids(text: str) -> list[str]:
    return list(dict.fromkeys(re.findall(r"review[_ ]#?([A-Za-z0-9-]+)", text)))
