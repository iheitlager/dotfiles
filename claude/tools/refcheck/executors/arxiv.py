"""arXiv API executor — search by title/author/ID.

API docs: https://info.arxiv.org/help/api/index.html
Uses Atom feed endpoint. Free, no key required, rate limit ~1 req/3sec.
"""

import re
import xml.etree.ElementTree as ET

import httpx

from tools.refcheck.executors.base import BaseExecutor
from tools.refcheck.models import ReferenceQuery, ReferenceResult
from tools.refcheck.scoring import MIN_TITLE_SIMILARITY, best_similarity

ARXIV_API = "http://export.arxiv.org/api/query"
REQUEST_TIMEOUT = 15

# Namespace for Atom feed parsing
NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}

# Match arXiv IDs in various formats
ARXIV_ID_PATTERN = re.compile(
    r"(?:arXiv:?)?(\d{4}\.\d{4,5}(?:v\d+)?)"  # new format: 2604.04990
    r"|(?:arXiv:?)?([\w-]+/\d{7}(?:v\d+)?)",    # old format: cs.AI/0601234
    re.IGNORECASE,
)


def extract_arxiv_id(text: str) -> str | None:
    """Extract arXiv ID from a string (DOI, URL, or raw text)."""
    # From DOI: 10.48550/arXiv.2604.04990
    if "arXiv." in text:
        match = re.search(r"arXiv\.(\d{4}\.\d{4,5})", text)
        if match:
            return match.group(1)

    # From URL or plain ID
    match = ARXIV_ID_PATTERN.search(text)
    if match:
        return match.group(1) or match.group(2)

    return None


class ArxivExecutor(BaseExecutor):
    """Search arXiv by ID or title+author."""

    @property
    def name(self) -> str:
        return "arxiv"

    def check(self, query: ReferenceQuery) -> ReferenceResult | None:
        # Try ID-based lookup first (fastest, most precise)
        arxiv_id = None
        if query.doi:
            arxiv_id = extract_arxiv_id(query.doi)
        if not arxiv_id and query.raw_text:
            arxiv_id = extract_arxiv_id(query.raw_text)

        if arxiv_id:
            return self._lookup_by_id(arxiv_id, query)

        # Fall back to search
        return self._search(query)

    def _lookup_by_id(self, arxiv_id: str, query: ReferenceQuery) -> ReferenceResult | None:
        """Direct lookup by arXiv ID."""
        try:
            resp = httpx.get(
                ARXIV_API,
                params={"id_list": arxiv_id, "max_results": 1},
                timeout=REQUEST_TIMEOUT,
                follow_redirects=True,
            )
            if resp.status_code != 200:
                return None

            return self._parse_first_entry(resp.text, query, id_lookup=True)

        except (httpx.HTTPError, httpx.TimeoutException):
            return None

    def _search(self, query: ReferenceQuery) -> ReferenceResult | None:
        """Search by title and/or author."""
        parts: list[str] = []

        title = query.title or query.raw_text
        if title:
            # Clean title for search
            clean = re.sub(r"[^\w\s]", " ", title)
            parts.append(f'ti:"{clean}"')

        if query.authors:
            parts.append(f'au:"{query.authors[0]}"')

        if not parts:
            return None

        search_query = " AND ".join(parts)

        try:
            resp = httpx.get(
                ARXIV_API,
                params={"search_query": search_query, "max_results": 5},
                timeout=REQUEST_TIMEOUT,
                follow_redirects=True,
            )
            if resp.status_code != 200:
                return None

            return self._parse_first_entry(resp.text, query, id_lookup=False)

        except (httpx.HTTPError, httpx.TimeoutException):
            return None

    def _parse_first_entry(
        self, xml_text: str, query: ReferenceQuery, id_lookup: bool
    ) -> ReferenceResult | None:
        """Parse Atom feed and return best matching entry."""
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError:
            return None

        entries = root.findall("atom:entry", NS)
        if not entries:
            return None

        best_entry = None
        best_score = 0.0

        for entry in entries:
            title_el = entry.find("atom:title", NS)
            if title_el is None or not title_el.text:
                continue

            entry_title = " ".join(title_el.text.split())  # normalize whitespace

            if id_lookup:
                # ID lookup — trust the result
                best_entry = entry
                best_score = 1.0
                break
            else:
                score = best_similarity(query, entry_title)
                if score > best_score:
                    best_score = score
                    best_entry = entry

        if best_entry is None or best_score < MIN_TITLE_SIMILARITY:
            return None

        # Extract fields
        title_el = best_entry.find("atom:title", NS)
        title = " ".join(title_el.text.split()) if title_el is not None and title_el.text else ""

        authors = []
        for author_el in best_entry.findall("atom:author", NS):
            name_el = author_el.find("atom:name", NS)
            if name_el is not None and name_el.text:
                authors.append(name_el.text)

        # Extract year from published date
        year = None
        published_el = best_entry.find("atom:published", NS)
        if published_el is not None and published_el.text:
            match = re.match(r"(\d{4})", published_el.text)
            if match:
                year = int(match.group(1))

        # Extract arXiv ID and build DOI/URL
        entry_id = ""
        id_el = best_entry.find("atom:id", NS)
        if id_el is not None and id_el.text:
            entry_id = id_el.text  # http://arxiv.org/abs/2604.04990v1

        arxiv_id = extract_arxiv_id(entry_id) or ""
        doi = f"10.48550/arXiv.{arxiv_id}" if arxiv_id else None
        url = entry_id or None

        # Build raw dict
        summary_el = best_entry.find("atom:summary", NS)
        raw = {
            "arxiv_id": arxiv_id,
            "title": title,
            "authors": authors,
            "year": year,
            "url": url,
            "abstract": " ".join(summary_el.text.split()) if summary_el is not None and summary_el.text else "",
        }

        return ReferenceResult(
            source=self.name,
            title=title,
            authors=authors,
            year=year,
            doi=doi,
            url=url,
            confidence=round(best_score, 3),
            raw=raw,
        )
