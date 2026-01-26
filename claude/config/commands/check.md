Run code quality checks (linting, type checking, formatting) and interpret results.

## Usage

```
/check                Run all checks
/check lint           Run linter only (ruff)
/check types          Run type checker only (mypy)
/check format         Check formatting (ruff format --check)
/check <file>         Check specific file or directory
```

## Agent Strategy

This skill can run autonomously via a Bash agent, making it suitable for background execution or quick status checks.

```
┌─────────────────────────────────────────────────────────────┐
│  /check                                                     │
│                                                             │
│  Option A: Quick (foreground)                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Run checks directly in main conversation            │   │
│  │ Best for: Quick feedback during development         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Option B: Thorough (background agent)                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Bash Agent (background)                             │   │
│  │                                                     │   │
│  │ - Run all linters                                   │   │
│  │ - Run type checker                                  │   │
│  │ - Check formatting                                  │   │
│  │ - Run tests                                         │   │
│  │ - Compile report                                    │   │
│  └──────────────────────┬──────────────────────────────┘   │
│                         │                                   │
│                         ▼                                   │
│  Notify when complete, offer fixes                          │
└─────────────────────────────────────────────────────────────┘
```

## Process

### Quick Mode (default)

Run checks directly and report results:

```bash
# Detect project type and run appropriate checks
uv run ruff check src/ tests/ && \
uv run mypy src/ && \
uv run ruff format --check src/ tests/
```

### Thorough Mode (background)

For comprehensive checks, spawn a background Bash agent:

```
Task tool:
  subagent_type: Bash
  run_in_background: true
  prompt: |
    Run comprehensive code quality checks for this project.

    1. Detect project type (Python/Node/Rust) from config files
    2. Run linting:
       - Python: uv run ruff check src/ tests/ (or ruff if no uv)
       - Node: npm run lint (if available)
    3. Run type checking:
       - Python: uv run mypy src/
       - TypeScript: npx tsc --noEmit
    4. Check formatting:
       - Python: uv run ruff format --check src/ tests/
       - Node: npm run format:check (if available)
    5. Run tests (optional, if quick):
       - Python: uv run pytest tests/ -x --tb=short
       - Node: npm test

    Compile results into a structured report:
    - Total issues by severity
    - Auto-fixable count
    - Files affected
    - Suggested fix commands

    If Makefile exists with lint/check targets, prefer those.
```

Continue working while checks run. Read results when notified.

## Project Type Detection

Look for configuration files:

```bash
# Python
ls pyproject.toml setup.py requirements.txt 2>/dev/null

# Node/TypeScript
ls package.json tsconfig.json 2>/dev/null

# Rust
ls Cargo.toml 2>/dev/null
```

## Check Commands by Project Type

### Python (with uv)

```bash
# Linting
uv run ruff check src/ tests/

# Type checking
uv run mypy src/

# Format check
uv run ruff format --check src/ tests/

# Import sorting
uv run ruff check --select I src/ tests/
```

### Python (without uv)

```bash
ruff check src/ tests/
mypy src/
ruff format --check src/ tests/
```

### Makefile Projects

```bash
make lint    # Often combines multiple checks
make check   # Alternative name
make test    # Include test run
```

## Interpreting Results

### Ruff Output

```
src/api.py:42:5: E501 Line too long (89 > 88)
src/api.py:45:1: F401 'os' imported but unused
src/models.py:12:5: B006 Do not use mutable data structures for argument defaults
```

**Severity mapping:**
- `E` — Style errors (usually auto-fixable)
- `F` — Pyflakes errors (unused imports, undefined names)
- `B` — Bugbear (likely bugs, code smells)
- `I` — Import sorting issues
- `W` — Warnings

### Mypy Output

```
src/api.py:42: error: Argument 1 to "process" has incompatible type "str"; expected "int"
src/models.py:15: error: "User" has no attribute "full_name"
```

**Common issues:**
- Type mismatches — Check function signatures
- Missing attributes — Typo or wrong type
- Optional access — Need `if x is not None` check
- Import errors — Missing type stubs

## Output Format

```
Code Quality Check
═══════════════════════════════════════════════════════════════

Linting (ruff)
────────────────────────────────────────────────────────────────
✗ 5 issues found

  Errors (2):
    src/api.py:45    F401  Unused import 'os'
    src/models.py:12 B006  Mutable default argument

  Warnings (3):
    src/api.py:42    E501  Line too long
    src/api.py:50    E501  Line too long
    src/utils.py:8   W291  Trailing whitespace

  Auto-fixable: 4/5
  Run: uv run ruff check --fix src/

Type Checking (mypy)
────────────────────────────────────────────────────────────────
✗ 2 errors found

  src/api.py:42     Incompatible type "str"; expected "int"
  src/models.py:15  "User" has no attribute "full_name"

Formatting
────────────────────────────────────────────────────────────────
✗ 3 files would be reformatted

  src/api.py
  src/models.py
  src/utils.py

  Run: uv run ruff format src/

Summary
────────────────────────────────────────────────────────────────
Status: FAILED

Quick fixes:
  uv run ruff check --fix src/    # Fix lint issues
  uv run ruff format src/         # Fix formatting

Manual fixes needed:
  - src/api.py:42 — Fix type mismatch
  - src/models.py:15 — Check attribute name
```

## Auto-Fix Actions

After showing results, offer to fix automatically:

**If auto-fixable issues exist:**
```bash
uv run ruff check --fix src/
uv run ruff format src/
```

**If type errors need manual fixes:**
> "2 type errors need manual fixes. Want me to help fix them?"

Use the refactor-helper agent for complex type fixes:
```
Task tool:
  subagent_type: refactor-helper
  prompt: |
    Fix these type errors:
    - src/api.py:42 — Incompatible type "str"; expected "int"
    - src/models.py:15 — "User" has no attribute "full_name"

    Investigate each error and suggest minimal fixes.
```

## Configuration Detection

Check for existing config:
- `pyproject.toml` — `[tool.ruff]`, `[tool.mypy]`
- `ruff.toml` — Ruff-specific config
- `mypy.ini` — Mypy-specific config
- `.flake8` — Legacy (suggest migration)

Report if no config found:
> "No ruff config found. Consider adding `[tool.ruff]` to pyproject.toml for consistent settings."

## Pre-commit Integration

If `.pre-commit-config.yaml` exists:
```bash
# Run all pre-commit hooks
pre-commit run --all-files
```

This may include additional checks beyond the standard linters.

## Workflow Integration

Use `/check` at key moments:
- Before `/commit` — Ensure clean code
- After `/take` implementation — Verify quality
- During `/review` — Part of code quality scan
- Before `/pr` — Final quality gate
