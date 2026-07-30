# Testing Strategy - Code Analyzer

## Overview

The code-analyzer project uses a **multi-layered testing approach** combining unit tests, integration tests, and research spikes to validate architecture decisions. The test suite is extensive: **77,437 LOC across 97 unit test files and 98 experimental spike files**.

## Test Organization

### Test Categories

| Category | Location | Files | Purpose | Execution |
|----------|----------|-------|---------|-----------|
| **Unit Tests** | `tests/unit/` | 97 | Core functionality in isolation | Always runs |
| **Integration Tests** | `tests/integration/` | ~5 | Database persistence | Auto-skips if DB unavailable |
| **Research Spikes** | `tests/spikes/` | 98 | ADR validation & prototyping | Manual investigation |
| **Test Corpus** | `tests/corpus/` | N/A | Reference code samples | Data source, not executed |

### Pytest Configuration (pytest.ini)

```ini
[pytest]
testpaths = ["tests/unit", "tests/integration"]
norecursedirs = ["tests/corpus", "tests/spikes", ".git", ".venv"]
addopts = -v --tb=short
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

**Key Design**:
- `tests/corpus/` and `tests/spikes/` explicitly excluded from auto-discovery
- Corpus provides reference data for testing, not executed as tests
- Spikes are manually investigated during research phases

## Unit Testing Strategy

### Frameworks & Tools

```python
# Test Execution
pytest>=9.0.0
pytest-cov>=4.1.0              # Code coverage reporting
pytest-mock>=3.12.0            # Mocking utilities

# Development Support
icecream>=2.1.8                # Debug printing (print(var))
```

### Module Coverage

```
tests/unit/
├── core/             (16 test files, ~7,154 LOC)
│   ├── test_code_graph.py              # Graph construction & queries
│   ├── test_fully_qualified_name.py    # FQN parsing & formatting (ADR-0008)
│   ├── test_models.py                  # Symbol, Import, Metadata models
│   ├── test_enums.py                   # Language & format enums
│   └── ... (other core tests)
│
├── parsers/          (15 test files)
│   ├── test_python_parser.py           # Python AST parsing
│   ├── test_go_parser.py               # Go parsing
│   ├── test_java_parser.py             # Java parsing
│   └── ... (other language tests)
│
├── tools/            (20+ test files)
│   ├── test_graph_tools.py             # Graph algorithms
│   ├── test_metrics.py                 # Complexity analysis
│   ├── test_graph_query_*.py           # Cypher DSL tests (35+ tests)
│   └── test_extractors.py              # Data extraction
│
├── actions/          (8 test files)   # Analysis operations
├── agent/            (11 test files)  # Agentic querying system
├── db/               (2 test files)   # Database persistence
├── tui/              (12 test files)  # Terminal UI components
│
└── conftest.py                         # Shared fixtures & global mocks
```

### Global Mocking Strategy

**Location**: `tests/unit/conftest.py`

```python
@pytest.fixture(autouse=True)
def mock_database_manager(monkeypatch):
    """Mock DatabaseManager for all unit tests to avoid DB dependencies."""
    monkeypatch.setattr(
        'code_analyzer.db.database_manager.DatabaseManager',
        MagicMock()
    )
```

**Purpose**: Isolate unit tests from database layer, enabling fast execution without PostgreSQL.

**Result**: Unit tests run in seconds without external dependencies.

### Module-Scoped Fixtures

**Location**: `tests/unit/tools/conftest.py`

```python
@pytest.fixture(scope="module")
def sample_code_graph():
    """Create reusable CodeGraph instance for tool tests."""
    graph = CodeGraph()
    graph.add_symbol(Symbol(...))
    return graph
```

**Benefit**: Expensive graph construction happens once per test module, improving test speed.

### Testing by Module

#### **Core Models (tests/unit/core/)**

- **CodeGraph**: Construction, node/edge operations, cycle detection
- **Symbol**: Model validation, FQN formatting, method resolution
- **Import**: Dependency tracking, categorization (STDLIB/POPULAR/OTHER/INTERNAL)
- **FullyQualifiedName**: Parsing `path#NN_section.MM_subsection` format

**Example Test Pattern**:
```python
def test_symbol_with_full_fqn():
    sym = Symbol(name="process", fqn="app/api.py#01_api.02_routes.03_process")
    assert sym.module == "app/api"
    assert sym.section_number == 1
```

#### **Parsers (tests/unit/parsers/)**

- Language-specific AST parsing validation
- Symbol extraction accuracy
- Import detection (local vs external)
- Edge cases (decorators, nested classes, generics)

**Example Test Pattern**:
```python
def test_python_parser_extracts_class_methods():
    code = """
    class MyClass:
        def method(self): pass
    """
    symbols = PythonParser().extract_symbols(code)
    assert any(s.name == "method" for s in symbols)
```

#### **Graph Tools (tests/unit/tools/)**

- Path finding algorithms (shortest path, all paths)
- Neighbor queries (incoming/outgoing edges)
- Metrics computation (cyclomatic complexity)
- Graph query DSL execution

**Example Test Pattern**:
```python
def test_find_all_callers_of_function(sample_code_graph):
    callers = find_all_callers(sample_code_graph, "target_function")
    assert len(callers) == 2
    assert "caller_a" in [c.name for c in callers]
```

#### **Graph Query Language (tests/unit/tools/test_graph_query_*.py)**

- **Parser tests**: Cypher DSL syntax parsing (35+ tests)
- **Executor tests**: Query execution on sample graphs
- **Integration tests**: End-to-end query workflows

**Status**: ADR-0017, 35/35 core tests passing (see `tests/unit/tools/test_graph_query_*.py`)

## Integration Testing Strategy

### Database Integration Tests

**Location**: `tests/integration/`

**Purpose**: Validate database persistence layer without mocking

**Setup** (`tests/integration/conftest.py`):
```python
@pytest.fixture(scope="session")
def db_connection():
    """Connect to running PostgreSQL instance."""
    conn = psycopg2.connect(
        host="localhost",
        dbname="codeanalyzer",
        user="user",
        password="pass"
    )
    yield conn
    conn.close()

@pytest.fixture(scope="function")
def clean_database(db_connection):
    """Reset database for each test."""
    cursor = db_connection.cursor()
    cursor.execute("TRUNCATE symbols, imports, code_metadata CASCADE")
    cursor.close()
    db_connection.commit()
    yield
```

**Auto-Skip Mechanism**:
```python
@pytest.mark.skipif(
    not db_available(),
    reason="PostgreSQL not running"
)
def test_persist_symbols_to_db(db_connection):
    # Test code
    pass
```

If PostgreSQL is not available (e.g., CI without Docker Compose), integration tests are skipped automatically.

### Testing Database Layer

- Symbol persistence and retrieval
- Import relationship storage
- Graph reconstruction from database
- Vector similarity searches (pgvector integration)
- Transaction handling and rollbacks

## Research Spike Strategy

### 14 Experimental Phases

Spikes validate ADRs before committing to production. Each spike has:

| Phase | ADR Targets | Purpose | Status |
|-------|-------------|---------|--------|
| **001** | ADR-0001, ADR-0002 | Core data model | ✅ Complete (348 tests) |
| **002** | ADR-0004 | Python parser implementation | ✅ Complete |
| **003** | ADR-0001, ADR-0003 | NetworkX graph & queries | ✅ Complete |
| **004** | ADR-0006, ADR-0011 | PostgreSQL schema design | ✅ Complete |
| **005** | ADR-0008 | Fluent API & lazy pipelines | ✅ Complete |
| **006** | ADR-0005 | CodeBERT embeddings | ✅ Complete |
| **007** | ADR-0014 | Agentic querying system | ✅ Complete |
| **008** | ADR-0004 | Multi-language parsing | ✅ Complete |
| **009** | ADR-0010 | Import categorization | ✅ Complete |
| **010** | ADR-0012 | Git temporal analysis | ✅ Complete |
| **011** | ADR-0013 | LLM enrichment pipeline | ✅ Complete |
| **012** | ADR-0016 | LLM memory & token tracking | ✅ Complete |
| **013** | ADR-0005 | Embedding system refactor | ✅ Complete |
| **014** | ADR-0017 | Cypher-like query language | ✅ Complete (35/35 tests) |

### Spike Structure

```
tests/spikes/001_core_model/
├── conftest.py                  # Spike-specific fixtures
├── test_01_symbol_model.py      # Basic symbol validation
├── test_02_import_model.py      # Import tracking
├── test_03_graph_construction.py # Graph building
└── try_01_real_project.py       # Real codebase validation
```

### Running Spikes

```bash
# Run single spike
uv run pytest tests/spikes/001_core_model/ -v

# Run all spikes (manual investigation)
uv run pytest tests/spikes/ -v

# Real-project validation (uses actual code)
uv run pytest tests/spikes/001_core_model/try_01_real_project.py -v
```

### Real-Project Validation

Each spike includes `try_*.py` files that test against real codebases:

```python
def test_parse_real_codebase():
    """Validate on code-analyzer project itself."""
    parser = PythonParser()
    symbols = parser.parse_directory("src/code_analyzer/")
    assert len(symbols) > 100  # Should find substantial code
```

This ensures ADRs work on production code, not just toy examples.

## Code Coverage

### Coverage Command

```bash
make test
# Runs: uv run pytest --cov=src/code_analyzer tests/unit tests/integration
```

### Coverage Reports

- **Console output**: Coverage percentages per module
- **HTML report**: `htmlcov/index.html` (generated)
- **Minimum threshold**: Enforced in CI/CD

### Coverage by Module

| Module | Coverage | Target |
|--------|----------|--------|
| `core/` | ~95% | High (critical data models) |
| `parsers/` | ~90% | High (language parsing) |
| `tools/` | ~92% | High (analysis algorithms) |
| `db/` | ~85% | Medium (mocked in unit tests) |
| `tui/` | ~80% | Medium (interactive components) |

## Test Execution

### Command Patterns

```bash
# Unit tests only (default)
make test
# Runs: uv run pytest --cov=src/code_analyzer tests/unit tests/integration

# Full test run
uv run pytest tests/ -q

# Specific test file
uv run pytest tests/unit/core/test_models.py -v

# Specific test function
uv run pytest tests/unit/core/test_models.py::test_symbol_creation -v

# With coverage
uv run pytest --cov=src/code_analyzer tests/unit/

# Quiet mode (fewer logs)
uv run pytest tests/unit/ -q

# Specific marker
uv run pytest -m "not slow" tests/unit/
```

### CI/CD Test Execution

**GitHub Actions** (`.github/workflows/validate.yml`):

```yaml
- name: Run tests
  run: make test
```

- Triggered on every PR and push to main
- Requires all tests to pass before merge
- Coverage report attached to PR

## Test Design Principles

### 1. **Isolation**

- Unit tests are fully isolated via mocking
- No database dependencies
- No filesystem dependencies (use in-memory data)
- No network calls

### 2. **Determinism**

- Tests produce same results on repeated runs
- No random data unless explicitly seeded
- No time-dependent logic
- No ordering dependencies between tests

### 3. **Clarity**

- Test names describe exactly what's being tested
- Arrange-Act-Assert pattern
- Single assertion per test when possible
- Descriptive failure messages

**Example**:
```python
def test_fqn_parser_extracts_module_and_section_numbers():
    fqn = FullyQualifiedName.parse("app/api.py#01_routes.02_users")
    assert fqn.module == "app/api"
    assert fqn.section_number == 1
    assert fqn.subsection_number == 2
```

### 4. **Speed**

- Unit tests complete in seconds (no I/O)
- Integration tests run only when DB is available
- Expensive fixtures use module scope
- Spike tests are manual, don't block CI

## Common Testing Patterns

### Testing Parsers

```python
def test_parser_extracts_function_definition(python_parser):
    code = "def hello(name): return f'Hello {name}'"
    symbols = python_parser.extract_symbols(code)

    hello_func = next(s for s in symbols if s.name == "hello")
    assert hello_func.type == SymbolType.FUNCTION
    assert len(hello_func.parameters) == 1
```

### Testing Graph Operations

```python
def test_graph_finds_dependency_path(sample_code_graph):
    path = sample_code_graph.find_path("module_a", "module_z")
    assert path is not None
    assert path[0].name == "module_a"
    assert path[-1].name == "module_z"
```

### Testing with Fixtures

```python
@pytest.fixture
def populated_graph():
    g = CodeGraph()
    g.add_symbol(Symbol(name="foo"))
    g.add_symbol(Symbol(name="bar"))
    return g

def test_graph_operation(populated_graph):
    assert len(populated_graph.nodes) == 2
```

## Debugging Tests

### Useful Commands

```bash
# Show print statements and debug output
uv run pytest -s tests/unit/test_file.py

# Stop at first failure
uv run pytest -x tests/unit/

# Enter debugger on failure
uv run pytest --pdb tests/unit/

# Verbose output with assertions
uv run pytest -vv tests/unit/

# Run last failed tests only
uv run pytest --lf tests/unit/
```

### Using icecream for Debugging

```python
from icecream import ic

def test_complex_logic():
    result = complex_function()
    ic(result)  # Prints: result: <value>
    assert result == expected
```

## Best Practices

1. **Mock external dependencies**: Database, network, filesystem
2. **Test edge cases**: Empty inputs, None values, boundary conditions
3. **Avoid test interdependencies**: Tests should be runnable in any order
4. **Name tests descriptively**: `test_parser_handles_nested_classes` not `test_parse_1`
5. **Keep tests focused**: One behavior per test when possible
6. **Use fixtures for setup**: Reduces duplication
7. **Validate ADRs with spikes**: Before production code changes
