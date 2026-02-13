"""
Data models for Grounded C4 architecture.

These dataclasses match the JSON schemas defined in local/share/arch/schemas/
and provide the in-memory representation of architecture models.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class Interface:
    """An interface for interacting with a resource."""

    id: str
    protocol: str
    direction: str
    description: Optional[str] = None
    topic: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Computed fields (not in YAML)
    parent_resource: Optional['Resource'] = field(default=None, repr=False)
    full_path: str = field(default="", repr=False)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (for serialization)."""
        data = {
            "id": self.id,
            "protocol": self.protocol,
            "direction": self.direction,
        }
        if self.description:
            data["description"] = self.description
        if self.topic:
            data["topic"] = self.topic
        if self.metadata:
            data["metadata"] = self.metadata
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Interface':
        """Create from dictionary."""
        return cls(
            id=data["id"],
            protocol=data["protocol"],
            direction=data["direction"],
            description=data.get("description"),
            topic=data.get("topic"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class CodeRef:
    """Reference to code implementing a resource."""

    path: str
    lines: Optional[str] = None
    function: Optional[str] = None
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = {"path": self.path}
        if self.lines:
            data["lines"] = self.lines
        if self.function:
            data["function"] = self.function
        if self.description:
            data["description"] = self.description
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CodeRef':
        """Create from dictionary."""
        return cls(
            path=data["path"],
            lines=data.get("lines"),
            function=data.get("function"),
            description=data.get("description"),
        )


@dataclass
class Resource:
    """A concrete or abstract resource in the architecture."""

    id: str
    name: str
    type: str
    abstract: bool = False
    technology: Optional[str] = None
    description: Optional[str] = None
    repository: Optional[str] = None
    instance: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    interfaces: List[Interface] = field(default_factory=list)
    children: List['Resource'] = field(default_factory=list)
    implementation: List[CodeRef] = field(default_factory=list)

    # Computed fields (not in YAML)
    parent: Optional['Resource'] = field(default=None, repr=False)
    full_path: str = field(default="", repr=False)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (for serialization)."""
        data = {
            "id": self.id,
            "name": self.name,
            "type": self.type,
        }
        if self.abstract:
            data["abstract"] = self.abstract
        if self.technology:
            data["technology"] = self.technology
        if self.description:
            data["description"] = self.description
        if self.repository:
            data["repository"] = self.repository
        if self.instance:
            data["instance"] = self.instance
        if self.tags:
            data["tags"] = self.tags
        if self.metadata:
            data["metadata"] = self.metadata
        if self.interfaces:
            data["interfaces"] = [i.to_dict() for i in self.interfaces]
        if self.children:
            data["children"] = [c.to_dict() for c in self.children]
        if self.implementation:
            data["implementation"] = [c.to_dict() for c in self.implementation]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Resource':
        """Create from dictionary."""
        # Parse interfaces
        interfaces = [
            Interface.from_dict(i) for i in data.get("interfaces", [])
        ]

        # Parse children (recursive)
        children = [
            cls.from_dict(c) for c in data.get("children", [])
        ]

        # Parse implementation
        implementation = [
            CodeRef.from_dict(c) for c in data.get("implementation", [])
        ]

        return cls(
            id=data["id"],
            name=data["name"],
            type=data["type"],
            abstract=data.get("abstract", False),
            technology=data.get("technology"),
            description=data.get("description"),
            repository=data.get("repository"),
            instance=data.get("instance"),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
            interfaces=interfaces,
            children=children,
            implementation=implementation,
        )

    def walk_tree(self):
        """Generator that yields (resource, depth) for tree traversal."""
        yield (self, 0)
        for child in self.children:
            for node, depth in child.walk_tree():
                yield (node, depth + 1)


@dataclass
class Relationship:
    """A relationship connecting two interfaces or resources."""

    from_ref: str  # "from" is Python keyword
    to_ref: str    # "to" is Python keyword
    via: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = {
            "from": self.from_ref,
            "to": self.to_ref,
        }
        if self.via:
            data["via"] = self.via
        if self.description:
            data["description"] = self.description
        if self.tags:
            data["tags"] = self.tags
        if self.metadata:
            data["metadata"] = self.metadata
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Relationship':
        """Create from dictionary."""
        return cls(
            from_ref=data["from"],
            to_ref=data["to"],
            via=data.get("via"),
            description=data.get("description"),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
        )


@dataclass
class AlternativeBlock:
    """Alternative flow block in a sequence (if/else branch)."""

    condition: str
    steps: List['Step']

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "condition": self.condition,
            "steps": [s.to_dict() for s in self.steps],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AlternativeBlock':
        """Create from dictionary."""
        from . import model  # Avoid circular import
        steps = [model.Step.from_dict(s) for s in data["steps"]]
        return cls(condition=data["condition"], steps=steps)


@dataclass
class Step:
    """A step in a sequence diagram."""

    from_ref: str  # "from" is Python keyword
    to_ref: str    # "to" is Python keyword
    action: str
    condition: Optional[str] = None
    note: Optional[str] = None
    parallel: List['Step'] = field(default_factory=list)
    alt: List[AlternativeBlock] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = {
            "from": self.from_ref,
            "to": self.to_ref,
            "action": self.action,
        }
        if self.condition:
            data["condition"] = self.condition
        if self.note:
            data["note"] = self.note
        if self.parallel:
            data["parallel"] = [s.to_dict() for s in self.parallel]
        if self.alt:
            data["alt"] = [a.to_dict() for a in self.alt]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Step':
        """Create from dictionary."""
        parallel = [cls.from_dict(s) for s in data.get("parallel", [])]
        alt = [AlternativeBlock.from_dict(a) for a in data.get("alt", [])]
        return cls(
            from_ref=data["from"],
            to_ref=data["to"],
            action=data["action"],
            condition=data.get("condition"),
            note=data.get("note"),
            parallel=parallel,
            alt=alt,
        )


@dataclass
class Sequence:
    """A sequence diagram modeling runtime interactions."""

    id: str
    name: str
    steps: List[Step]
    description: Optional[str] = None
    trigger: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = {
            "id": self.id,
            "name": self.name,
            "steps": [s.to_dict() for s in self.steps],
        }
        if self.description:
            data["description"] = self.description
        if self.trigger:
            data["trigger"] = self.trigger
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Sequence':
        """Create from dictionary."""
        steps = [Step.from_dict(s) for s in data["steps"]]
        return cls(
            id=data["id"],
            name=data["name"],
            steps=steps,
            description=data.get("description"),
            trigger=data.get("trigger"),
        )


@dataclass
class State:
    """A state in a state machine."""

    id: str
    name: str
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = {
            "id": self.id,
            "name": self.name,
        }
        if self.description:
            data["description"] = self.description
        if self.tags:
            data["tags"] = self.tags
        if self.metadata:
            data["metadata"] = self.metadata
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'State':
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
        )


@dataclass
class Transition:
    """A transition between states in a state machine."""

    from_state: str  # "from" is Python keyword
    to_state: str    # "to" is Python keyword
    trigger: str
    guard: Optional[str] = None
    action: Optional[str] = None
    sequence: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = {
            "from": self.from_state,
            "to": self.to_state,
            "trigger": self.trigger,
        }
        if self.guard:
            data["guard"] = self.guard
        if self.action:
            data["action"] = self.action
        if self.sequence:
            data["sequence"] = self.sequence
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transition':
        """Create from dictionary."""
        return cls(
            from_state=data["from"],
            to_state=data["to"],
            trigger=data["trigger"],
            guard=data.get("guard"),
            action=data.get("action"),
            sequence=data.get("sequence"),
        )


@dataclass
class StateMachine:
    """A state machine capturing operational states for a resource."""

    id: str
    name: str
    resource: str
    initial: str
    states: List[State]
    transitions: List[Transition]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "resource": self.resource,
            "initial": self.initial,
            "states": [s.to_dict() for s in self.states],
            "transitions": [t.to_dict() for t in self.transitions],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StateMachine':
        """Create from dictionary."""
        states = [State.from_dict(s) for s in data["states"]]
        transitions = [Transition.from_dict(t) for t in data["transitions"]]
        return cls(
            id=data["id"],
            name=data["name"],
            resource=data["resource"],
            initial=data["initial"],
            states=states,
            transitions=transitions,
        )


@dataclass
class ArchitectureModel:
    """Complete architecture model with resources, relationships, sequences, and state machines."""

    resources: List[Resource] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)
    sequences: List[Sequence] = field(default_factory=list)
    state_machines: List[StateMachine] = field(default_factory=list)

    # Indexes for fast lookup (built by PathResolver)
    _resource_index: Dict[str, Resource] = field(default_factory=dict, repr=False)
    _interface_index: Dict[str, Interface] = field(default_factory=dict, repr=False)
    _sequence_index: Dict[str, Sequence] = field(default_factory=dict, repr=False)
    _state_machine_index: Dict[str, StateMachine] = field(default_factory=dict, repr=False)

    # Source files (for error reporting)
    _source_files: List[str] = field(default_factory=list, repr=False)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = {}
        if self.resources:
            data["resources"] = [r.to_dict() for r in self.resources]
        if self.relationships:
            data["relationships"] = [r.to_dict() for r in self.relationships]
        if self.sequences:
            data["sequences"] = [s.to_dict() for s in self.sequences]
        if self.state_machines:
            data["state_machines"] = [sm.to_dict() for sm in self.state_machines]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ArchitectureModel':
        """Create from dictionary."""
        resources = [
            Resource.from_dict(r) for r in data.get("resources", [])
        ]
        relationships = [
            Relationship.from_dict(r) for r in data.get("relationships", [])
        ]
        sequences = [
            Sequence.from_dict(s) for s in data.get("sequences", [])
        ]
        state_machines = [
            StateMachine.from_dict(sm) for sm in data.get("state_machines", [])
        ]
        return cls(
            resources=resources,
            relationships=relationships,
            sequences=sequences,
            state_machines=state_machines,
        )

    def resource_count(self) -> int:
        """Total number of resources (including nested)."""
        count = 0
        for resource in self.resources:
            for _, _ in resource.walk_tree():
                count += 1
        return count

    def interface_count(self) -> int:
        """Total number of interfaces across all resources."""
        count = 0
        for resource in self.resources:
            for node, _ in resource.walk_tree():
                count += len(node.interfaces)
        return count

    def sequence_count(self) -> int:
        """Total number of sequences."""
        return len(self.sequences)

    def state_machine_count(self) -> int:
        """Total number of state machines."""
        return len(self.state_machines)
