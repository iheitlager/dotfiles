"""Semantic Scholar API executor — search by title+year.

API docs: https://api.semanticscholar.org/api-docs/graph
Free tier: 100 requests per 5 minutes.
"""

import httpx

from tools.refcheck.executors.base import BaseExecutor
from tools.refcheck.models import ReferenceQuery, ReferenceResult
from tools.refcheck.scoring import MIN_TITLE_SIMILARITY, best_similarity

S2_API = "https://api.semanticscholar.org/graph/v1"
REQUEST_TIMEOUT = 15
FIELDS = "paperId,title,authors,year,externalIds,url"


class SemanticScholarExecutor(BaseExecutor):
    """Search Semantic Scholar by title+year."""

    @property
    def name(self) -> str:
        return "semantic_scholar"

    def check(self, query: ReferenceQuery) -> ReferenceResult | None:
        search_text = query.raw_text or query.title
        if not search_text:
            return None

        params: dict[str, str | int] = {
            "query": search_text,
            "limit": 5,
            "fields": FIELDS,
        }
        if query.year:
            params["year"] = str(query.year)

        try:
            resp = httpx.get(
                f"{S2_API}/paper/search",
                params=params,
                timeout=REQUEST_TIMEOUT,
            )
            if resp.status_code != 200:
                return None

            papers = resp.json().get("data", [])
            if not papers:
                return None

            # Score candidates
            best = None
            best_score = 0.0
            for paper in papers:
                candidate_title = paper.get("title", "")
                if not candidate_title:
                    continue
                score = best_similarity(query, candidate_title)
                if score > best_score:
                    best_score = score
                    best = paper

            if best is None or best_score < MIN_TITLE_SIMILARITY:
                return None

            title = best.get("title", "")
            authors = []
            for a in best.get("authors", []):
                name = a.get("name", "") if isinstance(a, dict) else str(a)
                if name:
                    authors.append(name)

            year = best.get("year")
            external_ids = best.get("externalIds", {}) or {}
            doi = external_ids.get("DOI")
            url = best.get("url")

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
