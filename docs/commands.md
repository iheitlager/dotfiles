# Claude Code Commands

Slash commands for software engineering workflows. These work in both single-agent and multi-agent (swarm) modes.

## Quick Reference

| Command | Purpose | Effect |
|---------|---------|--------|
| `/review` | Analyze project health | Read-only report |
| `/issue` | List/create GitHub issues | Issue management |
| `/take` | Implement an issue | Code changes + PR |
| `/plan` | Design implementation | Plan document |
| `/spike` | Experimental exploration | Prototype code |
| `/swarm` | Manage task queue | Queue operations |
| `/commit` | Create git commit | Commit |
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
│  /spike           Prototype to validate approach            │
└─────────────────────────────────┬───────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│                      EXECUTION                              │
│  /take #N         Implement issue directly                  │
│  /take #N queue   Load issue to swarm queue                 │
│  /swarm           Manage swarm task queue                   │
└─────────────────────────────────┬───────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│                      SHIPPING                               │
│  /br              Create feature branch                     │
│  /commit          Conventional commit                       │
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

**Queue mode:** Creates swarm task(s) with priority and complexity mapping from issue labels.

---

### /plan

Create a detailed implementation plan before coding.

```
/plan                Start planning (asks for context)
/plan <feature>      Plan specific feature
```

**Output:** `docs/plans/<feature>.md` with:
- Problem statement
- Proposed solution
- Files to modify
- Edge cases
- Test strategy

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

Manage the swarm task queue.

```
/swarm               Show queue status
/swarm list          List pending/active/done tasks
/swarm add <title>   Create new task
```

See also: `swarm-task` CLI and `swarm-watcher` daemon.

---

### /commit

Create a conventional commit from staged changes.

```
/commit              Analyze staged changes, draft message
```

**Format:** `<type>: <description>`

Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`

---

### /br

Create a feature branch following naming conventions.

```
/br                  Interactive branch creation
/br <name>           Create branch with name
```

**Conventions:**
- `feat/<name>` — New feature
- `fix/<name>` — Bug fix
- `refactor/<name>` — Code restructuring
- `docs/<name>` — Documentation
- `chore/<name>` — Maintenance

---

### /purge

Clean up merged git branches.

```
/purge               Remove merged local branches
/purge --remote      Also remove merged remote branches
```

Safe by default — only removes branches merged into main.

## Single-Agent vs Multi-Agent

| Mode | Commands | Notes |
|------|----------|-------|
| Single | All except `/swarm` | `/take` implements directly |
| Swarm | All | `/take queue` loads work for agents |

In swarm mode, the task queue coordinates work:
```
/take #123 queue  →  swarm-task claim  →  work  →  swarm-task complete
```

## Adding Custom Commands

Commands are markdown files in `~/.dotfiles/claude/config/commands/`:

```
~/.dotfiles/claude/config/commands/
├── review.md
├── issue.md
├── take.md
├── plan.md
├── spike.md
├── swarm.md
├── commit.md
├── br.md
└── purge.md
```

Each file defines:
1. Purpose and usage
2. Process steps
3. Output format
4. Examples

Claude Code loads these as slash commands automatically.
