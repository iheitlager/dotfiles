"""Architecture model validation.

Validates referential integrity, uniqueness constraints, and structural rules
for Grounded C4 architecture models.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from .model import ArchitectureModel, Resource, Interface
from .path_resolver import PathResolver


class Severity(Enum):
    """Validation issue severity levels."""
    ERROR = "error"
    WARNING = "warning"


@dataclass
class ValidationIssue:
    """A single validation issue found in a model."""
    severity: Severity
    message: str
    file_path: Optional[str] = None
    line: Optional[int] = None
    path: Optional[str] = None  # Resource or interface path
    rule: Optional[str] = None  # Rule identifier (e.g., "unique-ids")


@dataclass
class ValidationResult:
    """Result of validating an architecture model."""
    valid: bool
    errors: List[ValidationIssue] = field(default_factory=list)
    warnings: List[ValidationIssue] = field(default_factory=list)

    @property
    def total_issues(self) -> int:
        """Total number of issues (errors + warnings)."""
        return len(self.errors) + len(self.warnings)

    def add_error(self, message: str, **kwargs) -> None:
        """Add an error to the result."""
        self.errors.append(ValidationIssue(Severity.ERROR, message, **kwargs))
        self.valid = False

    def add_warning(self, message: str, **kwargs) -> None:
        """Add a warning to the result."""
        self.warnings.append(ValidationIssue(Severity.WARNING, message, **kwargs))


class ArchitectureValidator:
    """Validates architecture models for referential integrity and constraints."""

    def __init__(self, model: ArchitectureModel):
        """Initialize validator with a model.

        Args:
            model: The architecture model to validate
        """
        self.model = model
        self.resolver = PathResolver(model)
        self.result = ValidationResult(valid=True)

    def validate(self) -> ValidationResult:
        """Run all validation checks on the model.

        Returns:
            ValidationResult with any errors or warnings found
        """
        # Core validation rules (MUST pass)
        self._validate_unique_ids()
        self._validate_abstract_resources()
        self._validate_relationship_references()

        # Informational checks (warnings only)
        self._check_orphan_interfaces()

        return self.result

    def _validate_unique_ids(self) -> None:
        """Validate that no sibling resources share the same ID.

        Rule: Resource IDs must be unique within their parent scope.
        Full paths (dot-notation) must be globally unique.
        """
        seen_paths = set()

        def check_resource(resource: Resource, parent_path: str = "") -> None:
            # Build full path
            current_path = f"{parent_path}.{resource.id}" if parent_path else resource.id

            # Check for duplicate path
            if current_path in seen_paths:
                self.result.add_error(
                    f"Duplicate resource path: {current_path}",
                    path=current_path,
                    rule="unique-ids"
                )
            seen_paths.add(current_path)

            # Check children for duplicates among siblings
            child_ids = {}
            for child in resource.children:
                if child.id in child_ids:
                    self.result.add_error(
                        f"Duplicate sibling ID '{child.id}' under '{current_path}'",
                        path=current_path,
                        rule="unique-ids"
                    )
                child_ids[child.id] = child

            # Recursively check children
            for child in resource.children:
                check_resource(child, current_path)

        # Check all top-level resources
        for resource in self.model.resources:
            check_resource(resource)

    def _validate_abstract_resources(self) -> None:
        """Validate that abstract resources have at least one child.

        Rule: Resources marked as abstract=true must contain children.
        Abstractions don't exist in isolation—they're groupings.
        """
        def check_resource(resource: Resource) -> None:
            if resource.abstract and not resource.children:
                self.result.add_error(
                    f"Abstract resource '{resource.full_path}' has no children",
                    path=resource.full_path,
                    rule="abstract-resources"
                )

            # Recursively check children
            for child in resource.children:
                check_resource(child)

        for resource in self.model.resources:
            check_resource(resource)

    def _validate_relationship_references(self) -> None:
        """Validate that all relationship references resolve to actual resources/interfaces.

        Rule: Every from_ref and to_ref in relationships must point to:
        - A valid resource path (e.g., "system.service")
        - A valid interface path (e.g., "system.service.api")
        """
        for rel in self.model.relationships:
            # Validate 'from' reference
            from_result = self.resolver.resolve(rel.from_ref)
            if not from_result.found:
                self.result.add_error(
                    f"Relationship 'from' reference not found: {rel.from_ref}",
                    path=rel.from_ref,
                    rule="relationship-references"
                )

            # Validate 'to' reference
            to_result = self.resolver.resolve(rel.to_ref)
            if not to_result.found:
                self.result.add_error(
                    f"Relationship 'to' reference not found: {rel.to_ref}",
                    path=rel.to_ref,
                    rule="relationship-references"
                )

            # Validate 'via' reference if present
            if rel.via:
                via_result = self.resolver.resolve(rel.via)
                if not via_result.found:
                    self.result.add_error(
                        f"Relationship 'via' reference not found: {rel.via}",
                        path=rel.via,
                        rule="relationship-references"
                    )

    def _check_orphan_interfaces(self) -> None:
        """Check for interfaces that aren't used in any relationships (warning only).

        This is informational—orphan interfaces may be intentional (future use,
        documentation, external consumption).
        """
        # Collect all interface paths used in relationships
        used_interfaces = set()
        for rel in self.model.relationships:
            # Parse paths to see if they reference interfaces
            from_result = self.resolver.resolve(rel.from_ref)
            if from_result.is_interface:
                used_interfaces.add(rel.from_ref)

            to_result = self.resolver.resolve(rel.to_ref)
            if to_result.is_interface:
                used_interfaces.add(rel.to_ref)

        # Check all interfaces in the model
        all_interface_paths = set(self.resolver.get_all_interface_paths())

        for interface_path in all_interface_paths:
            if interface_path not in used_interfaces:
                self.result.add_warning(
                    f"Interface '{interface_path}' is not used in any relationships",
                    path=interface_path,
                    rule="orphan-interfaces"
                )
