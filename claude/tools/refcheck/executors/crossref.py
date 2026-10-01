"""Crossref API executor — search by title+author+year.

API docs: https://github.com/CrossRef/rest-api-doc
Uses bibliographic search endpoint, not DOI lookup.
"""

import httpx

from tools.refcheck.executors.base import BaseExecutor
from tools.refcheck.models import ReferenceQuery, ReferenceResult
from tools.refcheck.scoring import MIN_TITLE_SIMILARITY, best_similarity

CROSSREF_API = "https://api.crossref.org"
POLITE_EMAIL = "i.heitlager@tue.nl"
USER_AGENT = f"my-brain-refcheck/1.0 (mailto:{POLITE_EMAIL})"
REQUEST_TIMEOUT = 15


class CrossrefExecutor(BaseExecutor):
    """Search Crossref by bibliographic query."""

    @property
    def name(self) -> str:
        return "crossref"

    def check(self, query: ReferenceQuery) -> ReferenceResult | None:
        # Build search query — use raw_text when available (richer signal)
        search_text = query.raw_text or query.title
        if not search_text and not query.authors:
            return None

        parts: list[str] = []
        if search_text:
            parts.append(search_text)
        if query.authors:
            parts.append(query.authors[0])

        params: dict[str, str | int] = {
            "query.bibliographic": " ".join(parts),
            "rows": 5,
        }

        headers = {"User-Agent": USER_AGENT}

        try:
            resp = httpx.get(
                f"{CROSSREF_API}/works",
                params=params,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )
            if resp.status_code != 200:
                return None

            data = resp.json()
            items = data.get("message", {}).get("items", [])
            if not items:
                return None

            # Score each candidate against query
            best = None
            best_score = 0.0
            for item in items:
                titles = item.get("title", [])
                if not titles:
                    continue
                score = best_similarity(query, titles[0])
                if score > best_score:
                    best_score = score
                    best = item

            if best is None or best_score < MIN_TITLE_SIMILARITY:
                return None

            # Extract fields
            title = (best.get("title") or [""])[0]
            authors = []
            for a in best.get("author", []):
                given = a.get("given", "")
                family = a.get("family", "")
                authors.append(f"{given} {family}".strip())

            year = None
            for date_field in ("published-print", "published-online", "issued"):
                parts_d = best.get(date_field, {}).get("date-parts", [[]])
                if parts_d and parts_d[0] and parts_d[0][0]:
                    try:
                        year = int(parts_d[0][0])
                        break
                    except (ValueError, TypeError):
                        pass

            doi = best.get("DOI")
            url = best.get("URL")

            return ReferenceResult(
                source=self.name,
                title=title,
                authors=authors,
                year=year,
                doi=doi,
                url=url,
                confidence=round(best_score, 3),
                raw=best,
            )

        except (httpx.HTTPError, httpx.TimeoutException):
            return None
