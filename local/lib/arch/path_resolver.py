"""
Path resolution for architecture models.

Handles dotted path notation for resources and interfaces:
- ResourceRef: system.domain.service
- InterfaceRef: system.domain.service.interface-id

Builds indexes for O(1) lookup performance.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Tuple

from .model import ArchitectureModel, Resource, Interface


@dataclass
class ResolutionResult:
    """Result of resolving a path reference."""

    path: str
    resource: Optional[Resource] = None
    interface: Optional[Interface] = None
    is_resource: bool = False
    is_interface: bool = False

    @property
    def found(self) -> bool:
        """Whether the path resolved to something."""
        return self.resource is not None or self.interface is not None


class PathResolver:
    """
    Resolves dotted path notation to resources and interfaces.

    Builds indexes for O(1) lookup:
    - _resource_index: Maps full path -> Resource
    - _interface_index: Maps full path -> Interface

    Example:
        >>> resolver = PathResolver(model)
        >>> resource = resolver.resolve_resource("dotfiles.bootstrap")
        >>> interface = resolver.resolve_interface("dotfiles.bootstrap.cli")
    """

    def __init__(self, model: ArchitectureModel):
        """
        Initialize path resolver with architecture model.

        Args:
            model: Architecture model to index
        """
        self.model = model
        self._build_indexes()

    def _build_indexes(self) -> None:
        """Build path indexes by walking the resource tree."""

        def walk_resource(resource: Resource, parent_path: str = ""):
            # Build full path for this resource
            full_path = f"{parent_path}.{resource.id}" if parent_path else resource.id
            resource.full_path = full_path

            # Index this resource
            self.model._resource_index[full_path] = resource

            # Index interfaces for this resource
            for interface in resource.interfaces:
                interface_path = f"{full_path}.{interface.id}"
                interface.full_path = interface_path
                interface.parent_resource = resource
                self.model._interface_index[interface_path] = interface

            # Recurse into children
            for child in resource.children:
                child.parent = resource
                walk_resource(child, full_path)

        # Walk all root resources
        for root in self.model.resources:
            walk_resource(root)

    def resolve_resource(self, path: str) -> Optional[Resource]:
        """
        Resolve dotted path to resource.

        Args:
            path: Dotted path (e.g., "dotfiles.bootstrap")

        Returns:
            Resource if found, None otherwise

        Example:
            >>> resource = resolver.resolve_resource("dotfiles.bootstrap")
            >>> print(resource.name)  # "Bootstrap Script"
        """
        return self.model._resource_index.get(path)

    def resolve_interface(self, path: str) -> Optional[Interface]:
        """
        Resolve dotted path to interface.

        Args:
            path: Dotted path (e.g., "dotfiles.bootstrap.cli")

        Returns:
            Interface if found, None otherwise

        Example:
            >>> interface = resolver.resolve_interface("dotfiles.bootstrap.cli")
            >>> print(interface.protocol)  # "bash"
        """
        return self.model._interface_index.get(path)

    def resolve(self, path: str) -> ResolutionResult:
        """
        Resolve path to either resource or interface.

        Tries interface first (longer path), then resource.

        Args:
            path: Dotted path

        Returns:
            ResolutionResult with found resource/interface

        Example:
            >>> result = resolver.resolve("dotfiles.bootstrap.cli")
            >>> if result.is_interface:
            ...     print(f"Found interface: {result.interface.protocol}")
        """
        # Try interface first (longer path)
        interface = self.resolve_interface(path)
        if interface:
            # Get parent resource
            resource_path = ".".join(path.split(".")[:-1])
            resource = self.resolve_resource(resource_path)
            return ResolutionResult(
                path=path,
                resource=resource,
                interface=interface,
                is_interface=True
            )

        # Try resource
        resource = self.resolve_resource(path)
        if resource:
            return ResolutionResult(
                path=path,
                resource=resource,
                is_resource=True
            )

        # Not found
        return ResolutionResult(path=path)

    def get_all_resource_paths(self) -> list[str]:
        """Get all resource paths in the model."""
        return list(self.model._resource_index.keys())

    def get_all_interface_paths(self) -> list[str]:
        """Get all interface paths in the model."""
        return list(self.model._interface_index.keys())

    def find_resources_by_type(self, resource_type: str) -> list[Resource]:
        """
        Find all resources with a specific type.

        Args:
            resource_type: Type to search for (e.g., "bash-script")

        Returns:
            List of matching resources
        """
        return [
            resource
            for resource in self.model._resource_index.values()
            if resource.type == resource_type
        ]

    def find_interfaces_by_protocol(self, protocol: str) -> list[Interface]:
        """
        Find all interfaces with a specific protocol.

        Args:
            protocol: Protocol to search for (e.g., "kafka")

        Returns:
            List of matching interfaces
        """
        return [
            interface
            for interface in self.model._interface_index.values()
            if interface.protocol == protocol
        ]

    def get_parent_chain(self, resource: Resource) -> list[Resource]:
        """
        Get the chain of parent resources up to the root.

        Args:
            resource: Starting resource

        Returns:
            List of resources from resource to root (inclusive)

        Example:
            >>> resource = resolver.resolve_resource("dotfiles.bootstrap.cli")
            >>> chain = resolver.get_parent_chain(resource)
            >>> [r.id for r in chain]  # ["cli", "bootstrap", "dotfiles"]
        """
        chain = [resource]
        current = resource.parent
        while current is not None:
            chain.append(current)
            current = current.parent
        return chain

    def get_child_resources(self, resource: Resource, recursive: bool = False) -> list[Resource]:
        """
        Get child resources of a resource.

        Args:
            resource: Parent resource
            recursive: If True, include all descendants

        Returns:
            List of child resources
        """
        if not recursive:
            return resource.children

        # Recursive: walk entire subtree
        children = []
        for child in resource.children:
            children.append(child)
            children.extend(self.get_child_resources(child, recursive=True))
        return children
