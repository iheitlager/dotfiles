"""Tests for reverse engineering functionality."""

import pytest
from pathlib import Path

from local.lib.arch.reverse_engineer import ReverseEngineer
from local.lib.arch.extractors.bash import BashExtractor
from local.lib.arch.extractors.docker import DockerExtractor


class TestBashExtractor:
    """Tests for BashExtractor."""

    def test_can_extract_sh_extension(self, tmp_path):
        """Test detection of .sh files."""
        extractor = BashExtractor()
        test_file = tmp_path / "test.sh"
        test_file.write_text("#!/bin/bash\necho hello")

        assert extractor.can_extract(test_file)

    def test_can_extract_bash_shebang(self, tmp_path):
        """Test detection via shebang."""
        extractor = BashExtractor()
        test_file = tmp_path / "test"
        test_file.write_text("#!/usr/bin/env bash\necho hello")

        assert extractor.can_extract(test_file)

    def test_cannot_extract_non_bash(self, tmp_path):
        """Test rejection of non-bash files."""
        extractor = BashExtractor()
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        assert not extractor.can_extract(test_file)

    def test_extract_functions(self):
        """Test function extraction from bash script."""
        extractor = BashExtractor()
        fixture_path = Path("tests/arch/fixtures/bash/simple_script.sh")

        resources = extractor.extract(fixture_path)

        assert len(resources) == 1
        resource = resources[0]

        assert resource.id == "simple-script"
        assert resource.type == "bash-script"
        assert len(resource.interfaces) == 3  # setup, cleanup, main
        assert len(resource.implementation) == 3

        # Check interface names
        interface_ids = {i.id for i in resource.interfaces}
        assert "setup" in interface_ids
        assert "cleanup" in interface_ids
        assert "main" in interface_ids


class TestDockerExtractor:
    """Tests for DockerExtractor."""

    def test_can_extract_docker_compose(self, tmp_path):
        """Test detection of docker-compose files."""
        extractor = DockerExtractor()
        test_file = tmp_path / "docker-compose.yml"
        test_file.write_text("version: '3'")

        assert extractor.can_extract(test_file)

    def test_extract_services(self):
        """Test service extraction from docker-compose."""
        extractor = DockerExtractor()
        fixture_path = Path("tests/arch/fixtures/docker/docker-compose.yml")

        resources = extractor.extract(fixture_path)

        assert len(resources) == 2  # web, db

        # Check web service
        web = next(r for r in resources if r.id == "web")
        assert web.type == "docker-service"
        assert web.technology == "nginx"
        assert len(web.interfaces) == 1
        assert web.interfaces[0].id == "port-80"

        # Check db service
        db = next(r for r in resources if r.id == "db")
        assert db.type == "docker-service"
        assert db.technology == "PostgreSQL"
        assert len(db.interfaces) == 1
        assert db.interfaces[0].id == "port-5432"


class TestReverseEngineer:
    """Tests for ReverseEngineer orchestrator."""

    def test_extract_from_directory(self):
        """Test extracting from a directory."""
        reverser = ReverseEngineer()
        fixture_dir = Path("tests/arch/fixtures/bash")

        model = reverser.extract_from_directory(fixture_dir, recursive=False)

        assert len(model.resources) >= 1
        assert any(r.id == "simple-script" for r in model.resources)

    def test_extract_from_file(self):
        """Test extracting from a single file."""
        reverser = ReverseEngineer()
        fixture_path = Path("tests/arch/fixtures/bash/simple_script.sh")

        resources = reverser.extract_from_file(fixture_path)

        assert len(resources) == 1
        assert resources[0].id == "simple-script"

    def test_deduplication(self):
        """Test resource deduplication."""
        reverser = ReverseEngineer()

        # Create duplicate resources
        from local.lib.arch.model import Resource
        r1 = Resource(id="test", name="Test", type="bash-script")
        r2 = Resource(id="test", name="Test 2", type="bash-script")
        r3 = Resource(id="other", name="Other", type="bash-script")

        unique = reverser._deduplicate_resources([r1, r2, r3])

        assert len(unique) == 2
        assert unique[0].id == "test"
        assert unique[0].name == "Test"  # First wins
        assert unique[1].id == "other"
