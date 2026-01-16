# Skill: Feature Model Management

> **Location**: `.claude/skills/feature-model/SKILL.md`  
> **Purpose**: Guide for maintaining the Czarnecki-style feature model documentation

---

## Overview

This skill explains how to maintain the **Feature Model** for the Code Analyzer project. The feature model uses Krzysztof Czarnecki's Feature-Oriented Domain Analysis (FODA) methodology to document all features, their relationships, and status.

### File Structure

```
docs/features/
├── features.yaml          # Source of truth (machine-readable)
├── FEATURES.md            # Auto-generated human-readable index
└── generate_features_md.py # Generator script
```

---

## Quick Reference

### Adding a New Feature

1. **Edit `docs/features/features.yaml`**
2. **Add entry under `features:`** with required fields
3. **Run generator**: `python docs/features/generate_features_md.py`
4. **Commit both files**

### Feature Entry Template

```yaml
- id: "F-NNN"                    # Unique ID (F-000 to F-999)
  name: "Feature Name"           # Human-readable name
  type: mandatory | optional     # Feature type
  status: planned | in-progress | implemented | deprecated
  parent: "F-XXX"                # Parent feature ID
  description: >
    Multi-line description of what this feature does.
  requires: ["F-YYY"]            # Cross-tree dependencies (optional)
  excludes: ["F-ZZZ"]            # Mutual exclusions (optional)
  implementation:
    adr: ["ADR-0001"]            # Related ADR documents
    modules: ["src/path/"]       # Source code locations
    tests: ["tests/path/"]       # Test locations
    docs: ["docs/page.md"]       # Additional documentation
  tags: [keyword1, keyword2]     # Searchable tags
```

---

## Detailed Instructions

### 1. Understanding Feature IDs

Feature IDs follow a hierarchical numbering scheme:

| Range | Layer/Category |
|-------|----------------|
| F-000 | Root (system) |
| F-1xx | Layer 1: Parsing |
| F-2xx | Layer 2: Metadata Curation |
| F-3xx | Layer 3: Graph Analysis |
| F-4xx | Layer 4: Persistence |
| F-5xx | User Interface |
| F-6xx | AI & Agent |
| F-7xx | Reserved for future |
| F-8xx | Reserved for future |
| F-9xx | Cross-cutting concerns |

**Sub-features**: Use the pattern `F-X10`, `F-X11`, `F-X12` for children of `F-X00`.

### 2. Feature Types (Czarnecki Notation)

| Type | Symbol | Meaning | When to Use |
|------|--------|---------|-------------|
| `mandatory` | ● | Must be included | Core functionality |
| `optional` | ○ | Can be included | Extensions, add-ons |
| `alternative` | ◇ | One of group | Mutually exclusive choices |
| `or-group` | ◆ | One or more | At least one required |

### 3. Status Values

| Status | Symbol | Meaning |
|--------|--------|---------|
| `planned` | 📋 | Designed but not started |
| `in-progress` | 🔨 | Currently being implemented |
| `implemented` | ✅ | Complete and working |
| `deprecated` | ⚠️ | Scheduled for removal |

### 4. Linking to ADRs

Always link features to relevant Architectural Decision Records:

```yaml
implementation:
  adr: ["ADR-0001", "ADR-0004"]  # List of ADR IDs
```

The generator will create clickable links to `docs/adr/NNNN-*.md`.

**Current ADRs** (as of 2026-01-14):

| ADR | Title | Status |
|-----|-------|--------|
| 0001 | Four-Layer Architecture | ✅ Validated |
| 0002 | Granularity Levels | ✅ Validated |
| 0003 | PostgreSQL Persistence | ✅ Validated |
| 0004 | Multi-Language Parsing | ✅ Validated |
| 0005 | Analysis Pipeline | ✅ Validated |
| 0006 | Semantic Embeddings | ✅ Validated |
| 0007 | Symbol Table Structure | ⚠️ Rejected |
| 0008 | FQN Format | ✅ Validated |
| 0009 | Lazy Fluent Pipeline | ✅ Validated |
| 0010 | External Import Categorization | ✅ Validated |
| 0011 | Pydantic Layer Projections | ✅ Validated |
| 0012 | Deterministic Analysis | ✅ Validated |
| 0013 | LLM Integration | ✅ Validated |
| 0014 | Agentic Querying | 📋 Proposed |
| 0015 | Agentic Response Loop | 📋 Proposed |
| 0016 | LLM Memory Slots | ✅ Validated |

### 5. Cross-Tree Constraints

Define dependencies between features that span the hierarchy:

```yaml
constraints:
  - type: requires       # Source needs target
    source: "F-410"
    target: "F-400"
    reason: "Vector search requires PostgreSQL storage"
    
  - type: excludes       # Cannot have both
    source: "F-XXX"
    target: "F-YYY"
    reason: "Mutually exclusive implementations"
```

### 6. Feature Groups

Group related features for selection rules:

```yaml
groups:
  - id: "G-100"
    name: "Language Parsers"
    type: or-group           # At least one required
    features: ["F-110", "F-111", "F-112"]
    min_select: 1
    max_select: null         # No maximum (optional)
    description: "At least one parser must be enabled"
```

---

## Workflow Examples

### Example 1: Adding a New Parser

```yaml
# Add to features.yaml under features:
- id: "F-113"
  name: "Java Parser"
  type: optional
  status: planned
  parent: "F-100"
  description: >
    Parse Java source files using tree-sitter for class, method,
    and interface extraction.
  implementation:
    adr: ["ADR-0004"]
    modules: ["src/code_analyzer/parsers/java_parser.py"]
  tags: [parser, java, tree-sitter]

# Add to G-100 group
groups:
  - id: "G-100"
    features: ["F-110", "F-111", "F-112", "F-113"]  # Add F-113
```

### Example 2: Marking Feature Complete

```yaml
# Change status from in-progress to implemented
- id: "F-410"
  name: "Vector Search"
  type: optional
  status: implemented  # Was: planned
  # ... rest unchanged
```

### Example 3: Deprecating a Feature

```yaml
- id: "F-XXX"
  name: "Old Feature"
  type: optional
  status: deprecated  # Mark as deprecated
  description: >
    DEPRECATED: Use F-YYY instead. Will be removed in v2.0.
```

---

## Generator Usage

### Basic Usage

```bash
# From project root
python docs/features/generate_features_md.py

# With custom paths
python docs/features/generate_features_md.py \
  --input docs/features/features.yaml \
  --output docs/features/FEATURES.md
```

### What the Generator Does

1. Reads `features.yaml`
2. Builds feature hierarchy tree
3. Counts features by status
4. Generates ASCII tree visualization
5. Creates detailed sections per layer
6. Renders cross-tree constraints
7. Outputs `FEATURES.md`

### Generator Features

- **ADR linking**: Converts `ADR-0001` → `[ADR-0001](../adr/0001-*.md)`
- **Module linking**: Converts paths to code links
- **Status symbols**: Renders ✅ 🔨 📋 ⚠️
- **Type symbols**: Renders ● ○ ◇ ◆
- **Hierarchy tree**: ASCII visualization

---

## Validation Checklist

Before committing changes:

- [ ] Feature ID is unique and follows numbering scheme
- [ ] Parent feature exists
- [ ] Status is valid (`planned`, `in-progress`, `implemented`, `deprecated`)
- [ ] Type is valid (`mandatory`, `optional`, `alternative`, `or-group`)
- [ ] ADR references exist in `docs/adr/`
- [ ] Module paths exist in `src/`
- [ ] Tags are lowercase, hyphenated
- [ ] Generator runs without errors
- [ ] FEATURES.md is regenerated

---

## Integration with CI/CD

Add to your CI pipeline:

```yaml
# .github/workflows/docs.yml
- name: Validate Feature Model
  run: |
    python -c "import yaml; yaml.safe_load(open('docs/features/features.yaml'))"
    python docs/features/generate_features_md.py
    git diff --exit-code docs/features/FEATURES.md
```

This ensures:
1. YAML is valid
2. Generator runs successfully
3. FEATURES.md is up-to-date

---

## References

### Czarnecki's Feature Modeling

- Czarnecki, K., & Eisenecker, U. W. (2000). *Generative programming*. Addison-Wesley.
- Czarnecki, K., Helsen, S., & Eisenecker, U. (2004). Staged configuration using feature models. *SPLC 2004*.
- Kang, K. C., et al. (1990). *Feature-oriented domain analysis (FODA)*. SEI Technical Report.

### Project Documentation

- [ADR Index](../docs/adr/index.md)
- [Vision Document](../docs/vision.md)
- [Language Parsers](../docs/language_parsers.md)

---

## Troubleshooting

### "Feature ID already exists"

Each `id` must be unique. Check existing IDs before adding.

### "Parent feature not found"

The `parent` field must reference an existing feature ID, or `F-000` for root.

### "Generator fails with KeyError"

Ensure all required fields are present: `id`, `name`, `type`, `status`, `parent`.

### "Links broken in FEATURES.md"

Verify ADR files exist at `docs/adr/NNNN-*.md` with correct naming.

---

*Last Updated: 2026-01-14*