import csv
import hashlib
import io
import re
from datetime import datetime, timezone

import httpx
from langdetect import LangDetectException, detect
from sqlalchemy.orm import Session

from app.config import get_source_config
from app.db.models import Review


def _clean_text(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _detect_lang(text: str) -> str:
    if not text.strip():
        return "unknown"
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"


def _fallback_id(row: dict, fields: list[str]) -> str:
    payload = "|".join(str(row.get(field, "")) for field in fields)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]


def fetch_sheet_rows() -> list[dict[str, str]]:
    config = get_source_config()
    url = config["sheet"]["csv_url"]
    response = httpx.get(url, timeout=60.0, follow_redirects=True)
    response.raise_for_status()
    reader = csv.DictReader(io.StringIO(response.text))
    return [dict(row) for row in reader]


def validate_schema(rows: list[dict[str, str]]) -> None:
    config = get_source_config()
    required = list(config["column_mapping"].keys())
    if not rows:
        return
    missing = [column for column in required if column not in rows[0]]
    if missing:
        raise ValueError(f"Sheet schema drift: missing columns {missing}")


def normalize_row(row: dict[str, str]) -> dict:
    config = get_source_config()
    dedupe = config["dedupe"]

    review_id = (row.get(dedupe["primary_key"]) or "").strip()
    if not review_id:
        review_id = _fallback_id(row, dedupe["fallback_hash_fields"])

    review_text = _clean_text(row.get("text", ""))
    rating_raw = row.get("score", "0")
    try:
        rating = int(float(rating_raw))
    except ValueError:
        rating = 0

    try:
        thumbs_up = int(float(row.get("thumbsUp") or 0))
    except ValueError:
        thumbs_up = 0

    lang = _detect_lang(review_text)

    return {
        "id": review_id,
        "user_name": (row.get("userName") or "Anonymous").strip(),
        "user_image": (row.get("userImage") or "").strip(),
        "review_date": (row.get("date") or "").strip(),
        "rating": rating,
        "score_text": (row.get("scoreText") or "").strip(),
        "url": (row.get("url") or "").strip(),
        "title": (row.get("title") or "").strip(),
        "review_text": review_text,
        "cleaned_text": review_text,
        "reply_date": (row.get("replyDate") or "").strip(),
        "reply_text": _clean_text(row.get("replyText", "")),
        "app_version": (row.get("version") or "").strip(),
        "thumbs_up": thumbs_up,
        "criterias": (row.get("criterias") or "").strip(),
        "lang": lang,
        "ingested_at": datetime.now(timezone.utc),
    }


def ingest_reviews(db: Session) -> int:
    rows = fetch_sheet_rows()
    validate_schema(rows)
    inserted = 0

    for row in rows:
        normalized = normalize_row(row)
        if not normalized["review_text"] and not normalized["id"]:
            continue

        existing = db.get(Review, normalized["id"])
        if existing:
            continue

        db.add(Review(**normalized))
        inserted += 1

    db.commit()
    return inserted
