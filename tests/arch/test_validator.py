"""Tests for arch.validator module."""

import pytest
from arch.model import Resource, Interface, Relationship, ArchitectureModel
from arch.validator import ArchitectureValidator, Severity


def test_validator_empty_model():
    """Test validator with empty model."""
    model = ArchitectureModel()
    validator = ArchitectureValidator(model)
    result = validator.validate()

    assert result.valid
    assert len(result.errors) == 0
    assert len(result.warnings) == 0


def test_validator_valid_model():
    """Test validator with a valid model."""
    interface = Interface(id="api", protocol="https", direction="request-response")
    resource = Resource(id="service", name="Service", type="go-service", interfaces=[interface])
    model = ArchitectureModel(resources=[resource])

    validator = ArchitectureValidator(model)
    result = validator.validate()

    assert result.valid
    assert len(result.errors) == 0


def test_unique_ids_duplicate_siblings():
    """Test that duplicate sibling IDs are detected."""
    r1 = Resource(id="service", name="Service 1", type="service")
    r2 = Resource(id="service", name="Service 2", type="service")  # duplicate ID

    model = ArchitectureModel(resources=[r1, r2])
    validator = ArchitectureValidator(model)
    result = validator.validate()

    assert not result.valid
    assert len(result.errors) >= 1
    assert any("Duplicate" in e.message and "service" in e.message for e in result.errors)
    assert any(e.rule == "unique-ids" for e in result.errors)


def test_unique_ids_nested_duplicates():
    """Test that duplicate IDs in nested children are detected."""
    parent = Resource(id="parent", name="Parent", type="system")
    child1 = Resource(id="child", name="Child 1", type="service")
    child2 = Resource(id="child", name="Child 2", type="service")  # duplicate
    parent.children = [child1, child2]

    model = ArchitectureModel(resources=[parent])
    validator = ArchitectureValidator(model)
    result = validator.validate()

    assert not result.valid
    assert len(result.errors) >= 1
    assert any("sibling ID 'child'" in e.message for e in result.errors)


def test_abstract_resource_without_children():
    """Test that abstract resources without children are flagged."""
    resource = Resource(id="service", name="Service", type="service", abstract=True)
    # No children!

    model = ArchitectureModel(resources=[resource])
    validator = ArchitectureValidator(model)
    result = validator.validate()

    assert not result.valid
    assert len(result.errors) == 1
    assert "Abstract resource" in result.errors[0].message
    assert "no children" in result.errors[0].message
    assert result.errors[0].rule == "abstract-resources"


def test_abstract_resource_with_children():
    """Test that abstract resources with children pass validation."""
    parent = Resource(id="domain", name="Domain", type="service", abstract=True)
    child = Resource(id="service", name="Service", type="go-service")
    parent.children = [child]

    model = ArchitectureModel(resources=[parent])
    validator = ArchitectureValidator(model)
    result = validator.validate()

    assert result.valid
    assert len(result.errors) == 0


def test_relationship_invalid_from_reference():
    """Test that invalid 'from' references are detected."""
    resource = Resource(id="service", name="Service", type="service")
    relationship = Relationship(
        from_ref="nonexistent",
        to_ref="service",
        description="Invalid from"
    )

    model = ArchitectureModel(resources=[resource], relationships=[relationship])
    validator = ArchitectureValidator(model)
    result = validator.validate()

    assert not result.valid
    assert len(result.errors) >= 1
    assert any("from" in e.message and "not found" in e.message for e in result.errors)
    assert any(e.rule == "relationship-references" for e in result.errors)


def test_relationship_invalid_to_reference():
    """Test that invalid 'to' references are detected."""
    resource = Resource(id="service", name="Service", type="service")
    relationship = Relationship(
        from_ref="service",
        to_ref="nonexistent",
        description="Invalid to"
    )

    model = ArchitectureModel(resources=[resource], relationships=[relationship])
    validator = ArchitectureValidator(model)
    result = validator.validate()

    assert not result.valid
    assert len(result.errors) >= 1
    assert any("to" in e.message and "not found" in e.message for e in result.errors)


def test_relationship_invalid_via_reference():
    """Test that invalid 'via' references are detected."""
    r1 = Resource(id="service1", name="Service 1", type="service")
    r2 = Resource(id="service2", name="Service 2", type="service")
    relationship = Relationship(
        from_ref="service1",
        to_ref="service2",
        via="nonexistent-gateway",
        description="Invalid via"
    )

    model = ArchitectureModel(resources=[r1, r2], relationships=[relationship])
    validator = ArchitectureValidator(model)
    result = validator.validate()

    assert not result.valid
    assert len(result.errors) >= 1
    assert any("via" in e.message and "not found" in e.message for e in result.errors)


def test_relationship_valid_references():
    """Test that valid relationship references pass validation."""
    i1 = Interface(id="api", protocol="https", direction="request-response")
    i2 = Interface(id="handler", protocol="https", direction="request-response")
    r1 = Resource(id="client", name="Client", type="web-app", interfaces=[i1])
    r2 = Resource(id="server", name="Server", type="go-service", interfaces=[i2])

    relationship = Relationship(
        from_ref="client.api",
        to_ref="server.handler",
        description="Client calls server"
    )

    model = ArchitectureModel(resources=[r1, r2], relationships=[relationship])
    validator = ArchitectureValidator(model)
    result = validator.validate()

    assert result.valid
    assert len(result.errors) == 0


def test_orphan_interface_warning():
    """Test that unused interfaces generate warnings."""
    i1 = Interface(id="api", protocol="https", direction="request-response")
    i2 = Interface(id="unused", protocol="grpc", direction="request-response")  # orphan

    resource = Resource(id="service", name="Service", type="service", interfaces=[i1, i2])
    model = ArchitectureModel(resources=[resource])

    validator = ArchitectureValidator(model)
    result = validator.validate()

    # Model is still valid (warnings don't invalidate)
    assert result.valid
    assert len(result.errors) == 0
    assert len(result.warnings) >= 1
    assert any("not used" in w.message for w in result.warnings)
    assert any(w.rule == "orphan-interfaces" for w in result.warnings)


def test_orphan_interface_used_in_relationship():
    """Test that interfaces used in relationships are not flagged as orphans."""
    i1 = Interface(id="api", protocol="https", direction="request-response")
    i2 = Interface(id="handler", protocol="https", direction="request-response")

    r1 = Resource(id="client", name="Client", type="web-app", interfaces=[i1])
    r2 = Resource(id="server", name="Server", type="go-service", interfaces=[i2])

    relationship = Relationship(
        from_ref="client.api",
        to_ref="server.handler",
        description="Client to server"
    )

    model = ArchitectureModel(resources=[r1, r2], relationships=[relationship])
    validator = ArchitectureValidator(model)
    result = validator.validate()

    assert result.valid
    # No orphan warnings because both interfaces are used
    assert not any(w.rule == "orphan-interfaces" for w in result.warnings)


def test_multiple_errors():
    """Test that multiple errors are collected."""
    # Create a model with multiple issues:
    # 1. Duplicate IDs
    # 2. Abstract without children
    # 3. Invalid relationship reference

    r1 = Resource(id="service", name="Service 1", type="service")
    r2 = Resource(id="service", name="Service 2", type="service")  # duplicate
    r3 = Resource(id="abstract", name="Abstract", type="service", abstract=True)  # no children

    relationship = Relationship(
        from_ref="nonexistent",
        to_ref="service",
        description="Invalid"
    )

    model = ArchitectureModel(resources=[r1, r2, r3], relationships=[relationship])
    validator = ArchitectureValidator(model)
    result = validator.validate()

    assert not result.valid
    assert len(result.errors) >= 3
    assert result.total_issues >= 3


def test_validation_result_properties():
    """Test ValidationResult helper methods."""
    result = ArchitectureValidator(ArchitectureModel()).result

    assert result.valid
    assert result.total_issues == 0

    result.add_error("Test error", rule="test")
    assert not result.valid
    assert len(result.errors) == 1
    assert result.total_issues == 1

    result.add_warning("Test warning", rule="test")
    assert not result.valid  # Still invalid due to error
    assert len(result.warnings) == 1
    assert result.total_issues == 2


def test_validation_issue_fields():
    """Test that ValidationIssue captures all fields correctly."""
    validator = ArchitectureValidator(ArchitectureModel())
    validator.result.add_error(
        "Test error",
        file_path="test.yaml",
        line=42,
        path="system.service",
        rule="test-rule"
    )

    issue = validator.result.errors[0]
    assert issue.severity == Severity.ERROR
    assert issue.message == "Test error"
    assert issue.file_path == "test.yaml"
    assert issue.line == 42
    assert issue.path == "system.service"
    assert issue.rule == "test-rule"
