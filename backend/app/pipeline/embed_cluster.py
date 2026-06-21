import pickle
import uuid
from datetime import datetime, timezone

import hdbscan
import numpy as np
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session

from app.config import get_source_config
from app.db.models import Review, ReviewEmbedding


class Embedder:
    _model: SentenceTransformer | None = None

    @classmethod
    def get_model(cls) -> SentenceTransformer:
        if cls._model is None:
            config = get_source_config()
            cls._model = SentenceTransformer(config["clustering"]["embedding_model"])
        return cls._model


def embed_and_cluster(db: Session) -> tuple[int, int]:
    config = get_source_config()
    english_reviews = (
        db.query(Review)
        .filter(Review.lang == "en", Review.review_text != "")
        .order_by(Review.review_date.desc())
        .all()
    )

    if len(english_reviews) < config["clustering"]["min_cluster_size"]:
        return 0, 0

    model = Embedder.get_model()
    texts = [review.cleaned_text or review.review_text for review in english_reviews]
    vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)

    for review, vector in zip(english_reviews, vectors, strict=True):
        existing = db.get(ReviewEmbedding, review.id)
        payload = pickle.dumps(np.asarray(vector, dtype=np.float32))
        if existing:
            existing.vector = payload
        else:
            db.add(ReviewEmbedding(review_id=review.id, vector=payload))

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=config["clustering"]["min_cluster_size"],
        min_samples=config["clustering"]["min_samples"],
        metric="euclidean",
    )
    labels = clusterer.fit_predict(vectors)

    new_clusters = len({label for label in labels if label >= 0})
    for review, label in zip(english_reviews, labels, strict=True):
        review.cluster_id = int(label) if label >= 0 else None
        review.theme_id = None

    db.commit()
    return len(english_reviews), new_clusters


def get_review_vectors(db: Session, review_ids: list[str]) -> dict[str, np.ndarray]:
    rows = db.query(ReviewEmbedding).filter(ReviewEmbedding.review_id.in_(review_ids)).all()
    return {row.review_id: pickle.loads(row.vector) for row in rows}


def search_similar_reviews(db: Session, query: str, limit: int = 8) -> list[Review]:
    english_reviews = db.query(Review).filter(Review.lang == "en", Review.review_text != "").all()
    if not english_reviews:
        return []

    model = Embedder.get_model()
    query_vector = model.encode([query], normalize_embeddings=True)[0]

    scored: list[tuple[float, Review]] = []
    for review in english_reviews:
        embedding = db.get(ReviewEmbedding, review.id)
        if not embedding:
            continue
        vector = pickle.loads(embedding.vector)
        score = float(np.dot(query_vector, vector))
        scored.append((score, review))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [review for _, review in scored[:limit]]
