---
description: Help fix an error or problem.
---
Help fix an error or problem.

In the workflow `/review → /pr → /fix → /merge`, this step addresses review findings with a plan-first approach.

## Usage

```
/fix                   Address review findings on current PR (plan-first)
/fix <error>           Analyze and suggest fix for a specific error
ai --fix "error msg"   Same, one-shot
```

## Examples

```
/fix                                                    # Address PR review findings
/fix "ModuleNotFoundError: No module named 'foo'"       # Quick error fix
ai --fix "permission denied"
some_cmd 2>&1 | ai --fix
```

## Process

### Mode 1: PR Review Findings (no argument, or after `/review`)

**Step 1 — Gather findings**

Read the PR review comment (or use findings from the current conversation). List all critical, warning, and suggestion items.

**Step 2 — Present fix plan (MANDATORY — do not skip)**

Before touching any code, present a plan:

```
Fix Plan for PR #N
══════════════════

Findings to address (N items):

1. [critical] src/engine.py:78 — missing null check
   → Add guard: `if depot is None: return`

2. [warning] src/metrics.py:265 — wrong denominator
   → Change to `sim_days * capacity_trains_per_day`

3. [suggestion] src/geo.py:34 — unused parameter
   → SKIP — intentional, documented in docstring

Skipping (with reason):
- Item 3: deliberate design choice, documented

Proceed? (go / revise / skip items)
```

**Wait for user approval.** Do not implement until the user says "go" or equivalent.

**Step 3 — Implement fixes**

Apply approved fixes. For each:
- Make the change
- Run relevant tests
- Stage the file

**Step 4 — Verify**

After all fixes applied:

```bash
# Run full quality check
uv run ruff check src/        # lint
uv run pyright src/            # types
uv run pytest tests/ -x --tb=short  # tests
```

If anything fails, fix it before reporting done.

**Step 5 — Report**

```
✓ Fixed N of M review findings
  - 2 critical: fixed
  - 1 warning: fixed
  - 1 suggestion: skipped (documented reason)

Tests: ✓ all passing
Types: ✓ clean
Lint:  ✓ clean

Next: commit and push, then /merge
```

### Mode 2: Specific Error (with argument)

For quick error fixes, be concise and actionable:

- **Problem**: What went wrong (one line)
- **Fix**: The command or code to fix it
- **Why**: Brief explanation (optional)

## Anti-patterns

- ❌ Jumping straight to code without showing the plan
- ❌ Fixing suggestions that are intentional design choices
- ❌ Skipping the verify step (lint/types/tests)
- ❌ Fixing things not in the review findings (scope creep)
- ❌ Presenting a plan with 20+ items — batch into groups of 5-7, fix iteratively
