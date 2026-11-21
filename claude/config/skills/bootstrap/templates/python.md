# <project> — agent instructions

<one-line purpose>

## Project

<!-- TODO: architecture boundaries, invariants, what must never happen. Link ADRs. -->

## Commands

Everything through `uv`; never bare `python` or `pytest`.

| Task | Command |
|---|---|
| All CI gates | `make check` |
| Tests | `uv run pytest` (coverage target > 80%) |
| Lint | `uv run ruff check` |
| Format | `uv run ruff format` (imports sorted by ruff's `I` rules) |
| Types | `uv run pyright` |

Run `make check` before declaring work done.

## Code

- Python 3.12+: modern type hints (`list[str]`, `X | None`), no `typing.List`.
- Layout: `src/<package>/`, tests in `tests/unit/` and `tests/integration/`.
- Type hints on all public functions. No bare `except:`; don't swallow errors silently.
- Dependencies via `uv add`; commit `uv.lock` only when dependencies changed (a lock re-resolved against a local proxy is noise).

## Tests

- pytest, fixtures over setup methods, one behavior per test.
- A bug fix starts with a failing test.

## Specs and decisions

- ADRs in `.openspec/adr/NNNN-title.md`; check them before an architectural change, add one when you make one.
- Specs in `.openspec/specs/NNN-name/spec.md`, requirements as `### Requirement N: Title [MUST|SHOULD|MAY]` with `**Implementation:**` and `**Tests:**` links. `make assurance` validates spec coverage.

## Releases

- A version bump is **one commit**: `pyproject.toml` version, `src/<package>/__init__.py::__version__`, `CHANGELOG.md` entry, and `uv.lock`. Then tag that commit.
- After any bump tool, run `git status` and grep the old version string repo-wide before committing.
- `feat/` → minor, `fix/` → patch, others no bump.
- Don't write markdown docs nobody asked for; update existing ones when behavior changes.
