# Claude Code Instructions for code-analyzer

This document provides guidance for Claude Code when working on the code-analyzer project.

## Project Overview

**code-analyzer** is an LLM-powered code analysis research tool that extracts and analyzes code structure, relationships, and semantics across multiple programming languages and file formats.

---

## Key Project Files & Structure

### 📋 Dependencies & Configuration

#### `pyproject.toml`
- **Python version**: ≥3.14
- **Core dependencies**:
  - `networkx>=3.6.1` — Graph data structure for code representation
- **Optional dependencies**:
  - `docs` group: mkdocs, mkdocs-material for documentation
- **Development dependencies** (in `[dependency-groups] dev`):
  - Testing: pytest, pytest-cov, pytest-mock
  - Linting & formatting: ruff, mypy, isort, refurb, vulture
  - Debugging: icecream

#### `Makefile`
- **Key targets**:
  - `make env` — Create and populate development virtual environment with Python 3.14
  - `make sync` — Sync dependencies using `uv`
  - `make lock` — Lock dependencies into uv.lock
  - `make test` — Run all tests
  - `make lint` — Run code quality checks (ruff, mypy)
  - `make format` — Auto-format code
  - `make type-check` — Run static type checking
  - `make check` — Verify required tooling is available

> **Tool**: This project uses `uv` for dependency management (https://github.com/astral-sh/uv). Commands are run via `uv run <cmd>`.

---

## Folder Structure

### 📁 `src/code_analyzer/`
Main source code for the code-analyzer package.

**Key modules**:
- `core/` — Core data models and enums
  - `models.py` — Entity, Relationship, and Metadata models
  - `enum.py` — EntityType, EdgeType, SourceType enums
  - `exceptions.py` — Custom exceptions
- `cli/` — Command-line interface
- `actions/` — Core analysis actions and operations
- `parsers/` — Language/format-specific parsers
- `db/` — Database layer (PostgreSQL)

### 🧪 `tests/`
Test suite for the project.

**Structure**:
- `unit/` — Unit tests for individual components
- `spikes/` — Experimental/exploratory test code
  - `001_core_model/` — Core model spike experiments

- Always create a new test case when new bugs are found.

**Running tests**:
```bash
make test          # Run all tests
uv run pytest      # Run with pytest directly
uv run pytest -v   # Verbose output
uv run pytest --cov  # With coverage report
```

### 📚 `docs/`
Project documentation and architectural decisions.

**Key subdirectories**:
- `adr/` — **Architectural Decision Records (ADRs)** — Critical for understanding design decisions
- `plans/` — Feature implementation plans
- `features/` — Feature documentation
- `templates/` — Documentation templates

**Key files**:
- `vision.md` — Project vision and goals
- `philosophy.md` — Design principles and philosophy
- `approach.md` — Technical approach
- `high_level_design.md` — Architecture overview
- `language_parsers.md` — Supported languages and parsing details
- `query_tools.md` — How to query the code graph
- `cypher_query.md` — Cypher-like query language
- `actions.md` — Analysis actions documentation

**Documentation site** (MkDocs):
```bash
.venv/bin/mkdocs serve     # Local dev server with hot reload
.venv/bin/mkdocs build     # Build static site to site/
.venv/bin/mkdocs gh-deploy # Deploy to GitHub Pages
```

### ✅ Important: Architectural Decision Records (ADRs)

The `docs/adr/` folder contains **Architectural Decision Records** that document major design decisions:

| ADR | Title | Focus |
|:----|:------|:------|
| [ADR-0001](docs/adr/0001-four_layer_architecture.md) | Four-Layer Architecture | Parser Output → Metadata → Graph → Storage pipeline for multi-source code analysis |
| [ADR-0002](docs/adr/0002-granularity_analysis.md) | Granularity Levels | Multi-level granularity model (function-level primary, statement-level on-demand) |
| [ADR-0003](docs/adr/0003-sql_persistence.md) | PostgreSQL Persistence | pgvector integration for embedding storage and JSONB for flexible metadata |
| [ADR-0004](docs/adr/0004-parsing_architecture.md) | Multi-Language Parsing | SourceParser framework with language-specific adapters for unified code extraction |
| [ADR-0005](docs/adr/0005-analysis_pipeline.md) | Code Analysis Pipeline | AST, symbol tables, relationship extraction with clear dependency ordering |
| [ADR-0006](docs/adr/0006-semantic_embeddings.md) | Semantic Embeddings | Embedding models, granularity levels, and pgvector persistence for similarity search |
| [ADR-0007](docs/adr/0007-symboltable_structure.md) | Symbol Table Structure | Symbol table design for scope tracking and name resolution |
| [ADR-0008](docs/adr/0008-fqn_format.md) | FQN Format | Fully Qualified Name format for unique entity identification across languages |
| [ADR-0009](docs/adr/0009-lazy_fluent_pipeline.md) | Lazy Fluent Pipeline | Fluent API with lazy evaluation for efficient code analysis workflows |
| [ADR-0010](docs/adr/0010-external_import_categorization.md) | External Import Categorization | Classification of external imports (stdlib, popular, other) for dependency analysis |
| [ADR-0011](docs/adr/0011-pydantic_layer_projections.md) | Pydantic Layer Projections | Pydantic models for layer transformations and validation |
| [ADR-0012](docs/adr/0012-deterministic_analysis.md) | Deterministic Analysis | Deterministic code analysis without LLM dependencies |
| [ADR-0013](docs/adr/0013-probabilistic_llm_enrichment.md) | Probabilistic LLM Enrichment | LLM-based semantic enrichment for code understanding |
| [ADR-0014](docs/adr/0014-agentic_querying.md) | Agentic Querying | Agent-based code querying and exploration |
| [ADR-0015](docs/adr/0015-agentic_response_loop.md) | Agentic Response Loop | Iterative agent response loop for complex queries |
| [ADR-0016](docs/adr/0016-llm_memory_slots.md) | LLM Memory Slots | Memory management for LLM context and state |
| [ADR-0017](docs/adr/0017-graph_query_language.md) | Graph Query Language | Cypher-like query language for code graph traversal |

**Always reference relevant ADRs** when:
- Working with data models (core/models.py)
- Adding new parsers
- Implementing storage/database logic
- Making architectural changes

**Note on Fluent Interfaces**: When discussing or implementing "fluent" design patterns in code, always refer to [ADR-0009](docs/adr/0009-lazy_fluent_pipeline.md) for context on lazy evaluation and the fluent pattern used in this project.

---

## Development Workflow

### Setting Up

```bash
# Create virtual environment and install dependencies
make env

# Activate the environment
source .venv/bin/activate

# Verify setup
make check
```

### Common Tasks

```bash
# Run tests with coverage
make test

# Lint and format code
make lint
make format

# Type checking
make type-check

# Full quality check
make check
```

### Key Coding Patterns

1. **Four-Layer Architecture** (ADR-0001):
   - Layer 1: `ParsedEntity`/`ParsedRelationship` — Language-specific parser output
   - Layer 2: `NodeMetadata`/`EdgeMetadata` — Language-agnostic curated representation
   - Layer 3: NetworkX CodeGraph — In-memory graph queries (FQN objects as keys)
   - Layer 4: PostgreSQL with pgvector — Persistent storage

2. **FQN Objects as Graph Keys** (ADR-0008):
   - NetworkX graph uses **FQN objects** as node/edge keys (not strings)
   - Ensures type safety and consistent hashable keys
   - Example: `graph.graph.nodes[FQN("path/file.py")]` ✅ not `graph.graph.nodes["path/file.py"]` ❌

3. **Granularity Model** (ADR-0002):
   - Primary: Function/method level nodes
   - Secondary: Statement-level CFG (on-demand)
   - Tertiary: Expression level (future research)

4. **Multi-Language Support** (ADR-0004, ADR-0010):
   - Language-agnostic `ReferenceResolver` with pluggable `LanguageResolver` instances
   - External import categorization: STDLIB, POPULAR, OTHER, INTERNAL
   - Strategy pattern enables adding new languages without modifying core logic

---

## Code Quality Standards

- **Linter**: `ruff` — Fast Python linter
- **Type Checking**: `mypy` — Static type analysis
- **Imports**: `isort` — Import sorting and organization
- **Testing**: pytest with coverage targets
- **Python Version**: 3.14+ (use type hints, modern syntax)

---

## Claude Code Workflow Preferences

### Planning and Consciousness
- Plan complex tasks and explore the codebase thoughtfully
- Read files before modifying them
- Use TodoWrite to track progress on multi-step work
- Think through architectural decisions carefully

### Bash and Git Usage
- **Use Bash commands freely** for tests, builds, dependency installation, git status checks, etc.
- **Use Git operations freely** (commits, pushing, creating branches, rebasing) as natural parts of the workflow
- No need to ask permission for Bash or git actions
- Still be cautious with destructive git operations (no force pushes or hard resets unless explicitly requested)

### Feature Development Workflow

#### Starting a New Feature
1. **Create a branch** following [branch naming conventions](#branch-naming-conventions)
2. **Create a plan** in `docs/planning/` with:
   - Feature description
   - Implementation approach
   - Files to be modified
   - Estimated complexity

#### Finalizing a Feature
1. **Ensure tests are running** — all tests pass locally
2. **Ask about ADR records** — determine if architectural decisions need documentation
3. **Consider updating existing documentation** — review ADRs, philosophy, approach docs for relevance
4. **Commit changes** — create meaningful, semantic commits
5. **Squash commits** — clean up commit history before PR
6. **File a pull request** — include summary and test plan

### Summary
Be conscious and plan carefully, but move efficiently with Bash and git tools without hesitation.

---

## Tool Usage Guidelines

### Always Use `uv` for Commands

**This project uses `uv` exclusively for dependency and command management**. Always run commands through `uv`:

```bash
# ✅ DO THIS
uv run pytest tests/
uv run python script.py
uv run ruff check src/
uv run mypy src/

# ❌ DO NOT DO THIS
pytest tests/
python script.py
ruff check src/
mypy src/
```

Why? `uv` ensures:
- Correct virtual environment activation
- Dependency isolation
- Consistent tooling across all environments
- Proper Python 3.14+ usage

See `Makefile` for convenient shortcuts: `make test`, `make lint`, `make format`, etc.

### Markdown Generation Policy

**STRICT: Never generate markdown documentation files unless explicitly requested by the user**.

**What NOT to do:**
- ❌ Do NOT create `.md` summary/overview documents
- ❌ Do NOT create `.md` files to explain or document code changes
- ❌ Do NOT create `.md` files for architecture overviews or implementation summaries
- ❌ Do NOT add comments in markdown format to code files

**What TO do:**
- ✅ Use inline code comments for complex logic
- ✅ Reference existing ADRs and documentation
- ✅ Generate markdown ONLY when user EXPLICITLY asks: "Create a README", "Document this", "Write an ADR", etc.
- ✅ Update existing markdown files when specifically requested

**This means:**
- No "summary" documents
- No "overview" documents
- No "implementation guide" documents
- No auto-generated documentation files

If you create even one markdown file the user didn't ask for, you have failed.

---

## Git Workflow & Branching Strategy

### Branch Naming Conventions

All branches must follow these conventions:

| Branch Type | Format | Purpose | Version Impact |
|-------------|--------|---------|-----------------|
| Feature | `feat/xxxxx` | New functionality | Minor update |
| Bug Fix | `fix/xxxxx` | Code fixes | Patch update |
| Refactor | `refactor/xxxxx` | Code refactoring | No update |
| Spike | `spike/DDD_xxxxx` | Experimental exploration | No update |
| Documentation | `docs/xxxxx` | Documentation updates | No update |
| Chore | `chore/xxxxx` | Maintenance, tooling | No update |

**Examples**:
- `feat/python-parser` — New Python parser implementation
- `fix/symbol-table-closure` — Fix closure detection in symbol tables
- `refactor/three-layer-models` — Refactor model hierarchy
- `spike/001_core_model_validation` — Spike to validate core models
- `docs/adr-0007` — Document new architectural decision
- `chore/update-dependencies` — Dependency updates

Be sure to update `CHANGELOG.md` and version numbers as appropriate when merging feature or fix branches.

### Version Bumping

When releasing a new version, update these **three locations**:

1. **`src/code_analyzer/__init__.py`**
   ```python
   __version__ = "0.1.0"  # Update here
   ```

2. **`README.md`**
   ```markdown
   ## Version: 0.1.0  # Update here
   ```

3. **`CHANGELOG.md`**
   ```markdown
   # Changelog

   ## [0.1.0] - 2026-01-05  # Update here
   - Feature A
   - Feature B
   ```

**Versioning Scheme**: Semantic Versioning (MAJOR.MINOR.PATCH)
- **Minor**: New features (`feat/` branches)
- **Patch**: Bug fixes (`fix/` branches)
- **No change**: Refactors, spikes, docs, chores

---

## Useful Resources

- **Project README**: [README.md](README.md)
- **Change Log**: [CHANGELOG.md](CHANGELOG.md)
- **ADR Index**: [docs/adr/index.md](docs/adr/index.md)
- **Vision**: [docs/vision.md](docs/vision.md)

---

## Notes for Contributors

- **Always check ADRs** before proposing architectural changes
- **Respect the four-layer architecture** when adding parsers or storage logic
- **Add tests** for all new features (aim for coverage > 80%)
- **Update ADRs** if making decisions that affect architecture
- **Use type hints** consistently across the codebase
- **Document complex logic** with comments referencing relevant ADRs

---

*Last updated: 2026-01-14*
