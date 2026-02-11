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
class ArchitectureModel:
    """Complete architecture model with resources and relationships."""

    resources: List[Resource] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)

    # Indexes for fast lookup (built by PathResolver)
    _resource_index: Dict[str, Resource] = field(default_factory=dict, repr=False)
    _interface_index: Dict[str, Interface] = field(default_factory=dict, repr=False)

    # Source files (for error reporting)
    _source_files: List[str] = field(default_factory=list, repr=False)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = {}
        if self.resources:
            data["resources"] = [r.to_dict() for r in self.resources]
        if self.relationships:
            data["relationships"] = [r.to_dict() for r in self.relationships]
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
        return cls(resources=resources, relationships=relationships)

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
