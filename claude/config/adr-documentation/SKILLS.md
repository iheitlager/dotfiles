# ADR Documentation Strategy - Code Analyzer

## Overview

The code-analyzer project uses **Architecture Decision Records (ADRs)** to document major design decisions. There are **17 ADRs total**, with **13 validated through empirical testing** and 3 in design phase.

## What is an ADR?

An ADR is a lightweight document that records a significant architectural decision, including:
- **Context**: Why the decision was needed
- **Decision**: What was decided
- **Consequences**: Impacts (positive and negative)
- **Alternatives Considered**: Other options evaluated
- **Status**: Proposed/Accepted/Superseded/Deprecated
- **Validation**: How the decision was validated

**Philosophy**: ADRs are living documentation—updated as understanding evolves and decisions are validated.

## ADR Repository Structure

```
docs/adr/
├── index.md                  # Master index with status summary
├── 0001-core_architecture.md # Individual ADRs (numbered)
├── 0002-four_layer_model.md
├── ... (0003-0017) ...
├── templates/
│   ├── adr-template.md       # Standard ADR template
│   └── plan-template.md      # Implementation plan template
└── README.md                 # ADR documentation guide
```

## The 17 ADRs

### Architecture & Core (ADR-0001 to ADR-0002)

#### **ADR-0001: Four-Layer Architecture**

**Status**: ✅ Accepted & Validated

**Context**: Need to support static analysis across multiple programming languages without duplicating logic for each language.

**Decision**: Implement a four-layer architecture:
1. **Parser Layer**: Language-specific AST parsers
2. **Metadata Layer**: Language-agnostic Symbol, Import, Metadata models
3. **Storage Layer**: NetworkX graphs and PostgreSQL persistence
4. **Query Layer**: Graph algorithms and analysis tools

```
┌─────────────────────────────────────┐
│  Language-Specific Parsers          │
│  (Python, Go, Java, Rust, ...)      │
└──────────────┬──────────────────────┘
               ↓ (extract symbols)
┌─────────────────────────────────────┐
│  Language-Agnostic Models           │
│  (Symbol, Import, Metadata)         │
└──────────────┬──────────────────────┘
               ↓ (construct graph)
┌─────────────────────────────────────┐
│  Storage Layer                      │
│  (NetworkX Graph, PostgreSQL)       │
└──────────────┬──────────────────────┘
               ↓ (query)
┌─────────────────────────────────────┐
│  Analysis & Tools                   │
│  (Graph algorithms, metrics, etc)   │
└─────────────────────────────────────┘
```

**Validation**: Spike 001 (348 tests) + real parsing of code-analyzer project

**Implementation**: `src/code_analyzer/core/`, `src/code_analyzer/parsers/`

#### **ADR-0002: SourceParser Base Class Pattern**

**Status**: ✅ Accepted & Validated

**Decision**: All language parsers inherit from abstract `SourceParser` base class, ensuring consistent interface.

**Interface**:
```python
class SourceParser(ABC):
    @abstractmethod
    def parse_file(self, file_path: str) -> CodeGraph: pass

    @abstractmethod
    def extract_symbols(self, source_code: str) -> List[Symbol]: pass

    @abstractmethod
    def extract_imports(self, source_code: str) -> List[Import]: pass
```

**Validation**: Spike 002 (Python parser implementation)

**Implementation**: `src/code_analyzer/parsers/base.py`, `src/code_analyzer/parsers/python.py`, etc.

### Parsing & Analysis (ADR-0004 to ADR-0007)

#### **ADR-0004: Multi-Language Parsing Framework**

**Status**: ✅ Accepted & Validated

**Decision**: Support parsing via:
- **Tree-sitter** for languages with grammars (Go, Java, JavaScript, Rust)
- **Native AST** for languages with built-in parsing (Python)
- **Custom parsers** for specialized formats (Makefile, TOML, YAML)

**Coverage**:

| Language | Method | Completeness |
|----------|--------|--------------|
| Python | AST | 100% (full introspection) |
| Go | tree-sitter | 95% (via tree-sitter-go) |
| Java | tree-sitter | 90% (via tree-sitter-java) |
| JavaScript | tree-sitter | 90% (via tree-sitter-javascript) |
| Rust | tree-sitter | 85% (via tree-sitter-rust) |
| Makefile | Custom | 80% (target detection) |
| TOML | Custom | 85% (key-value parsing) |
| YAML | Custom | 80% (structure parsing) |
| SQL | Framework-ready | 0% (interface defined) |
| Zig | Framework-ready | 0% (interface defined) |

**Validation**: Spike 008 (multi-language parsing)

**Implementation**: `src/code_analyzer/parsers/` directory

#### **ADR-0005: Embedding-Enriched Code Analysis**

**Status**: ✅ Accepted & Validated

**Decision**: Use CodeBERT (sentence-transformers) embeddings to enrich code symbols with semantic information for similarity search.

**Process**:
1. Extract symbol documentation (docstrings, comments)
2. Generate embeddings via CodeBERT
3. Store in pgvector (PostgreSQL vector extension)
4. Enable semantic similarity queries

**Benefits**: Find similar code patterns across codebase

**Validation**: Spike 006 (embedding implementation)

**Implementation**: `src/code_analyzer/tools/embeddings.py`

#### **ADR-0007: Parser Composability via Lark**

**Status**: ✅ Accepted & Validated

**Decision**: Use Lark parser combinator library for custom grammars (Makefile, TOML, YAML) instead of regex.

**Advantage**: Composable, maintainable grammar definitions

**Example** (Makefile parser):
```python
MAKEFILE_GRAMMAR = """
    ?start: rule+
    rule: target ":" dependencies "\n" commands
    target: WORD
    dependencies: WORD*
    commands: COMMAND+

    %import common.WORD
    %import common.WS
    %ignore WS
"""
```

**Validation**: Spike 003 (grammar-based parsing)

**Implementation**: `src/code_analyzer/parsers/makefile.py`, etc.

### Storage & Persistence (ADR-0003, ADR-0006, ADR-0011)

#### **ADR-0003: PostgreSQL with pgvector**

**Status**: ✅ Accepted & Validated

**Decision**: Use PostgreSQL as primary persistent store with pgvector extension for vector embeddings.

**Schema**:
```sql
CREATE TABLE symbols (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    type SymbolType,
    fqn VARCHAR(512),
    embedding vector(384)  -- CodeBERT embedding dimension
);

CREATE TABLE imports (
    id UUID PRIMARY KEY,
    source_symbol_id UUID,
    target_module VARCHAR(512),
    import_type ImportType,
    category ImportCategory
);

CREATE EXTENSION pgvector;
CREATE INDEX ON symbols USING ivfflat (embedding vector_cosine_ops);
```

**Advantages**:
- Persistent storage of analysis results
- Vector similarity search via pgvector
- Transactional integrity
- Proven scalability

**Validation**: Spike 004 (schema design) + v0.10.1 release (production use)

**Setup**: `etc/docker-compose.yml` provides containerized PostgreSQL

#### **ADR-0006: Lazy Fluent Pipeline API**

**Status**: ✅ Accepted & Validated

**Decision**: Provide fluent API for deferred analysis execution.

**Example**:
```python
analysis = CodeAnalyzer("project/path")
    .extract_symbols()
    .build_graph()
    .analyze_dependencies()
    .persist_to_db()
    .execute()  # Deferred evaluation
```

**Benefit**: Enables optimization and lazy evaluation

**Validation**: Spike 005 (fluent pipeline implementation)

**Implementation**: `src/code_analyzer/core/analyzer.py`

#### **ADR-0011: Graph Database Integration Strategy**

**Status**: ✅ Accepted & Validated

**Decision**: Use NetworkX in-memory graphs for analysis, PostgreSQL for persistence, with explicit sync points.

**Workflow**:
```
Parse → Build NetworkX Graph → Analyze → Persist to PostgreSQL
                ↑                              ↓
         (Fast in-memory)          (Long-term storage)
```

**Sync Pattern**:
```python
def persist_graph(graph: CodeGraph, db: DatabaseManager):
    for symbol in graph.nodes:
        db.insert_symbol(symbol)
    for edge in graph.edges:
        db.insert_import(edge)
```

**Validation**: v0.10.1 production release

### Data Models (ADR-0008 to ADR-0010)

#### **ADR-0008: Fully Qualified Name (FQN) Format**

**Status**: ✅ Accepted & Validated

**Decision**: Use hierarchical FQN format with order preservation: `path#NN_section.MM_subsection`

**Format**:
```
app/api.py#01_routes.02_users.03_get_user

├── path: app/api.py
├── section_number: 01 (routes)
├── section_name: routes
├── subsection_number: 02 (users)
├── subsection_name: users
└── item_number: 03 (get_user)
```

**Benefits**:
- Order-preserving (enables source code navigation)
- Language-agnostic
- Hierarchical (reflects code structure)
- Sortable and comparable

**Examples**:
```
app/core.py#01_models.02_user.03_validate
api/handlers.py#01_auth.02_login
utils/helpers.py#01_string_ops
```

**Validation**: Spike 005 (real codebase FQN generation)

**Implementation**: `src/code_analyzer/core/fully_qualified_name.py`

#### **ADR-0009: Symbol Type Classification**

**Status**: ✅ Accepted & Validated

**Decision**: Classify symbols into standard types across languages.

**Types**:
```python
class SymbolType(Enum):
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    VARIABLE = "variable"
    CONSTANT = "constant"
    INTERFACE = "interface"
    ENUM = "enum"
    STRUCT = "struct"
    DECORATOR = "decorator"
    ALIAS = "alias"
```

**Mapping by Language**:
| Python | Go | Java | JavaScript |
|--------|----|----|------------|
| class → CLASS | struct → STRUCT | class → CLASS | class → CLASS |
| def → FUNCTION | func → FUNCTION | method → METHOD | function → FUNCTION |
| var → VARIABLE | var → VARIABLE | field → VARIABLE | const → CONSTANT |

**Validation**: Spike 001 (type system validation)

#### **ADR-0010: External Import Categorization**

**Status**: ✅ Accepted & Validated

**Decision**: Categorize all imports into 4 standard categories.

**Categories**:
```python
class ImportCategory(Enum):
    STDLIB = "stdlib"           # Standard library (os, sys, json)
    POPULAR = "popular"         # Well-known packages (requests, numpy, django)
    OTHER = "other"             # Unpopular third-party packages
    INTERNAL = "internal"       # Project-internal modules
```

**Detection Logic**:
```python
def categorize_import(module_name: str, stdlib_list: Set[str]) -> ImportCategory:
    if module_name in stdlib_list:
        return ImportCategory.STDLIB
    if module_name in POPULAR_PACKAGES:
        return ImportCategory.POPULAR
    if is_project_internal(module_name):
        return ImportCategory.INTERNAL
    return ImportCategory.OTHER
```

**Validation**: Spike 009 (categorization on real projects)

**Implementation**: `src/code_analyzer/tools/import_analyzer.py`

### Temporal & Advanced Analysis (ADR-0012, ADR-0013)

#### **ADR-0012: Git-Based Temporal Analysis**

**Status**: ✅ Accepted & Validated

**Decision**: Use git history to analyze code evolution and identify changing symbols over time.

**Process**:
1. Walk git history (from HEAD to initial commit)
2. For each commit, extract code state
3. Track symbol changes (additions, deletions, modifications)
4. Build temporal dependency graph
5. Analyze change patterns and hotspots

**Performance**: Sub-second analysis of large repositories

**Validation**: Spike 010 (git processing on real projects)

**Use Cases**:
- Identify frequently changing modules
- Find circular dependencies introduced over time
- Understand architecture drift

#### **ADR-0013: Probabilistic LLM Enrichment with Hash-Based Caching**

**Status**: ✅ Accepted & Validated

**Decision**: Use LLM (Claude) to enrich code analysis with semantic insights, with deterministic caching via content hashing.

**Architecture**:
```
Symbol + Documentation
    ↓ (hash content)
Hash Lookup (cache)
    ├─ Hit: Return cached insight
    └─ Miss: Call LLM API
            ↓ (store result)
    Database Cache

Next run: Hash-based lookup skips LLM call
```

**Benefits**:
- Reduces LLM API calls (cost optimization)
- Deterministic caching (same input = same output)
- Graceful degradation (works without LLM)

**Validation**: Spike 011 (LLM integration with Ollama)

**Implementation**: `src/code_analyzer/agent/enricher.py`

### Querying & Interaction (ADR-0014 to ADR-0017)

#### **ADR-0014: Agentic Querying System** (Proposed)

**Status**: 📋 Design Phase

**Decision**: Enable agentic querying where:
1. User asks natural language question
2. Agent decomposes into graph queries
3. Agent iteratively refines results
4. Agent provides explanation

**Process**:
```
User: "Find all modules that depend on the authentication system"
    ↓
Agent: Decomposes into:
  - Find "auth" module (name matching)
  - Find incoming edges (dependents)
  - Filter by strength/importance
    ↓
Results + Explanation
```

**Implementation**: `src/code_analyzer/agent/query_agent.py`

#### **ADR-0015: Response Loop UX Design** (Proposed)

**Status**: 📋 Design Phase

**Decision**: Implement Claude Code-inspired interactive response loop where:
1. User provides query
2. System shows incremental results
3. User can refine/clarify
4. System re-executes with feedback

**Interface** (inspired by Claude Code):
```
Query: Find all callers of 'parse_file'
────────────────────────────────────────
Results (3 found):
  - api/handlers.py:api_handler()
  - cli/main.py:main()
  - tests/test_parsers.py:test_parse()

Refine? (add more criteria, adjust results, etc.)
```

#### **ADR-0016: LLM Memory & Token Tracking**

**Status**: ✅ Accepted & Validated

**Decision**: Implement LLM memory slots to track conversation context and token usage.

**Memory System**:
```python
class MemorySlot:
    slot_id: str
    max_tokens: int
    used_tokens: int
    content: str  # Stored context

    def can_add(self, new_content: str) -> bool:
        return estimated_tokens(new_content) <= available_tokens
```

**Tracking**:
- Per-conversation token budget
- Slot-based context management
- Automatic LRU eviction when full

**Validation**: Spike 012 (21 tests validating memory system)

**Implementation**: `src/code_analyzer/agent/memory.py`

#### **ADR-0017: Cypher-Like Graph Query Language** ✅

**Status**: ✅ Accepted & Validated

**Decision**: Implement custom graph query DSL inspired by Neo4j Cypher for intuitive code querying.

**Syntax**:
```cypher
# Find all functions calling a target function
MATCH (f:Function)-[calls]->(target:Function {name: 'process'})
RETURN f.name, f.module

# Find dependency chains
MATCH (a:Module)-[depends*1..3]->(b:Module {name: 'core'})
RETURN a.name, b.name

# Pattern with filters
MATCH (class:Class)-[contains]->(method:Method)
WHERE method.cyclomatic_complexity > 5
RETURN class.name, method.name, method.cyclomatic_complexity
```

**Components**:
- **Parser** (Lark-based): Converts Cypher-like syntax to AST
- **Executor** (NetworkX): Traverses graph based on AST
- **Type System**: Validates syntax and types

**Status**: **35/35 core tests passing**

**Validation**: Spike 014 (comprehensive query language testing)

**Implementation**:
- `src/code_analyzer/graph_query/parser.py` (syntax parsing)
- `src/code_analyzer/graph_query/executor.py` (execution)
- `src/code_analyzer/graph_query/models.py` (AST models)
- `tests/unit/tools/test_graph_query_*.py` (comprehensive tests)

## ADR Index & Validation Status

| ADR | Title | Status | Validated | Tests | Implementation |
|-----|-------|--------|-----------|-------|-----------------|
| 0001 | Four-Layer Architecture | ✅ | Spike 001 | 348 | `src/code_analyzer/core/` |
| 0002 | SourceParser Pattern | ✅ | Spike 002 | 150+ | `src/code_analyzer/parsers/base.py` |
| 0003 | PostgreSQL + pgvector | ✅ | v0.10.1 | DB tests | `src/code_analyzer/db/` |
| 0004 | Multi-Language Parsing | ✅ | Spike 008 | 200+ | `src/code_analyzer/parsers/` |
| 0005 | Embedding Enrichment | ✅ | Spike 006 | 50+ | `src/code_analyzer/tools/embeddings.py` |
| 0006 | Lazy Fluent Pipeline | ✅ | Spike 005 | 75+ | `src/code_analyzer/core/analyzer.py` |
| 0007 | Lark-Based Parsing | ✅ | Spike 003 | 100+ | Various parsers |
| 0008 | FQN Format | ✅ | Spike 005 | 85+ | `src/code_analyzer/core/fully_qualified_name.py` |
| 0009 | Symbol Classification | ✅ | Spike 001 | 60+ | `src/code_analyzer/core/models.py` |
| 0010 | Import Categorization | ✅ | Spike 009 | 70+ | `src/code_analyzer/tools/import_analyzer.py` |
| 0011 | Graph Storage Strategy | ✅ | v0.10.1 | DB tests | `src/code_analyzer/db/` |
| 0012 | Git Temporal Analysis | ✅ | Spike 010 | 45+ | `src/code_analyzer/tools/git_analyzer.py` |
| 0013 | LLM Enrichment Caching | ✅ | Spike 011 | 55+ | `src/code_analyzer/agent/enricher.py` |
| 0014 | Agentic Querying | 📋 | Design | — | `src/code_analyzer/agent/query_agent.py` |
| 0015 | Response Loop UX | 📋 | Design | — | `src/code_analyzer/tui/` |
| 0016 | LLM Memory Tracking | ✅ | Spike 012 | 21 | `src/code_analyzer/agent/memory.py` |
| 0017 | Cypher Query Language | ✅ | Spike 014 | 35 | `src/code_analyzer/graph_query/` |

**Summary**: 13/16 Accepted ADRs validated; 3 in design phase

## ADR Template

Location: `docs/adr/templates/adr-template.md`

```markdown
# ADR-NNNN: [Title]

## Status
- [ ] Proposed
- [x] Accepted
- [ ] Superseded
- [ ] Deprecated

## Context
[Describe the issue leading to this decision, including background and motivation]

## Decision
[Describe the decision made, with rationale and key details]

## Consequences
### Positive
- Benefit 1
- Benefit 2

### Negative
- Trade-off 1
- Trade-off 2

## Alternatives Considered
1. [Alternative A]: [Why not chosen]
2. [Alternative B]: [Why not chosen]

## Implementation
- **File(s)**: src/code_analyzer/...
- **Tests**: tests/unit/...
- **Validation**: Spike NNN / Release vX.Y.Z

## References
- [Related ADR](./NNNN-*.md)
- [Issue](https://github.com/...)
- [PR](https://github.com/...)
```

## How ADRs Guide Development

### 1. **Decision Recording**

When facing an architectural choice:
1. Create new ADR (next number)
2. Document context, decision, consequences
3. Mark as "Proposed"
4. Request feedback from team

### 2. **Hypothesis Validation**

Before implementing in production:
1. Create spike phase in `tests/spikes/NNN_*.py`
2. Implement hypothesis
3. Write exhaustive tests
4. Validate ADR assumptions
5. Update ADR status to "Accepted"

### 3. **Implementation**

Once validated:
1. Implement in production code
2. Cross-reference ADR in docstrings
3. Reference ADR in PR description
4. Link tests to ADR

### 4. **Evolution**

As requirements change:
1. Update ADR status (Superseded/Deprecated)
2. Create new ADR for revised decision
3. Update references

## Querying ADRs

### ADR Index

`docs/adr/index.md` provides overview:

```markdown
# Architecture Decision Records

## Accepted & Validated (13)
- ADR-0001: Four-Layer Architecture ✅
- ADR-0002: SourceParser Pattern ✅
- ...

## Proposed (3)
- ADR-0014: Agentic Querying ⏳
- ADR-0015: Response Loop UX ⏳
```

### Finding Related ADRs

Use these commands:

```bash
# Find ADRs mentioning "parser"
grep -r "parser" docs/adr/

# Find ADRs by status
grep "Status:" docs/adr/*.md

# List all ADRs
ls docs/adr/[0-9]*.md | sort
```

## Best Practices

1. **Write ADRs Early**: Document decisions as they're made, not retroactively
2. **Validate with Spikes**: Use experimental phases to test hypotheses
3. **Justify Alternatives**: Explain why other approaches were rejected
4. **Link to Code**: Reference implementation files in ADR
5. **Update Status**: Mark ADRs as accepted/superseded as reality evolves
6. **Keep Concise**: 1-2 pages per ADR is ideal
7. **Include Metrics**: Quantify impacts where possible

## References

- **ADR Home**: `docs/adr/`
- **Spike Tests**: `tests/spikes/`
- **Implementation**: `src/code_analyzer/`
- **External**: https://adr.github.io/ (ADR standard)
