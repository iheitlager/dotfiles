# Package Handling - Python Projects

## Overview

Modern Python projects use **pyproject.toml** with the `uv` package manager. No `setup.py` needed—all configuration follows PEP 517/518/621 specifications.

## Project Metadata (pyproject.toml)

### Basic Configuration

```toml
[project]
name = "my-project"
description = "Project description"
requires-python = ">=3.12"
dynamic = ["version"]  # Version read from src/my_project/__init__.py

[project.urls]
homepage = "https://github.com/org/my-project"
repository = "https://github.com/org/my-project"

[project.license]
text = "MIT"
```

### Entry Points (CLI Scripts)

```toml
[project.scripts]
my-cli = "my_project.cli:main"
```

**Effect**: Creates `my-cli` command after installation.

## Dependencies

### Production Dependencies

```toml
[project]
dependencies = [
    "httpx>=0.28.0",
    "pydantic>=2.10.0",
    "rich>=13.8.0",
]
```

### Optional Dependencies

```toml
[project.optional-dependencies]
docs = [
    "mkdocs>=1.6.0",
    "mkdocs-material>=9.5.0",
]
```

### Development Dependencies (Dependency Groups)

```toml
[dependency-groups]
dev = [
    "pytest>=9.0.0",
    "pytest-cov>=4.1.0",
    "mypy>=1.8.0",
    "ruff>=0.14.0",
]
```

### Dependency Philosophy

- **Minimal but complete**: Include necessary packages, avoid bloat
- **Version constraints**: Use `>=X.Y.Z` for flexibility
- **Optional deps**: Documentation requires separate install (`pip install project[docs]`)
- **Separated dev deps**: Development tools don't inflate production dependencies

## Package Manager: uv

### Why uv?

- **Speed**: 10-100x faster than pip
- **Lockfile support**: Reproducible installs with `uv.lock`
- **Workspace management**: Handles monorepos naturally
- **PEP compliant**: Works with any package

### Installation

```bash
brew install uv        # macOS
curl -LsSf https://astral.sh/uv/install.sh | sh  # Linux
```

### Key Commands

```bash
# Create environment and install all dependencies
uv sync --all-groups

# Update lock file (when dependencies change)
uv lock

# Add package
uv add package_name
uv add "package_name>=1.2.0"

# Add to dev group
uv add -G dev pytest-plugin

# Remove package
uv remove package_name

# Update all packages to latest
uv lock --upgrade

# Run command in environment
uv run pytest
uv run python script.py
```

## Dependency Lock File (uv.lock)

The `uv.lock` file (committed to git) ensures **reproducible builds**:

```
Every developer and CI/CD system gets identical package versions
```

### Update Workflow

```bash
# After modifying pyproject.toml dependencies
uv lock

# Check for outdated packages
uv pip list --outdated

# Update specific package
uv add "package_name>=2.0.0"
```

## Version Management

### Version Source

Version defined **once** in `src/my_project/__init__.py`:

```python
__version__ = "1.0.0"
```

### Dynamic Version Reading

```toml
[project]
dynamic = ["version"]

[tool.setuptools.dynamic]
version = {attr = "my_project.__version__"}
```

### Version Bumping

```bash
# 1. Update version in src/my_project/__init__.py
# 2. Run tests
uv run pytest

# 3. Create git tag
git tag v1.0.1
git push origin v1.0.1
```

## Build System

### PEP 517 Compliance

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

Build without `setup.py`:

```bash
uv build
# Outputs:
# dist/my_project-1.0.0-py3-none-any.whl
# dist/my_project-1.0.0.tar.gz
```

## Tool Configuration (pyproject.toml)

### Ruff (Linting & Formatting)

```toml
[tool.ruff]
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "I", "W"]
ignore = ["E501"]

[tool.ruff.format]
quote-style = "double"
```

### MyPy (Type Checking)

```toml
[tool.mypy]
strict = true
python_version = "3.12"
disallow_untyped_defs = true
```

### Pytest

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=src --cov-report=term-missing"
```

## Makefile Targets

```makefile
.PHONY: env sync lock test lint format type-check

env:
uv venv --python 3.12 --seed .venv
uv sync --all-groups

sync:
uv sync

lock:
uv lock

test:
uv run pytest

lint:
uv run ruff check src/ tests/

format:
uv run ruff check --fix src/ tests/
uv run ruff format src/ tests/

type-check:
uv run mypy src/
```

## GitHub Actions CI/CD

### Test Workflow

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv sync --all-groups
      - run: uv run pytest
```

### Release Workflow

```yaml
name: Release
on:
  push:
    tags: ['v*.*.*']

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv build
      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
```

## Troubleshooting

### Dependencies conflict

```bash
uv lock --upgrade-all
```

### Python version mismatch

```bash
uv python install 3.12
uv run --python 3.12 pytest
```

### Virtual environment corruption

```bash
rm -rf .venv
uv sync --all-groups
```

### Package import errors

```bash
uv pip show package_name
uv add --force package_name
```

## Best Practices

### Version Constraints

```toml
# Good: Allows flexibility
"httpx>=0.28.0"

# Avoid: Too restrictive
"httpx>=0.28.0,<0.29.0"

# Compatible release (allows patch updates)
"httpx~=0.28.0"  # Same as >=0.28.0,<0.29.0
```

### Security Updates

```bash
# Check for vulnerabilities
uv pip audit

# Update all packages
uv lock --upgrade
```

### Adding/Removing Dependencies

```bash
# Add production dependency
uv add requests

# Add dev dependency
uv add -G dev pytest-mock

# Add optional dependency
uv add -o docs mkdocs

# Remove unused
uv remove package_name
```

## Summary

| Aspect | Implementation |
|--------|----------------|
| **Package Manager** | uv |
| **Config File** | pyproject.toml |
| **Version Source** | `src/pkg/__init__.py` |
| **Lock File** | uv.lock |
| **Build System** | hatchling/flit/setuptools |
| **Linting** | ruff |
| **Type Checking** | mypy |
| **Testing** | pytest |
