# Package Handling - Code Analyzer

## Overview

The code-analyzer project uses **modern Python packaging standards** with the `uv` package manager. There is no `setup.py`—all configuration is in `pyproject.toml` following PEP 517/518 specifications.

## Project Metadata (pyproject.toml)

### Basic Configuration

```toml
[project]
name = "code-analyzer"
description = "Unified multi-language static code analysis framework"
requires-python = ">=3.14"
dynamic = ["version"]  # Version read from src/code_analyzer/__init__.py

[project.urls]
homepage = "https://github.com/anthropics/code-analyzer"
repository = "https://github.com/anthropics/code-analyzer"
documentation = "https://example.com/docs"

[project.authors]
{name = "Authors", email = "contact@example.com"}

[project.license]
text = "MIT"
```

### Entry Points (CLI Scripts)

```toml
[project.scripts]
code-analyzer-tui = "code_analyzer.tui.main:main"
```

**Effect**: Creates `code-analyzer-tui` command after installation:

```bash
uv run code-analyzer-tui
# or after 'make sync': code-analyzer-tui
```

## Dependencies

### Production Dependencies (47+ packages)

```toml
[project]
dependencies = [
    # API & HTTP
    "anthropic>=0.75.0",           # Claude API client
    "httpx>=0.28.0",               # HTTP client for Ollama

    # Data Processing
    "lark>=1.1.0",                 # Parser combinator library
    "networkx>=3.6.1",             # Graph algorithms
    "pydantic>=2.10.0",            # Data validation & models
    "sentence-transformers>=5.2.0",# CodeBERT embeddings
    "torch>=2.9.1",                # PyTorch ML framework

    # Database
    "pgvector>=0.4.2",             # PostgreSQL vector type
    "psycopg2-binary>=2.9.11",     # PostgreSQL adapter

    # UI & Output
    "rich>=13.8.0",                # Terminal formatting
    "textual>=0.89.0",             # TUI framework

    # File Processing
    "pypdf>=6.6.0",                # PDF parsing

    # Environment & System
    "dotenv>=0.9.9",               # .env file support
    "setproctitle>=1.3.0",         # Process title setting
]
```

### Optional Dependencies

```toml
[project.optional-dependencies]
docs = [
    "mkdocs>=1.6.0",
    "mkdocs-material>=9.5.0",
    "mkdocs-awesome-pages-plugin>=2.10.0",
    "pymdown-extensions>=10.5",
]

# Development dependencies via dependency groups
[dependency-groups]
dev = [
    "pytest>=9.0.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.12.0",
    "mypy>=1.8.0",
    "ruff>=0.14.0",
    "isort",
    "refurb",
    "vulture",
    "icecream>=2.1.8",
]
```

### Dependency Philosophy

- **Minimal but complete**: Include all necessary packages, no unnecessary bloat
- **Version constraints**: Use `>=X.Y.Z` for flexibility, avoid pinning minor versions
- **Optional deps**: Documentation requires separate install (`pip install code-analyzer[docs]`)
- **Separated dev deps**: Development tools don't inflate production dependencies

## Package Manager: uv

### Why uv?

- **Speed**: 10-100x faster than pip
- **Lockfile support**: Reproducible installs with `uv.lock`
- **Workspace management**: Handles monorepos naturally
- **PEP 508/517 compliant**: Works with any package

### Installation

```bash
# uv is pre-installed or installed via:
brew install uv  # macOS
curl -LsSf https://astral.sh/uv/install.sh | sh  # Linux
```

### Key Commands

```bash
# Create environment and install all dependencies
make env
# Runs: uv sync --all-groups

# Sync dependencies into existing environment
make sync
# Runs: uv sync

# Update lock file (when dependencies change)
make lock
# Runs: uv lock

# Install specific package
uv add package_name

# Install with specific version
uv add "package_name>=1.2.0"

# Remove package
uv remove package_name

# Update all packages to latest
uv lock --upgrade

# Install from local
uv pip install -e .
```

## Dependency Lock File (uv.lock)

### Purpose

The `uv.lock` file (committed to git) ensures **reproducible builds**:

```
Every developer and CI/CD system gets identical package versions
```

### Example Entry

```toml
[[package]]
name = "anthropic"
version = "0.75.1"
source = { type = "registry", url = "https://pypi.org/simple", subdirectory = null }
dependencies = [
    { name = "httpx", version = ">=0.28.0" },
    { name = "pydantic", version = ">=2.0" },
]
```

### Update Workflow

```bash
# After modifying pyproject.toml dependencies
make lock
# Regenerates uv.lock with latest compatible versions

# Check if updates are available
uv pip index refresh

# Pin specific version
uv add "package_name==1.2.3"
```

## Version Management

### Version Source

Version is defined **once** in `src/code_analyzer/__init__.py`:

```python
__version__ = "0.16.0"
```

### Dynamic Version Reading

In `pyproject.toml`:

```toml
[project]
dynamic = ["version"]

[tool.setuptools.dynamic]
version = {attr = "code_analyzer.__version__"}
```

**Benefit**: Single source of truth—no duplication in setup.py

### Version Bumping

For release:

```bash
# 1. Update version in src/code_analyzer/__init__.py
# 2. Run tests to confirm
make test

# 3. Create git tag
git tag v0.16.1

# 4. Push tag (triggers build-package.yml)
git push origin v0.16.1
```

GitHub Actions automatically:
- Builds wheel and tarball
- Creates GitHub Release
- Attaches distributions

## Build System

### PEP 517 Compliance

```toml
[build-system]
requires = ["hatchling"]  # or flit_core
build-backend = "hatchling.build"
```

Allows building without `setup.py`:

```bash
# Build distributions
uv build

# Or manually
python -m build

# Outputs:
# dist/code-analyzer-0.16.0-py3-none-any.whl
# dist/code-analyzer-0.16.0.tar.gz
```

## Tool Configuration (pyproject.toml)

### Ruff Configuration

```toml
[tool.ruff]
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "I", "W"]  # Errors, imports, warnings
ignore = ["E501", "E741"]       # Allow long lines, ambiguous names

[tool.ruff.format]
quote-style = "double"
```

### MyPy Configuration

```toml
[tool.mypy]
strict = true
python_version = "3.14"
disallow_untyped_defs = true
warn_unused_ignores = true
```

### isort Configuration

```toml
[tool.isort]
profile = "black"
line_length = 120
skip_gitignore = true
```

### Pytest Configuration

See `pytest.ini` separately, but can also be in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests/unit", "tests/integration"]
norecursedirs = ["tests/corpus", "tests/spikes"]
```

## Installation Methods

### From Source (Development)

```bash
# Clone repository
git clone https://github.com/anthropics/code-analyzer
cd code-analyzer

# Create environment with all dependencies
make env

# Install in development mode
uv pip install -e .

# Now can run:
code-analyzer-tui
```

### From PyPI (Production)

```bash
# Once published to PyPI
pip install code-analyzer

# With optional docs dependencies
pip install "code-analyzer[docs]"
```

## Dependency Management Best Practices

### 1. **Minimal Versions**

Keep dependency versions loose unless there's a specific requirement:

```toml
# Good: Allows flexibility
"anthropic>=0.75.0"

# Avoid: Too restrictive
"anthropic>=0.75.1,<0.76.0"

# Only when necessary
"torch>=2.9.1"  # Specific version for stability
```

### 2. **Security Updates**

```bash
# Check for security vulnerabilities
uv pip audit

# Update all packages (respecting constraints)
uv lock --upgrade
```

### 3. **Adding New Dependencies**

```bash
# Interactive package selection
uv add package_name

# Specify version
uv add "package_name>=1.2.0"

# Add to optional group
uv add -o docs mkdocs

# Add to dev group
uv add -G dev pytest-plugin
```

### 4. **Removing Unused Dependencies**

```bash
# Check for unused imports and packages
uv run vulture src/

# Remove unused package
uv remove package_name
```

### 5. **Python Version Compatibility**

Current requirement: `requires-python = ">=3.14"`

**To update**:
1. Modify `pyproject.toml`
2. Test with target Python version: `uv run --python 3.13 pytest`
3. Update CI/CD in `.github/workflows/validate.yml`

## Makefile Package Targets

### Environment Setup

```makefile
env:
	uv venv --python 3.14 --seed .venv
	uv sync --all-groups

sync:
	uv sync

lock:
	uv lock
```

### Development Commands Using uv

```makefile
test:
	uv run pytest --cov=src/code_analyzer tests/unit tests/integration

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff check --fix src/ tests/
	uv run ruff format src/ tests/
	uv run isort src/ tests/

type-check:
	uv run mypy src/ --strict

imports:
	uv run isort --check-only src/ tests/
	uv run ruff check --select F401 src/
```

## Continuous Integration (CI/CD)

### validate.yml - Test Workflow

```yaml
name: Unittests Python
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v2  # Install uv
      - uses: actions/setup-python@v4
        with:
          python-version: 3.14
      - run: make sync           # Install dependencies
      - run: make test           # Run tests with coverage
```

### build-package.yml - Release Workflow

```yaml
name: Build and Release Package
on:
  push:
    tags: ['v*.*.*']
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v2
      - uses: actions/setup-python@v4
        with:
          python-version: 3.14
      - run: uv build
      - uses: actions/upload-artifact@v4
        with:
          name: distributions
          path: dist/
```

## Troubleshooting

### Issue: Dependencies conflict

```bash
# Check dependency tree
uv pip compile pyproject.toml

# Force update lock file
uv lock --upgrade-all
```

### Issue: Python version mismatch

```bash
# Install specific Python version
uv python install 3.14

# Run with specific Python version
uv run --python 3.14 pytest
```

### Issue: Virtual environment corruption

```bash
# Remove old environment
rm -rf .venv

# Recreate fresh environment
make env
```

### Issue: Package import errors

```bash
# Verify installation
uv pip show package_name

# Reinstall package
uv add --force package_name

# Sync all dependencies
make sync
```

## Publishing to PyPI

### Prerequisites

1. Create account on PyPI: https://pypi.org
2. Generate API token
3. Store in GitHub Secrets as `PYPI_TOKEN`

### Automatic Release (GitHub Actions)

```bash
# 1. Update version in src/code_analyzer/__init__.py
# 2. Push tag
git tag v0.17.0
git push origin v0.17.0

# GitHub Actions automatically builds and publishes to PyPI
```

### Manual Release

```bash
# Build distributions
uv build

# Install twine
uv add twine

# Upload to PyPI
uv run twine upload dist/*
```

## Environment Variables

### Development (.env)

```bash
# PostgreSQL
DATABASE_URL="postgresql://user:pass@localhost:5432/codeanalyzer"

# API Keys
ANTHROPIC_API_KEY="sk-..."
OLLAMA_API_URL="http://localhost:11434"

# Debug
DEBUG=true
LOG_LEVEL="DEBUG"
```

Load via `dotenv` package:

```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
```

## Summary

| Aspect | Implementation |
|--------|-----------------|
| **Package Manager** | uv (modern, fast) |
| **Config File** | pyproject.toml (PEP 517) |
| **Version Source** | src/code_analyzer/__init__.py |
| **Lock File** | uv.lock (reproducibility) |
| **Python Version** | >=3.14 |
| **Dependencies** | 47+ production packages |
| **Build System** | hatchling (PEP 517) |
| **CLI Entry Point** | code-analyzer-tui |
| **CI/CD Tool** | GitHub Actions |
