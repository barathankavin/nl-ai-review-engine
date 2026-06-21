#!/usr/bin/env python3
"""Phase 8: lightweight eval harness for chat routing and citations."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.models import SessionLocal, init_db
from app.rag.chat import answer_query
from app.rag.router import classify_intent


QUESTIONS = [
    ("What are people complaining about?", "theme_overview"),
    ("Show me examples of app crash reviews", "drill_down"),
    ("Should we discontinue Spotify?", "out_of_scope"),
    ("Why do users struggle to discover new music?", "discovery_analysis"),
    ("What are the most common frustrations with recommendations?", "discovery_analysis"),
]


def main() -> None:
    init_db()
    db = SessionLocal()
    passed = 0

    for question, expected_intent in QUESTIONS:
        actual = classify_intent(question)
        ok = actual == expected_intent
        passed += int(ok)
        print(f"[{'PASS' if ok else 'FAIL'}] intent {actual} expected {expected_intent} :: {question}")

    result = answer_query(db, "What are people complaining about?")
    has_answer = bool(result["answer"].strip())
    print(f"[{'PASS' if has_answer else 'FAIL'}] chat answer generated")
    passed += int(has_answer)

    db.close()
    print(f"Eval complete: {passed}/{len(QUESTIONS) + 1} checks passed")


if __name__ == "__main__":
    main()
