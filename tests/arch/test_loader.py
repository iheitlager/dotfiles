"""Tests for arch.loader module."""

import pytest
import tempfile
from pathlib import Path
from arch.loader import (
    load_yaml_file,
    load_architecture,
    save_architecture,
    LoadError,
    _merge_models,
)
from arch.model import Resource, ArchitectureModel


def test_load_yaml_file_nonexistent():
    """Test loading nonexistent file raises LoadError."""
    with pytest.raises(LoadError, match="File not found"):
        load_yaml_file("nonexistent.yaml")


def test_load_yaml_file_valid():
    """Test loading valid YAML file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("resources:\n  - id: test\n    name: Test\n    type: service\n")
        temp_path = f.name

    try:
        data = load_yaml_file(temp_path)
        assert "resources" in data
        assert len(data["resources"]) == 1
        assert data["resources"][0]["id"] == "test"
    finally:
        Path(temp_path).unlink()


def test_load_yaml_file_empty():
    """Test loading empty YAML file returns empty dict."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("")
        temp_path = f.name

    try:
        data = load_yaml_file(temp_path)
        assert data == {}
    finally:
        Path(temp_path).unlink()


def test_load_yaml_file_invalid_yaml():
    """Test loading invalid YAML raises LoadError."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("invalid: yaml: content:\n  - broken")
        temp_path = f.name

    try:
        with pytest.raises(LoadError, match="YAML parsing error"):
            load_yaml_file(temp_path)
    finally:
        Path(temp_path).unlink()


def test_merge_models_empty():
    """Test merging empty models."""
    result = _merge_models([])
    assert result["resources"] == []
    assert result["relationships"] == []


def test_merge_models_single():
    """Test merging single model."""
    model = {
        "resources": [{"id": "r1", "name": "R1", "type": "service"}],
        "relationships": []
    }
    result = _merge_models([model])
    assert len(result["resources"]) == 1


def test_merge_models_multiple():
    """Test merging multiple models."""
    model1 = {
        "resources": [{"id": "r1", "name": "R1", "type": "service"}],
        "relationships": []
    }
    model2 = {
        "resources": [{"id": "r2", "name": "R2", "type": "service"}],
        "relationships": [{"from": "r1", "to": "r2"}]
    }
    result = _merge_models([model1, model2])
    assert len(result["resources"]) == 2
    assert len(result["relationships"]) == 1


def test_merge_models_duplicate_ids():
    """Test merging models with duplicate IDs raises error."""
    model1 = {
        "resources": [{"id": "r1", "name": "R1", "type": "service"}],
    }
    model2 = {
        "resources": [{"id": "r1", "name": "R1 Again", "type": "service"}],
    }
    with pytest.raises(LoadError, match="Duplicate resource ID: r1"):
        _merge_models([model1, model2])


def test_load_architecture_nonexistent():
    """Test loading from nonexistent path raises error."""
    with pytest.raises(LoadError, match="Path not found"):
        load_architecture("nonexistent/path")


def test_load_architecture_single_file():
    """Test loading architecture from single file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("""
resources:
  - id: test-service
    name: Test Service
    type: go-service
relationships: []
""")
        temp_path = f.name

    try:
        model = load_architecture(temp_path, validate_schema=False)
        assert len(model.resources) == 1
        assert model.resources[0].id == "test-service"
        assert len(model._source_files) == 1
    finally:
        Path(temp_path).unlink()


def test_load_architecture_directory():
    """Test loading architecture from directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create two YAML files
        file1 = Path(tmpdir) / "file1.yaml"
        file1.write_text("""
resources:
  - id: service1
    name: Service 1
    type: service
""")

        file2 = Path(tmpdir) / "file2.yaml"
        file2.write_text("""
resources:
  - id: service2
    name: Service 2
    type: service
relationships:
  - from: service1
    to: service2
""")

        model = load_architecture(tmpdir, validate_schema=False)
        assert len(model.resources) == 2
        assert len(model.relationships) == 1
        assert len(model._source_files) == 2


def test_save_architecture():
    """Test saving architecture to file."""
    resource = Resource(id="test", name="Test", type="service")
    model = ArchitectureModel(resources=[resource])

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_path = f.name

    try:
        save_architecture(model, temp_path)

        # Load it back
        loaded = load_architecture(temp_path, validate_schema=False)
        assert len(loaded.resources) == 1
        assert loaded.resources[0].id == "test"
    finally:
        Path(temp_path).unlink()
