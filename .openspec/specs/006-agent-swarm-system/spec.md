# Agent Swarm System Specification

**Domain:** Developer Tooling / Multi-Agent Orchestration
**Version:** 1.0.0
**Status:** Implemented
**Date:** 2026-02-10
**Owner:** Ilja Heitlager

## Overview

The Agent Swarm System orchestrates multiple AI coding agents (Claude, Copilot, Gemini) working
in parallel on the same git repository. It provides tmux-based session management, git worktree
isolation per agent, a file-based job queue for cross-agent coordination, and a monitoring daemon
for observability.

The system is composed of four tools that work together:

- **`launch-agents`** — Bootstraps the swarm: creates git worktrees, configures tmux sessions,
  injects agent instructions, and manages session lifecycle.
- **`swarm-job`** — File-based job queue. Agents create, claim, and complete jobs atomically.
- **`swarm-daemon`** — Background monitoring daemon with REPL and hook integration for event
  tracking and analytics.
- **`swarm-hook`** — Claude Code hook adapter. Translates Claude lifecycle events (SessionStart,
  PostToolUse) into swarm-daemon events.

### Philosophy

- **Peer model**: All agents are equal peers — no coordinator/worker hierarchy.
- **Worktree isolation**: Each agent works in its own git worktree on a dedicated `agent-N`
  branch, preventing branch conflicts.
- **File-based coordination**: Shared state lives in `~/.local/state/agent-context/<repo>/`.
  No network services or databases required.
- **Atomic operations**: Job claiming uses `flock` to prevent two agents claiming the same job.
- **Fire-and-forget hooks**: Hook events are non-blocking; swarm-daemon never slows down
  Claude Code itself.

### Key Capabilities

- **Session bootstrapping**: Creates git worktrees, configures tmux layouts, injects AGENTS.md
  instructions, activates virtual environments.
- **Per-agent tmux windows**: New default layout gives each agent its own window with
  `claude` on left pane and `bash` shell on right pane.
- **Job queue**: Agents create, score, and claim jobs based on model tier matching.
- **Event logging**: Append-only `events.log` records all lifecycle events for audit and analysis.
- **Monitoring phases**: Phase 1 (agent lifecycle), Phase 2 (job metrics), Phase 3 (semantic
  activity tracking).

---

## RFC 2119 Keywords

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT",
"RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in
[RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

---

## ADDED Requirements

### Requirement 1: Git Repository Context Detection

The system MUST detect the current git repository root and derive the project name from it.

The project name is used as the shared state namespace and tmux session name.

Rules for name derivation:
- If inside `<name>-worktree/agent-N/`: extract `<name>`
- If inside `<name>-worktree/`: extract `<name>`
- Otherwise: use the git root directory name
- Leading dots are stripped from names (e.g., `.dotfiles` becomes `dotfiles`)

#### Scenario: Normal Repository

- GIVEN the current directory is inside `/home/user/myproject/`
- WHEN `launch-agents` or `swarm-job` starts
- THEN `REPO_NAME` SHALL be `myproject`
- AND the tmux session SHALL be named `claude-myproject`
- AND shared state SHALL be at `~/.local/state/agent-context/myproject/`

#### Scenario: Worktree Agent Directory

- GIVEN the current directory is `/home/user/myproject-worktree/agent-1/`
- WHEN the tool starts
- THEN `REPO_NAME` SHALL be `myproject` (strips `-worktree` suffix)

#### Scenario: Not a Git Repository

- GIVEN the current directory is not inside a git repository
- WHEN `launch-agents` or `swarm-job` starts
- THEN the tool SHALL print an error message
- AND exit with non-zero status

---

### Requirement 2: Shared State Directory Layout

The system MUST store all shared state in XDG-compliant directories under
`~/.local/state/agent-context/<repo>/`.

#### Scenario: Directory Initialization

- GIVEN the swarm is started for the first time
- WHEN `launch-agents start` or `swarm-job ensure_dirs` runs
- THEN the following directory tree SHALL be created:

```
~/.local/state/agent-context/<repo>/
├── jobs/
│   ├── pending/     # Unclaimed jobs (YAML files)
│   ├── active/      # Claimed jobs (YAML files)
│   └── done/        # Completed jobs (YAML files)
├── events.log       # Append-only event log
└── daemon/
    ├── agent-state.yaml     # Per-agent status tracking
    ├── job-metrics.yaml     # Active/completed job metrics
    └── swarm-daemon.log     # Rotating daemon log (1MB, 3 backups)
```

#### Scenario: AGENTS.md Gitignore

- GIVEN a git repository without `.gitignore`
- WHEN `launch-agents start` runs
- THEN `AGENTS.md` SHALL be added to `.gitignore`
- AND a commit SHALL be created automatically

---

### Requirement 3: Launch-Agents Session Lifecycle

`launch-agents` MUST manage the full lifecycle of a tmux swarm session.

#### Scenario: Smart Default (Start or Attach)

- GIVEN `launch-agents` is run without arguments
- WHEN a session already exists
- THEN it SHALL attach to the existing session
- WHEN no session exists
- THEN it SHALL start a new session (equivalent to `launch-agents start`)

#### Scenario: Start New Session

- GIVEN `launch-agents start` is run
- WHEN the session does not exist
- THEN it SHALL: initialize shared state, create/verify git worktrees for each agent,
  generate AGENTS.md in each worktree, create the tmux layout, start each agent process,
  and attach to the session

#### Scenario: Stop Session (Graceful)

- GIVEN `launch-agents stop` is run without `--force`
- THEN it SHALL send a graceful shutdown message to each agent pane
- AND kill the tmux session

#### Scenario: Stop Session (Forced)

- GIVEN `launch-agents stop --force` is run
- THEN it SHALL send Ctrl-C to each pane
- AND kill the tmux session immediately

#### Scenario: Restart Session

- GIVEN `launch-agents restart` is run
- THEN it SHALL stop the existing session (force) and start a new one

#### Scenario: Already Running

- GIVEN `launch-agents start` is run while a session exists
- AND `--force` is NOT passed
- THEN it SHALL prompt the user to attach or cancel
- AND NOT kill the existing session without consent

---

### Requirement 4: Git Worktree Management

For each agent, `launch-agents` MUST create and maintain an isolated git worktree.

#### Scenario: Worktree Creation

- GIVEN an agent number `N`
- WHEN a worktree does not exist at `<repo>-worktree/agent-N/`
- THEN `launch-agents` SHALL:
  1. Create the `<repo>-worktree/` directory
  2. Create a local branch `agent-N` if it does not exist
  3. Run `git worktree add <path> agent-N`
  4. Symlink `CLAUDE.md` from the main repo if it exists
  5. Run `uv venv` if `uv` is available

#### Scenario: Existing Worktree

- GIVEN the worktree directory already exists
- WHEN `launch-agents start` runs
- THEN it SHALL skip worktree creation and proceed with AGENTS.md generation

#### Scenario: Worktree Cleanup (clean command)

- GIVEN `launch-agents clean` is run
- WHEN a worktree's branch is merged into `main` AND has no uncommitted changes
- THEN it SHALL remove the worktree and delete the local branch
- WHEN uncommitted changes exist and `--force` is NOT set
- THEN it SHALL skip that worktree and warn

---

### Requirement 5: Tmux Layout — New Default (Per-Agent Windows)

The default tmux layout MUST give each agent its own window with a two-pane split.

#### Scenario: New Default Layout for N Agents

- GIVEN `launch-agents -n N start` without `--classic`
- THEN the session SHALL contain:
  - N windows named `agent-1` through `agent-N`
  - Each window split horizontally: left pane = claude process, right pane = bash shell
  - Both panes rooted in the agent's worktree directory
  - One additional `daemon` window at the end

#### Scenario: Daemon Window (Always Present)

- GIVEN the new default layout
- WHEN `--daemon` / `-d` is NOT passed
- THEN the `daemon` window SHALL exist but contain only a bare shell
- WHEN `--daemon` / `-d` IS passed
- THEN `swarm-daemon daemon` SHALL be started in the `daemon` window

#### Scenario: Agent Pane Addressing

- GIVEN the new default layout
- WHEN an agent needs to signal another agent via tmux
- THEN the target pane address SHALL be `$SESSION:agent-N.1` (left/claude pane)

---

### Requirement 6: Tmux Layout — Classic Mode

The classic layout (all agents in one window) MUST remain available via `--classic` / `-o`.

#### Scenario: Classic Layout for N Agents

| N | Layout |
|---|--------|
| 2 | `agents` window: two horizontal panes (left=1, right=2) |
| 3 | `agents` window: three horizontal panes |
| 4 | `agents` window: 2x2 grid (columns of 2 vertical panes) |
| 6 | `agents` window: 2x3 grid (three columns, two rows each) |

Additionally, for each agent N, a separate `shell-N` window is created.

#### Scenario: Classic Pane Addressing

- GIVEN the classic layout
- WHEN an agent signals another
- THEN the target pane SHALL be addressed as `$SESSION:agents.N` (1-based)

---

### Requirement 7: Agent Client and Model Configuration

`launch-agents` MUST configure each agent with the appropriate client and model.

#### Scenario: Default (All Sonnet)

- GIVEN `launch-agents -n N` without `--opus`
- THEN all Claude agents SHALL use the `sonnet` model

#### Scenario: Opus Mode

- GIVEN `launch-agents --opus` is set
- THEN model distribution SHALL follow:
  - N=2: all opus
  - N=3: agents 1-2 sonnet, agent 3 opus
  - N=4: agents 1-2 sonnet, agent 3 opus, agent 4 haiku
  - N=6: agents 1-2 opus, agents 3-4 sonnet

#### Scenario: Multi-Client (N=6 only)

- GIVEN `launch-agents -n 6` without `--equal`
- THEN the default distribution SHALL be:
  - Agents 1-4: claude (sonnet or opus depending on --opus)
  - Agent 5: copilot (5.1-codex)
  - Agent 6: gemini (gemini-pro)
- GIVEN `--equal` is set
- THEN: agents 1-2 claude, agents 3-4 copilot, agents 5-6 gemini

---

### Requirement 8: Agent Instructions (AGENTS.md)

`launch-agents` MUST generate a fresh `AGENTS.md` in each worktree on every start.

#### Scenario: AGENTS.md Content

- GIVEN an agent is started
- THEN its `AGENTS.md` SHALL contain:
  - Agent identity (ID, client, model, worktree path, shared state path)
  - Job queue instructions using `swarm-job` commands
  - Polling instructions (check every 30-60s when idle)
  - Capability matching guidance (model tier)
  - Peer communication via tmux send-keys (using new window addressing)
  - Git workflow instructions (rebase from main, PR on completion)
  - Reference to `~/.dotfiles/docs/agent-system.md`

#### Scenario: System Prompt Injection

- GIVEN a Claude agent is started
- THEN AGENTS.md SHALL be injected via `--append-system-prompt "$(cat AGENTS.md)"`
- AND `--add-dir .` SHALL be set to grant access to the worktree

#### Scenario: AGENTS.md Is Gitignored

- GIVEN AGENTS.md is regenerated each run with dynamic paths
- THEN it SHALL be listed in `.gitignore` to prevent accidental commits

---

### Requirement 9: Workspace Mode

`launch-agents workspace` MUST create a single-developer workspace with claude and shell.

#### Scenario: Workspace Creation

- GIVEN `launch-agents workspace` is run in any directory
- WHEN no `ws-<dir>` session exists
- THEN it SHALL create a tmux session named `ws-<sanitized-dir-name>`
- AND create a `workspace` window with left pane (claude) and right pane (shell)
- AND create a `monitors` window with left pane (ctop) and right pane (htop)

#### Scenario: Workspace Session Naming

- GIVEN the current directory is `/home/user/my.project`
- THEN the session SHALL be named `ws-my_project` (dots replaced with underscores)

#### Scenario: Workspace Already Running

- GIVEN a workspace session already exists
- WHEN `launch-agents workspace` is run without `--force`
- THEN it SHALL prompt: attach or cancel
- WHEN `--force` is set
- THEN it SHALL kill and restart the workspace

---

### Requirement 10: Swarm-Job Job Queue

`swarm-job` MUST implement an atomic, file-based job queue for cross-agent coordination.

#### Scenario: Job File Format

- GIVEN a job is created
- THEN the job YAML file SHALL contain these fields:

```yaml
id: job-<timestamp>-<pid>
created: <ISO-8601 timestamp>
created_by: <agent-id>
priority: low | medium | high | urgent
complexity: simple | moderate | complex
recommended_model: haiku | sonnet | opus
title: <short title>
description: |
  <detailed description>
depends_on: []
claimed_by: null
claimed_at: null
completed_at: null
result: null
```

#### Scenario: Job Creation (new)

- GIVEN `swarm-job new "Title" -p high -c complex`
- THEN a YAML file SHALL be written to `jobs/pending/`
- AND the event SHALL be logged to `events.log`
- AND complexity SHALL map to recommended_model:
  - simple → haiku
  - moderate → sonnet
  - complex → opus

#### Scenario: Atomic Job Claim (claim)

- GIVEN `swarm-job claim` is run by an agent
- THEN the tool SHALL score all pending jobs using the agent's model tier
- AND atomically move the best-scoring job from `pending/` to `active/` using `flock`
- AND update `claimed_by` and `claimed_at` in the YAML file
- AND append a `JOB_CLAIMED` line to `events.log`
- AND call `swarm-daemon hook JOB_CLAIMED <job-id> --issue N --title "..."` in the background
- WHEN two agents try to claim the same job simultaneously
- THEN only one SHALL succeed; the other SHALL get a "being claimed" message

#### Scenario: Job Scoring

- GIVEN an agent with model tier T and a job with recommended tier J
- THEN the score SHALL be:
  - 100 if T == J (perfect match)
  - 50 if J < T (agent is overqualified)
  - 0 if J > T (job too complex for agent)
- AND priority bonus SHALL be added: urgent=+40, high=+30, medium=+20, low=+10

#### Scenario: Job Completion (complete)

- GIVEN `swarm-job complete <job-id>` is run
- THEN the job YAML SHALL be moved from `active/` to `done/`
- AND `completed_at` and `result` SHALL be set
- AND a `JOB_COMPLETED` line SHALL be appended to `events.log`
- AND `swarm-daemon hook JOB_COMPLETED <job-id>` SHALL be called in the background

#### Scenario: Atomic Issue Take (take)

- GIVEN `swarm-job take 123` is run
- THEN the tool SHALL acquire a global lock
- AND check if any pending or active job already references issue #123
- WHEN already exists: SHALL print the existing job and exit with error
- WHEN clear: SHALL create a new job already in `active/` (pre-claimed)
- AND the global lock ensures no two agents claim the same issue

---

### Requirement 11: Swarm-Daemon Hook Events

`swarm-daemon hook` MUST provide fast, non-blocking event recording from agents.

#### Scenario: Hook Must Be Fast

- GIVEN `swarm-daemon hook <EVENT>` is called from a Claude Code hook
- THEN it SHALL write to `events.log`, update `agent-state.yaml`, and exit
- AND the total execution time SHOULD be under 200ms
- AND Claude Code's tool execution SHALL NOT be blocked by hook failures

#### Scenario: Event Log Format

- GIVEN any event is recorded
- THEN the line format SHALL be:
  `<ISO-8601> | <agent-id> | <event-type> | <data>`

#### Scenario: Phase 1 Events (Agent Lifecycle)

- GIVEN a Claude agent starts (SessionStart hook)
- THEN `AGENT_STARTUP` SHALL be emitted
- AND `agent-state.yaml` SHALL be updated with `status: working`

- GIVEN any Claude tool is used (PostToolUse hook)
- THEN `REQUEST` (or tool-specific event) SHALL be emitted
- AND the agent's `last_heartbeat` SHALL be updated

#### Scenario: Phase 2 Events (Job Lifecycle)

- GIVEN `swarm-job claim` succeeds
- THEN `JOB_CLAIMED <job-id> --issue N --title "..."` SHALL be emitted automatically by `swarm-job`
- AND `job-metrics.yaml` SHALL record the new active job

- GIVEN `swarm-job complete` is run
- THEN `JOB_COMPLETED <job-id>` SHALL be emitted automatically by `swarm-job`

- GIVEN a PR is created for a job (after using `/pr` skill)
- THEN the agent SHALL manually call `swarm-daemon hook JOB_PR_READY <job-id> <pr-number>`
- AND the job's `state` SHALL change to `pr_ready`

- GIVEN a PR is merged (after using `/merge` skill)
- THEN the agent SHALL manually call `swarm-daemon hook JOB_PR_MERGED <job-id>`
- AND time-to-PR and total-time metrics SHALL be calculated and stored

#### Scenario: Phase 3 Events (Semantic Activity)

- GIVEN Claude uses Read/Edit/Write/Bash tools
- THEN `TOOL_READ`, `TOOL_EDIT`, `TOOL_WRITE`, `TOOL_BASH` events SHALL be emitted
- AND file/edit counters for the current active job SHALL be incremented

- GIVEN a git commit is made
- THEN `GIT_COMMIT` SHALL be emitted and the commit counter SHALL increment

- GIVEN tests run
- THEN `TEST_STARTED` and `TEST_FAILED` (if failing) SHALL be emitted

---

### Requirement 12: Swarm-Daemon Monitoring Modes

`swarm-daemon` MUST provide three operational modes: daemon, REPL, and CLI.

#### Scenario: Daemon Mode

- GIVEN `swarm-daemon daemon` is run
- THEN it SHALL run in the background, polling at `stale_check_interval` seconds
- AND write its PID to `daemon/daemon.pid`
- AND log to `daemon/swarm-daemon.log` (rotating: 1MB max, 3 backups)
- AND handle SIGINT/SIGTERM for graceful shutdown

#### Scenario: Stale Agent Detection (configurable)

- GIVEN `enable_stale_check: true` in config
- WHEN an agent has no heartbeat for `stale_threshold_minutes`
- THEN `AGENT_STALE` SHALL be logged to events.log
- AND a warning SHALL be logged (rate-limited to once per `stale_log_interval` seconds)

#### Scenario: Pattern Detection

- GIVEN the daemon loop runs
- THEN every ~1 minute it SHALL check for:
  - Jobs with 3+ test failures → log `PATTERN_TEST_FAILURES`
  - Jobs claimed for 60+ minutes with less than 2 total file/commit activity → log `PATTERN_STUCK_JOB`

#### Scenario: REPL Mode

- GIVEN `swarm-daemon repl` is run
- THEN an interactive shell SHALL be presented with these commands:

| Command | Description |
|---------|-------------|
| `status` | Agent count and working/idle summary |
| `agents` | Per-agent status with elapsed time |
| `work` | What each agent is currently working on (Phase 2) |
| `queue [pending\|active\|done]` | Job queue overview |
| `metrics` | Performance statistics (avg time-to-PR, total) |
| `activity [agent]` | File/edit/commit counters per job (Phase 3) |
| `timeline <job-id>` | Chronological event view for a job (Phase 3) |
| `bottlenecks` | Stuck agents, high failure rates, low-activity jobs |
| `compare` | Per-agent performance comparison |
| `cleanup [--hours N] [--dry-run]` | Remove stale agent entries |
| `log [-f] [--agent A] [--tail N]` | Event log viewer with follow mode |

#### Scenario: CLI Mode

- GIVEN `swarm-daemon status` / `agents` / `log` / `cleanup` is run directly (non-REPL)
- THEN the same underlying output SHALL be produced without the interactive prompt

---

### Requirement 13: Swarm-Hook Claude Code Integration

`swarm-hook` MUST integrate `swarm-daemon` event emission with Claude Code hooks.

#### Scenario: SessionStart Registration

- GIVEN a Claude Code session starts in a git repository
- WHEN the `SessionStart` hook fires
- THEN `swarm-hook register` SHALL call `swarm-daemon hook AGENT_STARTUP`
- AND the agent ID SHALL be derived from `$AGENT_ID` env var or the repo name

#### Scenario: PostToolUse Tracking

- GIVEN a Claude Code tool completes
- WHEN the `PostToolUse` hook fires
- THEN `swarm-hook hook` SHALL emit the appropriate event type based on tool name:
  - `Read` → `TOOL_READ`
  - `Edit` → `TOOL_EDIT`
  - `Write` → `TOOL_WRITE`
  - `Bash` → `TOOL_BASH`
  - Others → `REQUEST`

#### Scenario: Hook Timeout Safety

- GIVEN the daemon is not running or is slow
- THEN `swarm-hook` SHALL have a 200ms timeout on the subprocess call
- AND SHALL exit successfully regardless (fire-and-forget)
- AND SHALL NOT cause Claude Code to fail or slow down

---

### Requirement 14: Daemon Configuration

`swarm-daemon` MUST support file-based configuration with sensible defaults.

#### Scenario: Config File Location

- GIVEN a `config/swarm-daemon/config.yml` exists in the current git repo
- THEN it SHALL be used as the config source
- OTHERWISE the daemon SHALL look at `~/.dotfiles/config/swarm-daemon/config.yml`
- OTHERWISE XDG config at `~/.config/swarm-daemon/config.yml`

#### Scenario: Config File Format

```yaml
monitoring:
  enable_stale_check: false    # Disabled by default
  stale_check_interval: 5      # Seconds between polls
  stale_log_interval: 300      # Seconds between repeated stale warnings
  stale_threshold_minutes: 5   # Minutes before agent is considered stale

logging:
  level: INFO
  max_log_size_mb: 10
  backup_count: 5
```

#### Scenario: Missing Config File

- GIVEN no config file exists
- THEN all defaults SHALL apply (stale check disabled, 5s interval)

---

### Requirement 15: Launch-Agents Info and Clean Commands

`launch-agents info` MUST provide a status summary; `clean` MUST safely remove merged worktrees.

#### Scenario: Info Output

- GIVEN `launch-agents info` is run
- THEN it SHALL show:
  - Project name
  - Session status (running/stopped) and attach command
  - Per-agent: worktree exists, current branch, uncommitted changes
  - Job queue counts: pending, active, done
  - Active job details (id, title, claimed_by)
  - Recent events (last 5 from events.log)
  - Path summary (worktrees, shared state)

#### Scenario: Clean — Safe Mode

- GIVEN `launch-agents clean` without `--force`
- WHEN a worktree's branch IS merged into main AND has no uncommitted changes
- THEN it SHALL remove the worktree and delete the branch
- WHEN uncommitted changes OR branch not merged
- THEN it SHALL skip with a warning

#### Scenario: Clean — Force Mode

- GIVEN `launch-agents clean --force`
- THEN it SHALL kill all related processes (tmux, claude, gemini, copilot)
- AND remove ALL worktrees regardless of merge status
- AND remove shared state if no pending/active jobs remain

---

## Current Implementation

All tools are implemented as standalone scripts in `~/.dotfiles/local/bin/`:

| Script | Language | Version |
|--------|----------|---------|
| `launch-agents` | bash | 0.8.0 |
| `swarm-job` | bash | 2.0.0 |
| `swarm-daemon` | Python 3 | 1.0.0 |
| `swarm-hook` | Python 3 | (inline) |

Supporting files:
- `~/.dotfiles/local/share/launch-agents/WORKSPACE_AGENT.md` — Workspace agent instructions
- `~/.dotfiles/config/swarm-daemon/config.yml` — Daemon configuration

---

## Dependencies

- `tmux` — Terminal multiplexer (required for all modes)
- `git` — Version control with worktree support
- `flock` — File locking for atomic job operations (Linux/macOS)
- `uv` — Python package manager (optional, for venv setup)
- `claude` — Anthropic Claude Code CLI
- `gh` — GitHub CLI (optional, for PR checks in `swarm-job take`)
- `bat` — Enhanced file viewer (optional, for help formatting)
- `glow` / `bat` — Markdown renderer (optional, for workspace agent)

---

## References

- **RFC 2119**: https://datatracker.ietf.org/doc/html/rfc2119
- **XDG Base Directory**: https://specifications.freedesktop.org/basedir-spec/latest/

## Internal Documentation

- `~/.dotfiles/docs/agent-system.md` — Architecture and usage guide
- Spec 001: `001-dotfiles-core` — Core dotfiles system
- Spec 005: `005-aliases-system` — Shell aliases (includes swarm-job aliases)

---

**License:** Apache-2.0
**Copyright:** 2026 Ilja Heitlager
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
