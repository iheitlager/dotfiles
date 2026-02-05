# Claude Team Container

Multi-repo, multi-agent team development container for Claude Code.

## Quick Build

```bash
make build
# or
podman build -t claudeteam:latest .
```

## Features

- **Multi-layer build** for efficient caching
- **XDG compliant** configuration
- **Multi-language support**: Python (UV), Node.js, Go, Rust
- **Team settings** via symlinks from mounted workspace
- **GitHub CLI** auth mounted from host
- **Claude OAuth** persisted in volume

## Layer Structure

```
Layer 4: PROJECT  - Claude CLI, entrypoint
Layer 3: TOOLS    - Python/UV, Node.js, Go, Rust
Layer 2: BASICS   - Git, gh, tmux, nvim, utilities
Layer 1: BUILDER  - Base OS, compilers
```

## Usage

This container is managed by the `claude-team` CLI. See [docs/claude-team-container.md](../../docs/claude-team-container.md) for full documentation.

```bash
# From workspace directory
claude-team init        # Generate Makefile
make workstation        # Start workstation mode
make run PROJECT=X      # Start 2 agents
make run4 PROJECT=X     # Start 4 agents
```

## Manual Run

```bash
podman run --rm -it \
    -v ~/wc/myproject:/workspace:z \
    -v ~/.config/gh:/home/claude/.config/gh:ro \
    -v ~/.claude-credentials/$USER:/home/claude/.config/claude:z \
    -e CLAUDE_USER=$(whoami) \
    claudeteam:latest \
    workstation
```

## Modes

- `workstation` - Team config + shell (2 panes)
- `agent <project> <n>` - N agents in worktrees
- `shell` - Just bash
