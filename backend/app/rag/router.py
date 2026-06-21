OUT_OF_SCOPE_KEYWORDS = [
    "should we discontinue",
    "shut down spotify",
    "invest in",
    "acquire spotify",
    "forecast revenue",
    "stock price",
]

DISCOVERY_ANALYSIS_KEYWORDS = [
    "discover",
    "discovery",
    "new music",
    "find music",
    "recommendation",
    "recommended",
    "algorithm",
    "playlist",
    "shuffle",
    "repeat",
    "same song",
    "same content",
    "listening behavior",
    "user segment",
    "segment",
    "unmet need",
    "frustration",
    "struggle",
    "why do users",
    "what causes",
    "what are users trying",
    "common frustration",
    "consistently",
]

DRILL_DOWN_KEYWORDS = [
    "example",
    "show me",
    "reviews about",
    "quote",
    "give me a review",
]


def classify_intent(query: str) -> str:
    lowered = query.lower()

    if any(keyword in lowered for keyword in OUT_OF_SCOPE_KEYWORDS):
        return "out_of_scope"

    if any(keyword in lowered for keyword in DRILL_DOWN_KEYWORDS):
        return "drill_down"

    if any(keyword in lowered for keyword in DISCOVERY_ANALYSIS_KEYWORDS):
        return "discovery_analysis"

    if any(keyword in lowered for keyword in ["why", "what causes", "how do users", "what are the most"]):
        return "discovery_analysis"

    return "theme_overview"
