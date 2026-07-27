---
description: Review changed code for simplification opportunities and apply improvements while preserving all functionality.
---
Review changed code for simplification opportunities and apply improvements while preserving all functionality.

## Usage

```
/simplify              Simplify recently changed code (git diff HEAD)
/simplify <file>       Simplify a specific file
/simplify <file:line>  Focus on a specific section
```

## Process

### Step 1 — Identify scope

Without arguments: read `git diff HEAD` to find recently modified files and focus on those hunks.
With a file argument: read the specified file and focus on the full contents.

### Step 2 — Analyze for simplification

Scan the target code for these issues (in priority order):

**Complexity**
- Unnecessary nesting (deeply nested if/else, loops)
- Redundant abstractions (helper that wraps a single built-in)
- Over-engineered patterns for a single use case (Strategy, Factory, etc. with one implementation)
- Repeated code that could be a simple loop or list comprehension

**Clarity**
- Confusing variable or function names that need a comment to explain
- Nested ternary operators — prefer if/else chains or match statements
- Boolean logic that can be simplified
- Dead code, unused variables, or commented-out blocks

**Consistency**
- Code style that deviates from the rest of the file
- Import ordering (isort rules)
- Missing or inconsistent type hints on modified functions

**Redundancy**
- Comments that just describe what the code literally does
- Intermediate variables that are used exactly once and add no clarity
- Unnecessary `else` after a `return`

### Step 3 — Present findings

Before making any changes, show a concise plan:

```
Simplify Plan
═════════════

Target: src/foo.py (lines 45-80, recently modified)

Opportunities found:

1. [complexity] line 52 — nested if/else 4 levels deep
   → Extract inner logic to helper `_resolve_target()`

2. [clarity] line 61 — nested ternary (a if x else b if y else c)
   → Replace with if/else chain

3. [redundancy] line 70 — comment "increment counter by 1" above `count += 1`
   → Remove obvious comment

4. [consistency] lines 45, 58 — missing return type annotations (other functions have them)
   → Add `-> None` and `-> str`

Skipping:
- line 55: intermediate variable `result` used once but aids debugging readability

Proceed? (go / revise / skip N)
```

Wait for user approval before applying changes.

### Step 4 — Apply changes

For each approved item:
- Make the change surgically — touch only what was identified
- Do not reformat surrounding untouched code
- Do not add type hints, comments, or docstrings to unchanged functions

### Step 5 — Verify

After all changes:

```bash
# Python projects
uv run ruff check src/         # lint
uv run pyright src/            # types (only if project uses pyright)
uv run pytest tests/ -x --tb=short  # tests
```

Use `make lint` / `make test` if a Makefile target exists. If tests fail, revert the change that broke them.

### Step 6 — Report

```
Simplified N items in <file>
  - 2 complexity: reduced nesting
  - 1 clarity: replaced nested ternary
  - 1 redundancy: removed obvious comment

Tests: ✓  Lint: ✓  Types: ✓
```

## Principles

**Never** change what code does — only *how* it does it.

**Never** simplify in ways that hurt readability:
- Don't collapse 5 clear lines into one clever expression
- Don't remove meaningful intermediate variables
- Don't combine unrelated concerns to save lines
- Don't delete abstractions that exist for testing or extension

**Scope**: Only touch recently modified code unless the user explicitly asks for broader cleanup.
