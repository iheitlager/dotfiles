"""
Reverse engineering orchestrator for architecture extraction.

Scans directories for code and config files, applies appropriate extractors,
and generates architectural models.
"""

from pathlib import Path
from typing import List, Optional, Dict, Set

from .model import ArchitectureModel, Resource
from .extractors import Extractor, ExtractionError
from .extractors.bash import BashExtractor
from .extractors.docker import DockerExtractor
from .extractors.kubernetes import KubernetesExtractor


class ReverseEngineer:
    """Orchestrate reverse engineering of architecture from code."""

    def __init__(self):
        """Initialize with all available extractors."""
        self.extractors: List[Extractor] = [
            BashExtractor(),
            DockerExtractor(),
            KubernetesExtractor(),
        ]

    def extract_from_directory(
        self,
        source_dir: Path,
        recursive: bool = True,
        exclude_patterns: Optional[List[str]] = None
    ) -> ArchitectureModel:
        """Extract architecture from all files in a directory.

        Args:
            source_dir: Directory to scan
            recursive: Whether to scan subdirectories (default: True)
            exclude_patterns: Glob patterns to exclude (e.g., ['*.pyc', '__pycache__'])

        Returns:
            ArchitectureModel with extracted resources

        Raises:
            ValueError: If source_dir doesn't exist
        """
        if not source_dir.exists() or not source_dir.is_dir():
            raise ValueError(f"Source directory not found: {source_dir}")

        # Default exclusions
        if exclude_patterns is None:
            exclude_patterns = [
                '*.pyc', '*.pyo', '__pycache__',
                '.git', '.svn', 'node_modules',
                '*.min.js', '*.min.css'
            ]

        # Collect files to process
        files_to_process = self._collect_files(source_dir, recursive, exclude_patterns)

        # Extract resources from each file
        all_resources = []
        extraction_errors = []

        for file_path in files_to_process:
            try:
                resources = self.extract_from_file(file_path)
                all_resources.extend(resources)
            except ExtractionError as e:
                extraction_errors.append(e)

        # Deduplicate resources by ID
        unique_resources = self._deduplicate_resources(all_resources)

        # Build model
        model = ArchitectureModel(resources=unique_resources)

        # Store extraction errors as metadata
        if extraction_errors:
            model.metadata = {
                'extraction_errors': [str(e) for e in extraction_errors]
            }

        return model

    def extract_from_file(self, file_path: Path) -> List[Resource]:
        """Extract architecture from a single file.

        Args:
            file_path: File to extract from

        Returns:
            List of Resources extracted from the file

        Raises:
            ExtractionError: If extraction fails
        """
        # Find appropriate extractor
        for extractor in self.extractors:
            if extractor.can_extract(file_path):
                return extractor.extract(file_path)

        # No extractor found
        return []

    def _collect_files(
        self,
        directory: Path,
        recursive: bool,
        exclude_patterns: List[str]
    ) -> List[Path]:
        """Collect files to process from directory.

        Args:
            directory: Directory to scan
            recursive: Whether to recurse into subdirectories
            exclude_patterns: Glob patterns to exclude

        Returns:
            List of file paths to process
        """
        files = []

        if recursive:
            # Recursive scan
            for file_path in directory.rglob('*'):
                if file_path.is_file() and not self._is_excluded(file_path, exclude_patterns):
                    files.append(file_path)
        else:
            # Non-recursive scan
            for file_path in directory.iterdir():
                if file_path.is_file() and not self._is_excluded(file_path, exclude_patterns):
                    files.append(file_path)

        return sorted(files)

    def _is_excluded(self, file_path: Path, exclude_patterns: List[str]) -> bool:
        """Check if file matches any exclusion pattern.

        Args:
            file_path: File to check
            exclude_patterns: List of glob patterns

        Returns:
            True if file should be excluded
        """
        for pattern in exclude_patterns:
            if file_path.match(pattern):
                return True

            # Also check if any parent directory matches
            for parent in file_path.parents:
                if parent.name and parent.match(pattern):
                    return True

        return False

    def _deduplicate_resources(self, resources: List[Resource]) -> List[Resource]:
        """Remove duplicate resources by ID.

        Args:
            resources: List of resources (may contain duplicates)

        Returns:
            List of unique resources (first occurrence wins)
        """
        seen_ids: Set[str] = set()
        unique = []

        for resource in resources:
            if resource.id not in seen_ids:
                seen_ids.add(resource.id)
                unique.append(resource)

        return unique

    def get_supported_extensions(self) -> List[str]:
        """Get list of file extensions supported by extractors.

        Returns:
            List of file extensions (e.g., ['.sh', '.yml'])
        """
        # This is informational - actual detection uses can_extract()
        return ['.sh', '.bash', '.yml', '.yaml']

    def get_extractor_info(self) -> Dict[str, str]:
        """Get information about available extractors.

        Returns:
            Dictionary mapping extractor name to description
        """
        return {
            'BashExtractor': 'Extracts functions and interfaces from bash scripts',
            'DockerExtractor': 'Extracts services from docker-compose files',
            'KubernetesExtractor': 'Extracts resources from Kubernetes manifests',
        }
