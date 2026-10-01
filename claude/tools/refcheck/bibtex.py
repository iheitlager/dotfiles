"""Lightweight BibTeX parser — no external dependencies.

Extracts title, author, year, doi from .bib entries.
Good enough for reference validation; not a full BibTeX parser.
"""

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class BibEntry:
    """Minimal BibTeX entry."""

    cite_key: str
    title: str | None = None
    author: str | None = None
    year: int | None = None
    doi: str | None = None

    def author_list(self) -> list[str]:
        """Split 'and'-delimited author string into list."""
        if not self.author:
            return []
        return [a.strip() for a in self.author.split(" and ") if a.strip()]


# Match @type{key, ... }
_ENTRY_RE = re.compile(
    r"@\w+\s*\{\s*([^,]+)\s*,(.+?)\n\s*\}",
    re.DOTALL,
)

# Match field = {value} or field = "value" or field = number
_FIELD_RE = re.compile(
    r"(\w+)\s*=\s*(?:\{((?:[^{}]|\{[^{}]*\})*)\}|\"([^\"]*)\"|(\d+))",
)


def parse_bib(text: str) -> list[BibEntry]:
    """Parse BibTeX string into list of BibEntry."""
    entries = []
    for match in _ENTRY_RE.finditer(text):
        cite_key = match.group(1).strip()
        body = match.group(2)

        fields: dict[str, str] = {}
        for fm in _FIELD_RE.finditer(body):
            key = fm.group(1).lower()
            value = fm.group(2) or fm.group(3) or fm.group(4) or ""
            fields[key] = value.strip()

        year = None
        if "year" in fields:
            try:
                year = int(fields["year"])
            except ValueError:
                pass

        entries.append(
            BibEntry(
                cite_key=cite_key,
                title=fields.get("title"),
                author=fields.get("author"),
                year=year,
                doi=fields.get("doi"),
            )
        )
    return entries


def parse_bib_file(path: str | Path) -> list[BibEntry]:
    """Parse a .bib file."""
    return parse_bib(Path(path).read_text(encoding="utf-8"))
