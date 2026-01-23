# Claude Swarm: Multi-Agent Development System

## Overview

Claude Swarm is a coordination system for running multiple AI coding agents as equal peers working on a shared codebase. Agents collaborate through a shared task queue and state directory, with no fixed hierarchy. Any agent can receive user requests, create tasks, or execute work.

**Version 0.4.0** introduces multi-client support, allowing Claude, GitHub Copilot, and Gemini agents to work together in the same swarm.

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

### Commands

```bash
launch-agents [OPTIONS] COMMAND

Commands:
    start           Launch agents in tmux (or attach if running)
    stop            Kill tmux session
    clean           Remove worktrees (if branches merged and clean)
    info            Show status of agents, models, and tasks

Options:
    -n COUNT        Number of agents: 2, 3, 4, or 6 (default: 2)
    --equal         For n=6, use equal distribution instead of default
    -v, --verbose   Print commands being executed
    --force         Force clean even with uncommitted changes
    --yolo          Skip permission prompts (Claude agents only)
    -h, --help      Show this help message
    --version       Show version number
```

### Examples

```bash
launch-agents start             # Start 2 agents (default)
launch-agents -n 4 start        # Start 4 agents
launch-agents -n 6 start        # Start 6 agents with multi-client
launch-agents -n 6 --equal start # Start 6 agents with equal client distribution
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

Multi-client mode with Claude majority:

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

Session is named `claude-<project-name>` where project name is derived from the git repository directory.

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

### Task Claiming

Agents claim tasks by moving files from `pending/` to `active/` and writing their ID into the file. Filesystem move is atomic on POSIX systems, preventing double-claims.

```bash
# Find work
ls ~/.local/state/agent-context/<project>/tasks/pending/

# Claim a task
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

1. Stops tmux session if running
2. For each agent worktree:
   - Checks for uncommitted changes (blocks unless `--force`)
   - Checks if branch is merged into main
   - Removes worktree and branch if safe
3. Removes shared state if no pending/active tasks (or `--force`)

```bash
launch-agents clean         # Safe cleanup (merged branches only)
launch-agents --force clean # Force cleanup (removes everything)
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

## Summary

Claude Swarm treats agents as fungible workers differentiated only by capability tier and client. Users interact through conversation or task files. Coordination happens through filesystem primitives. The result is a system that scales from 2 to 6 agents without architectural changes, debuggable with `ls` and `cat`, and recoverable by editing YAML files.

No dispatcher. No hierarchy. Just peers, tasks, and git.
