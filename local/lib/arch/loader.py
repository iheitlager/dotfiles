"""
YAML loading and schema validation for architecture models.

This module handles:
- Loading single YAML files
- Loading directories of YAML fragments (merging)
- Validating against JSON schemas
- Parsing into dataclass models
- Error handling with file/line context
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from jsonschema import validate as schema_validate, ValidationError

from .model import ArchitectureModel, Resource, Relationship, Sequence, StateMachine


class LoadError(Exception):
    """Error loading or parsing architecture model."""

    def __init__(self, message: str, file_path: Optional[str] = None, line: Optional[int] = None):
        self.message = message
        self.file_path = file_path
        self.line = line
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format error message with file/line context."""
        parts = []
        if self.file_path:
            parts.append(f"File: {self.file_path}")
        if self.line:
            parts.append(f"Line: {self.line}")
        parts.append(self.message)
        return " | ".join(parts)


def _load_schema(schema_name: str) -> Dict[str, Any]:
    """Load JSON schema from local/share/arch/schemas/."""
    # Find schema directory (relative to this file)
    lib_dir = Path(__file__).parent
    schema_dir = lib_dir.parent.parent / "share" / "arch" / "schemas"
    schema_path = schema_dir / f"{schema_name}.schema.json"

    if not schema_path.exists():
        raise LoadError(f"Schema not found: {schema_path}")

    with open(schema_path, 'r') as f:
        return json.load(f)


def _load_all_schemas() -> Dict[str, Any]:
    """Load all JSON schemas and create resolver."""
    schemas = {}
    for name in ["interface", "resource", "relationship", "sequence", "state-machine"]:
        schemas[name] = _load_schema(name)
    return schemas


def load_yaml_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load and parse a single YAML file.

    Args:
        file_path: Path to YAML file

    Returns:
        Parsed YAML data as dictionary

    Raises:
        LoadError: If file cannot be loaded or parsed
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise LoadError(f"File not found: {file_path}")

    try:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)

        # Handle empty files
        if data is None:
            return {}

        if not isinstance(data, dict):
            raise LoadError(
                f"YAML must be a dictionary, got {type(data).__name__}",
                file_path=str(file_path)
            )

        return data

    except yaml.YAMLError as e:
        # Extract line number if available
        line = None
        if hasattr(e, 'problem_mark'):
            line = e.problem_mark.line + 1

        raise LoadError(
            f"YAML parsing error: {e}",
            file_path=str(file_path),
            line=line
        )
    except Exception as e:
        raise LoadError(
            f"Error loading file: {e}",
            file_path=str(file_path)
        )


def _validate_against_schema(data: Dict[str, Any], schema_name: str, file_path: Optional[str] = None):
    """
    Validate data against JSON schema.

    Args:
        data: Data to validate
        schema_name: Name of schema (resource, relationship, etc.)
        file_path: Optional file path for error reporting

    Raises:
        LoadError: If validation fails
    """
    try:
        schema = _load_schema(schema_name)
        schema_validate(instance=data, schema=schema)
    except ValidationError as e:
        # Build helpful error message
        path = " -> ".join(str(p) for p in e.path) if e.path else "root"
        raise LoadError(
            f"Schema validation failed at '{path}': {e.message}",
            file_path=file_path
        )


def _merge_models(models: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merge multiple model dictionaries into one.

    Args:
        models: List of model dictionaries to merge

    Returns:
        Merged model dictionary

    Raises:
        LoadError: If duplicate resource IDs or sequence IDs are found
    """
    merged = {
        "resources": [],
        "relationships": [],
        "sequences": [],
        "state_machines": [],
    }

    # Track IDs to detect duplicates
    seen_resource_ids = set()
    seen_sequence_ids = set()
    seen_state_machine_ids = set()

    for model in models:
        # Merge resources
        for resource in model.get("resources", []):
            resource_id = resource.get("id")
            if resource_id in seen_resource_ids:
                raise LoadError(f"Duplicate resource ID: {resource_id}")
            seen_resource_ids.add(resource_id)
            merged["resources"].append(resource)

        # Merge relationships
        for relationship in model.get("relationships", []):
            merged["relationships"].append(relationship)

        # Merge sequences
        for sequence in model.get("sequences", []):
            sequence_id = sequence.get("id")
            if sequence_id in seen_sequence_ids:
                raise LoadError(f"Duplicate sequence ID: {sequence_id}")
            seen_sequence_ids.add(sequence_id)
            merged["sequences"].append(sequence)

        # Merge state machines
        for state_machine in model.get("state_machines", []):
            sm_id = state_machine.get("id")
            if sm_id in seen_state_machine_ids:
                raise LoadError(f"Duplicate state machine ID: {sm_id}")
            seen_state_machine_ids.add(sm_id)
            merged["state_machines"].append(state_machine)

    return merged


def _find_yaml_files(directory: Path) -> List[Path]:
    """
    Find all YAML files in directory (recursively).

    Args:
        directory: Directory to search

    Returns:
        List of YAML file paths
    """
    patterns = ["**/*.yaml", "**/*.yml"]
    files = []
    for pattern in patterns:
        files.extend(directory.glob(pattern))

    # Sort for deterministic ordering
    return sorted(set(files))


def load_architecture(path: Union[str, Path], validate_schema: bool = True) -> ArchitectureModel:
    """
    Load architecture model from file or directory.

    For single file: Loads and validates that file
    For directory: Finds all YAML files and merges them

    Args:
        path: Path to YAML file or directory
        validate_schema: Whether to validate against JSON schemas (default: True)

    Returns:
        Loaded and parsed ArchitectureModel

    Raises:
        LoadError: If loading or validation fails

    Example:
        >>> model = load_architecture(".openspec/architecture/")
        >>> print(f"Loaded {len(model.resources)} resources")
    """
    path = Path(path)

    if not path.exists():
        raise LoadError(f"Path not found: {path}")

    # Determine if single file or directory
    if path.is_file():
        # Load single file
        data = load_yaml_file(path)
        source_files = [str(path)]

        # Validate resources if present
        if validate_schema:
            for resource in data.get("resources", []):
                _validate_against_schema(resource, "resource", str(path))
            for relationship in data.get("relationships", []):
                _validate_against_schema(relationship, "relationship", str(path))
            for sequence in data.get("sequences", []):
                _validate_against_schema(sequence, "sequence", str(path))
            for state_machine in data.get("state_machines", []):
                _validate_against_schema(state_machine, "state-machine", str(path))

    elif path.is_dir():
        # Find all YAML files
        yaml_files = _find_yaml_files(path)

        if not yaml_files:
            raise LoadError(f"No YAML files found in directory: {path}")

        # Load and validate each file
        models = []
        source_files = []

        for file_path in yaml_files:
            file_data = load_yaml_file(file_path)

            # Validate if requested
            if validate_schema:
                for resource in file_data.get("resources", []):
                    _validate_against_schema(resource, "resource", str(file_path))
                for relationship in file_data.get("relationships", []):
                    _validate_against_schema(relationship, "relationship", str(file_path))
                for sequence in file_data.get("sequences", []):
                    _validate_against_schema(sequence, "sequence", str(file_path))
                for state_machine in file_data.get("state_machines", []):
                    _validate_against_schema(state_machine, "state-machine", str(file_path))

            models.append(file_data)
            source_files.append(str(file_path))

        # Merge all models
        data = _merge_models(models)

    else:
        raise LoadError(f"Path is neither file nor directory: {path}")

    # Parse into dataclass model
    try:
        model = ArchitectureModel.from_dict(data)
        model._source_files = source_files
        return model

    except Exception as e:
        raise LoadError(f"Error parsing model: {e}")


def save_architecture(model: ArchitectureModel, path: Union[str, Path]) -> None:
    """
    Save architecture model to YAML file.

    Args:
        model: Architecture model to save
        path: Output file path

    Raises:
        LoadError: If saving fails
    """
    path = Path(path)

    try:
        # Convert to dictionary
        data = model.to_dict()

        # Write YAML
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    except Exception as e:
        raise LoadError(f"Error saving model: {e}", file_path=str(path))
