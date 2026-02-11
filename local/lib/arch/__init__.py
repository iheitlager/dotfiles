"""
Grounded C4 Architecture Modeling Library

Python library for loading, validating, and querying architecture models
defined using the Grounded C4 approach.
"""

__version__ = "0.1.0"

from .model import (
    Interface,
    CodeRef,
    Resource,
    Relationship,
    ArchitectureModel,
)

from .loader import (
    load_architecture,
    load_yaml_file,
    LoadError,
)

from .path_resolver import (
    PathResolver,
    ResolutionResult,
)

from .validator import (
    ArchitectureValidator,
    ValidationResult,
    ValidationIssue,
    Severity,
)

__all__ = [
    # Models
    "Interface",
    "CodeRef",
    "Resource",
    "Relationship",
    "ArchitectureModel",
    # Loader
    "load_architecture",
    "load_yaml_file",
    "LoadError",
    # Path resolver
    "PathResolver",
    "ResolutionResult",
    # Validator
    "ArchitectureValidator",
    "ValidationResult",
    "ValidationIssue",
    "Severity",
]
