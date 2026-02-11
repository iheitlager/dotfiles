"""Tests for arch.model module."""

import pytest
from arch.model import Interface, CodeRef, Resource, Relationship, ArchitectureModel


def test_interface_creation():
    """Test Interface dataclass creation."""
    interface = Interface(
        id="cli",
        protocol="bash",
        direction="request-response",
        description="Command-line interface"
    )
    assert interface.id == "cli"
    assert interface.protocol == "bash"
    assert interface.direction == "request-response"


def test_interface_to_dict():
    """Test Interface serialization."""
    interface = Interface(id="api", protocol="https", direction="request-response")
    data = interface.to_dict()
    assert data["id"] == "api"
    assert data["protocol"] == "https"
    assert data["direction"] == "request-response"


def test_interface_from_dict():
    """Test Interface deserialization."""
    data = {
        "id": "cache",
        "protocol": "redis",
        "direction": "bidirectional"
    }
    interface = Interface.from_dict(data)
    assert interface.id == "cache"
    assert interface.protocol == "redis"


def test_code_ref_creation():
    """Test CodeRef dataclass creation."""
    ref = CodeRef(
        path="script/bootstrap",
        lines="53-73",
        function="setup_xdg_dirs()"
    )
    assert ref.path == "script/bootstrap"
    assert ref.lines == "53-73"


def test_resource_creation():
    """Test Resource dataclass creation."""
    resource = Resource(
        id="bootstrap",
        name="Bootstrap Script",
        type="bash-script",
        technology="Bash 5.2"
    )
    assert resource.id == "bootstrap"
    assert resource.name == "Bootstrap Script"
    assert resource.abstract is False


def test_resource_with_children():
    """Test Resource with nested children."""
    parent = Resource(id="system", name="System", type="system")
    child = Resource(id="service", name="Service", type="go-service")
    parent.children = [child]

    assert len(parent.children) == 1
    assert parent.children[0].id == "service"


def test_resource_walk_tree():
    """Test Resource tree walking."""
    root = Resource(id="root", name="Root", type="system")
    child1 = Resource(id="child1", name="Child 1", type="service")
    child2 = Resource(id="child2", name="Child 2", type="service")
    root.children = [child1, child2]

    nodes = list(root.walk_tree())
    assert len(nodes) == 3  # root + 2 children
    assert nodes[0][1] == 0  # root at depth 0
    assert nodes[1][1] == 1  # child1 at depth 1
    assert nodes[2][1] == 1  # child2 at depth 1


def test_relationship_creation():
    """Test Relationship dataclass creation."""
    rel = Relationship(
        from_ref="system.service-a",
        to_ref="system.service-b",
        description="Makes requests"
    )
    assert rel.from_ref == "system.service-a"
    assert rel.to_ref == "system.service-b"


def test_relationship_from_dict():
    """Test Relationship deserialization with 'from'/'to' keywords."""
    data = {
        "from": "service-a",
        "to": "service-b",
        "description": "Connects"
    }
    rel = Relationship.from_dict(data)
    assert rel.from_ref == "service-a"
    assert rel.to_ref == "service-b"


def test_architecture_model_empty():
    """Test empty ArchitectureModel."""
    model = ArchitectureModel()
    assert len(model.resources) == 0
    assert len(model.relationships) == 0
    assert model.resource_count() == 0
    assert model.interface_count() == 0


def test_architecture_model_with_resources():
    """Test ArchitectureModel with resources."""
    r1 = Resource(id="r1", name="Resource 1", type="service")
    r2 = Resource(id="r2", name="Resource 2", type="service")
    model = ArchitectureModel(resources=[r1, r2])

    assert len(model.resources) == 2
    assert model.resource_count() == 2


def test_architecture_model_interface_count():
    """Test counting interfaces across resources."""
    i1 = Interface(id="i1", protocol="https", direction="request-response")
    i2 = Interface(id="i2", protocol="kafka", direction="publish")

    r1 = Resource(id="r1", name="R1", type="service", interfaces=[i1, i2])
    model = ArchitectureModel(resources=[r1])

    assert model.interface_count() == 2
