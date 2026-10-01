"""OpenAlex API executor — search by title.

API docs: https://docs.openalex.org/
Free, no API key required. Polite pool via email.
"""

import httpx

from tools.refcheck.executors.base import BaseExecutor
from tools.refcheck.models import ReferenceQuery, ReferenceResult
from tools.refcheck.scoring import MIN_TITLE_SIMILARITY, best_similarity

OPENALEX_API = "https://api.openalex.org"
USER_AGENT = "my-brain-refcheck/1.0 (mailto:i.heitlager@tue.nl)"
REQUEST_TIMEOUT = 15


class OpenAlexExecutor(BaseExecutor):
    """Search OpenAlex by title."""

    @property
    def name(self) -> str:
        return "openalex"

    def check(self, query: ReferenceQuery) -> ReferenceResult | None:
        search_text = query.raw_text or query.title
        if not search_text:
            return None

        params: dict[str, str | int] = {
            "search": search_text,
            "per_page": 5,
        }

        headers = {"User-Agent": USER_AGENT}

        try:
            resp = httpx.get(
                f"{OPENALEX_API}/works",
                params=params,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )
            if resp.status_code != 200:
                return None

            results = resp.json().get("results", [])
            if not results:
                return None

            # Score candidates
            best = None
            best_score = 0.0
            for work in results:
                candidate_title = work.get("title", "")
                if not candidate_title:
                    continue
                score = best_similarity(query, candidate_title)
                if score > best_score:
                    best_score = score
                    best = work

            if best is None or best_score < MIN_TITLE_SIMILARITY:
                return None

            # Extract fields
            title = best.get("title", "")
            authors = []
            for authorship in best.get("authorships", []):
                name = authorship.get("author", {}).get("display_name", "")
                if name:
                    authors.append(name)

            year = best.get("publication_year")
            doi_url = best.get("doi")
            doi = doi_url.replace("https://doi.org/", "") if doi_url else None

            url = None
            loc = best.get("primary_location")
            if loc:
                url = loc.get("landing_page_url")

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
