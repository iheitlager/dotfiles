"""Tests for arch.path_resolver module."""

import pytest
from arch.model import Resource, Interface, ArchitectureModel
from arch.path_resolver import PathResolver, ResolutionResult


def test_path_resolver_empty_model():
    """Test PathResolver with empty model."""
    model = ArchitectureModel()
    resolver = PathResolver(model)

    result = resolver.resolve("nonexistent")
    assert not result.found


def test_path_resolver_single_resource():
    """Test resolving single root resource."""
    resource = Resource(id="dotfiles", name="Dotfiles", type="system")
    model = ArchitectureModel(resources=[resource])
    resolver = PathResolver(model)

    # Resource should be indexed
    assert len(model._resource_index) == 1
    assert "dotfiles" in model._resource_index

    # Resolve by path
    resolved = resolver.resolve_resource("dotfiles")
    assert resolved is not None
    assert resolved.id == "dotfiles"
    assert resolved.full_path == "dotfiles"


def test_path_resolver_nested_resources():
    """Test resolving nested resources."""
    parent = Resource(id="system", name="System", type="system")
    child = Resource(id="service", name="Service", type="go-service")
    parent.children = [child]
    model = ArchitectureModel(resources=[parent])
    resolver = PathResolver(model)

    # Both should be indexed
    assert len(model._resource_index) == 2

    # Resolve parent
    parent_resolved = resolver.resolve_resource("system")
    assert parent_resolved is not None
    assert parent_resolved.id == "system"

    # Resolve child
    child_resolved = resolver.resolve_resource("system.service")
    assert child_resolved is not None
    assert child_resolved.id == "service"
    assert child_resolved.parent == parent
    assert child_resolved.full_path == "system.service"


def test_path_resolver_interfaces():
    """Test resolving interfaces."""
    interface = Interface(id="cli", protocol="bash", direction="request-response")
    resource = Resource(id="bootstrap", name="Bootstrap", type="bash-script", interfaces=[interface])
    model = ArchitectureModel(resources=[resource])
    resolver = PathResolver(model)

    # Interface should be indexed
    assert len(model._interface_index) == 1
    assert "bootstrap.cli" in model._interface_index

    # Resolve interface
    resolved = resolver.resolve_interface("bootstrap.cli")
    assert resolved is not None
    assert resolved.id == "cli"
    assert resolved.full_path == "bootstrap.cli"
    assert resolved.parent_resource == resource


def test_path_resolver_resolve_ambiguous():
    """Test resolve() method with both resource and interface."""
    interface = Interface(id="api", protocol="https", direction="request-response")
    resource = Resource(id="service", name="Service", type="go-service", interfaces=[interface])
    model = ArchitectureModel(resources=[resource])
    resolver = PathResolver(model)

    # Resolve resource path
    result = resolver.resolve("service")
    assert result.found
    assert result.is_resource
    assert result.resource.id == "service"
    assert result.interface is None

    # Resolve interface path
    result = resolver.resolve("service.api")
    assert result.found
    assert result.is_interface
    assert result.interface.id == "api"
    assert result.resource.id == "service"


def test_path_resolver_all_paths():
    """Test getting all resource and interface paths."""
    i1 = Interface(id="cli", protocol="bash", direction="request-response")
    r1 = Resource(id="root", name="Root", type="system", interfaces=[i1])
    r2 = Resource(id="child", name="Child", type="service")
    r1.children = [r2]

    model = ArchitectureModel(resources=[r1])
    resolver = PathResolver(model)

    # Get all paths
    resource_paths = resolver.get_all_resource_paths()
    interface_paths = resolver.get_all_interface_paths()

    assert "root" in resource_paths
    assert "root.child" in resource_paths
    assert "root.cli" in interface_paths


def test_path_resolver_find_by_type():
    """Test finding resources by type."""
    r1 = Resource(id="script1", name="Script 1", type="bash-script")
    r2 = Resource(id="script2", name="Script 2", type="bash-script")
    r3 = Resource(id="service", name="Service", type="go-service")

    model = ArchitectureModel(resources=[r1, r2, r3])
    resolver = PathResolver(model)

    # Find bash scripts
    scripts = resolver.find_resources_by_type("bash-script")
    assert len(scripts) == 2
    assert all(r.type == "bash-script" for r in scripts)


def test_path_resolver_find_by_protocol():
    """Test finding interfaces by protocol."""
    i1 = Interface(id="api1", protocol="https", direction="request-response")
    i2 = Interface(id="api2", protocol="https", direction="request-response")
    i3 = Interface(id="events", protocol="kafka", direction="publish")

    r1 = Resource(id="r1", name="R1", type="service", interfaces=[i1, i3])
    r2 = Resource(id="r2", name="R2", type="service", interfaces=[i2])

    model = ArchitectureModel(resources=[r1, r2])
    resolver = PathResolver(model)

    # Find HTTPS interfaces
    https_interfaces = resolver.find_interfaces_by_protocol("https")
    assert len(https_interfaces) == 2
    assert all(i.protocol == "https" for i in https_interfaces)


def test_path_resolver_parent_chain():
    """Test getting parent chain."""
    root = Resource(id="root", name="Root", type="system")
    child1 = Resource(id="child1", name="Child 1", type="service")
    child2 = Resource(id="child2", name="Child 2", type="module")

    root.children = [child1]
    child1.children = [child2]

    model = ArchitectureModel(resources=[root])
    resolver = PathResolver(model)

    # Get parent chain for deepest child
    child2_resolved = resolver.resolve_resource("root.child1.child2")
    chain = resolver.get_parent_chain(child2_resolved)

    assert len(chain) == 3
    assert [r.id for r in chain] == ["child2", "child1", "root"]


def test_path_resolver_child_resources():
    """Test getting child resources."""
    root = Resource(id="root", name="Root", type="system")
    child1 = Resource(id="child1", name="Child 1", type="service")
    child2 = Resource(id="child2", name="Child 2", type="service")
    grandchild = Resource(id="grandchild", name="Grandchild", type="module")

    child1.children = [grandchild]
    root.children = [child1, child2]

    model = ArchitectureModel(resources=[root])
    resolver = PathResolver(model)

    # Get direct children only
    children = resolver.get_child_resources(root, recursive=False)
    assert len(children) == 2
    assert [c.id for c in children] == ["child1", "child2"]

    # Get all descendants
    descendants = resolver.get_child_resources(root, recursive=True)
    assert len(descendants) == 3
    assert "grandchild" in [d.id for d in descendants]
