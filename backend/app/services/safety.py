"""
Safety / scam detection service — stub for now.
Will call Claude API to analyze messages for suspicious patterns.
"""


def analyze_message(content: str) -> dict:
    """
    Stub: always returns safe.
    Will be replaced with Claude-powered scam/safety detection.
    """
    return {"flagged": False, "reason": None}
