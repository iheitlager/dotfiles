"""Reference validation result model."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ReferenceResult:
    """Result of a reference validation check."""

    source: str  # "doi" | "crossref" | "openalex" | "semantic_scholar"
    title: str
    authors: list[str]
    year: int | None
    doi: str | None
    url: str | None
    confidence: float  # 0-1, fuzzy match score against query
    cache_hit: bool = False
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class ReferenceQuery:
    """Input query for reference validation."""

    title: str | None = None
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    doi: str | None = None
    raw_text: str | None = None  # free-form query string
