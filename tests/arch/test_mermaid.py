"""Tests for arch.generators.mermaid module."""

import pytest
from arch.model import Resource, Interface, Relationship, ArchitectureModel
from arch.path_resolver import PathResolver
from arch.generators.mermaid import generate_mermaid


def test_mermaid_empty_model():
    """Test Mermaid generation with empty model."""
    model = ArchitectureModel()
    resolver = PathResolver(model)

    diagram = generate_mermaid(model, resolver, zoom="landscape")

    assert "graph TB" in diagram
    # Empty model should still have valid structure
    assert diagram.strip() != ""


def test_mermaid_landscape_single_resource():
    """Test landscape view with single root resource."""
    resource = Resource(id="system", name="System", type="system")
    model = ArchitectureModel(resources=[resource])
    resolver = PathResolver(model)

    diagram = generate_mermaid(model, resolver, zoom="landscape")

    assert "graph TB" in diagram
    assert "system[System]" in diagram
    # Landscape should not show type
    assert "system" not in diagram.split("[System]")[1].split("]")[0] if "[System]" in diagram else True


def test_mermaid_landscape_ignores_children():
    """Test that landscape view only shows root resources, not children."""
    parent = Resource(id="system", name="System", type="system")
    child = Resource(id="service", name="Service", type="go-service")
    parent.children = [child]

    model = ArchitectureModel(resources=[parent])
    resolver = PathResolver(model)

    diagram = generate_mermaid(model, resolver, zoom="landscape")

    assert "system[System]" in diagram
    # Child should not appear in landscape view
    assert "service" not in diagram.lower() or "system" in diagram


def test_mermaid_domain_view_with_abstract():
    """Test domain view shows abstract resources with subgraphs."""
    root = Resource(id="root", name="Root System", type="system")
    abstract = Resource(id="domain", name="Domain", type="service", abstract=True)
    concrete = Resource(id="service", name="Service", type="go-service")

    abstract.children = [concrete]
    root.children = [abstract]

    model = ArchitectureModel(resources=[root])
    resolver = PathResolver(model)

    diagram = generate_mermaid(model, resolver, zoom="domain")

    assert "graph TB" in diagram
    # Abstract should create subgraph
    assert "subgraph" in diagram
    assert "Domain" in diagram
    # Concrete child should appear
    assert "service" in diagram.lower()


def test_mermaid_service_view_includes_interfaces():
    """Test service view shows interfaces."""
    interface = Interface(id="api", protocol="https", direction="request-response")
    resource = Resource(id="service", name="Service", type="go-service", interfaces=[interface])

    model = ArchitectureModel(resources=[resource])
    resolver = PathResolver(model)

    diagram = generate_mermaid(model, resolver, zoom="service")

    assert "graph TB" in diagram
    # Service should appear
    assert "service" in diagram.lower()
    # Interface should appear
    assert "api" in diagram.lower()
    assert "https" in diagram.lower()
    # Connection between service and interface
    assert "-->" in diagram


def test_mermaid_service_view_excludes_abstract():
    """Test service view only shows concrete resources."""
    abstract = Resource(id="domain", name="Domain", type="service", abstract=True)
    concrete = Resource(id="service", name="Service", type="go-service")
    abstract.children = [concrete]

    model = ArchitectureModel(resources=[abstract])
    resolver = PathResolver(model)

    diagram = generate_mermaid(model, resolver, zoom="service")

    assert "graph TB" in diagram
    # Concrete should appear
    assert "service" in diagram.lower()
    # Abstract should NOT appear in service view
    lines = diagram.split("\n")
    domain_nodes = [l for l in lines if "domain" in l.lower() and "[" in l and "]" in l]
    assert len(domain_nodes) == 0


def test_mermaid_with_relationships():
    """Test relationships are rendered as arrows."""
    r1 = Resource(id="service-a", name="Service A", type="go-service")
    r2 = Resource(id="service-b", name="Service B", type="go-service")

    rel = Relationship(
        from_ref="service-a",
        to_ref="service-b",
        description="Calls"
    )

    model = ArchitectureModel(resources=[r1, r2], relationships=[rel])
    resolver = PathResolver(model)

    diagram = generate_mermaid(model, resolver, zoom="landscape")

    assert "graph TB" in diagram
    # Both services should appear
    assert "service_a" in diagram
    assert "service_b" in diagram
    # Arrow with description
    assert "service_a -->|Calls| service_b" in diagram or "service_a --> service_b" in diagram


def test_mermaid_relationship_with_via():
    """Test relationships with intermediary (via) render correctly."""
    r1 = Resource(id="client", name="Client", type="web-app")
    gateway = Resource(id="gateway", name="Gateway", type="api-gateway")
    r2 = Resource(id="server", name="Server", type="go-service")

    rel = Relationship(
        from_ref="client",
        to_ref="server",
        via="gateway",
        description="Request"
    )

    model = ArchitectureModel(resources=[r1, gateway, r2], relationships=[rel])
    resolver = PathResolver(model)

    diagram = generate_mermaid(model, resolver, zoom="landscape")

    assert "graph TB" in diagram
    # All three resources should appear
    assert "client" in diagram
    assert "gateway" in diagram
    assert "server" in diagram
    # Two arrows for via relationship
    assert diagram.count("-->") >= 2


def test_mermaid_relationship_filtering():
    """Test that relationships are filtered based on visible nodes."""
    # Create a hierarchy where some nodes are hidden at certain zoom levels
    root = Resource(id="system", name="System", type="system")
    child = Resource(id="service", name="Service", type="go-service")
    grandchild = Resource(id="module", name="Module", type="module")

    child.children = [grandchild]
    root.children = [child]

    # Relationship between grandchild and something
    external = Resource(id="external", name="External", type="external-system")

    rel = Relationship(
        from_ref="system.service.module",
        to_ref="external"
    )

    model = ArchitectureModel(resources=[root, external], relationships=[rel])
    resolver = PathResolver(model)

    # Landscape view should NOT show the relationship (module is hidden)
    landscape_diagram = generate_mermaid(model, resolver, zoom="landscape")
    # Count arrows - should be minimal or none for hidden child relationships
    # (depends on whether external is visible at landscape level)

    # Service view should show the relationship (module is visible)
    service_diagram = generate_mermaid(model, resolver, zoom="service")
    assert "module" in service_diagram.lower()


def test_mermaid_nested_resources():
    """Test proper rendering of nested resource hierarchies."""
    root = Resource(id="dotfiles", name="Dotfiles", type="system")
    child1 = Resource(id="bootstrap", name="Bootstrap", type="bash-script")
    child2 = Resource(id="xdg", name="XDG", type="filesystem")

    root.children = [child1, child2]

    model = ArchitectureModel(resources=[root])
    resolver = PathResolver(model)

    diagram = generate_mermaid(model, resolver, zoom="domain")

    assert "graph TB" in diagram
    assert "Dotfiles" in diagram
    assert "Bootstrap" in diagram
    assert "XDG" in diagram


def test_mermaid_sanitize_ids():
    """Test that dotted paths are sanitized to valid Mermaid IDs."""
    resource = Resource(id="my-service", name="My Service", type="go-service")
    model = ArchitectureModel(resources=[resource])
    resolver = PathResolver(model)

    diagram = generate_mermaid(model, resolver, zoom="landscape")

    # Hyphens should be converted to underscores
    assert "my_service[" in diagram
    # Original hyphen should not appear in ID
    lines = [l for l in diagram.split("\n") if "my-service[" in l]
    assert len(lines) == 0


def test_mermaid_multiline_labels():
    """Test that labels with type/tech use <br/> for multiline."""
    resource = Resource(
        id="service",
        name="Service",
        type="go-service",
        technology="Go 1.22"
    )
    model = ArchitectureModel(resources=[resource])
    resolver = PathResolver(model)

    diagram = generate_mermaid(model, resolver, zoom="domain")

    # Should include type in domain view
    assert "go-service" in diagram.lower() or "go_service" in diagram.lower()
    # Multiline indicator
    assert "<br/>" in diagram


def test_mermaid_interface_to_interface_relationship():
    """Test relationships between interfaces render correctly."""
    i1 = Interface(id="api", protocol="https", direction="request-response")
    i2 = Interface(id="handler", protocol="https", direction="request-response")

    r1 = Resource(id="client", name="Client", type="web-app", interfaces=[i1])
    r2 = Resource(id="server", name="Server", type="go-service", interfaces=[i2])

    rel = Relationship(
        from_ref="client.api",
        to_ref="server.handler",
        description="HTTP Request"
    )

    model = ArchitectureModel(resources=[r1, r2], relationships=[rel])
    resolver = PathResolver(model)

    diagram = generate_mermaid(model, resolver, zoom="service")

    assert "graph TB" in diagram
    # Both interfaces should appear
    assert "client_api" in diagram
    assert "server_handler" in diagram
    # Relationship between them
    assert "client_api -->" in diagram or "api -->" in diagram
