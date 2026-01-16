# Project Structure - Code Analyzer

## Overview

**code-analyzer** is a unified multi-language static code analysis framework (v0.16.0) following professional Python package standards. This is NOT a cookiecutter template—it's a production research project with a structured, extensible architecture.

## Directory Layout

```
code-analyzer/
├── src/code_analyzer/              # Main package (36,863 LOC)
│   ├── core/                       # Data models & core abstractions
│   │   ├── code_graph.py           # NetworkX graph representation
│   │   ├── enums.py                # Language, FQN format enums
│   │   ├── models.py               # Symbol, import, metadata models
│   │   └── fully_qualified_name.py # FQN parsing & formatting
│   ├── parsers/                    # Multi-language parsing adapters
│   │   ├── base.py                 # SourceParser abstract base
│   │   ├── python.py, go.py, etc   # Language-specific parsers
│   │   └── file_handlers/          # Custom AST walkers per language
│   ├── actions/                    # Analysis operations (Phase 3+)
│   ├── tools/                      # Analysis tools & query interfaces
│   │   ├── graph_tools.py          # Graph algorithms (paths, neighbors)
│   │   ├── graph_query/            # Cypher-like DSL query engine
│   │   ├── metrics.py              # Complexity/cyclomatic metrics
│   │   └── extractors.py           # Data extraction utilities
│   ├── agent/                      # Agentic querying system
│   ├── db/                         # Database persistence layer
│   │   └── database_manager.py     # PostgreSQL + pgvector integration
│   ├── tui/                        # Terminal UI components
│   │   └── main.py                 # TUI entry point
│   └── __init__.py                 # Version: 0.16.0 (read from here)
│
├── tests/                          # Comprehensive test suite (77,437 LOC)
│   ├── unit/                       # Unit tests (97 test files)
│   │   ├── core/                   # Tests for models, graphs, FQN
│   │   ├── parsers/                # Parser implementation tests
│   │   ├── tools/                  # Graph tools, metrics tests
│   │   ├── actions/, agent/, db/, tui/
│   │   └── conftest.py             # Shared fixtures, global mocks
│   ├── integration/                # Database persistence tests
│   │   └── conftest.py             # DB connection auto-setup
│   ├── spikes/                     # 14 research phases (098 files)
│   │   ├── 001_core_model/         # Core model validation
│   │   ├── 002_python_parser/      # Parser implementation
│   │   ├── 003_networkx_graph/     # Graph algorithms
│   │   ├── ... (004-014) ...       # Various research phases
│   │   └── conftest.py             # Spike-wide fixtures
│   └── corpus/                     # Reference code samples (NOT executed)
│
├── docs/                           # MkDocs + Markdown documentation
│   ├── adr/                        # 17 Architectural Decision Records
│   │   ├── index.md                # ADR index with validation status
│   │   ├── 0001-0017.md            # Individual ADRs
│   │   └── templates/              # ADR & plan templates
│   ├── vision.md, philosophy.md    # Design documentation
│   ├── high_level_design.md        # Architecture & diagrams
│   ├── language_parsers.md         # Parser capabilities
│   ├── ROADMAP.md                  # Phase-based timeline
│   └── plans/                      # Implementation plans
│
├── etc/                            # Configuration & deployment
│   ├── docker-compose.yml          # PostgreSQL + pgvector
│   └── init-db.sql                 # Database schema initialization
│
├── .github/workflows/              # CI/CD automation
│   ├── validate.yml                # Unit tests (PR/push)
│   └── build-package.yml           # Package building & release
│
├── .claude/                        # Claude Code configuration
│   ├── settings.json               # IDE integration settings
│   ├── SKILLS_*.md                 # Knowledge base files
│   └── README.md                   # Claude Code instructions
│
├── pyproject.toml                  # Project metadata & dependencies
├── pytest.ini                      # Test configuration
├── Makefile                        # Development commands
├── uv.lock                         # Locked dependency versions
└── README.md, CHANGELOG.md         # Version history
```

## Key Structural Principles

### 1. **Modern Python Package Layout**

- **src/ directory layout**: Source code isolated from tests and build artifacts
- **No setup.py**: Uses `pyproject.toml` exclusively (PEP 517/518 compliant)
- **Dynamic versioning**: Version read from `src/code_analyzer/__init__.py`
- **Entry points**: CLI scripts defined in `pyproject.toml`

### 2. **Extensible Architecture**

The design follows a **4-layer pattern**:

```
Language Source Files (Python, Go, Java, etc.)
    ↓
Parsers (SourceParser implementations)
    ↓
Core Models (Symbol, Import, Metadata)
    ↓
Storage Layer (NetworkX Graph, PostgreSQL)
    ↓
Query/Analysis Tools (Graph algorithms, metrics)
```

**Core Classes**:
- `SourceParser`: Abstract base for language-specific parsers
- `CodeGraph`: NetworkX graph representation of codebase
- `Symbol`: Represents code definitions (functions, classes, variables)
- `Import`: Tracks dependencies and external packages
- `FullyQualifiedName`: Standardized naming convention

### 3. **Supported Languages (Framework-Ready)**

| Language | Status | Implementation |
|----------|--------|-----------------|
| Python | ✅ Full | AST-based parser with full introspection |
| Go | ✅ Full | ast package parsing |
| Java | ✅ Full | Tree-sitter integration |
| JavaScript | ✅ Full | Tree-sitter integration |
| Rust | ✅ Full | Tree-sitter integration |
| Makefile, TOML, YAML | ✅ Full | Custom parsers |
| SQL | 📋 Framework-ready | Parser stub exists |
| Zig | 📋 Framework-ready | Parser interface defined |

### 4. **Database & Persistence**

- **PostgreSQL** with **pgvector** extension (semantic embeddings)
- **Schema**: Auto-initialized via `etc/init-db.sql`
- **ORM**: Direct SQL via psycopg2 (no SQLAlchemy)
- **Docker**: `make docker-up` starts containerized PostgreSQL

### 5. **Graph Query Engine**

Custom Cypher-like DSL (`graph_query/`) for code querying:

```python
# Example: Find all functions calling a specific method
query = "MATCH (f:Function)-[calls]->(m:Method {name: 'process'}) RETURN f"
```

- **Parser**: Lark-based grammar parsing
- **Executor**: NetworkX graph traversal
- **Status**: ADR-0017, 35/35 core tests passing

## Development Workflow

### Standard Tasks

```bash
make env              # Create venv with all dependencies
make test             # Run all unit tests with coverage
make lint             # Check code style (ruff)
make format           # Auto-format code (ruff + isort)
make type-check       # Static type checking (mypy strict)
make docker-up        # Start PostgreSQL
```

### Adding a New Language Parser

1. Create `src/code_analyzer/parsers/<language>.py` extending `SourceParser`
2. Implement required methods: `parse_file()`, `extract_symbols()`, etc.
3. Add unit tests in `tests/unit/parsers/test_<language>.py`
4. Reference implementation: `src/code_analyzer/parsers/python.py`

### Adding New Analysis Tools

1. Create tool in `src/code_analyzer/tools/<tool_name>.py`
2. Operate on `CodeGraph` and `Symbol` models
3. Add comprehensive unit tests
4. Document in `docs/query_tools.md`

## Configuration Files

### pyproject.toml

Defines:
- **Project metadata**: name, version (dynamic), description
- **Dependencies**: 47+ core packages
- **Optional groups**: docs, dev dependencies
- **Tool configs**: ruff, mypy, pytest
- **Scripts**: CLI entry points

### pytest.ini

```ini
[pytest]
testpaths = ["tests/unit", "tests/integration"]
norecursedirs = ["tests/corpus", "tests/spikes"]  # Exclude from auto-discovery
```

- **Rationale**: Corpus provides test data; spikes are experimental

### Makefile

Over 20 targets organized into categories:
- **Environment**: `env`, `sync`, `lock`
- **Testing**: `test`, `py-test`, `py-test-all`
- **Code quality**: `lint`, `format`, `type-check`, `imports`
- **Docker**: `docker-up`, `docker-down`, `docker-fresh`
- **Cleanup**: `clean`

## Important Paths

| Purpose | Path |
|---------|------|
| Main package | `src/code_analyzer/` |
| Unit tests | `tests/unit/` |
| Research spikes | `tests/spikes/` |
| Test data | `tests/corpus/` |
| Architecture docs | `docs/adr/` |
| Database config | `etc/` |
| Version | `src/code_analyzer/__init__.py` |
| Dependencies | `pyproject.toml` + `uv.lock` |

## Key Patterns

### Lazy Evaluation Pipeline

Components use fluent API for deferred execution:

```python
analysis = CodeAnalyzer(project_path)
    .extract_symbols()
    .build_graph()
    .analyze_dependencies()
    .persist_to_db()
```

### Mocking in Tests

Global mock in `tests/unit/conftest.py` replaces `DatabaseManager` to avoid DB dependencies during unit testing.

### Hypothesis Validation

Spikes (14 research phases) validate ADRs before committing to production code.

## Performance Characteristics

- **Python parsing**: Full AST with symbol resolution
- **Graph traversal**: Optimized NetworkX algorithms
- **Temporal analysis**: Sub-second Git history processing (ADR-0012)
- **LLM enrichment**: Probabilistic with hash-based caching (ADR-0013)
