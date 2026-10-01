"""Fuzzy matching utilities for reference validation."""

from difflib import SequenceMatcher

from tools.refcheck.models import ReferenceQuery


def title_similarity(query_text: str, candidate: str) -> float:
    """Score how well query_text matches a candidate title.

    Uses both SequenceMatcher ratio AND containment check:
    - If query is a substring of candidate (or vice versa): high score
    - Otherwise: SequenceMatcher ratio adjusted for length difference
    """
    q = query_text.lower().strip()
    c = candidate.lower().strip()

    if not q or not c:
        return 0.0

    # Containment: query fully inside candidate or vice versa
    if q in c:
        return 0.9 + 0.1 * (len(q) / len(c))  # 0.9-1.0
    if c in q:
        return 0.85 + 0.1 * (len(c) / len(q))

    # Standard ratio
    ratio = SequenceMatcher(None, q, c).ratio()

    # Boost if query words all appear in candidate
    q_words = set(q.split())
    c_words = set(c.split())
    if q_words and q_words.issubset(c_words):
        ratio = max(ratio, 0.8)

    return ratio


def best_similarity(query: ReferenceQuery, candidate: str) -> float:
    """Best fuzzy match score across all query text signals."""
    scores: list[float] = []
    if query.title:
        scores.append(title_similarity(query.title, candidate))
    if query.raw_text:
        scores.append(title_similarity(query.raw_text, candidate))
    return max(scores) if scores else 0.0
