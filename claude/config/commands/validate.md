Validate codebase health: link checking, drift detection, gap analysis, test cleanup, and conformance scoring.

An open inspection of all artifacts — specs, code, tests, ADRs — run any time, independent of PRs or branches. The static tools produce findings; /validate interprets them.

## Usage

```
/validate                  Full codebase validation
/validate src/auth/        Validate specific component or directory
/validate --quick          Fast pass/fail: tests, lint, link existence only
/validate --scope specs    Focus on spec↔code traceability only
/validate --scope tests    Focus on test coverage and cleanup only
/validate --scope drift    Focus on ADR drift detection only
```

## Agent Strategy

Parallel agents scan the codebase; the main conversation interprets and scores.

```
┌─────────────────────────────────────────────────────────────┐
│  /validate                                                   │
│                                                             │
│  0. Detect project structure and scope                      │
│                    │                                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Explore     │  │ Explore     │  │ general-    │         │
│  │ Agent       │  │ Agent       │  │ purpose     │         │
│  │             │  │             │  │ Agent       │         │
│  │ Link check  │  │ Drift &     │  │ Test &      │         │
│  │ Traceability│  │ Gap analysis│  │ Static      │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                 │
│         └────────────┬───┴────────────────┘                 │
│                      ▼                                      │
│              Interpret & Score                              │
│              (main conversation)                            │
│                      │                                      │
│                      ▼                                      │
│              Validation Report                              │
│              + Named Gaps                                   │
│                      │                                      │
│                      ▼                                      │
│              Offer remediation actions                      │
└─────────────────────────────────────────────────────────────┘
```

## Process

### 0. Detect Project Structure

Before spawning agents, understand what's available:

```bash
# What artifact types exist?
ls .openspec/specs/ 2>/dev/null    # OpenSpec specifications
ls .openspec/adr/ 2>/dev/null      # Architectural Decision Records
ls tests/ 2>/dev/null              # Test suite
ls src/ 2>/dev/null                # Source code
ls pyproject.toml Makefile 2>/dev/null  # Build config
```

Adapt the validation to what the project actually has. A project with no OpenSpec
skips spec traceability. A project with no ADRs skips drift detection. Report what
was checked and what was skipped.

If a scope argument is provided (path or `--scope`), narrow all agents to that scope.

### 1. Spawn Agents (parallel)

Launch three agents in parallel:

**Agent 1: Link Check & Traceability**
```
Task tool:
  subagent_type: Explore
  prompt: |
    Verify traceability links across the codebase.
    Scope: <full project or narrowed path>

    Check these traceability edges:

    1. Spec → Code: For each OpenSpec in .openspec/specs/:
       - Find `Implementation:` references — do the referenced files exist?
       - Are there specs with no implementation references at all?

    2. Spec → Test: For each scenario (GIVEN-WHEN-THEN) in the specs:
       - Find `Tests:` references — do the referenced test files/functions exist?
       - Are there scenarios without test references?

    3. Code → ADR: For source files that reference ADRs (in comments, docstrings):
       - Do the referenced ADRs exist in .openspec/adr/?
       - Are the ADR references still relevant (ADR not superseded)?

    4. Test → Code: For test files:
       - Does every test file correspond to a source module?
       - Are there test files testing code that no longer exists?

    Report:
    - VALID links (confirmed both ends exist)
    - BROKEN links (reference target missing or moved)
    - ORPHANED artifacts (code/tests with no spec link)
    - MISSING links (specs with no implementation reference)
    - Total link count and validity percentage
```

**Agent 2: Drift Detection & Gap Analysis**
```
Task tool:
  subagent_type: Explore
  prompt: |
    Analyze architectural drift and specification gaps across the codebase.
    Scope: <full project or narrowed path>

    Drift detection:
    1. Read all ADRs in .openspec/adr/
    2. For each ADR that prescribes patterns (e.g., "use repository pattern",
       "all endpoints must authenticate"), check if the codebase follows them
    3. Look for deprecated patterns flagged in ADRs appearing in current code
    4. Check if actual dependencies conflict with architectural constraints

    Gap analysis:
    5. What is specified in OpenSpec but NOT tested?
       (scenarios without corresponding test assertions)
    6. What is tested but NOT specified?
       (test files covering code with no spec reference)
    7. Are there source modules with no spec and no tests? (dark zones)
    8. Are there safety/security properties implied by specs but with no evidence?

    Report each finding with:
    - Category: DRIFT | SPEC_GAP | TEST_GAP | DARK_ZONE | SECURITY_GAP
    - Severity: critical | warning | info
    - File and line reference
    - Description
    - Suggested remediation
```

**Agent 3: Test Analysis & Static Checks**
```
Task tool:
  subagent_type: general-purpose
  prompt: |
    Run test analysis and static checks across the codebase.
    Scope: <full project or narrowed path>

    1. Run tests and collect results:
       - If Makefile exists with test target: make test
       - Else Python: uv run pytest tests/ -x --tb=short -q
       - Else Node: npm test
       Report: pass/fail count, any failures with details

    2. Run coverage (if available):
       - Python: uv run pytest --cov=src/ --cov-report=term-missing -q
       - Report overall coverage and uncovered modules

    3. Run linting and type checks:
       - Python: uv run ruff check src/ tests/ && uv run mypy src/
       - Node: npx eslint src/ && npx tsc --noEmit
       Report: issues by severity

    4. Identify test quality issues:
       - Tests with TODO/FIXME markers
       - Overly broad assertions (assert True, expect(true))
       - Empty test bodies or skipped tests
       - Temporary fixtures or helpers that should be cleaned up
       - Duplicate or near-duplicate test cases

    5. If mutation testing is available (mutmut, stryker):
       - Run and report mutation score

    Output a structured summary of all findings.
```

### 2. Interpret & Score (main conversation)

Once agents return, synthesize findings into a conformance assessment.

**Scoring dimensions:**

| Dimension | Weight | Source | Metric |
|-----------|--------|--------|--------|
| Spec coverage | 30% | Agent 1 | % of spec requirements with valid implementation links |
| Test coverage | 30% | Agent 3 | % of scenarios with passing tests |
| Traceability | 20% | Agent 1 | % of links that are valid (not broken/orphaned) |
| Conformance | 20% | Agent 2+3 | Inverse of drift findings + static check issues |

**Conformance score** = weighted sum across dimensions (0-100%)

**AAE level mapping:**
- 90-100%: AAE-4 (Assured) — full traceability, all scenarios tested, no drift
- 70-89%: AAE-3 (Verified) — most scenarios tested, minor gaps named
- 50-69%: AAE-2 (Checked) — tests pass, some traceability gaps
- 0-49%: AAE-1 (Generated) — code exists but assurance is thin

Dimensions that could not be evaluated (e.g., no specs exist) are excluded from
the weighted score and noted as "not assessed."

### 3. Present Validation Report

```
Validation Report                           <project-name>
═══════════════════════════════════════════════════════════════

Scope: full project (src/, tests/, .openspec/)

Traceability
────────────────────────────────────────────────────────────────
✓ 14 valid spec→code links
✗ 2 broken links:
    spec/auth.md → src/auth/legacy.py (file deleted)
    spec/api.md → src/api/v1.py (file renamed to v2.py)
✗ 3 orphaned tests (no spec reference):
    tests/test_helpers.py
    tests/test_utils.py
    tests/conftest.py
  18 scenarios found, 15 with test references

Drift Detection
────────────────────────────────────────────────────────────────
✓ 8 ADRs checked
⚠ ADR-0012 prescribes repository pattern — direct DB access found
  in src/auth/oauth.py:45 and src/billing/charge.py:23
✗ ADR-0005 deprecated OldCache — still used in src/cache/warm.py:12

Test Analysis
────────────────────────────────────────────────────────────────
✓ 87 tests pass, 0 fail
✓ Coverage: 82% overall
⚠ 3 scenarios without test coverage:
    "Token expires during network outage" (spec/auth.md:34)
    "Admin revokes app access" (spec/auth.md:56)
    "Rate limit exceeded on batch endpoint" (spec/api.md:89)
⚠ Test cleanup needed:
    tests/test_oauth.py:12 — TODO: add edge case tests
    tests/test_billing.py:45 — @pytest.mark.skip("WIP")

Static Checks
────────────────────────────────────────────────────────────────
✓ Linting: 2 minor issues
✓ Types: clean
  src/auth/oauth.py:78 — B006 mutable default argument
  src/api/routes.py:120 — E501 line too long

Gap Analysis
────────────────────────────────────────────────────────────────
Dark zones (no spec, no tests):
    src/utils/retry.py
    src/migrations/

Named gaps:
  1. [warning] 3 scenarios untested
  2. [warning] 2 ADR drift violations
  3. [info] 2 broken traceability links (likely from refactoring)
  4. [info] Token refresh error path not specified in OpenSpec
  5. [info] No security properties documented for OAuth state param

Conformance Score
────────────────────────────────────────────────────────────────
  Spec coverage:   87% (14/16 requirements linked)     × 0.30 = 0.26
  Test coverage:   83% (15/18 scenarios tested)         × 0.30 = 0.25
  Traceability:    82% (14/17 links valid)              × 0.20 = 0.16
  Conformance:     75% (2 drift, 2 lint issues)         × 0.20 = 0.15

  Overall: 82% — AAE-3 (Verified)

Remediation Items
────────────────────────────────────────────────────────────────
Priority  Item                                          Action
high      Fix 2 ADR drift violations                    Refactor to match ADRs
high      Remove deprecated OldCache usage              Replace per ADR-0005
medium    Add tests for 3 uncovered scenarios           Write tests
medium    Fix 2 broken spec→code links                  Update spec references
low       Clean up test scaffolding (TODO, skip)        Remove or implement
low       Cover dark zones (retry.py, migrations/)      Add specs or tests
low       Fix 2 lint issues                             Quick fix
```

### 4. Offer Actions (Interactive)

After presenting the report, suggest next steps:

- **Fix items directly** — "Want me to fix the broken spec links?"
- **Create issues** — "Create GitHub issues for the remediation items?"
- **Focus on critical items** — "Should I address the ADR drift first?"
- **Re-validate after fixes** — `/validate --quick` to confirm improvements
- **Accept current state** — named gaps become funded technical debt

## Quick Mode

With `--quick`, skip deep analysis agents and run deterministic checks only:

```bash
# Tests pass?
uv run pytest tests/ -x --tb=short -q || make test

# Linting clean?
uv run ruff check src/ tests/

# Types clean?
uv run mypy src/

# Spec links exist? (quick file existence check)
grep -r "Implementation:" .openspec/specs/ 2>/dev/null | while read line; do
  FILE=$(echo "$line" | grep -oP '`[^`]+`' | tr -d '`')
  [ -f "$FILE" ] && echo "✓ $FILE" || echo "✗ $FILE (missing)"
done
```

Quick mode produces a simplified pass/fail without scoring:

```
Quick Validation                            <project-name>
═══════════════════════════════════════════════════════════════
✓ Tests: 87 pass, 0 fail
✓ Lint: clean
✗ Types: 1 error (src/api/routes.py:45)
✓ Spec links: 14/16 valid (2 broken)

Status: ISSUES FOUND — run /validate for full report
```

## Scoped Mode

With `--scope`, run only one validation dimension:

| Scope | What runs | Use when |
|-------|-----------|----------|
| `specs` | Agent 1 only (link check, traceability) | After refactoring, to catch broken refs |
| `tests` | Agent 3 only (test analysis, coverage, cleanup) | Before release, to assess test health |
| `drift` | Agent 2 only (ADR drift, gap analysis) | After ADR changes, to find violations |

## Integration with /ca-assurance

If the `code-analyzer` MCP server is available, /validate enriches its analysis:

- Use Cypher queries to verify traceability edges in the parsed graph
- Compute scenario coverage from `TESTED_BY` edges
- Check `IMPLEMENTED_BY` edges against `:Module` nodes (not ghost references)
- Incorporate the ADR-0019 convergence assurance score

When MCP is available, the conformance score uses graph-native data instead of
file scanning — more reliable and deterministic. Agent 1 (link check) is largely
replaced by Cypher queries in this mode.

## Philosophy

/validate is an **interpretation engine**, not a pass/fail gate. The static tools
produce data; /validate produces understanding.

A conformance score of 82% is not just a number. It means: "most scenarios are
tested, traceability is strong, but three edge cases lack evidence and two
architectural patterns are drifting." The human reads this and decides what to
do about it.

Named gaps are not failures — they are **funded risks**. A gap you know about
can be accepted, deferred, or fixed. A gap you don't know about becomes an incident.

/validate differs from /review: review checks **alignment** within a PR (do spec,
code, and tests agree?). Validate checks **completeness** across the codebase
(is anything missing? has anything drifted?). These are different epistemic
questions. /validate can be run at any time — after a merge, before a release,
during a refactor, or just to understand the health of the codebase.
