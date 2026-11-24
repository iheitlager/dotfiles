"""DOI redirect validation executor.

Validates a DOI by checking if https://doi.org/{doi} resolves (HTTP redirect).
Adapted from latex-tools doi_validator pattern.
"""

import httpx

from tools.refcheck.executors.base import BaseExecutor
from tools.refcheck.models import ReferenceQuery, ReferenceResult

REQUEST_TIMEOUT = 10


class DOIExecutor(BaseExecutor):
    """Validate DOI existence via redirect check."""

    @property
    def name(self) -> str:
        return "doi"

    def check(self, query: ReferenceQuery) -> ReferenceResult | None:
        if not query.doi:
            return None

        doi = query.doi.strip()
        # Normalize: strip URL prefix if present
        for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
            if doi.lower().startswith(prefix.lower()):
                doi = doi[len(prefix):]

        url = f"https://doi.org/{doi}"
        try:
            # Follow redirects to see where DOI resolves
            resp = httpx.get(url, timeout=REQUEST_TIMEOUT, follow_redirects=True)
            if resp.status_code < 400:
                return ReferenceResult(
                    source=self.name,
                    title=query.title or "",
                    authors=query.authors,
                    year=query.year,
                    doi=doi,
                    url=str(resp.url),
                    confidence=1.0,
                    raw={"status_code": resp.status_code, "resolved_url": str(resp.url)},
                )
        except (httpx.HTTPError, httpx.TimeoutException):
            pass

        return None
