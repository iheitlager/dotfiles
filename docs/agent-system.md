# Claude Swarm: Multi-Agent Development System

## Overview

Claude Swarm is a coordination system for running multiple Claude Code agents as equal peers working on a shared codebase. Agents collaborate through a shared task queue and state directory, with no fixed hierarchy. Any agent can receive user requests, create tasks, or execute work.

## Design Principles

### Symmetry Over Hierarchy

All agents run identical instructions. There is no dispatcher, coordinator, or manager. When a user talks to any agent, that agent can either handle the request directly or break it into tasks for the swarm.

This avoids the complexity of role-based systems where you need to define boundaries between "the planner" and "the executor" or decide which agent owns what responsibility.

### Capability Differentiation Without Role Differentiation

Agents may run on different model tiers (Opus, Sonnet, Haiku) but they all follow the same workflow. A Haiku agent receiving a complex request doesn't refuse it—it creates a task tagged for a stronger model. An Opus agent finding only simple tasks in the queue doesn't wait—it helps clear them.

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
└── agent-4/                        # Git worktree on branch agent-4

Shared state (XDG compliant):
~/.local/state/agent-context/
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

## Agent Scaling

### Two Agents

Best for focused work with clear separation:
- Both run at full capability (Opus)
- One might handle feature work, one handles integration
- Low coordination overhead

### Three Agents

Introduces capability tiers:
- Agent-1: Opus (complex reasoning, architecture)
- Agent-2: Sonnet (standard implementation)
- Agent-3: Sonnet (standard implementation)

Two Sonnet agents can parallelize moderate work while Opus handles thorny problems.

### Four Agents

Full spectrum:
- Agent-1: Opus (complex)
- Agent-2: Opus (complex)
- Agent-3: Sonnet (moderate)
- Agent-4: Haiku (simple, high volume)

Haiku clears routine tasks (docs, formatting, simple tests) cheaply, freeing expensive models for hard problems.

## Workflow Patterns

### Direct Execution

User talks to agent, agent handles it immediately.

```
User: "Add a --verbose flag to the CLI"
Agent-2: [assesses: simple, I can do this]
         [implements, commits, done]
```

No task file created. Suitable for small, immediate requests.

### Task Creation and Self-Claim

User makes larger request, agent breaks it down and takes part of it.

```
User: "Refactor the data layer to support async"
Agent-1: [assesses: complex, multi-part]
         [creates task-001: design async interfaces (opus)]
         [creates task-002: update data models (sonnet)]
         [creates task-003: migrate callers (sonnet)]
         [creates task-004: update tests (haiku)]
         [claims task-001, starts work]
```

Other agents pick up remaining tasks as they become available.

### Pure Dispatch

User creates task via CLI, doesn't talk to any agent.

```
$ ./new-task.sh "Fix memory leak in parser" --priority high --complexity complex
Created: tasks/pending/task-1737372800.yaml
```

Next idle Opus agent claims it.

### Dependent Tasks

Some tasks must wait for others.

```yaml
# task-002.yaml
depends_on:
  - task-001
```

Agents check dependencies before claiming. Task stays in pending until dependencies are in done.

## Tmux Layout

The system runs in a tmux session with a practical layout for monitoring and interaction. Layout adapts to agent count.

### Window 1: Agent Grid

**Two Agents — Horizontal Split**

```
┌─────────────────┬─────────────────┐
│                 │                 │
│ agent-1 (opus)  │ agent-2 (opus)  │
│                 │                 │
└─────────────────┴─────────────────┘
```

Tmux: `split-window -h`

**Three Agents — Left Panel + Right Stack**

```
┌─────────────────┬─────────────────┐
│                 │ agent-2 (sonnet)│
│ agent-1 (opus)  ├─────────────────┤
│                 │ agent-3 (sonnet)│
└─────────────────┴─────────────────┘
```

Tmux: `split-window -h` then `split-window -v` on right pane

Agent-1 gets more vertical space — natural for the agent receiving initial instructions or handling complex work. Agents 2 and 3 stack for parallel execution visibility.

**Four Agents — 2x2 Grid**

```
┌─────────────────┬─────────────────┐
│ agent-1 (opus)  │ agent-2 (opus)  │
├─────────────────┼─────────────────┤
│ agent-3 (sonnet)│ agent-4 (haiku) │
└─────────────────┴─────────────────┘
```

Tmux: `split-window -h`, `split-window -v` on left, `split-window -v` on right

Balanced grid. Top row for complex work, bottom row for moderate and simple tasks.

### Windows 2+: Individual Shells

One shell window per agent worktree for running tests, checking output, manual git operations.

### Navigation

- `Ctrl-b 1` through `Ctrl-b 5`: Jump to window
- `Ctrl-b arrow`: Move between panes
- `Ctrl-b z`: Zoom current pane to full screen
- `Ctrl-b d`: Detach (agents keep running)

## User Interaction Modes

### Interactive

Talk directly to any agent in its tmux pane. Good for exploration, discussion, immediate small tasks.

### Task Queue

Create tasks via CLI or by asking any agent to plan work. Good for batched work, overnight runs, parallelizable tasks.

### Hybrid

Start with conversation to explore the problem, then ask the agent to formalize it into tasks for the swarm.

## Coordination Mechanisms

### Task Claiming

Agents claim tasks by moving files from `pending/` to `active/` and writing their ID into the file. Filesystem move is atomic on POSIX systems, preventing double-claims.

### Event Log

All significant events append to `events.log`:

```
2025-01-20T10:00:00Z | agent-1 | CLAIMED | task-001 | Design async interfaces
2025-01-20T10:45:00Z | agent-1 | DONE | task-001 | Created interface specs
2025-01-20T10:46:00Z | agent-3 | CLAIMED | task-002 | Update data models
```

Agents can tail this to stay aware of swarm activity.

### Peer Notification

For urgent coordination, agents can signal each other via tmux:

```bash
tmux send-keys -t claude-agents:agent-2 "FYI: I updated the API interface, rebase recommended" C-m
```

This is optional—polling the event log works for most cases.

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

Agents include this assessment when creating tasks, but can override based on context.

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

## Extension Points

### Webhooks

Watch `events.log` or `tasks/done/` and trigger external actions:
- Slack notification on task completion
- Auto-merge PRs that pass CI
- Spin up additional agents under load

### Different Contexts

The project name is derived from the current git repository directory. The launch script must be run from within a git clone:

```bash
cd ~/wc/project-a
./launch-agents.sh 3    # Creates ~/.local/state/agent-context/project-a/

cd ~/wc/project-b
./launch-agents.sh 2    # Creates ~/.local/state/agent-context/project-b/
```

State directories are isolated per project:
- `~/.local/state/agent-context/project-a/tasks/`
- `~/.local/state/agent-context/project-b/tasks/`

This convention matches the worktree structure which also derives from the git root:
- `~/wc/project-a-worktree/agent-1/`
- `~/wc/project-b-worktree/agent-1/`

No configuration needed — location is implicit from where you launch.

### Persistent Agents

For long-running projects, agents could write checkpoints:
- Current understanding of codebase
- Decisions made and rationale
- Known gotchas

New agents read these to onboard faster.

## Summary

Claude Swarm treats agents as fungible workers differentiated only by capability tier. Users interact through conversation or task files. Coordination happens through filesystem primitives. The result is a system that scales from 2 to N agents without architectural changes, debuggable with `ls` and `cat`, and recoverable by editing YAML files.

No dispatcher. No hierarchy. Just peers, tasks, and git.