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
        self._validate_sequence_references()
        self._validate_state_machine_references()
        self._validate_state_machine_anchors()
        self._validate_state_transitions()

        # Informational checks (warnings only)
        self._check_orphan_interfaces()
        self._check_orphan_sequences()

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

    def _validate_sequence_references(self) -> None:
        """Validate that all sequence step references resolve to actual resources/interfaces.

        Rule: Every from_ref and to_ref in sequence steps must point to:
        - A valid resource path (e.g., "system.service")
        - A valid interface path (e.g., "system.service.api")
        - Special actor "user" (external actor)
        """
        for sequence in self.model.sequences:
            self._validate_steps(sequence.steps, sequence.id)

    def _validate_steps(self, steps: list, sequence_id: str, step_context: str = "") -> None:
        """Recursively validate steps (including parallel and alt blocks)."""
        for idx, step in enumerate(steps):
            context = f"{step_context}step[{idx}]" if step_context else f"step[{idx}]"

            # Allow 'user' as a special external actor
            if step.from_ref != "user":
                from_result = self.resolver.resolve(step.from_ref)
                if not from_result.found:
                    self.result.add_error(
                        f"Sequence '{sequence_id}' {context} 'from' reference not found: {step.from_ref}",
                        path=step.from_ref,
                        rule="sequence-references"
                    )

            # Validate 'to' reference
            to_result = self.resolver.resolve(step.to_ref)
            if not to_result.found:
                self.result.add_error(
                    f"Sequence '{sequence_id}' {context} 'to' reference not found: {step.to_ref}",
                    path=step.to_ref,
                    rule="sequence-references"
                )

            # Recursively validate parallel steps
            if step.parallel:
                self._validate_steps(step.parallel, sequence_id, f"{context}.parallel.")

            # Recursively validate alternative blocks
            if step.alt:
                for alt_idx, alt_block in enumerate(step.alt):
                    self._validate_steps(
                        alt_block.steps,
                        sequence_id,
                        f"{context}.alt[{alt_idx}]."
                    )

    def _validate_state_machine_references(self) -> None:
        """Validate that state machine resource and sequence references resolve.

        Rules:
        - resource field must point to a valid resource
        - initial field must match a state ID
        - transition from/to must match state IDs
        - transition sequence (if present) must reference an existing sequence
        """
        # Build sequence ID index
        sequence_ids = {seq.id for seq in self.model.sequences}

        for sm in self.model.state_machines:
            # Validate resource reference
            resource_result = self.resolver.resolve(sm.resource)
            if not resource_result.found:
                self.result.add_error(
                    f"State machine '{sm.id}' resource not found: {sm.resource}",
                    path=sm.resource,
                    rule="state-machine-references"
                )

            # Build state ID index for this state machine
            state_ids = {state.id for state in sm.states}

            # Validate initial state exists
            if sm.initial not in state_ids:
                self.result.add_error(
                    f"State machine '{sm.id}' initial state '{sm.initial}' not found in states",
                    path=sm.id,
                    rule="state-machine-references"
                )

            # Validate transitions
            for trans in sm.transitions:
                # Validate from state
                if trans.from_state not in state_ids:
                    self.result.add_error(
                        f"State machine '{sm.id}' transition 'from' state '{trans.from_state}' not found",
                        path=sm.id,
                        rule="state-machine-references"
                    )

                # Validate to state
                if trans.to_state not in state_ids:
                    self.result.add_error(
                        f"State machine '{sm.id}' transition 'to' state '{trans.to_state}' not found",
                        path=sm.id,
                        rule="state-machine-references"
                    )

                # Validate sequence reference if present
                if trans.sequence and trans.sequence not in sequence_ids:
                    self.result.add_error(
                        f"State machine '{sm.id}' transition references unknown sequence: {trans.sequence}",
                        path=sm.id,
                        rule="state-machine-references"
                    )

    def _validate_state_machine_anchors(self) -> None:
        """Validate that state machines anchor to concrete (non-abstract) resources.

        Rule: State machines must anchor to concrete resources, not abstract groupings.
        Abstract resources are logical groupings and don't have operational states.
        """
        for sm in self.model.state_machines:
            resource_result = self.resolver.resolve(sm.resource)
            if resource_result.found and resource_result.is_resource:
                resource = resource_result.resource
                if resource.abstract:
                    self.result.add_error(
                        f"State machine '{sm.id}' anchored to abstract resource: {sm.resource}",
                        path=sm.resource,
                        rule="state-machine-anchoring"
                    )

    def _validate_state_transitions(self) -> None:
        """Validate that state machines have valid transition graphs.

        Rules:
        - Each state should be reachable from the initial state (warning)
        - Terminal states (no outgoing transitions) should be intentional (info)
        """
        for sm in self.model.state_machines:
            # Build transition graph
            outgoing = {state.id: [] for state in sm.states}
            incoming = {state.id: [] for state in sm.states}

            for trans in sm.transitions:
                if trans.from_state in outgoing:
                    outgoing[trans.from_state].append(trans.to_state)
                if trans.to_state in incoming:
                    incoming[trans.to_state].append(trans.from_state)

            # Check reachability from initial state using BFS
            reachable = set()
            queue = [sm.initial]
            while queue:
                current = queue.pop(0)
                if current in reachable:
                    continue
                reachable.add(current)
                queue.extend(outgoing.get(current, []))

            # Warn about unreachable states
            for state in sm.states:
                if state.id not in reachable and state.id != sm.initial:
                    self.result.add_warning(
                        f"State machine '{sm.id}' state '{state.id}' is not reachable from initial state '{sm.initial}'",
                        path=sm.id,
                        rule="state-transitions"
                    )

    def _check_orphan_sequences(self) -> None:
        """Check for sequences that aren't referenced by state machines (warning only).

        This is informational—orphan sequences may be intentional (documentation,
        future use, or referenced from specs).
        """
        # Collect all sequence IDs referenced by state machines
        used_sequences = set()
        for sm in self.model.state_machines:
            for trans in sm.transitions:
                if trans.sequence:
                    used_sequences.add(trans.sequence)

        # Check all sequences in the model
        for sequence in self.model.sequences:
            if sequence.id not in used_sequences:
                self.result.add_warning(
                    f"Sequence '{sequence.id}' is not referenced by any state machine transition",
                    path=sequence.id,
                    rule="orphan-sequences"
                )
