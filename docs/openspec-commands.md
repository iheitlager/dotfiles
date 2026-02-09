# OpenSpec Command Suite Design

**Status**: Approved
**Date**: 2026-02-09
**Version**: 1.0

## Design Decisions (Finalized)

✅ **1. Metadata NOT required in strict mode** - Focus on core spec compliance, not traceability
✅ **2. Orphan detection enabled** - `coverage --verbose` shows implementation files not referenced
✅ **3. Individual metrics** - Not a single quality score (more actionable)
✅ **4. Guidance messages helpful** - Keep actionable suggestions with examples
✅ **5. Exit codes**: 0=success, 1=failure, 2=bad usage

---

## Overview

Unified command interface with consistent flags across all commands:
- **Modes**: Compact (default) | Verbose (`-v`/`--verbose`) | JSON (`--json`)
- **Validation Levels**: Strict (`--strict`) | Standard (default) | Lenient
- **Fail Behavior**: `--fail-on-warning` converts warnings to failures

**Dropped**: `--full` flag (replaced by `--verbose`)

---

## Decision Table: Command × Mode × Level

### 1. `openspec list` - List all specifications

**Purpose**: Discover and catalog available specifications

| Mode | Output | Information Shown |
|------|--------|-------------------|
| **Compact** | Table | Name, Status, Version, Req Count |
| **Verbose** | Table + Details | + Owner, Date, Domain, File Size, Last Modified |
| **JSON** | Structured | All metadata + file paths + stats |

**Example Outputs:**

```bash
# Compact (default)
openspec list
╭────────────────────────────┬────────┬─────────┬──────╮
│ Spec                       │ Status │ Version │ Reqs │
├────────────────────────────┼────────┼─────────┼──────┤
│ 001-dotfiles-core          │ Impl   │ 1.0.0   │  9   │
│ 002-dotfiles-caching       │ Impl   │ 1.0.0   │  4   │
│ 003-shortcuts-system       │ Impl   │ 1.0.0   │  8   │
│ 004-openspec-specification │ Impl   │ 1.0.0   │ 13   │
╰────────────────────────────┴────────┴─────────┴──────╯

# Verbose
openspec list -v
╭────────────────────────────┬────────┬─────────┬──────┬────────────────┬────────────┬──────────┬──────────────╮
│ Spec                       │ Status │ Version │ Reqs │ Owner          │ Date       │ Size     │ Domain       │
├────────────────────────────┼────────┼─────────┼──────┼────────────────┼────────────┼──────────┼──────────────┤
│ 001-dotfiles-core          │ Impl   │ 1.0.0   │  9   │ Ilja Heitlager │ 2026-02-07 │ 45.2 KB  │ Dev Env      │
│ 002-dotfiles-caching       │ Impl   │ 1.0.0   │  4   │ Ilja Heitlager │ 2026-02-07 │ 12.8 KB  │ Performance  │
│ 003-shortcuts-system       │ Impl   │ 1.0.0   │  8   │ Ilja Heitlager │ 2026-02-07 │ 18.5 KB  │ Productivity │
│ 004-openspec-specification │ Impl   │ 1.0.0   │ 13   │ Ilja Heitlager │ 2026-02-08 │ 28.1 KB  │ Specification│
╰────────────────────────────┴────────┴─────────┴──────┴────────────────┴────────────┴──────────┴──────────────╯

# JSON
openspec list --json
{
  "specs": [
    {
      "id": "001-dotfiles-core",
      "name": "Dotfiles System Core Specification",
      "status": "Implemented",
      "version": "1.0.0",
      "requirements": 9,
      "scenarios": 27,
      "owner": "Ilja Heitlager",
      "date": "2026-02-07",
      "domain": "Personal Development Environment",
      "file_path": ".openspec/specs/001-dotfiles-core/spec.md",
      "file_size": 46234
    }
  ]
}
```

---

### 2. `openspec validate` - Validate specifications

**Purpose**: Check spec compliance with OpenSpec format and rules

**Validation Levels:**

| Level | Checks | Exit Code |
|-------|--------|-----------|
| **Strict** (`--strict`) | Only MUST/SHALL requirements | Error on any MUST violation |
| **Standard** (default) | MUST + SHOULD + MAY | Error on MUST, warn on SHOULD |
| **Lenient** | Minimal MUST only | Error only on critical violations |

**Flags:**
- `--fail-on-warning`: Exit code 1 if any warnings (standard/lenient modes)
- `--strict`: Enable strict validation (MUST-only)
- `-v`: Show all issues with suggestions
- `--json`: Machine-readable validation results

| Mode | Output | Information Shown |
|------|--------|-------------------|
| **Compact** | Summary | Pass/Fail, Error count, Warning count, Info count |
| **Verbose** | Detailed Issues | + Line numbers, issue descriptions, fix suggestions |
| **JSON** | Structured | Full issue list with severity, rule, line, message |

**Example Outputs:**

```bash
# Compact (default)
openspec validate
✓ PASSED 001-dotfiles-core
✗ FAILED 002-dotfiles-caching (2 errors, 3 warnings)
✓ PASSED 003-shortcuts-system (1 warning)
✓ PASSED 004-openspec-specification
============================================================
Validated 4 spec(s)
  ✓ 3 passed
  ✗ 1 failed
  ⚠ 4 warnings
Exit code: 1

# Verbose
openspec validate -v
✓ PASSED 001-dotfiles-core
  No issues found

✗ FAILED 002-dotfiles-caching

  ERROR [line 45] missing_required_section
    Required section missing: ## RFC 2119 Keywords
    Fix: Add the RFC 2119 Keywords section after the Overview

  ERROR [line 78] invalid_requirement_statement
    Requirement missing RFC 2119 keyword (MUST/SHALL/SHOULD/MAY)
    Fix: Add a keyword like MUST or SHOULD to the requirement statement

  WARNING [line 102] incomplete_scenario
    Scenario missing THEN step
    Suggestion: Add a THEN step to complete the Given-When-Then format

✓ PASSED 003-shortcuts-system

  WARNING [line 67] missing_recommended_field
    Recommended metadata field missing: Owner
    Suggestion: Add Owner field to track responsibility

# Strict mode (MUST-only)
openspec validate --strict
✓ PASSED 001-dotfiles-core
✓ PASSED 002-dotfiles-caching (ignoring 3 SHOULD violations)
✓ PASSED 003-shortcuts-system
✓ PASSED 004-openspec-specification
============================================================
Validated 4 spec(s) in STRICT mode
  ✓ All critical requirements met
  ⚠ 3 SHOULD requirements ignored in strict mode

# JSON
openspec validate --json
{
  "summary": {
    "total_specs": 4,
    "passed": 3,
    "failed": 1,
    "errors": 2,
    "warnings": 4,
    "info": 0
  },
  "specs": [
    {
      "id": "001-dotfiles-core",
      "status": "passed",
      "issues": []
    },
    {
      "id": "002-dotfiles-caching",
      "status": "failed",
      "issues": [
        {
          "severity": "error",
          "rule": "missing_required_section",
          "line": 45,
          "message": "Required section missing: ## RFC 2119 Keywords",
          "suggestion": "Add the RFC 2119 Keywords section after the Overview"
        }
      ]
    }
  ]
}
```

---

### 3. `openspec stats` - Show statistics

**Purpose**: Provide quantitative analysis of specifications

**Categories:**
- **Completeness**: Reqs/Scenarios per spec
- **Complexity**: MUST vs SHOULD vs MAY distribution
- **Implementation**: Status distribution
- **Quality**: Individual metrics (not single score)

| Mode | Output | Information Shown |
|------|--------|-------------------|
| **Compact** | Summary | Total specs, reqs, scenarios, avg completeness |
| **Verbose** | Breakdown | + Per-spec details, requirement type distribution, quality metrics |
| **JSON** | Structured | All metrics with drill-down capability |

**Example Outputs:**

```bash
# Compact (default)
openspec stats
╭─────────────────────────────────────────╮
│          OpenSpec Statistics            │
├─────────────────────────────────────────┤
│ Total Specifications:  4                │
│ Total Requirements:    34               │
│ Total Scenarios:       87               │
│                                         │
│ Avg Reqs/Spec:        8.5               │
│ Avg Scenarios/Req:    2.6               │
│                                         │
│ Implementation Status:                  │
│   Implemented:        4 (100%)          │
│   In Progress:        0 (0%)            │
│   Proposed:           0 (0%)            │
╰─────────────────────────────────────────╯

# Verbose
openspec stats -v
╭─────────────────────────────────────────────────────────────────╮
│                   OpenSpec Statistics (Detailed)                │
├─────────────────────────────────────────────────────────────────┤

Summary
─────────────────────────────────────────
  Specifications:       4
  Requirements:        34 (MUST: 28, SHOULD: 5, MAY: 1)
  Scenarios:           87
  Avg Completeness:    97.3%

Per-Spec Breakdown
─────────────────────────────────────────
  001-dotfiles-core
    Requirements:       9 (MUST: 8, SHOULD: 1)
    Scenarios:         27 (3.0 per req)
    Completeness:     100% (all reqs have scenarios)

  002-dotfiles-caching
    Requirements:       4 (MUST: 4)
    Scenarios:         12 (3.0 per req)
    Completeness:     100%

  003-shortcuts-system
    Requirements:       8 (MUST: 6, SHOULD: 2)
    Scenarios:         21 (2.6 per req)
    Completeness:      95% (1 req missing scenario)

  004-openspec-specification
    Requirements:      13 (MUST: 10, SHOULD: 2, MAY: 1)
    Scenarios:         27 (2.1 per req)
    Completeness:      92% (1 req missing scenario)

Quality Metrics (Individual)
─────────────────────────────────────────
  Scenario Coverage:     97.1% (33/34 reqs have scenarios)
  Avg Scenario Depth:    2.6 scenarios per requirement
  MUST Coverage:        100% (all MUST reqs have scenarios)
  SHOULD Coverage:       80% (4/5 SHOULD reqs have scenarios)

Implementation Status
─────────────────────────────────────────
  Implemented:      4 (100%)
  In Progress:      0 (0%)
  Proposed:         0 (0%)
  Deprecated:       0 (0%)

# JSON
openspec stats --json
{
  "summary": {
    "total_specs": 4,
    "total_requirements": 34,
    "total_scenarios": 87,
    "avg_requirements_per_spec": 8.5,
    "avg_scenarios_per_requirement": 2.6
  },
  "requirement_distribution": {
    "MUST": 28,
    "SHOULD": 5,
    "MAY": 1
  },
  "quality_metrics": {
    "scenario_coverage_percent": 97.1,
    "avg_scenario_depth": 2.6,
    "must_coverage_percent": 100.0,
    "should_coverage_percent": 80.0
  },
  "specs": [
    {
      "id": "001-dotfiles-core",
      "requirements": 9,
      "scenarios": 27,
      "requirement_distribution": {
        "MUST": 8,
        "SHOULD": 1,
        "MAY": 0
      },
      "completeness_percent": 100.0
    }
  ]
}
```

---

### 4. `openspec coverage` - Show implementation coverage

**Purpose**: Track traceability from requirements to implementation

**Coverage Types:**
- **ADR**: Architecture Decision Records
- **Test**: Test files and procedures
- **Source**: Implementation files
- **External**: External references

**Validation Levels:**
- **Strict** (`--strict`): Only check coverage for MUST requirements
- **Standard** (default): Check all requirements
- `--fail-on-warning`: Exit 1 if any spec has 0 coverage in any category

**Orphan Detection** (verbose mode): Shows implementation files not referenced by any spec

| Mode | Output | Information Shown |
|------|--------|-------------------|
| **Compact** | Table | Reference counts by type per spec |
| **Verbose** | Detailed | + List all references, show missing coverage, **orphan detection** |
| **JSON** | Structured | Full reference list with metadata + orphans |

**Example Outputs:**

```bash
# Compact (default)
openspec coverage
╭────────────────────────────┬────────┬──────┬───────┬────────┬──────────┬───────╮
│ Spec                       │ Status │ ADRs │ Tests │ Source │ External │ Total │
├────────────────────────────┼────────┼──────┼───────┼────────┼──────────┼───────┤
│ 001-dotfiles-core          │ Impl   │  0   │   0   │   5    │    1     │  14   │
│ 002-dotfiles-caching       │ Impl   │  0   │   0   │   4    │    1     │   9   │
│ 003-shortcuts-system       │ Impl   │  0   │   0   │   1    │    1     │  11   │
│ 004-openspec-specification │ Impl   │  0   │   0   │   3    │    1     │  12   │
╰────────────────────────────┴────────┴──────┴───────┴────────┴──────────┴───────╯

Coverage Summary:
  Specs with ADR references:     0/4 (0%)
  Specs with test references:    0/4 (0%)
  Specs with source references:  4/4 (100%)

Guidance:
  ⚠ No specs have ADR references - consider documenting architectural decisions
  ⚠ No specs have test references - add test coverage links in Metadata section
  ✓ All specs have source references - good implementation traceability

# Verbose (with orphan detection)
openspec coverage -v
╭────────────────────────────┬────────┬──────┬───────┬────────┬──────────┬───────╮
│ Spec                       │ Status │ ADRs │ Tests │ Source │ External │ Total │
├────────────────────────────┼────────┼──────┼───────┼────────┼──────────┼───────┤
│ 001-dotfiles-core          │ Impl   │  0   │   0   │   5    │    1     │  14   │
│ 002-dotfiles-caching       │ Impl   │  0   │   0   │   4    │    1     │   9   │
│ 003-shortcuts-system       │ Impl   │  0   │   0   │   1    │    1     │  11   │
│ 004-openspec-specification │ Impl   │  0   │   0   │   3    │    1     │  12   │
╰────────────────────────────┴────────┴──────┴───────┴────────┴──────────┴───────╯

Detailed Coverage - 001-dotfiles-core (9 requirements):
─────────────────────────────────────────────────────────
Source Files (5):
  ✓ script/bootstrap - Bootstrap process implementation
  ✓ local/bin/dot - Package management, status, cache control
  ✓ homebrew/brew_install.sh - Homebrew installation
  ✓ bash/bash_profile.symlink - Shell environment loading
  ✓ bash/bashrc.symlink - Shell aliases and completion

Cross-References (9):
  → .openspec/specs/002-dotfiles-caching/spec.md
  → .openspec/specs/003-shortcuts-system/spec.md
  → README.md
  → docs/xdg_setup.md
  → docs/coloring.md

External References (1):
  → https://specifications.freedesktop.org/basedir-spec/latest/

Coverage Analysis:
  ✓ All 9 MUST requirements have source references
  ✗ 0 requirements have test references
  ✗ 0 requirements have ADR references

Missing Coverage:
  ⚠ No test procedures linked (consider adding tests/ references)
  ⚠ No ADRs linked (consider documenting design decisions)

Orphan Files Detected (not referenced by any spec):
  ⚠ script/old_bootstrap.sh - No spec references this file
  ⚠ local/bin/deprecated_tool - No spec references this file

Suggestion: Either document these in a spec or remove if obsolete

Guidance:
  Add test references in Metadata section:
    - [Unit Tests](tests/unit/test_bootstrap.py)
    - [Integration Tests](tests/integration/test_dotfiles.py)

  Add ADR references for architectural decisions:
    - [ADR-001: Topic-Based Organization](docs/adr/001-topic-organization.md)

# Strict mode (MUST-only coverage)
openspec coverage --strict
╭────────────────────────────┬────────┬──────┬───────┬────────┬──────────┬───────╮
│ Spec                       │ Status │ ADRs │ Tests │ Source │ External │ Total │
├────────────────────────────┼────────┼──────┼───────┼────────┼──────────┼───────┤
│ 001-dotfiles-core          │ Impl   │  0   │   0   │   5    │    1     │  14   │
╰────────────────────────────┴────────┴──────┴───────┴────────┴──────────┴───────╯

STRICT MODE: Only checking MUST requirements (28/34 total)
  ✓ All 28 MUST requirements have source references (100%)
  ⚠ 5 SHOULD requirements ignored in strict mode

# JSON
openspec coverage --json
{
  "summary": {
    "total_specs": 4,
    "specs_with_adr": 0,
    "specs_with_tests": 0,
    "specs_with_source": 4,
    "adr_percent": 0,
    "test_percent": 0,
    "source_percent": 100
  },
  "specs": [
    {
      "id": "001-dotfiles-core",
      "status": "Implemented",
      "requirements": 9,
      "references": {
        "adr": 0,
        "test": 0,
        "source": 5,
        "external": 1,
        "internal": 8,
        "total": 14
      },
      "source_files": [
        "script/bootstrap",
        "local/bin/dot",
        "homebrew/brew_install.sh",
        "bash/bash_profile.symlink",
        "bash/bashrc.symlink"
      ],
      "coverage_analysis": {
        "must_requirements_with_source": 9,
        "should_requirements_with_source": 0,
        "uncovered_requirements": []
      }
    }
  ],
  "orphan_files": [
    "script/old_bootstrap.sh",
    "local/bin/deprecated_tool"
  ],
  "guidance": {
    "warnings": [
      "No specs have ADR references - consider documenting architectural decisions",
      "No specs have test references - add test coverage links in Metadata section",
      "2 orphan files detected - not referenced by any spec"
    ],
    "successes": [
      "All specs have source references - good implementation traceability"
    ]
  }
}
```

---

## Flag Behavior Matrix

| Flag | list | validate | stats | coverage |
|------|------|----------|-------|----------|
| `-v` / `--verbose` | ✓ | ✓ | ✓ | ✓ |
| `--json` | ✓ | ✓ | ✓ | ✓ |
| `--strict` | - | ✓ | - | ✓ |
| `--fail-on-warning` | - | ✓ | - | ✓ |
| `--project-folder` | ✓ | ✓ | ✓ | ✓ |
| `--dir` | ✓ | ✓ | ✓ | ✓ |

---

## Exit Codes

| Code | Meaning | When |
|------|---------|------|
| **0** | Success | All checks passed |
| **1** | Failure | Validation errors OR --fail-on-warning triggered |
| **2** | Invalid usage | Bad arguments, missing files |

---

## Validation Rules by Level

### Strict Mode (`--strict`)

**Required Metadata:**
- Domain (MUST)
- Version (MUST)
- Status (MUST)
- Date (MUST)

**NOT Required:**
- Metadata section (optional for traceability)
- Owner (recommended but not required)

**Required Sections:**
- Overview (MUST)
- RFC 2119 Keywords (MUST)
- Requirements (MUST with at least 1 requirement)

**Requirement Checks:**
- MUST have RFC 2119 keyword (MUST/SHALL only)
- MUST have at least one scenario
- Scenarios MUST be complete (GIVEN/WHEN/THEN)

### Standard Mode (default)

**Required Metadata:**
- Domain (MUST)
- Version (MUST)
- Status (MUST)
- Date (MUST)

**Recommended Metadata** (warnings):
- Owner (SHOULD)

**Required Sections:**
- Overview (MUST)
- RFC 2119 Keywords (MUST)
- Requirements (MUST)

**Recommended Sections** (warnings):
- Current Implementation (SHOULD)
- Testing Requirements (SHOULD)
- Dependencies (SHOULD)
- Metadata (SHOULD for traceability)

**Requirement Checks:**
- MUST have RFC 2119 keyword (MUST/SHALL/SHOULD/MAY)
- SHOULD have at least one scenario (warning if missing)
- Scenarios SHOULD be complete (info if missing steps)

### Lenient Mode

**Required Metadata:**
- Domain (MUST)
- Status (MUST)

**Required Sections:**
- Overview (MUST)
- Requirements (MUST with at least 1 requirement)

**Requirement Checks:**
- SHOULD have RFC 2119 keyword (info if missing)
- MAY have scenarios (no check)

---

## Guidance System

Each command provides actionable guidance:

### validate
- "Add RFC 2119 Keywords section after Overview"
- "Use MUST/SHALL/SHOULD/MAY in requirement statements"
- "Add THEN step to complete Given-When-Then format"

### stats
- "Spec X has 0 scenarios - consider adding test scenarios"
- "Only 60% MUST coverage - add scenarios for MUST requirements"
- "Average 1.2 scenarios per requirement - consider adding more edge cases"

### coverage
- "Add test references in Metadata section"
- "No ADRs linked - document architectural decisions"
- "Orphan file detected: tests/old_test.py not referenced by any spec"
- "2 orphan files found - review for removal or documentation"

---

## Implementation Priority

1. **Phase 1**: Compact/Verbose/JSON modes for all commands
2. **Phase 2**: Validation levels (strict/standard/lenient)
3. **Phase 3**: Guidance system with actionable suggestions
4. **Phase 4**: Fail-on-warning behavior
5. **Phase 5**: Completeness metrics (reqs/scenarios per spec)
6. **Phase 6**: Orphan detection in coverage

---

**License:** Apache-2.0
**Copyright:** 2026 Ilja Heitlager
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
