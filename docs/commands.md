# Claude Code Commands

Slash commands for software engineering workflows. These work in both single-agent and multi-agent (swarm) modes.

## Quick Reference

| Command | Purpose | Effect |
|---------|---------|--------|
| `/review` | Analyze project health | Read-only report |
| `/issue` | List/create GitHub issues | Issue management |
| `/take` | Implement an issue | Code changes + PR |
| `/plan` | Design implementation | docs/plans/*.md |
| `/plan adr` | Architectural decision | docs/adr/*.md |
| `/spike` | Experimental exploration | tests/spikes/* |
| `/swarm` | Manage job queue | Queue operations |
| `/check` | Run code quality checks | Lint report |
| `/changelog` | Generate CHANGELOG entries | CHANGELOG.md |
| `/version` | Validate release readiness | Sync check |
| `/commit` | Create git commit | Commit |
| `/pr` | Create pull request | PR |
| `/br` | Create feature branch | Branch |
| `/purge` | Clean merged branches | Delete branches |

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                      DISCOVERY                              │
│  /review          Analyze code, docs, issues for gaps       │
│  /issue           List open issues, suggest next work       │
└─────────────────────────────────┬───────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│                      PLANNING                               │
│  /issue <desc>    Quick-create issue from idea              │
│  /issue new       Structured issue with template            │
│  /plan            Detailed implementation plan              │
│  /plan adr        Architectural decision record             │
│  /spike           Prototype to validate approach            │
└─────────────────────────────────┬───────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│                      EXECUTION                              │
│  /take #N         Implement issue directly                  │
│  /take #N queue   Load issue to swarm queue                 │
│  /swarm           Manage swarm job queue                    │
└─────────────────────────────────┬───────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│                      QUALITY                                │
│  /check           Run linting, type checking, formatting    │
│  /review code     Check for TODOs, code smells              │
└─────────────────────────────────┬───────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│                      SHIPPING                               │
│  /br              Create feature branch                     │
│  /commit          Conventional commit                       │
│  /pr              Create pull request                       │
│  /changelog       Generate CHANGELOG entries                │
│  /version         Validate sync, bump version               │
│  /purge           Clean up merged branches                  │
└─────────────────────────────────────────────────────────────┘
```

## Commands

### /review

Analyze codebase, documentation, and GitHub issues to identify gaps.

```
/review              Full project review
/review code         Code quality and TODOs only
/review docs         Documentation completeness only
/review issues       GitHub issues health only
```

**Finds:**
- TODO/FIXME comments
- Missing tests
- Documentation gaps
- Stale or duplicate issues

**Actions:** Creates issues for gaps, closes fixed issues, queues work.

---

### /issue

List and manage GitHub issues.

```
/issue               List open issues
/issue <description> Quick create from informal input
/issue new           Structured create with template
/issue #123          Show specific issue details
```

**Quick create** investigates the codebase before drafting:
```
/issue fix that hover bug in the sidebar
/issue feat: add dark mode toggle
```

**Structured create** uses a template with complexity estimation and acceptance criteria.

---

### /take

Take ownership of an issue and implement it.

```
/take #123           Direct: implement yourself
/take #123 queue     Queue: load to swarm for agents to claim
/take                Show suggested issues to take
```

**Direct mode:** Research → Plan → Implement → PR

**Queue mode:** Creates swarm job(s) with priority and complexity mapping from issue labels.

---

### /plan

Create planning documents: feature plans or architectural decision records.

```
/plan                Start planning (asks for context)
/plan <feature>      Plan specific feature → docs/plans/
/plan adr <topic>    Architectural decision → docs/adr/
```

**Feature plans** output to `docs/plans/<feature>.md`:
- Problem statement
- Proposed solution
- Files to modify
- Edge cases
- Test strategy

**ADRs** output to `docs/adr/NNNN-<topic>.md`:
- Context and problem
- Decision made
- Consequences (positive/negative)
- Alternatives considered

---

### /spike

Experimental exploration to validate an approach.

```
/spike               Start a spike (asks for context)
/spike <topic>       Spike on specific topic
```

**Output:** `tests/spikes/<NNN>_<topic>/` with prototype code and findings.

Spikes are throwaway — learnings get captured, code may be discarded.

---

### /swarm

Manage the swarm job queue.

```
/swarm               Show queue overview + pending jobs
/swarm active        Show jobs currently being worked on
/swarm done          Show recently completed jobs
/swarm create <title> Create new job for the swarm
```

See also: `swarm-job` CLI and `swarm-watcher` daemon.

---

### /check

Run code quality checks (linting, type checking, formatting).

```
/check               Run all checks
/check lint          Run linter only (ruff)
/check types         Run type checker only (mypy)
/check format        Check formatting (ruff format --check)
/check <file>        Check specific file or directory
```

**Detects project type** and runs appropriate tools:
- Python: ruff, mypy, ruff format
- Uses `uv run` when available
- Falls back to Makefile targets if present

**Reports** issues grouped by severity with auto-fix suggestions.

---

### /changelog

Generate CHANGELOG entries from commits since last release.

```
/changelog           Generate entries for unreleased changes
/changelog preview   Show what would be added (no file changes)
/changelog <version> Generate entries for specific version
```

**Parses** conventional commit prefixes:
- `feat:` → Added
- `fix:` → Fixed
- `BREAKING CHANGE:` → Breaking Changes

**Ignores** internal commits: `chore:`, `test:`, `ci:`

---

### /commit

Create a conventional commit from staged changes.

```
/commit              Analyze staged changes, draft message
/commit --amend      Amend previous commit (use carefully)
```

**Format:** `type(scope): description`

**Types:** `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`, `style`

**Detects:**
- Breaking changes (adds `!` and footer)
- Scope from file paths
- Related issues

**Multi-file guidance:** Suggests splitting unrelated changes.

---

### /pr

Create, list, review, and manage pull requests.

```
/pr                  Create PR from current branch to main
/pr draft            Create as draft PR
/pr list             List open PRs with status
/pr #123             Show details for specific PR
/pr #123 review      Code review with agent
/pr #123 checkout    Checkout PR branch locally
/pr #123 continue    Checkout and continue working on PR
/pr #123 merge       Merge PR and clean up branches
```

**Create mode** generates:
- Title from branch name/commits
- Summary of all commits (not just latest)
- Related issues (auto-close syntax)
- Testing checklist

**Review mode** uses `code-reviewer` agent to analyze:
- Bugs, security issues, code quality
- Test coverage and project conventions
- Offers to post comments or approve/request changes

**Continue mode** uses `Explore` agent to understand PR context and remaining work.

**Merge mode** handles the full merge workflow:
- Pre-merge checks (approval, CI, conflicts)
- Merge with squash/merge/rebase options
- Delete remote branch (via `--delete-branch`)
- Delete local branch and switch to main
- Prune stale remote refs

---

### /br

Create a feature branch following naming conventions.

```
/br                           Interactive branch creation
/br <description>             Create branch from description
/br feat <description>        Shorthand: create feature branch
/br fix <description>         Shorthand: create fix branch
/br fix #123 <description>    Include issue number
```

**Shorthand examples:**
```
/br feat add user auth        → feat/add-user-auth
/br fix #42 token expiry      → fix/42-token-expiry
/br docs update readme        → docs/update-readme
```

**Conventions:**
- `feat/<name>` — New feature
- `fix/<name>` — Bug fix
- `refactor/<name>` — Code restructuring
- `docs/<name>` — Documentation
- `chore/<name>` — Maintenance
- `spike/<name>` — Experimental

---

### /version

Validate version consistency and release readiness.

```
/version             Full validation check
/version check       Same as above
/version bump patch  Bump patch version (0.6.0 → 0.6.1)
/version bump minor  Bump minor version (0.6.0 → 0.7.0)
/version bump major  Bump major version (0.6.0 → 1.0.0)
```

**Checks:**
- Version numbers match across all files
- CHANGELOG reflects recent commits
- Git state is clean
- Dependencies are up to date

**Bump mode** updates all version locations, CHANGELOG, and offers to commit + tag.

---

### /purge

Clean up merged git branches.

```
/purge               Clean both local and remote merged branches
/purge local         Clean only local merged branches
/purge remote        Clean only remote merged branches
/purge --dry-run     Show what would be deleted without deleting
```

**Safe by default:**
- Only removes branches merged into main
- Never deletes main, master, develop, or current branch
- Asks for confirmation before deletion

## Single-Agent vs Multi-Agent

| Mode | Commands | Notes |
|------|----------|-------|
| Single | All except `/swarm` | `/take` implements directly |
| Swarm | All | `/take queue` loads work for agents |

In swarm mode, the job queue coordinates work:
```
/take #123 queue  →  swarm-job claim  →  work  →  swarm-job complete
```

## Agent Delegation

Some skills delegate heavy work to specialized agents while keeping decisions interactive:

| Skill | Agent Usage | Pattern |
|-------|-------------|---------|
| `/review` | Explore agents (parallel) | Scan code, tests, docs → synthesize report |
| `/take` | Explore agent | Research codebase → validate → plan → implement |
| `/check` | Bash agent (background) | Run all linters → report → offer fixes |
| `/pr #N review` | code-reviewer agent | Analyze PR → report findings → offer actions |
| `/pr #N continue` | Explore agent | Understand PR context → show remaining work |

### Why Delegate?

**Agents handle:**
- Codebase exploration (finding files, patterns)
- Running commands (linting, tests)
- Gathering data (issue health, coverage gaps)

**Main conversation handles:**
- Judgment calls (is this issue valid?)
- User interaction (confirm before acting)
- Synthesis (combining agent results into reports)

### Example: /review

```
┌─────────────────────────────────────────────────────────────┐
│  Spawn in parallel:                                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │ Explore    │  │ Explore    │  │ Bash       │            │
│  │ Code scan  │  │ Doc scan   │  │ GH issues  │            │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘            │
│        └───────────────┼───────────────┘                    │
│                        ▼                                    │
│              Synthesize + Present                           │
│                        ▼                                    │
│              Offer Actions (interactive)                    │
└─────────────────────────────────────────────────────────────┘
```

This pattern keeps the skill responsive while offloading computation.

## Adding Custom Commands

Commands are markdown files in `~/.claude/commands/`:

```
~/.claude/commands/
├── br.md
├── changelog.md
├── check.md
├── commit.md
├── issue.md
├── plan.md
├── pr.md
├── purge.md
├── review.md
├── spike.md
├── swarm.md
├── take.md
└── version.md
```

Each file defines:
1. Purpose and usage
2. Process steps
3. Output format
4. Examples

Claude Code loads these as slash commands automatically.
