# Claude Swarm: Multi-Agent Development System

## Overview

Claude Swarm is a coordination system for running multiple AI coding agents as equal peers working on a shared codebase. Agents collaborate through a shared job queue and state directory, with no fixed hierarchy. Any agent can receive user requests, create jobs, or execute work.

**Version 2.0.0** introduces the three-layer terminology model:
- **Issue** — GitHub issue (external tracking, source of truth)
- **Job** — Swarm queue item (cross-agent coordination, ephemeral)
- **Task** — LLM session item (in-agent execution, personal scratchpad)

Previous versions used "task" for both swarm coordination and in-agent tracking, causing confusion.

## Design Principles

### Three-Layer Work Management

Work is managed at three distinct layers:

| Layer | Term | Tool | Scope | Persistence | Purpose |
|-------|------|------|-------|-------------|----------|
| **External** | Issue | GitHub Issues | All work | Permanent | Tracking, tracing, history |
| **Coordination** | Job | Swarm Queue | Current session | Ephemeral | Cross-agent coordination |
| **Execution** | Task | Claude Code | Single agent | In-memory | Personal scratchpad |

**GitHub Issues** are the source of truth for *what needs to be done*:
- Feature requests, bugs, analysis results
- Human-readable descriptions and discussion
- Linked to PRs and commits
- Survives across sessions

**Swarm Queue** coordinates *what we're doing now*:
- Subset of issues selected for current work session
- Agent-optimized format (YAML with capability matching)
- Real-time claiming, completion, dependency tracking
- Can be cleared after session ends

**Workflow:**
```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Issues                            │
│  (backlog: all work that needs doing)                       │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              │  /take #123 queue
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Swarm Queue                              │
│  (sprint: work for this session)                            │
│                                                             │
│   pending/ ──claim──▶ active/ ──complete──▶ done/          │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              │  PR + close issue
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    GitHub (closed)                          │
│  (history: traceable record)                                │
└─────────────────────────────────────────────────────────────┘
```

**Commands:**
- `/take #123` — Direct mode: single agent implements immediately
- `/take #123 queue` — Queue mode: creates swarm job(s) for multi-agent work

See [commands.md](commands.md) for the complete command reference.

This separation keeps project tracking (permanent) distinct from session coordination (ephemeral).

### Symmetry Over Hierarchy

All agents run identical instructions. There is no dispatcher, coordinator, or manager. When a user talks to any agent, that agent can either handle the request directly or break it into jobs for the swarm.

This avoids the complexity of role-based systems where you need to define boundaries between "the planner" and "the executor" or decide which agent owns what responsibility.

### Capability Differentiation Without Role Differentiation

Agents may run on different model tiers (Opus, Sonnet, Haiku for Claude; Codex for Copilot; Gemini Pro) but they all follow the same workflow. A Haiku agent receiving a complex request doesn't refuse it—it creates a job tagged for a stronger model. An Opus agent finding only simple jobs in the queue doesn't wait—it helps clear them.

The model strength is a resource constraint, not an identity.

### Filesystem as Message Bus

Agents communicate through files in a shared state directory. No custom protocols, no database, no message queue. Plain YAML files that can be inspected, edited, and version-controlled.

This means:
- Debugging is trivial (just read the files)
- Recovery is simple (fix the file, restart the agent)
- Humans can participate (create jobs by hand)

### Git Worktrees for Isolation

Each agent operates in its own git worktree. This provides:
- Independent working directories (no stepping on each other)
- Separate branches for parallel work
- Clean PR workflow (one branch per agent per job)
- Easy cleanup when done

## Architecture

### Directory Structure

```
Project layout:
~/wc/my-project/                    # Main repository
~/wc/my-project-worktree/
├── agent-1/                        # Git worktree on branch agent-1
├── agent-2/                        # Git worktree on branch agent-2
├── agent-3/                        # Git worktree on branch agent-3
├── agent-4/                        # Git worktree on branch agent-4
├── agent-5/                        # Git worktree on branch agent-5 (6-agent mode)
└── agent-6/                        # Git worktree on branch agent-6 (6-agent mode)

Shared state (XDG compliant):
~/.local/state/agent-context/<project-name>/
├── jobs/
│   ├── pending/                    # Unclaimed jobs
│   ├── active/                     # Currently being worked
│   └── done/                       # Completed jobs
├── events.log                      # Append-only audit trail
└── agents/                         # Agent heartbeats (optional)
```

### Job Lifecycle

```
                    ┌─────────────────┐
                    │  User Request   │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
    ┌─────────────────┐           ┌─────────────────┐
    │ Talk to Agent   │           │ Create Job      │
    │ (any agent)     │           │ (CLI tool)      │
    └────────┬────────┘           └────────┬────────┘
             │                             │
             │   Agent assesses:           │
             │   - Do it now?              │
             │   - Create sub-jobs?        │
             │                             │
             └──────────────┬──────────────┘
                            ▼
                  ┌─────────────────┐
                  │ jobs/pending/  │
                  └────────┬────────┘
                           │
                           │  Any agent claims
                           ▼
                  ┌─────────────────┐
                  │ jobs/active/   │
                  │ (claimed_by: X) │
                  └────────┬────────┘
                           │
                           │  Agent completes work
                           ▼
                  ┌─────────────────┐
                  │ jobs/done/     │
                  │ + events.log    │
                  └─────────────────┘
```

### Job File Format

Jobs are YAML files with enough metadata for agents to self-organize:

```yaml
id: job-1737372800
created: 2025-01-20T10:00:00Z
created_by: agent-1          # or "user" if created via CLI
priority: medium             # low, medium, high, urgent
complexity: moderate         # simple, moderate, complex
recommended_model: sonnet    # haiku, sonnet, opus
title: Implement caching layer for API responses
description: |
  Add a caching layer between the API client and the data processing
  module. Use functools.lru_cache for in-memory caching initially.
  Include cache invalidation on config changes.
depends_on: []               # job IDs this blocks on
claimed_by: null
claimed_at: null
completed_at: null
result: null
```

The `recommended_model` field is advisory. An agent can work above or below its weight class based on queue depth and urgency.

## Usage

### Smart Default

Running `launch-agents` without a command will:
- **Attach** to an existing session if one is running
- **Start** a new swarm if no session exists

This makes it easy to jump back into your swarm without remembering which command to use.

### Commands

```bash
launch-agents [OPTIONS] [COMMAND]

Commands:
    (none)          Smart default: start or attach if already running
    start           Launch agents in tmux (prompt if already running)
    stop            Kill tmux session
    restart         Stop and restart the session
    attach          Attach to existing session
    workspace       Simple workspace: claude (opus) left, shell right
    clean           Remove worktrees (if branches merged and clean)
    info            Show status of agents, models, and jobs

Options:
    -n COUNT        Number of agents: 2, 3, 4, or 6 (default: 2)
    -d, --daemon    Start swarm-daemon (monitors agent activity, provides REPL)
    -r              Shortcut for 'restart'
    -a              Shortcut for 'attach'
    -w              Shortcut for 'workspace'
    --equal         For n=6, use equal distribution instead of default
    -v, --verbose   Print commands being executed
    --force         Force restart or clean (skips prompts)
    --yolo          Skip permission prompts (Claude agents only)
    -h, --help      Show this help message
    --version       Show version number
```

### Examples

```bash
launch-agents                   # Smart default: start or attach
launch-agents -n 4 start        # Start 4 agents
launch-agents -d start          # Start with swarm-daemon
launch-agents -r                # Restart session
launch-agents workspace         # Simple workspace (claude + shell)
launch-agents -w                # Shortcut for workspace
launch-agents info              # Show swarm status
launch-agents stop              # Stop all agents
launch-agents clean             # Remove merged worktrees
launch-agents --force clean     # Remove all worktrees (even with changes)
```

## Agent Scaling & Client Distribution

### Two Agents (Default)

Both agents run Claude Opus for maximum capability:

| Agent | Client | Model |
|-------|--------|-------|
| agent-1 | claude | opus |
| agent-2 | claude | opus |

**Layout:**
```
┌─────────────────┬─────────────────┐
│ agent-1 (opus)  │ agent-2 (opus)  │
└─────────────────┴─────────────────┘
```

### Three Agents

Introduces capability tiers with one Opus for complex work:

| Agent | Client | Model |
|-------|--------|-------|
| agent-1 | claude | opus |
| agent-2 | claude | sonnet |
| agent-3 | claude | sonnet |

**Layout:**
```
┌─────────────────┬─────────────────┐
│                 │ agent-2 (sonnet)│
│ agent-1 (opus)  ├─────────────────┤
│                 │ agent-3 (sonnet)│
└─────────────────┴─────────────────┘
```

### Four Agents

Full Claude spectrum from Opus to Haiku:

| Agent | Client | Model |
|-------|--------|-------|
| agent-1 | claude | opus |
| agent-2 | claude | opus |
| agent-3 | claude | sonnet |
| agent-4 | claude | haiku |

**Layout:**
```
┌─────────────────┬─────────────────┐
│ agent-1 (opus)  │ agent-2 (opus)  │
├─────────────────┼─────────────────┤
│ agent-3 (sonnet)│ agent-4 (haiku) │
└─────────────────┴─────────────────┘
```

### Six Agents — Default Distribution

Multi-client mode with Claude majority (4 Claude + 1 Copilot + 1 Gemini):

| Agent | Client | Model |
|-------|--------|-------|
| agent-1 | claude | opus |
| agent-2 | claude | opus |
| agent-3 | claude | sonnet |
| agent-4 | claude | sonnet |
| agent-5 | copilot | 5.1-codex |
| agent-6 | gemini | gemini-pro |

### Six Agents — Equal Distribution (`--equal`)

Balanced pairs across all three clients:

| Agent | Client | Model |
|-------|--------|-------|
| agent-1 | claude | opus |
| agent-2 | claude | sonnet |
| agent-3 | copilot | 5.1-codex |
| agent-4 | copilot | 5.1-codex |
| agent-5 | gemini | gemini-pro |
| agent-6 | gemini | gemini-pro |

**Layout (both 6-agent modes):**
```
┌─────────────────┬─────────────────┬─────────────────┐
│ agent-1         │ agent-3         │ agent-5         │
├─────────────────┼─────────────────┼─────────────────┤
│ agent-2         │ agent-4         │ agent-6         │
└─────────────────┴─────────────────┴─────────────────┘
```

### Workspace Mode

For simpler work, use workspace mode (`-w` or `workspace`) which creates a single Claude (opus) session with a shell:

```
┌─────────────────┬─────────────────┐
│ claude (opus)   │ shell           │
└─────────────────┴─────────────────┘
```

This runs in the current directory without worktrees, ideal for quick work or single-agent work.

## Tmux Session Structure

### Window 1: Agent Grid (`agents`)

All agents visible in a grid layout. Pane numbering is 1-based:
- `agent-1` → pane 1
- `agent-2` → pane 2
- etc.

### Windows 2+: Individual Shells (`shell-1`, `shell-2`, ...)

One shell window per agent worktree for running tests, checking output, manual git operations. Virtual environment is auto-activated if present.

### Navigation

| Keys | Action |
|------|--------|
| `Ctrl-b 1` | Jump to agents window |
| `Ctrl-b 2-N` | Jump to shell windows |
| `Alt ↑↓←→` | Move between panes |
| `Ctrl-b z` | Zoom current pane |
| `Ctrl-b d` | Detach (agents keep running) |

### Session Naming

- **Swarm sessions**: Named `claude-<project-name>` where project name is derived from the git repository directory.
- **Workspace sessions**: Named `ws-<directory-name>` for the simpler workspace mode.

## Agent Configuration

### Per-Agent Files

Each agent worktree contains:

- **AGENTS.md** — Auto-generated instructions injected via `--append-system-prompt`. Contains agent identity, job queue instructions, and peer communication protocols. This file is gitignored.

- **CLAUDE.md** (symlinked) — Project-specific instructions from the main repository. Shared across all agents.

- **.venv/** — Python virtual environment (created with `uv venv` if available).

### Environment Variables

Set in each agent's tmux pane:

```bash
AGENT_ID=agent-N
AGENT_CLIENT=claude|copilot|gemini
AGENT_MODEL=opus|sonnet|haiku|5.1-codex|gemini-pro
```

For Claude agents:
```bash
CLAUDE_SKIP_PERMISSION_PROMPTS=true
CLAUDE_AUTO_APPROVE_FOLDERS=true
```

### Permission Modes

| Flag | Claude CLI Flag | Behavior |
|------|----------------|----------|
| (default) | `--permission-mode acceptEdits` | Approve edits automatically |
| `--yolo` | `--dangerously-skip-permissions` | Skip all permission prompts |

## Coordination Mechanisms

### Job Management with swarm-job

The `swarm-job` CLI provides unified job management:

```bash
# List all jobs
swarm-job list                    # Shows pending, active, done
swarm-job list pending            # Only pending jobs with scores

# Create a new job
swarm-job new "Add feature X" -p high -c complex
swarm-job new "Fix bug" -c simple
swarm-job new "Blocked job" -D job-123,job-456  # Dependencies

# Claim a job (atomic with flock)
swarm-job claim                   # Auto-select best match for your tier
swarm-job claim job-XXX          # Claim specific job
swarm-job claim --dry-run         # Preview what would be claimed

# Complete a job
swarm-job complete job-XXX
swarm-job complete job-XXX -r "merged to main"
```

**Job scoring:** When listing or claiming, jobs are scored based on capability match:
- **100+** (green): Perfect match for agent tier
- **50+** (yellow): Agent can handle (simpler job)
- **0** (red): Too complex for agent

### Legacy: Manual Job Claiming

For debugging or manual intervention, jobs can still be managed directly:

```bash
# Find work
ls ~/.local/state/agent-context/<project>/jobs/pending/

# Claim a job manually
mv ~/.local/state/agent-context/<project>/jobs/pending/job-XXX.yaml \
   ~/.local/state/agent-context/<project>/jobs/active/
# Edit file: set claimed_by: agent-N, claimed_at: <timestamp>
```

### Event Log

All significant events append to `events.log`:

```
2025-01-20T10:00:00Z | agent-1 | CLAIMED | job-001 | Design async interfaces
2025-01-20T10:45:00Z | agent-1 | DONE | job-001 | Created interface specs
2025-01-20T10:46:00Z | agent-3 | CLAIMED | job-002 | Update data models
```

Agents can tail this to stay aware of swarm activity:

```bash
tail -30 ~/.local/state/agent-context/<project>/events.log
```

### Peer Notification

For urgent coordination, agents can signal each other via tmux:

```bash
tmux send-keys -t claude-<project>:agents.N "Message here" Enter
tmux send-keys -t claude-<project>:agents.N Enter  # Extra enter for visibility
```

Pane mapping: agent-1=1, agent-2=2, agent-3=3, agent-4=4, agent-5=5, agent-6=6 (1-based)

### Swarm Daemon

The `swarm-daemon` provides unified monitoring and investigation capabilities:

```bash
swarm-daemon daemon                # Background monitoring mode
swarm-daemon repl                  # Interactive investigation shell
swarm-daemon status                # Quick status overview
swarm-daemon agents                # List agent states
swarm-daemon log                   # Show recent events
swarm-daemon log -f                # Follow events in real-time
swarm-daemon --context <repo>      # Specify context from outside git repo
```

**Context Model:**
- Context = git repository (one daemon per repo)
- Agent ID = `<repo>` (e.g., "dotfiles", "my-project")
- State files: `~/.local/state/agent-context/<repo>/`
- Each context is isolated with its own events and state

**Event Tracking:**

**Currently Active:**

**Phase 1 (Basic Lifecycle):**
- `AGENT_STARTUP` - When agent starts (via swarm-hook)
- `REQUEST` - Tool usage tracking (via swarm-hook)

**Phase 2 (Job Lifecycle):**
- `JOB_CLAIMED` - When agent claims job via `/take` skill
- `JOB_PR_READY` - When PR created via `/pr` skill
- `JOB_PR_MERGED` - When PR merged via `/merge` skill
- `JOB_COMPLETED` - When job marked complete

**Phase 3 (Semantic Events):**
- **Tool Events:** TOOL_READ, TOOL_EDIT, TOOL_WRITE, TOOL_BASH, TOOL_GREP, TOOL_GLOB, TOOL_TASK
- **Git Events:** GIT_COMMIT, GIT_PUSH, GIT_REBASE, GIT_CONFLICT
- **Test/Lint Events:** TEST_STARTED, TEST_PASSED, TEST_FAILED, LINT_STARTED, LINT_PASSED, LINT_FAILED
- **Task Events:** TASK_CREATED, TASK_STARTED, TASK_COMPLETED, TASK_BLOCKED
- **Agent State:** AGENT_THINKING, AGENT_WAITING, AGENT_ERROR

**Implementation Status:**
- ✅ **Phase 1 Complete** - Basic agent lifecycle and request tracking
- ✅ **Phase 2 Complete** - Job lifecycle tracking enabled (see job metrics below)
- ✅ **Phase 3 Complete** - Semantic event tracking enabled (see event mappings below)

**Event Mappings (Phase 3):**

Phase 3 automatically emits semantic events based on tool usage:

| Claude Tool | Event Emitted | Metadata Captured |
|-------------|---------------|-------------------|
| Read | TOOL_READ | File path |
| Edit | TOOL_EDIT | File path, lines changed |
| Write | TOOL_WRITE | File path, lines written |
| Bash | TOOL_BASH (or specialized) | Command (first 100 chars) |
| Bash (git commit) | GIT_COMMIT | Git command |
| Bash (git push) | GIT_PUSH | Git command |
| Bash (git rebase) | GIT_REBASE | Git command |
| Bash (pytest, npm test, etc.) | TEST_STARTED | Test command |
| Bash (ruff, eslint, mypy, etc.) | LINT_STARTED | Lint command |
| Grep | TOOL_GREP | Search pattern |
| Glob | TOOL_GLOB | File pattern |
| Task | TOOL_TASK | Subagent type |

All events include: agent ID, timestamp, process ID, and context (repo name).

**Job Metrics (Phase 2):**

With Phase 2 enabled, swarm-daemon tracks:
- Time from job claim to PR creation (time-to-PR)
- Time from PR creation to merge (time-to-merge)
- Current job per agent (visible in `swarm-daemon agents`)
- Active jobs with metadata (issue #, title, PR #, timestamps)
- Completed jobs with performance metrics

View job tracking:
```bash
swarm-daemon agents              # See what each agent is working on
swarm-daemon log --agent agent-1 # Filter events by agent
swarm-daemon log | grep JOB_     # See all job lifecycle events
```

**Integration with Claude Code:**
The daemon integrates with Claude Code via `swarm-hook` (Python hooks):
- `SessionStart` → `swarm-hook register` → `AGENT_STARTUP` event
- `PostToolUse` → `swarm-hook hook` → `REQUEST` + tool-specific events (Phase 3)

Every tool use triggers two events:
1. Generic `REQUEST` event (Phase 1 - for basic tracking)
2. Tool-specific event (Phase 3 - for detailed activity analysis)

Configuration in `~/.dotfiles/claude/config/settings.json`:
```json
{
  "hooks": {
    "SessionStart": [{"command": "swarm-hook register"}],
    "PostToolUse": [{"command": "swarm-hook hook"}]
  }
}
```

**View events:**
```bash
swarm-daemon log              # All events
swarm-daemon log -f           # Follow mode
swarm-daemon log --agent dotfiles  # Filter by agent
```

**State files per context:**
```
~/.local/state/agent-context/<repo>/
├── events.log                # All events (append-only)
├── daemon/
│   ├── agent-state.yaml      # Current agent states
│   └── daemon.pid            # Daemon process ID
└── jobs/                     # Job queue (swarm-job)
```

**Phased Event Enablement Plan:**

The swarm-daemon supports progressive event tracking through a 3-phase enablement approach (see #14):

| Phase | Status | Events | Purpose |
|-------|--------|--------|---------|
| **Phase 1** | ✅ Active | AGENT_STARTUP, REQUEST | Basic agent lifecycle |
| **Phase 2** | ✅ Active | JOB_CLAIMED, JOB_PR_READY, JOB_PR_MERGED, JOB_COMPLETED | Job lifecycle tracking |
| **Phase 3** | ✅ Active | TOOL_*, GIT_*, TEST_*, TASK_* | Fine-grained activity tracking |

**All phases enabled!** The swarm-daemon now provides comprehensive visibility into:
- **Phase 1:** When agents start and what tools they use
- **Phase 2:** Job lifecycle from claim to PR to merge with time metrics
- **Phase 3:** Detailed activity including file operations, git commands, tests, and more

**Event Volume:** Phase 3 generates high event volume. Use filtering to focus:
```bash
swarm-daemon log --agent agent-1      # Single agent
swarm-daemon log | grep TOOL_EDIT     # Specific event type
swarm-daemon log | grep GIT_          # All git operations
```

### Communication Summary

| Method | Type | Direction | Use Case |
|--------|------|-----------|----------|
| `swarm-job list` | Polling | Agent → Queue | Check for available work |
| `tmux send-keys` | Direct | Agent → Agent | Peer-to-peer messaging |
| Watcher notify | Async | Daemon → Capable | New/unblocked job alerts |
| Watcher broadcast | Pub/sub | Daemon → All | Completion announcements |
| `events.log` | Append-only | All → File | Audit trail, swarm awareness |

**Recommended agent behavior:**
- Poll `swarm-job list pending` every 30-60 seconds when idle
- Watch for tmux notifications from watcher
- Check `events.log` for recent swarm activity

### Session Task Management (Claude Code)

Claude Code agents have built-in task tools (`TaskCreate`, `TaskList`, `TaskGet`, `TaskUpdate`) that operate within a single conversation session. These complement—but don't replace—the file-based swarm job queue.

**Two Task Systems:**

| System | Scope | Persistence | Visibility | Purpose |
|--------|-------|-------------|------------|---------|
| Swarm (YAML files) | Cross-agent | Persistent on disk | All agents + humans | Coordination |
| Claude Code (built-in) | Single session | In-memory | Only the agent | Personal tracking |

**When to Use Each:**

| Scenario | System |
|----------|--------|
| Creating work for other agents | Swarm (`swarm-job new`) |
| Claiming a task | Swarm (`swarm-job claim`) |
| Breaking down my claimed task into steps | Claude Code (`TaskCreate`) |
| Tracking progress within a session | Claude Code (`TaskUpdate`) |
| Signaling completion to swarm | Swarm (`swarm-job complete`) |
| Seeing what work is available | Swarm (`swarm-job list pending`) |

**Integrated Workflow:**

When an agent claims a swarm job:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. CLAIM (Swarm Job)                                        │
│    swarm-job claim job-XXX                                  │
│    (or: swarm-job claim  to auto-select best match)         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. DECOMPOSE (LLM Tasks)                                    │
│    TaskCreate: "Implement feature X"                        │
│    TaskCreate: "Add tests for feature X"                    │
│    TaskCreate: "Update documentation"                       │
│    TaskUpdate: Set dependencies (blockedBy)                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. EXECUTE (LLM Tasks)                                      │
│    TaskUpdate: status → in_progress                         │
│    ... do work ...                                          │
│    TaskUpdate: status → completed                           │
│    TaskList: check for next subtask                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. COMPLETE (Swarm Job)                                     │
│    swarm-job complete job-XXX -r "Implemented feature"      │
│    (watcher broadcasts completion to all agents)            │
└─────────────────────────────────────────────────────────────┘
```

**Key Principles:**

1. **Swarm jobs are source of truth** — Other agents can't see your LLM `TaskList`
2. **LLM tasks are personal scratchpad** — Use them to stay organized on complex work
3. **Always signal to swarm** — Move files and log events so other agents know what's happening
4. **Don't duplicate** — If a job is simple enough to do directly, skip LLM task tracking

**Example Session:**

```bash
# Agent checks for work
$ swarm-job list pending
Pending:
  job-001 [120] [high/complex] Implement config parser

# Agent claims swarm job
$ swarm-job claim job-001
✓ Claimed: job-001
  Title: Implement config parser

# Agent uses Claude Code for subtask tracking (internal to session)
> TaskCreate: "Parse input configuration"
> TaskCreate: "Implement transformation logic"
> TaskCreate: "Write unit tests"
> TaskUpdate: task-1 status=in_progress

# ... agent works through subtasks ...

# Agent completes swarm job
$ swarm-job complete job-001 -r "Implemented config parser with validation"
✓ Completed: job-001
  Title: Implement config parser
  By: agent-1

# Watcher broadcasts: "[swarm] Job completed: job-001 by agent-1"
```

## Git Workflow & Synchronization

Each agent works on its own branch (`agent-1`, `agent-2`, etc.):

1. Ensure branch is up to date: `git pull --rebase origin main`
2. Make changes, commit with clear messages
3. Create PR when complete: `gh pr create`
4. Log completion to events.log

### Sync Points

Agents must stay synchronized with `main`. These are the critical sync points:

| Command | Sync Action | Signal to Others |
|---------|-------------|------------------|
| `/take` | Rebase on main before starting | Register job in queue |
| `/pr` | Check if behind main, warn | Complete swarm job |
| `/merge` | Pull latest main | **Broadcast sync signal** |

### When Signals Are Sent

Only one event requires broadcasting to other agents:

**After `/merge`**: Main has changed, other agents need to rebase.

```bash
# Signal sent to all agents in swarm
tmux send-keys -t "$SESSION:agents.$pane" \
  "[sync] main updated via PR #$PR - run: git fetch && git rebase origin/main"
```

Other coordination (job claimed, job completed, new job) is handled by:
- The file-based queue system (atomic claims)
- The swarm-daemon (monitors agent activity)

### Pre-flight Checks (enforced by /take)

Before taking any issue:

1. **Working state** - Must be on clean main/agent-N branch
2. **Queue check** - Issue not already claimed by another agent
3. **Sync** - Rebase on latest main
4. **Register** - Create and claim job in queue

## Complexity Assessment Guide

When an agent receives a request or reviews a task, it assesses complexity:

| Signal | Complexity | Model |
|--------|------------|-------|
| Single file, mechanical change | Simple | Haiku |
| Docs, comments, formatting | Simple | Haiku |
| Standard feature, clear spec | Moderate | Sonnet |
| Refactoring across files | Moderate | Sonnet |
| New architecture, design decisions | Complex | Opus |
| Debugging subtle issues | Complex | Opus |
| Security-sensitive changes | Complex | Opus |
| Multi-step, needs breakdown | Complex | Opus (for planning) |

## Cleanup

The `clean` command handles worktree removal intelligently:

1. If `--force`: kills tmux and all agent processes (claude, gemini, copilot)
2. Stops tmux session if running
3. For each agent worktree:
   - Checks for uncommitted changes (blocks unless `--force`)
   - Checks if branch is merged into main
   - Removes worktree and branch if safe
4. Removes shared state if no pending/active tasks (or `--force`)

```bash
launch-agents clean         # Safe cleanup (merged branches only)
launch-agents --force clean # Force cleanup (kills processes, removes everything)
```

## Failure Handling

### Agent Crash

Task remains in `active/` with stale `claimed_by`. Options:
- Human moves it back to `pending/`
- Another agent notices stale claim (no progress, no heartbeat) and reclaims
- Restart crashed agent, it resumes its active task

### Conflicting Changes

Agents work on branches. Merge conflicts surface at PR time. Resolution:
- Agent rebases on main before PR
- If conflict, agent resolves or flags for human review
- Other agents avoid claiming tasks with same file dependencies

### Task Stuck

If an agent can't complete a task:
1. Write findings to task file
2. Move back to `pending/` or to a `blocked/` directory
3. Log the issue
4. Another agent or human can pick it up with context

## Graceful Shutdown

When a user types "shut down" to any agent:

1. Finish current task
2. Log shutdown event
3. Exit process
4. Run `launch-agents stop` to kill the tmux session

To restart the swarm quickly:
```bash
launch-agents restart    # or -r
launch-agents --force start  # equivalent
```

## Future Enhancements

### Job-Skill Binding

Tasks can reference Claude Code skills for consistent execution:

```yaml
id: job-1737372800
title: Document authentication architecture
skill: adr-documentation          # References ~/.claude/skills/adr-documentation/
skill_args: "authentication flow"
# ... rest of task fields
```

When an agent claims this task, it loads the skill context automatically, ensuring consistent approach across agents.

### Project-Specific Skills

Extend the shared state directory with project skills:

```
~/.local/state/agent-context/<project>/
├── tasks/
├── events.log
└── skills/                       # Project-specific skills
    ├── api-patterns/
    │   └── SKILLS.md             # How this project structures APIs
    ├── testing-conventions/
    │   └── SKILLS.md             # Project test patterns
    └── deployment/
        └── SKILLS.md             # Deployment procedures
```

**Skill Resolution Order:**
1. Project skills (`~/.local/state/agent-context/<project>/skills/`)
2. Global skills (`~/.claude/skills/`)

### Agent Profiles

Create `~/.claude/agents/` for agent-specific configurations:

```
~/.claude/agents/
├── profiles.yaml                 # Agent specialization preferences
└── capabilities.yaml             # Model-to-skill mapping
```

**profiles.yaml:**
```yaml
agent-1:
  specializations:
    - architecture
    - security
  preferred_skills:
    - adr-documentation
    - testing-strategy
  avoid_tasks:
    - formatting
    - docs-only

agent-4:
  specializations:
    - testing
    - documentation
  preferred_skills:
    - testing-strategy
  model: haiku
```

**capabilities.yaml:**
```yaml
# Which skills work best with which model tiers
skills:
  adr-documentation:
    minimum_model: sonnet
    recommended_model: opus
  testing-strategy:
    minimum_model: haiku
    recommended_model: sonnet
  git-commit:
    minimum_model: haiku
```

### Task Templates

Skills can define task templates for standardized task creation:

```
~/.claude/skills/adr-documentation/
├── SKILLS.md
└── job-template.yaml            # Template for ADR jobs
```

**job-template.yaml:**
```yaml
# Template variables: {{topic}}, {{context}}
priority: medium
complexity: moderate
recommended_model: opus
title: "Create ADR for {{topic}}"
description: |
  Document the architectural decision for {{topic}}.

  Context: {{context}}

  Follow the ADR documentation skill for structure and format.
  Place in docs/adr/ with next available number.
skill: adr-documentation
```

**Usage:**
```bash
# Future CLI command
create-task --template adr-documentation \
  --var topic="authentication" \
  --var context="Need to choose between JWT and session tokens"
```

### ~~Swarm Commands~~ (Implemented)

The `swarm-job` CLI now provides all task management commands:

```bash
swarm-job new "title" [-p priority] [-c complexity] [-D depends]
swarm-job claim [job-id] [--dry-run]
swarm-job complete <job-id> [-r result]
swarm-job list [pending|active|done|all]
```

The `swarm-daemon` provides agent monitoring and investigation:

```bash
swarm-daemon daemon           # Start background monitoring
swarm-daemon repl             # Interactive investigation
swarm-daemon agents           # List agent states
swarm-daemon log              # View events
```

See [Job Management with swarm-job](#job-management-with-swarm-job) and [Swarm Daemon](#swarm-daemon) for details.

### Agent Registry

Track active agents for intelligent coordination:

```
~/.local/state/agent-context/<project>/
├── agents/
│   ├── agent-1.yaml              # Heartbeat + current state
│   ├── agent-2.yaml
│   └── ...
```

**agent-N.yaml:**
```yaml
id: agent-1
client: claude
model: opus
status: active                    # active, idle, offline
current_task: job-1737372800
last_heartbeat: 2025-01-20T10:45:00Z
session_start: 2025-01-20T09:00:00Z
tasks_completed: 3
specializations:                  # From profile or learned
  - architecture
  - debugging
```

**Benefits:**
- Detect stale claims (no heartbeat update)
- Load balancing (route to idle agents)
- Capability matching (assign complex tasks to capable agents)
- Swarm health monitoring

### Implementation Priority

| Enhancement | Effort | Impact | Status |
|-------------|--------|--------|--------|
| Swarm Commands | Low | High | **Done** (swarm-job, swarm-daemon, swarm-hook) |
| Job-Skill Binding | Low | Medium | Planned |
| Project Skills | Medium | High | Planned |
| Task Templates | Medium | Medium | Planned |
| Agent Profiles | Medium | Medium | Planned |
| Agent Registry | High | High | Planned |

## Summary

Claude Swarm treats agents as fungible workers differentiated only by capability tier and client. Users interact through conversation or task files. Coordination happens through filesystem primitives. The result is a system that scales from 2 to 6 agents without architectural changes, debuggable with `ls` and `cat`, and recoverable by editing YAML files.

No dispatcher. No hierarchy. Just peers, tasks, and git.

## Evaluation of Existing Multi-Agent Frameworks

Several multi-agent frameworks exist, but none match the design goals of Claude Swarm. Here's what's relevant for Claude-based coding:

### 1. AutoGen (Microsoft)

- Multi-agent conversations with different roles
- Agents can be Claude, GPT, or local models
- Good for: Task decomposition, peer review, debate patterns
- Con: Heavily chat-based, not optimized for CLI workflows

```python
from autogen import AssistantAgent, UserProxyAgent

architect = AssistantAgent("architect", llm_config={"model": "claude-sonnet-4"})
coder = AssistantAgent("coder", llm_config={"model": "claude-sonnet-4"})
reviewer = AssistantAgent("reviewer", llm_config={"model": "claude-sonnet-4"})
```

### 2. CrewAI

- Role-based agents with hierarchical/sequential workflows
- Supports Claude via LiteLLM
- Good for: Defined roles (architect → coder → tester)
- Con: More structured than the peer-based swarm design

```python
from crewai import Agent, Task, Crew

architect_agent = Agent(
    role='System Architect',
    goal='Design system architecture',
    llm='claude-sonnet-4'
)
```

### 3. LangGraph

- State machine-based agent orchestration
- Good for: Complex workflows with cycles and conditions
- Con: Requires learning the graph paradigm

### 4. OpenHands (formerly OpenDevin)

- Full coding agent with browser, terminal, editor
- Multi-agent modes being developed
- Good for: Complete autonomous coding
- Con: Heavy framework, not lightweight coordination

### 5. Sweep

- GitHub-integrated coding agent
- Mostly single-agent but can spawn sub-tasks
- Con: Tied to GitHub workflow

### Why None Match Claude Swarm's Design

These frameworks are **task orchestrators** (top-down), while Claude Swarm enables **peer coordination** (emergent):

- They abstract away the filesystem; Claude Swarm leverages it
- They use their own state management; Claude Swarm uses hooks + tmux
- They're Python frameworks; Claude Swarm is lightweight coordination
- They impose role hierarchies; Claude Swarm treats agents as equals

**What Claude Swarm resembles instead:**
- **Ray** (distributed compute) but for AI agents
- **Kafka/Event Bus** but with filesystem + hooks
- **Actor Model** (Erlang/Akka) but pragmatic

### Framework Comparison

| Feature | AutoGen/CrewAI | Claude Swarm |
|---------|----------------|--------------|
| Agent equality | Hierarchical | Peer-based |
| Communication | API calls | Filesystem + sockets |
| State | Framework-managed | Git + shared files |
| Coordination | Programmed flows | Emergent from hooks |
| Overhead | High (Python frameworks) | Low (bash + python glue) |
| Claude Code | Wrapper needed | Native |
| Domain focus | General purpose | IT/OT operations optimized |

### Could We Use Them?

Yes, but we would lose:
- Direct tmux visibility
- Claude Code's native capabilities
- Lightweight hook-based sync
- WBSO/TSO domain-specific coordination

### Should We Use Them?

Only if we need their specific features:
- **AutoGen:** If we want agent debates/voting
- **CrewAI:** If we want strict role hierarchies
- **LangGraph:** If our workflow is a complex state machine

### Conclusion

Claude Swarm builds something these frameworks don't address: **lightweight peer coordination for specialized domain work**. The frameworks are generic task orchestrators; Claude Swarm is domain-specific collaborative tooling.

The hooks + daemon approach follows the **Unix philosophy** (small tools, composable) rather than adopting **monolithic frameworks**.

This architectural choice maintains simplicity, debuggability, and direct integration with the tools developers already use (git, tmux, filesystem).
