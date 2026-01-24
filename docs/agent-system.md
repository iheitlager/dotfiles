# Claude Swarm: Multi-Agent Development System

## Overview

Claude Swarm is a coordination system for running multiple AI coding agents as equal peers working on a shared codebase. Agents collaborate through a shared task queue and state directory, with no fixed hierarchy. Any agent can receive user requests, create tasks, or execute work.

**Version 0.6.0** introduces the `swarm-task` CLI for unified task management and `swarm-watcher` daemon for queue monitoring with broadcast notifications. Previous versions added smart defaults, workspace mode, and multi-client support (Claude, GitHub Copilot, Gemini).

## Design Principles

### Symmetry Over Hierarchy

All agents run identical instructions. There is no dispatcher, coordinator, or manager. When a user talks to any agent, that agent can either handle the request directly or break it into tasks for the swarm.

This avoids the complexity of role-based systems where you need to define boundaries between "the planner" and "the executor" or decide which agent owns what responsibility.

### Capability Differentiation Without Role Differentiation

Agents may run on different model tiers (Opus, Sonnet, Haiku for Claude; Codex for Copilot; Gemini Pro) but they all follow the same workflow. A Haiku agent receiving a complex request doesn't refuse it—it creates a task tagged for a stronger model. An Opus agent finding only simple tasks in the queue doesn't wait—it helps clear them.

The model strength is a resource constraint, not an identity.

### Filesystem as Message Bus

Agents communicate through files in a shared state directory. No custom protocols, no database, no message queue. Plain YAML files that can be inspected, edited, and version-controlled.

This means:
- Debugging is trivial (just read the files)
- Recovery is simple (fix the file, restart the agent)
- Humans can participate (create tasks by hand)

### Git Worktrees for Isolation

Each agent operates in its own git worktree. This provides:
- Independent working directories (no stepping on each other)
- Separate branches for parallel work
- Clean PR workflow (one branch per agent per task)
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
├── tasks/
│   ├── pending/                    # Unclaimed tasks
│   ├── active/                     # Currently being worked
│   └── done/                       # Completed tasks
├── events.log                      # Append-only audit trail
└── agents/                         # Agent heartbeats (optional)
```

### Task Lifecycle

```
                    ┌─────────────────┐
                    │  User Request   │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
    ┌─────────────────┐           ┌─────────────────┐
    │ Talk to Agent   │           │ Create Task     │
    │ (any agent)     │           │ (CLI tool)      │
    └────────┬────────┘           └────────┬────────┘
             │                             │
             │   Agent assesses:           │
             │   - Do it now?              │
             │   - Create subtasks?        │
             │                             │
             └──────────────┬──────────────┘
                            ▼
                  ┌─────────────────┐
                  │ tasks/pending/  │
                  └────────┬────────┘
                           │
                           │  Any agent claims
                           ▼
                  ┌─────────────────┐
                  │ tasks/active/   │
                  │ (claimed_by: X) │
                  └────────┬────────┘
                           │
                           │  Agent completes work
                           ▼
                  ┌─────────────────┐
                  │ tasks/done/     │
                  │ + events.log    │
                  └─────────────────┘
```

### Task File Format

Tasks are YAML files with enough metadata for agents to self-organize:

```yaml
id: task-1737372800
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
depends_on: []               # task IDs this blocks on
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
    info            Show status of agents, models, and tasks

Options:
    -n COUNT        Number of agents: 2, 3, 4, or 6 (default: 2)
    -d, --daemon    Start swarm-watcher daemon (monitors queue, broadcasts notifications)
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
launch-agents -d start          # Start with swarm-watcher daemon
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

For simpler tasks, use workspace mode (`-w` or `workspace`) which creates a single Claude (opus) session with a shell:

```
┌─────────────────┬─────────────────┐
│ claude (opus)   │ shell           │
└─────────────────┴─────────────────┘
```

This runs in the current directory without worktrees, ideal for quick tasks or single-agent work.

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

- **AGENTS.md** — Auto-generated instructions injected via `--append-system-prompt`. Contains agent identity, task queue instructions, and peer communication protocols. This file is gitignored.

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

### Task Management with swarm-task

The `swarm-task` CLI provides unified task management:

```bash
# List all tasks
swarm-task list                    # Shows pending, active, done
swarm-task list pending            # Only pending tasks with scores

# Create a new task
swarm-task new "Add feature X" -p high -c complex
swarm-task new "Fix bug" -c simple
swarm-task new "Blocked task" -D task-123,task-456  # Dependencies

# Claim a task (atomic with flock)
swarm-task claim                   # Auto-select best match for your tier
swarm-task claim task-XXX          # Claim specific task
swarm-task claim --dry-run         # Preview what would be claimed

# Complete a task
swarm-task complete task-XXX
swarm-task complete task-XXX -r "merged to main"
```

**Task scoring:** When listing or claiming, tasks are scored based on capability match:
- **100+** (green): Perfect match for agent tier
- **50+** (yellow): Agent can handle (simpler task)
- **0** (red): Too complex for agent

### Legacy: Manual Task Claiming

For debugging or manual intervention, tasks can still be managed directly:

```bash
# Find work
ls ~/.local/state/agent-context/<project>/tasks/pending/

# Claim a task manually
mv ~/.local/state/agent-context/<project>/tasks/pending/task-XXX.yaml \
   ~/.local/state/agent-context/<project>/tasks/active/
# Edit file: set claimed_by: agent-N, claimed_at: <timestamp>
```

### Event Log

All significant events append to `events.log`:

```
2025-01-20T10:00:00Z | agent-1 | CLAIMED | task-001 | Design async interfaces
2025-01-20T10:45:00Z | agent-1 | DONE | task-001 | Created interface specs
2025-01-20T10:46:00Z | agent-3 | CLAIMED | task-002 | Update data models
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

### Swarm Watcher Daemon

The `swarm-watcher` daemon monitors the task queue and broadcasts notifications:

```bash
swarm-watcher                      # Start daemon (usually via launch-agents -d)
swarm-watcher -i 10                # Custom poll interval (10 seconds)
```

**What it monitors:**

| Event | Action |
|-------|--------|
| New pending task | Notifies capable agents (by tier) |
| Task claimed | Logs pickup with agent ID |
| Task completed | Broadcasts to ALL agents |
| Task unblocked | Notifies capable agents |

**Output example:**
```
[14:32:10] INFO    Watching: ~/.local/state/agent-context/project/tasks/pending
[14:32:15] TASK    New: task-123 [high/complex] Add authentication
[14:32:15] NOTIFY  Notifying agents: 1,2 (tier >= 3)
[14:33:20] CLAIMED task-123 picked up by agent-1
[14:45:30] DONE    task-123 completed by agent-1 [success]
[14:45:30] UNBLOCK task-456 is now unblocked: Add tests
```

**Graceful shutdown:** Press `Ctrl-C` to trigger swarm shutdown via `launch-agents stop`.

### Communication Summary

| Method | Type | Direction | Use Case |
|--------|------|-----------|----------|
| `swarm-task list` | Polling | Agent → Queue | Check for available work |
| `tmux send-keys` | Direct | Agent → Agent | Peer-to-peer messaging |
| Watcher notify | Async | Daemon → Capable | New/unblocked task alerts |
| Watcher broadcast | Pub/sub | Daemon → All | Completion announcements |
| `events.log` | Append-only | All → File | Audit trail, swarm awareness |

**Recommended agent behavior:**
- Poll `swarm-task list pending` every 30-60 seconds when idle
- Watch for tmux notifications from watcher
- Check `events.log` for recent swarm activity

### Session Task Management (Claude Code)

Claude Code agents have built-in task tools (`TaskCreate`, `TaskList`, `TaskGet`, `TaskUpdate`) that operate within a single conversation session. These complement—but don't replace—the file-based swarm task queue.

**Two Task Systems:**

| System | Scope | Persistence | Visibility | Purpose |
|--------|-------|-------------|------------|---------|
| Swarm (YAML files) | Cross-agent | Persistent on disk | All agents + humans | Coordination |
| Claude Code (built-in) | Single session | In-memory | Only the agent | Personal tracking |

**When to Use Each:**

| Scenario | System |
|----------|--------|
| Creating work for other agents | Swarm (`swarm-task new`) |
| Claiming a task | Swarm (`swarm-task claim`) |
| Breaking down my claimed task into steps | Claude Code (`TaskCreate`) |
| Tracking progress within a session | Claude Code (`TaskUpdate`) |
| Signaling completion to swarm | Swarm (`swarm-task complete`) |
| Seeing what work is available | Swarm (`swarm-task list pending`) |

**Integrated Workflow:**

When an agent claims a swarm task:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. CLAIM (Swarm)                                            │
│    swarm-task claim task-XXX                                │
│    (or: swarm-task claim  to auto-select best match)        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. DECOMPOSE (Claude Code)                                  │
│    TaskCreate: "Implement feature X"                        │
│    TaskCreate: "Add tests for feature X"                    │
│    TaskCreate: "Update documentation"                       │
│    TaskUpdate: Set dependencies (blockedBy)                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. EXECUTE (Claude Code)                                    │
│    TaskUpdate: status → in_progress                         │
│    ... do work ...                                          │
│    TaskUpdate: status → completed                           │
│    TaskList: check for next subtask                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. COMPLETE (Swarm)                                         │
│    swarm-task complete task-XXX -r "Implemented feature"    │
│    (watcher broadcasts completion to all agents)            │
└─────────────────────────────────────────────────────────────┘
```

**Key Principles:**

1. **Swarm tasks are source of truth** — Other agents can't see your Claude Code `TaskList`
2. **Claude Code tasks are personal scratchpad** — Use them to stay organized on complex work
3. **Always signal to swarm** — Move files and log events so other agents know what's happening
4. **Don't duplicate** — If a task is simple enough to do directly, skip Claude Code task tracking

**Example Session:**

```bash
# Agent checks for work
$ swarm-task list pending
Pending:
  task-001 [120] [high/complex] Implement config parser

# Agent claims swarm task
$ swarm-task claim task-001
✓ Claimed: task-001
  Title: Implement config parser

# Agent uses Claude Code for subtask tracking (internal to session)
> TaskCreate: "Parse input configuration"
> TaskCreate: "Implement transformation logic"
> TaskCreate: "Write unit tests"
> TaskUpdate: task-1 status=in_progress

# ... agent works through subtasks ...

# Agent completes swarm task
$ swarm-task complete task-001 -r "Implemented config parser with validation"
✓ Completed: task-001
  Title: Implement config parser
  By: agent-1

# Watcher broadcasts: "[swarm] Task completed: task-001 by agent-1"
```

## Git Workflow

Each agent works on its own branch (`agent-1`, `agent-2`, etc.):

1. Ensure branch is up to date: `git pull --rebase origin main`
2. Make changes, commit with clear messages
3. Create PR when complete: `gh pr create`
4. Log completion to events.log

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

### Task-Skill Binding

Tasks can reference Claude Code skills for consistent execution:

```yaml
id: task-1737372800
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
└── task-template.yaml            # Template for ADR tasks
```

**task-template.yaml:**
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

The `swarm-task` CLI now provides all task management commands:

```bash
swarm-task new "title" [-p priority] [-c complexity] [-D depends]
swarm-task claim [task-id] [--dry-run]
swarm-task complete <task-id> [-r result]
swarm-task list [pending|active|done|all]
```

The `swarm-watcher` daemon provides queue monitoring and notifications:

```bash
swarm-watcher [-i interval]
```

See [Task Management with swarm-task](#task-management-with-swarm-task) and [Swarm Watcher Daemon](#swarm-watcher-daemon) for details.

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
current_task: task-1737372800
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
| Swarm Commands | Low | High | **Done** (swarm-task, swarm-watcher) |
| Task-Skill Binding | Low | Medium | Planned |
| Project Skills | Medium | High | Planned |
| Task Templates | Medium | Medium | Planned |
| Agent Profiles | Medium | Medium | Planned |
| Agent Registry | High | High | Planned |

## Summary

Claude Swarm treats agents as fungible workers differentiated only by capability tier and client. Users interact through conversation or task files. Coordination happens through filesystem primitives. The result is a system that scales from 2 to 6 agents without architectural changes, debuggable with `ls` and `cat`, and recoverable by editing YAML files.

No dispatcher. No hierarchy. Just peers, tasks, and git.
