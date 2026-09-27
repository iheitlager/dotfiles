"""Base executor interface for reference validation."""

from abc import ABC, abstractmethod

from tools.refcheck.models import ReferenceQuery, ReferenceResult


class BaseExecutor(ABC):
    """Abstract base for API-specific reference validators.

    Each executor tries one source. Returns ReferenceResult on success, None on miss.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Source name (e.g. 'crossref')."""

    @abstractmethod
    def check(self, query: ReferenceQuery) -> ReferenceResult | None:
        """Validate a reference against this source.

        Returns ReferenceResult if found, None otherwise.
        """
