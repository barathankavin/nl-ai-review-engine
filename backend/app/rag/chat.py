import re
import time
import uuid

from groq import Groq
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.models import ChatLog
from app.rag.citations import validate_citations
from app.rag.prompts import DISCOVERY_ANALYST_PROMPT, DRILL_DOWN_PROMPT, GENERAL_REVIEW_PROMPT
from app.rag.retriever import (
    build_analysis_context,
    build_dataset_summary,
    build_review_context,
    build_theme_context,
    retrieve_reviews_for_query,
)
from app.rag.router import classify_intent


def _extract_citations(answer: str, known_ids: list[str] | None = None) -> list[str]:
    sources_match = re.search(r"Sources?:\s*(.+)$", answer, re.IGNORECASE | re.MULTILINE)
    if sources_match:
        parts = re.split(r"[,;]\s*", sources_match.group(1).strip())
        cleaned = [part.replace("review #", "").strip() for part in parts if part.strip()]
        return list(dict.fromkeys(cleaned))

    found = list(
        dict.fromkeys(
            re.findall(
                r"review[_ ]#?([0-9a-fA-F-]{8,})",
                answer,
                flags=re.IGNORECASE,
            )
        )
    )
    if found:
        return found
    if known_ids:
        return [review_id[:8] for review_id in known_ids[:6]]
    return []


def _groq_missing_message() -> str:
    return (
        "Groq LLM is not configured. Add your API key to `backend/.env`:\n\n"
        "GROQ_API_KEY=your_key_here\n\n"
        "Get a free key at https://console.groq.com — then restart the backend server."
    )


def _call_groq(system_prompt: str, user_content: str) -> str:
    settings = get_settings()
    if not settings.groq_api_key:
        raise RuntimeError(_groq_missing_message())

    client = Groq(api_key=settings.groq_api_key)
    completion = client.chat.completions.create(
        model=settings.groq_model,
        temperature=0.2,
        max_tokens=1200,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
    )
    return completion.choices[0].message.content or ""


def answer_query(db: Session, query: str) -> dict:
    settings = get_settings()
    started = time.perf_counter()
    intent = classify_intent(query)
    known_ids: list[str] = []

    if intent == "out_of_scope":
        answer = (
            "I can explain what Spotify Play Store reviewers say about discovery, recommendations, "
            "and listening behavior — but I can't make business decisions like discontinuing products "
            "or revenue forecasts. Try one of the suggested discovery questions instead."
        )
        return _log_and_return(db, query, intent, answer, [], True, started)

    if not settings.groq_api_key:
        answer = _groq_missing_message()
        return _log_and_return(db, query, intent, answer, [], True, started)

    try:
        if intent == "discovery_analysis":
            context, known_ids = build_analysis_context(db, query)
            system_prompt = DISCOVERY_ANALYST_PROMPT
            user_content = f"Question: {query}\n\nContext:\n{context}"

        elif intent == "drill_down":
            reviews = retrieve_reviews_for_query(db, query, limit=12)
            context, known_ids = build_review_context(reviews)
            if not context.strip():
                answer = "I don't have enough review data on that yet. Run Refresh pipeline first."
                return _log_and_return(db, query, intent, answer, [], True, started)
            system_prompt = DRILL_DOWN_PROMPT
            user_content = f"Question: {query}\n\nReview excerpts:\n{context}"

        else:
            themes, theme_ids = build_theme_context(db, limit=10)
            summary = build_dataset_summary(db)
            known_ids = theme_ids
            if not themes.strip():
                answer = "No themes are available yet. Run Refresh pipeline to analyze reviews first."
                return _log_and_return(db, query, intent, answer, [], True, started)
            system_prompt = GENERAL_REVIEW_PROMPT
            user_content = f"Question: {query}\n\nDataset:\n{summary}\n\nThemes:\n{themes}"

        answer = _call_groq(system_prompt, user_content)

    except RuntimeError as exc:
        return _log_and_return(db, query, intent, str(exc), [], True, started)
    except Exception as exc:  # noqa: BLE001
        return _log_and_return(
            db,
            query,
            intent,
            f"Groq request failed: {exc}",
            [],
            False,
            started,
        )

    citations = _extract_citations(answer, known_ids)
    if not citations and known_ids:
        citations = [review_id[:8] for review_id in known_ids[:6]]

    citations_valid = validate_citations(db, answer, citations)
    if not citations_valid and citations:
        answer += "\n\n_Note: Some citations could not be fully verified against stored reviews._"

    return _log_and_return(db, query, intent, answer, citations, citations_valid, started)


def _log_and_return(
    db: Session,
    query: str,
    intent: str,
    answer: str,
    citations: list[str],
    citations_valid: bool,
    started: float,
) -> dict:
    log = ChatLog(
        id=str(uuid.uuid4()),
        query=query,
        intent=intent,
        answer=answer,
        citations=citations,
        citations_valid=citations_valid,
        latency_ms=int((time.perf_counter() - started) * 1000),
    )
    db.add(log)
    db.commit()
    return {
        "answer": answer,
        "citations": citations,
        "intent": intent,
        "citations_valid": citations_valid,
        "groq_enabled": bool(get_settings().groq_api_key),
    }


def get_chat_status() -> dict:
    settings = get_settings()
    return {
        "groq_enabled": bool(settings.groq_api_key),
        "groq_model": settings.groq_model if settings.groq_api_key else None,
        "sample_questions": [
            "Why do users struggle to discover new music?",
            "What are the most common frustrations with recommendations?",
            "What listening behaviors are users trying to achieve?",
            "What causes users to repeatedly listen to the same content?",
            "Which user segments experience different discovery challenges?",
            "What unmet needs emerge consistently across reviews?",
        ],
    }
