"""Integration tests for the architecture system.

Tests the complete system using the real dotfiles architecture model.
"""

import pytest
import tempfile
import subprocess
from pathlib import Path
from arch.loader import load_architecture, LoadError
from arch.path_resolver import PathResolver
from arch.validator import ArchitectureValidator
from arch.commands.list import render_list
from arch.commands.validate import render_validate
from arch.commands.diagram import render_diagram
from arch.generators.mermaid import generate_mermaid


# Fixture for the real dotfiles architecture directory
@pytest.fixture
def dotfiles_arch_dir():
    """Return the path to the dotfiles architecture directory."""
    repo_root = Path(__file__).parent.parent.parent
    arch_dir = repo_root / ".openspec" / "architecture"

    if not arch_dir.exists():
        pytest.skip(f"Architecture directory not found: {arch_dir}")

    return arch_dir


@pytest.fixture
def dotfiles_model(dotfiles_arch_dir):
    """Load the complete dotfiles architecture model."""
    return load_architecture(dotfiles_arch_dir)


@pytest.fixture
def dotfiles_resolver(dotfiles_model):
    """Create a PathResolver for the dotfiles model."""
    return PathResolver(dotfiles_model)


class TestMultiFileLoading:
    """Test loading architecture from multiple YAML files."""

    def test_load_multi_file_architecture(self, dotfiles_arch_dir):
        """Test loading the complete dotfiles architecture with 4 YAML files."""
        model = load_architecture(dotfiles_arch_dir)

        # Should have loaded landscape.yaml + 3 resource files
        assert len(model.resources) > 0

        # Check that we have the top-level resources
        resource_ids = {r.id for r in model.resources}
        assert "dotfiles" in resource_ids

        # Check that we have relationships
        assert len(model.relationships) > 0

    def test_multi_file_resource_count(self, dotfiles_model):
        """Test that all resources from all files are loaded."""
        # Count all resources (including nested)
        def count_resources(resources):
            count = len(resources)
            for r in resources:
                count += count_resources(r.children)
            return count

        total = count_resources(dotfiles_model.resources)

        # We should have around 49 resources (from validation output)
        assert total >= 40, f"Expected at least 40 resources, got {total}"
        assert total <= 60, f"Expected at most 60 resources, got {total}"

    def test_multi_file_interface_count(self, dotfiles_model):
        """Test that all interfaces from all files are loaded."""
        def count_interfaces(resources):
            count = sum(len(r.interfaces) for r in resources)
            for r in resources:
                count += count_interfaces(r.children)
            return count

        total = count_interfaces(dotfiles_model.resources)

        # We should have around 46 interfaces
        assert total >= 40, f"Expected at least 40 interfaces, got {total}"
        assert total <= 60, f"Expected at most 60 interfaces, got {total}"

    def test_multi_file_relationship_count(self, dotfiles_model):
        """Test that all relationships from all files are loaded."""
        # We should have around 43 relationships
        assert len(dotfiles_model.relationships) >= 40
        assert len(dotfiles_model.relationships) <= 60


class TestCrossFileReferences:
    """Test referential integrity across multiple files."""

    def test_cross_file_referential_integrity(self, dotfiles_model):
        """Test that relationships reference resources from different files."""
        validator = ArchitectureValidator(dotfiles_model)
        result = validator.validate()

        # Should have no referential integrity errors
        assert len(result.errors) == 0, \
            f"Found {len(result.errors)} referential integrity errors"

    def test_landscape_to_resource_references(self, dotfiles_model, dotfiles_resolver):
        """Test that landscape.yaml relationships reference resources from resource files."""
        # Find a relationship from landscape
        landscape_relationships = [
            r for r in dotfiles_model.relationships
            if r.from_ref.startswith("dotfiles.")
        ]

        assert len(landscape_relationships) > 0

        # Verify that these can be resolved
        for rel in landscape_relationships[:5]:  # Check first 5
            from_result = dotfiles_resolver.resolve(rel.from_ref)
            to_result = dotfiles_resolver.resolve(rel.to_ref)

            assert from_result.found, f"Cannot resolve from: {rel.from_ref}"
            assert to_result.found, f"Cannot resolve to: {rel.to_ref}"

    def test_resource_file_cross_references(self, dotfiles_model, dotfiles_resolver):
        """Test relationships between different resource files."""
        # Find relationships that cross between resource files
        # e.g., tools.yaml referencing core.yaml resources
        tool_to_core = [
            r for r in dotfiles_model.relationships
            if ("tool" in r.from_ref and "xdg" in r.to_ref) or
               ("tool" in r.from_ref and "bootstrap" in r.to_ref)
        ]

        # Should have some cross-file relationships
        assert len(tool_to_core) > 0

        # Verify they resolve correctly
        for rel in tool_to_core:
            from_result = dotfiles_resolver.resolve(rel.from_ref)
            to_result = dotfiles_resolver.resolve(rel.to_ref)

            assert from_result.found
            assert to_result.found


class TestDiagramGeneration:
    """Test diagram generation from the real model."""

    def test_generate_landscape_diagram(self, dotfiles_model, dotfiles_resolver):
        """Test generating landscape-level diagram."""
        diagram = generate_mermaid(dotfiles_model, dotfiles_resolver, zoom="landscape")

        assert "graph TB" in diagram
        assert "dotfiles" in diagram.lower()
        assert "developer" in diagram.lower() or "Dotfiles System" in diagram

    def test_generate_domain_diagram(self, dotfiles_model, dotfiles_resolver):
        """Test generating domain-level diagram."""
        diagram = generate_mermaid(dotfiles_model, dotfiles_resolver, zoom="domain")

        assert "graph TB" in diagram
        assert "subgraph" in diagram  # Should have domain groupings
        # Should have some concrete resources
        assert "bootstrap" in diagram.lower() or "xdg" in diagram.lower()

    def test_generate_service_diagram(self, dotfiles_model, dotfiles_resolver):
        """Test generating service-level diagram with full detail."""
        diagram = generate_mermaid(dotfiles_model, dotfiles_resolver, zoom="service")

        assert "graph TB" in diagram
        # Should have many resources at service level
        assert diagram.count("-->") > 20  # Many relationships

    def test_diagram_output_to_file(self, dotfiles_model, dotfiles_resolver):
        """Test writing diagram to file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            output_path = Path(f.name)

        try:
            exit_code = render_diagram(
                dotfiles_model,
                dotfiles_resolver,
                format="mermaid",
                zoom="landscape",
                output=str(output_path),
                preview=False
            )

            assert exit_code == 0
            assert output_path.exists()

            content = output_path.read_text()
            assert "# Architecture Diagram" in content
            assert "```mermaid" in content
            assert "```" in content
        finally:
            output_path.unlink(missing_ok=True)


class TestValidationWithErrors:
    """Test validation with intentionally broken references."""

    def test_validation_with_missing_resource_reference(self, dotfiles_arch_dir):
        """Test validation catches missing resource references."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create a model with a broken reference
            (tmpdir / "broken.yaml").write_text("""
resources:
  - id: service-a
    name: Service A
    type: service
    interfaces:
      - id: api
        protocol: https
        direction: request-response

relationships:
  - from: service-a.api
    to: nonexistent-service.api
    description: This reference is broken
""")

            # Load the model (should succeed)
            model = load_architecture(tmpdir)

            # But validation should find the broken reference
            validator = ArchitectureValidator(model)
            result = validator.validate()

            # Should have validation errors
            assert len(result.errors) > 0
            assert not result.valid

    def test_validation_with_duplicate_ids(self, dotfiles_arch_dir):
        """Test validation catches duplicate resource IDs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create model with duplicate IDs
            (tmpdir / "duplicates.yaml").write_text("""
resources:
  - id: service
    name: Service A
    type: service
  - id: service
    name: Service B (duplicate ID)
    type: service
""")

            with pytest.raises(LoadError, match="Duplicate resource ID"):
                load_architecture(tmpdir)


class TestListCommand:
    """Test arch list command integration."""

    def test_list_all_resources(self, dotfiles_model, dotfiles_resolver, capsys):
        """Test listing all resources."""
        render_list(dotfiles_model, dotfiles_resolver)

        captured = capsys.readouterr()
        output = captured.out

        # Should show top-level resources
        assert "Dotfiles System" in output or "dotfiles" in output
        # Should show some nested resources
        assert "Bootstrap" in output or "XDG" in output or "Shell" in output

    def test_list_with_type_filter(self, dotfiles_model, dotfiles_resolver, capsys):
        """Test filtering by resource type."""
        render_list(
            dotfiles_model,
            dotfiles_resolver,
            resource_type="cli-tool"
        )

        captured = capsys.readouterr()
        output = captured.out

        # Should show CLI tools
        assert "arch" in output.lower() or "spec" in output.lower() or "dot" in output.lower()


class TestValidateCommand:
    """Test arch validate command integration."""

    def test_validate_command_success(self, dotfiles_model):
        """Test validation command with valid model."""
        validator = ArchitectureValidator(dotfiles_model)
        result = validator.validate()

        exit_code = render_validate(dotfiles_model, result)

        # Should succeed (exit code 0)
        assert exit_code == 0
        assert len(result.errors) == 0

    def test_validate_shows_summary(self, dotfiles_model, capsys):
        """Test that validate command shows summary statistics."""
        validator = ArchitectureValidator(dotfiles_model)
        result = validator.validate()

        render_validate(dotfiles_model, result)

        captured = capsys.readouterr()
        output = captured.out

        # Should show summary statistics
        assert "Resources:" in output
        assert "Interfaces:" in output
        assert "Relationships:" in output


class TestDiagramCommand:
    """Test arch diagram command integration."""

    def test_diagram_command_stdout(self, dotfiles_model, dotfiles_resolver, capsys):
        """Test diagram output to stdout."""
        exit_code = render_diagram(
            dotfiles_model,
            dotfiles_resolver,
            format="mermaid",
            zoom="landscape",
            output=None,
            preview=False
        )

        assert exit_code == 0

        captured = capsys.readouterr()
        output = captured.out

        assert "graph TB" in output

    def test_diagram_command_file_output(self, dotfiles_model, dotfiles_resolver):
        """Test diagram output to file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            output_path = Path(f.name)

        try:
            exit_code = render_diagram(
                dotfiles_model,
                dotfiles_resolver,
                format="mermaid",
                zoom="domain",
                output=str(output_path),
                preview=False
            )

            assert exit_code == 0
            assert output_path.exists()

            content = output_path.read_text()
            assert "```mermaid" in content
            assert "graph TB" in content
        finally:
            output_path.unlink(missing_ok=True)

    def test_diagram_all_zoom_levels(self, dotfiles_model, dotfiles_resolver):
        """Test generating diagrams at all zoom levels."""
        for zoom in ["landscape", "domain", "service"]:
            diagram = generate_mermaid(dotfiles_model, dotfiles_resolver, zoom=zoom)
            assert "graph TB" in diagram
            assert len(diagram) > 100  # Should have substantial content


class TestEndToEnd:
    """End-to-end workflow tests."""

    def test_complete_workflow(self, dotfiles_arch_dir):
        """Test complete workflow: load → validate → list → diagram."""
        # 1. Load
        model = load_architecture(dotfiles_arch_dir)
        assert len(model.resources) > 0

        # 2. Validate
        validator = ArchitectureValidator(model)
        result = validator.validate()
        assert len(result.errors) == 0

        # 3. Create resolver
        resolver = PathResolver(model)

        # 4. Generate diagram
        diagram = generate_mermaid(model, resolver, zoom="landscape")
        assert "graph TB" in diagram

        # 5. Test path resolution
        dotfiles = resolver.resolve_resource("dotfiles")
        assert dotfiles is not None
        assert dotfiles.type == "system"

    def test_cli_integration_validate(self, dotfiles_arch_dir):
        """Test CLI arch validate command."""
        result = subprocess.run(
            ["uv", "run", "--script", "local/bin/arch", "validate"],
            cwd=dotfiles_arch_dir.parent.parent,
            capture_output=True,
            text=True
        )

        # Should succeed
        assert result.returncode == 0
        assert "✅" in result.stdout or "valid" in result.stdout.lower()

    def test_cli_integration_list(self, dotfiles_arch_dir):
        """Test CLI arch list command."""
        result = subprocess.run(
            ["uv", "run", "--script", "local/bin/arch", "list"],
            cwd=dotfiles_arch_dir.parent.parent,
            capture_output=True,
            text=True
        )

        # Should succeed and show resources
        assert result.returncode == 0
        assert len(result.stdout) > 0

    def test_cli_integration_diagram(self, dotfiles_arch_dir):
        """Test CLI arch diagram command."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            output_path = Path(f.name)

        try:
            result = subprocess.run(
                [
                    "uv", "run", "--script", "local/bin/arch", "diagram",
                    "--zoom", "landscape",
                    "--output", str(output_path)
                ],
                cwd=dotfiles_arch_dir.parent.parent,
                capture_output=True,
                text=True
            )

            # Should succeed
            assert result.returncode == 0
            assert output_path.exists()

            content = output_path.read_text()
            assert "```mermaid" in content
        finally:
            output_path.unlink(missing_ok=True)
