"""
Extractors for reverse engineering architecture from code and config files.

This module provides a plugin-based system for extracting architectural
resources from various file formats (bash scripts, docker-compose, kubernetes, etc.).
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from ..model import Resource


class Extractor(ABC):
    """Abstract base class for file format extractors.

    Extractors scan files and generate Resource objects representing
    the architectural elements found in the code.
    """

    @abstractmethod
    def can_extract(self, file_path: Path) -> bool:
        """Check if this extractor can handle the given file.

        Args:
            file_path: Path to the file to check

        Returns:
            True if this extractor can parse this file type
        """
        pass

    @abstractmethod
    def extract(self, file_path: Path) -> List[Resource]:
        """Extract architectural resources from the file.

        Args:
            file_path: Path to the file to extract from

        Returns:
            List of Resource objects found in the file

        Raises:
            ExtractionError: If extraction fails
        """
        pass


class ExtractionError(Exception):
    """Error during resource extraction."""

    def __init__(self, message: str, file_path: Path = None, line: int = None):
        self.message = message
        self.file_path = file_path
        self.line = line
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format error message with file/line context."""
        parts = []
        if self.file_path:
            parts.append(f"File: {self.file_path}")
        if self.line:
            parts.append(f"Line: {self.line}")
        parts.append(self.message)
        return " | ".join(parts)


__all__ = ['Extractor', 'ExtractionError']
