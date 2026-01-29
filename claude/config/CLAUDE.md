# Claude Code Instructions

Global coding preferences and workflow guidelines for all my projects.

---

## Code Quality Standards

- **Python Version**: 3.12+ (use modern type hints and syntax)
- **Linter**: `ruff` — Fast Python linter
- **Type Checking**: `mypy` — Static type analysis
- **Imports**: `isort` — Import sorting and organization
- **Testing**: pytest with coverage targets (aim for >80%)
- **Package Manager**: `uv` — Fast Python package manager

---

## Project Structure Conventions

### Standard Layout

```
project/
├── src/project_name/    # Main source code
│   ├── __init__.py
│   ├── core/            # Core models and types
│   ├── cli/             # Command-line interface
│   └── ...
├── tests/               # Test suite
│   ├── unit/            # Unit tests
│   └── integration/     # Integration tests
├── docs/                # Documentation
│   ├── adr/             # Architectural Decision Records
│   └── ...
├── pyproject.toml       # Project configuration
├── Makefile             # Common tasks
├── README.md
└── CHANGELOG.md
```

### Architectural Decision Records (ADRs)

I use ADRs to document significant design decisions:
- Store in `docs/adr/` with format `NNNN-title.md`
- Always check existing ADRs before proposing architectural changes
- Create new ADRs for decisions that affect architecture

---

## Claude Code Workflow Preferences

### Planning and Execution
- Plan complex tasks and explore the codebase thoughtfully
- Read files before modifying them
- Use TodoWrite to track progress on multi-step work
- Think through architectural decisions carefully

### Bash and Git Usage
- **Use Bash commands freely** for tests, builds, dependency installation, git status checks, etc.
- **Use Git operations freely** (commits, pushing, creating branches, rebasing) as natural parts of the workflow
- No need to ask permission for Bash or git actions
- Be cautious with destructive git operations (no force pushes or hard resets unless explicitly requested)

### GitHub Comment Attribution

When posting comments to GitHub issues or PRs using `gh issue comment` or `gh pr comment`, **always end the comment with an attribution signature**:

```
---
🤖 *Analysis by Claude*
```

This ensures comments posted through your account are clearly identified as AI-generated analysis.

### Feature Development Workflow

#### Starting a New Feature
1. **Create a branch** following branch naming conventions
2. **Create a plan** if complex — document approach before implementation

#### Finalizing a Feature
1. **Ensure tests pass** — all tests running locally
2. **Consider ADR** — determine if architectural decisions need documentation
3. **Update documentation** — review existing docs for relevance
4. **Commit changes** — create meaningful, semantic commits
5. **Squash if needed** — clean up commit history before PR
6. **File a pull request** — include summary and test plan

---

## Tool Usage Guidelines

### Use `uv` for Python Projects

For Python projects using `uv` for dependency management:

```bash
# ✅ DO THIS
uv run pytest tests/
uv run python script.py
uv run ruff check src/
uv run mypy src/

# ❌ AVOID THIS (unless project doesn't use uv)
pytest tests/
python script.py
```

Why? `uv` ensures correct virtual environment and dependency isolation.

Check `Makefile` for convenient shortcuts: `make test`, `make lint`, `make format`, etc.

### Markdown Generation Policy

**STRICT: Never generate markdown documentation files unless explicitly requested**.

**What NOT to do:**
- ❌ Do NOT create `.md` summary/overview documents
- ❌ Do NOT create `.md` files to explain code changes
- ❌ Do NOT create `.md` architecture overviews
- ❌ Do NOT auto-generate documentation files

**What TO do:**
- ✅ Use inline code comments for complex logic
- ✅ Reference existing documentation
- ✅ Generate markdown ONLY when explicitly asked: "Create a README", "Document this", "Write an ADR"
- ✅ Update existing markdown files when specifically requested

---

## Git Workflow & Branching Strategy

### Worktrees and Agent Branches

**IMPORTANT**: For projects using git worktrees, `agent-XX` branches (e.g., `agent-1`, `agent-2`) are **base branches** for parallel work, NOT feature branches.

**Rules for agent-XX branches:**
- ❌ **NEVER** create PRs directly from `agent-XX` branches
- ❌ **NEVER** push `agent-XX` branches to remote
- ✅ **DO** use them as base branches in worktrees for creating feature branches
- ✅ **DO** sync them with main: `git fetch && git rebase origin/main`

**Correct workflow from a worktree:**
```bash
# You're in a worktree on agent-1 branch
git branch --show-current  # → agent-1

# 1. Sync with main
git fetch origin
git rebase origin/main

# 2. Create feature branch
git checkout -b feat/my-feature

# 3. Make changes and commit
# ... work ...
git commit -m "feat: add feature"

# 4. Push feature branch and create PR
git push -u origin feat/my-feature
/pr  # This will work because you're on feat/my-feature, not agent-1
```

**Why this matters:**
- Worktrees enable parallel development without branch switching
- `agent-XX` branches are isolated workspace bases
- PRs should come from feature branches (`feat/`, `fix/`, etc.), not workspace bases

### Branch Naming Conventions

All branches must follow these conventions:

| Branch Type | Format | Purpose | Version Impact |
|-------------|--------|---------|-----------------|
| Feature | `feat/xxxxx` | New functionality | Minor update |
| Bug Fix | `fix/xxxxx` | Code fixes | Patch update |
| Refactor | `refactor/xxxxx` | Code refactoring | No update |
| Spike | `spike/DDD_xxxxx` | Experimental exploration | No update |
| Documentation | `docs/xxxxx` | Documentation updates | No update |
| Chore | `chore/xxxxx` | Maintenance, tooling | No update |

**Examples**:
- `feat/python-parser` — New Python parser implementation
- `fix/symbol-table-closure` — Fix closure detection in symbol tables
- `refactor/three-layer-models` — Refactor model hierarchy
- `spike/001_core_model_validation` — Spike to validate core models
- `docs/adr-0007` — Document new architectural decision
- `chore/update-dependencies` — Dependency updates

Be sure to update `CHANGELOG.md` and version numbers as appropriate when merging feature or fix branches.

### Version Bumping

When releasing a new version, update these **three locations**:

1. **`src/code_analyzer/__init__.py`**
   ```python
   __version__ = "0.1.0"  # Update here
   ```

2. **`README.md`**
   ```markdown
   ## Version: 0.1.0  # Update here
   ```

3. **`CHANGELOG.md`**
   ```markdown
   # Changelog

   ## [0.1.0] - 2026-01-05  # Update here
   - Feature A
   - Feature B
   ```

**Versioning Scheme**: Semantic Versioning (MAJOR.MINOR.PATCH)
- **Minor**: New features (`feat/` branches)
- **Patch**: Bug fixes (`fix/` branches)
- **No change**: Refactors, spikes, docs, chores

---

## Useful Resources

- **Project README**: [README.md](README.md)
- **Change Log**: [CHANGELOG.md](CHANGELOG.md)
- **ADR Index**: [docs/adr/index.md](docs/adr/index.md)
- **Vision**: [docs/vision.md](docs/vision.md)

---

## Notes for Contributors

- **Always check ADRs** before proposing architectural changes
- **Respect the four-layer architecture** when adding parsers or storage logic
- **Add tests** for all new features (aim for coverage > 80%)
- **Update ADRs** if making decisions that affect architecture
- **Use type hints** consistently across the codebase
- **Document complex logic** with comments referencing relevant ADRs

---

*Last updated: 2026-01-14*
