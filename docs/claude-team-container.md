# Claude Team Container: Multi-Repo, Multi-Agent Team Workspace

## Overview

The Claude Team Container is a reproducible, XDG-compliant development environment for collaborative AI agent work on multiple code repositories. It enables teams to share agent settings, coordinate work via GitHub Issues/PRs externally and worktrees internally, and maintain persistent, secure agent authentication within a containerized workspace.

**Version:** 1.0.0

## Design Principles

### Three-Layer Work Management (Inherited from Agent System)

Work coordination follows the established three-layer model:

| Layer | Term | Tool | Scope | Persistence | Purpose |
|-------|------|------|-------|-------------|---------|
| **External** | Issue | GitHub Issues | All work | Permanent | Tracking, tracing, history |
| **Coordination** | Job | Swarm Queue | Current session | Ephemeral | Cross-agent coordination |
| **Execution** | Task | Claude Code | Single agent | In-memory | Personal scratchpad |

**External Coordination:** GitHub Issues and PRs are the source of truth for what needs to be done. Teams coordinate through issue assignment, PR reviews, and discussion threads.

**Internal Coordination:** Worktrees provide isolation for parallel agent work within the container. The swarm job queue enables agents to claim and coordinate work without conflicts.

### XDG Compliance

All configuration, state, and cache files follow the XDG Base Directory Specification:

```
$XDG_CONFIG_HOME  → ~/.config
$XDG_DATA_HOME    → ~/.local/share
$XDG_STATE_HOME   → ~/.local/state
$XDG_CACHE_HOME   → ~/.cache
```

### Multi-Language Support

The container supports polyglot development with tooling for:

| Language | Toolchain | Package Manager |
|----------|-----------|-----------------|
| Python | Python 3.12+, UV | uv, pip |
| Go | Go 1.22+ | go mod |
| Rust | Rust (rustup) | cargo |
| TypeScript | Node.js 20+, tsx | npm, pnpm |
| JavaScript | Node.js 20+ | npm, pnpm |
| Angular | Angular CLI | npm |
| React | Vite/CRA | npm, pnpm |

## Architecture

### Team Config Detection

The team config repo is auto-detected by looking for a repo containing `claude/config/CLAUDE.md`. This follows the same structure as the personal dotfiles:

```
team-config-repo/
├── claude/
│   ├── config/              # Symlinked into ~/.claude
│   │   ├── CLAUDE.md        # Team-wide agent instructions
│   │   ├── settings.json    # Shared settings
│   │   ├── commands/        # Custom slash commands
│   │   ├── skills/          # Shared skills
│   │   ├── templates/       # Job templates
│   │   └── agents/          # Agent profiles
│   ├── install.sh           # Setup script (reference)
│   └── bash_aliases         # Optional shell aliases
└── ...
```

The container's `~/.claude` is populated via **symlinks** (not copies), mirroring the approach in `claude/install.sh`:

```bash
# In container entrypoint
ln -sf "/workspace/$TEAM_CONFIG/claude/config/CLAUDE.md" "$HOME/.claude/CLAUDE.md"
ln -sf "/workspace/$TEAM_CONFIG/claude/config/settings.json" "$HOME/.claude/settings.json"
for dir in "/workspace/$TEAM_CONFIG/claude/config"/*/; do
    [ -d "$dir" ] && ln -sfn "$dir" "$HOME/.claude/$(basename "$dir")"
done
```

### Directory Structure

**Example workspace: `/Users/iheitlager/wc/project1`**

```
Host filesystem (macOS):
~/wc/project1/                       # Workspace root
├── dotfiles/                        # Team config repo (auto-detected)
│   ├── claude/
│   │   ├── config/
│   │   │   ├── CLAUDE.md           # Team agent instructions
│   │   │   ├── settings.json       # Shared settings
│   │   │   ├── commands/
│   │   │   ├── skills/
│   │   │   ├── templates/
│   │   │   └── agents/
│   │   └── install.sh
│   └── ...                          # Other dotfiles
├── FRANK/                           # Project repo
│   ├── .git/
│   ├── CLAUDE.md                    # Project-specific instructions
│   └── ...
├── worktrees/                       # Created on first agent run
│   └── FRANK/
│       ├── alice-a.1/               # Alice's agent 1 worktree
│       ├── alice-a.2/               # Alice's agent 2 worktree
│       └── ...
└── Makefile                         # Workspace launch helper

Container filesystem:
/workspace/                          # Mounted from host (read-write)
├── dotfiles/                        # Team config (symlink source)
├── FRANK/                           # Project repo
└── worktrees/                       # Agent worktrees

/home/claude/                        # Container user home
├── .claude/                         # Symlinks to team config
│   ├── CLAUDE.md -> /workspace/dotfiles/claude/config/CLAUDE.md
│   ├── settings.json -> /workspace/dotfiles/claude/config/settings.json
│   ├── commands/ -> /workspace/dotfiles/claude/config/commands/
│   ├── skills/ -> /workspace/dotfiles/claude/config/skills/
│   └── templates/ -> /workspace/dotfiles/claude/config/templates/
├── .config/
│   ├── gh/                          # Mounted from host (read-only)
│   ├── claude/                      # OAuth credentials (persistent volume)
│   └── nvim/
├── .local/
│   ├── bin/
│   ├── share/
│   ├── state/
│   │   └── agent-context/           # Swarm state (per-project)
│   │       └── FRANK/
│   │           ├── jobs/
│   │           │   ├── pending/
│   │           │   ├── active/
│   │           │   └── done/
│   │           └── events.log
│   └── cache/
└── .cache/
```

### Agent/Worktree Naming Convention

Agent identities are derived from worktree names:

```
{username}-a.{agent_number}
```

Examples:
- `alice-a.1` — Alice's first agent
- `alice-a.2` — Alice's second agent
- `bob-a.1` — Bob's first agent

This ensures:
- Unique agent identities per user
- No worktree conflicts between team members
- Clear ownership of work branches

## Container Modes

The container supports multiple start modes. The same container image can be started multiple times in different modes.

### Mode 1: Workstation

Single-user development workspace with tmux split:

```
┌─────────────────────────────────────┬─────────────────────────────────────┐
│ team-settings/                      │ bash shell                          │
│ (claude code in config workspace)   │ (general work)                      │
└─────────────────────────────────────┴─────────────────────────────────────┘
```

**Use case:** Editing team settings, reviewing configurations, manual git operations.

### Mode 2: Agent (2-agent)

Two agents working in parallel on worktrees:

```
┌─────────────────────────────────────┬─────────────────────────────────────┐
│ {user}-a.1 worktree                 │ {user}-a.2 worktree                 │
│ (claude agent 1)                    │ (claude agent 2)                    │
└─────────────────────────────────────┴─────────────────────────────────────┘
```

**Use case:** Parallel development, one agent per feature/issue.

### Mode 3: Agent (4-agent)

Four agents in a grid:

```
┌─────────────────────┬─────────────────────┐
│ {user}-a.1          │ {user}-a.2          │
├─────────────────────┼─────────────────────┤
│ {user}-a.3          │ {user}-a.4          │
└─────────────────────┴─────────────────────┘
```

**Use case:** Complex projects requiring multiple parallel workstreams.

## Required Tooling

### Core Tools

| Tool | Purpose |
|------|---------|
| `podman` | Container runtime |
| `tmux` | Terminal multiplexer |
| `nvim` | Editor |
| `git` | Version control |
| `gh` | GitHub CLI (issues, PRs, auth) |
| `claude` | Claude Code CLI |

### Language Toolchains

| Tool | Purpose |
|------|---------|
| `uv` | Python package/environment manager |
| `python3` | Python runtime |
| `node` | Node.js runtime |
| `npm` / `pnpm` | JavaScript package managers |
| `go` | Go compiler |
| `rustup` / `cargo` | Rust toolchain |
| `tsx` | TypeScript execution |

### Utilities

| Tool | Purpose |
|------|---------|
| `ripgrep` (rg) | Fast search |
| `fd` | Fast find |
| `bat` | Better cat |
| `jq` | JSON processing |
| `yq` | YAML processing |
| `fzf` | Fuzzy finder |

## Container Specification

### Multi-Layer Build Architecture

The container uses a multi-layer build strategy for efficient caching and modularity:

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: PROJECT                                            │
│ - Entrypoint scripts                                        │
│ - Team-specific configuration                               │
│ - Claude Code CLI                                           │
│ (Changes: per-project, frequently)                          │
├─────────────────────────────────────────────────────────────┤
│ Layer 3: TOOLS (Language-Specific)                          │
│ - Python + UV                                               │
│ - Node.js + npm/pnpm                                        │
│ - Go toolchain                                              │
│ - Rust toolchain                                            │
│ (Changes: when adding language support)                     │
├─────────────────────────────────────────────────────────────┤
│ Layer 2: BASICS                                             │
│ - Git, GitHub CLI                                           │
│ - tmux, neovim                                              │
│ - ripgrep, fd, bat, jq, fzf                                 │
│ - User setup, XDG directories                               │
│ (Changes: rarely)                                           │
├─────────────────────────────────────────────────────────────┤
│ Layer 1: BUILDER                                            │
│ - Base OS (Fedora)                                          │
│ - System packages, compilers                                │
│ - Build essentials                                          │
│ (Changes: on OS updates only)                               │
└─────────────────────────────────────────────────────────────┘
```

**Benefits:**
- **Cache efficiency:** Lower layers change less frequently, maximizing cache hits
- **Modularity:** Language tools can be swapped or updated independently
- **Build speed:** Only rebuild from the layer that changed
- **Composability:** Teams can extend with custom project layers

### Containerfile (Multi-Stage)

```dockerfile
# ============================================================
# LAYER 1: BUILDER - Base OS and build essentials
# ============================================================
FROM fedora:latest AS builder

RUN dnf install -y \
    gcc gcc-c++ make cmake \
    openssl-devel zlib-devel \
    && dnf clean all

# ============================================================
# LAYER 2: BASICS - Core tools and user setup
# ============================================================
FROM fedora:latest AS basics

# Core development tools
RUN dnf install -y \
    git gh tmux neovim \
    procps-ng which curl wget \
    && dnf clean all

# Modern CLI utilities
RUN dnf install -y \
    ripgrep fd-find bat jq fzf \
    && dnf clean all

# Create user with XDG structure
RUN useradd -m -s /bin/bash claude
RUN mkdir -p /home/claude/.config \
             /home/claude/.local/bin \
             /home/claude/.local/share \
             /home/claude/.local/state \
             /home/claude/.cache \
    && chown -R claude:claude /home/claude

# XDG environment
ENV XDG_CONFIG_HOME=/home/claude/.config
ENV XDG_DATA_HOME=/home/claude/.local/share
ENV XDG_STATE_HOME=/home/claude/.local/state
ENV XDG_CACHE_HOME=/home/claude/.cache

# ============================================================
# LAYER 3: TOOLS - Language-specific toolchains
# ============================================================
FROM basics AS tools

# --- Python + UV ---
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# --- Node.js (via fnm) ---
RUN curl -fsSL https://fnm.vercel.app/install | bash -s -- --install-dir /usr/local/bin
RUN /usr/local/bin/fnm install 20 && /usr/local/bin/fnm default 20
ENV PATH="/root/.local/share/fnm/aliases/default/bin:$PATH"

# --- Go ---
RUN dnf install -y golang && dnf clean all
ENV GOPATH=/home/claude/go
ENV PATH="$GOPATH/bin:/usr/local/go/bin:$PATH"

# --- Rust ---
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:$PATH"

# ============================================================
# LAYER 4: PROJECT - Claude team container specifics
# ============================================================
FROM tools AS project

# Claude Code CLI
RUN npm install -g @anthropic-ai/claude-code

# Copy entrypoint and helper scripts
COPY entrypoint.sh /usr/local/bin/
COPY scripts/ /usr/local/bin/
RUN chmod +x /usr/local/bin/*.sh

# Switch to non-root user
USER claude
WORKDIR /home/claude

# Default command
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["workstation"]
```

### Building Specific Layers

```bash
# Build everything
podman build -t claudeteam:latest .

# Build up to tools layer (for caching)
podman build --target tools -t claudeteam:tools .

# Build with specific language support only (future)
podman build --build-arg LANGUAGES="python,node" -t claudeteam:py-node .
```

### Entrypoint Script

```bash
#!/bin/bash
set -e

# Get username from environment or whoami
USER_NAME="${CLAUDE_USER:-$(whoami)}"
MODE="${1:-workstation}"
PROJECT="${2:-}"
AGENTS="${3:-2}"

# Ensure ~/.claude symlink exists
if [ ! -L "$HOME/.claude" ]; then
    ln -sf /workspace/team-settings "$HOME/.claude"
fi

# Ensure state directories exist
mkdir -p "$XDG_STATE_HOME/agent-context"

case "$MODE" in
    workstation)
        exec tmux new-session -s "ws-${PROJECT:-team}" \
            "cd /workspace/team-settings && claude" \; \
            split-window -h "cd /workspace && bash" \; \
            select-pane -t 0
        ;;
    agent)
        # Create worktrees if needed
        for i in $(seq 1 "$AGENTS"); do
            WORKTREE="/workspace/worktrees/${PROJECT}/${USER_NAME}-a.${i}"
            if [ ! -d "$WORKTREE" ]; then
                cd "/workspace/${PROJECT}"
                git worktree add "$WORKTREE" -b "${USER_NAME}-a.${i}" 2>/dev/null || true
            fi
        done
        
        # Build tmux command
        TMUX_CMD="tmux new-session -s claude-${PROJECT}-${USER_NAME}"
        for i in $(seq 1 "$AGENTS"); do
            WORKTREE="/workspace/worktrees/${PROJECT}/${USER_NAME}-a.${i}"
            if [ "$i" -eq 1 ]; then
                TMUX_CMD="$TMUX_CMD \"cd $WORKTREE && AGENT_ID=${USER_NAME}-a.${i} claude\""
            else
                TMUX_CMD="$TMUX_CMD \; split-window \"cd $WORKTREE && AGENT_ID=${USER_NAME}-a.${i} claude\""
            fi
        done
        
        # Arrange panes
        if [ "$AGENTS" -eq 2 ]; then
            TMUX_CMD="$TMUX_CMD \; select-layout even-horizontal"
        elif [ "$AGENTS" -eq 4 ]; then
            TMUX_CMD="$TMUX_CMD \; select-layout tiled"
        fi
        
        eval "$TMUX_CMD"
        ;;
    shell)
        exec bash
        ;;
    *)
        echo "Unknown mode: $MODE"
        echo "Usage: $0 [workstation|agent|shell] [project] [agents]"
        exit 1
        ;;
esac
```

## Host Tooling

### claude-team CLI

The `claude-team` script (`~/.local/bin/claude-team`) manages container lifecycle:

```bash
Claude Team Container - Multi-repo, multi-agent team workspace

Usage: claude-team [OPTIONS] MODE [PROJECT]

Modes:
    workstation     Single workspace (team-config + shell)
    agent           Multi-agent mode with worktrees (default: 2 agents)
    shell           Just a shell in the container
    build           Build the container image
    validate        Validate workspace structure
    init            Initialize workspace (generate Makefile)

Options:
    -w, --workspace PATH    Workspace directory (default: current dir)
    -n, --agents N          Number of agents: 2 or 4 (default: 2)
    -p, --project NAME      Project to work on (required for agent mode)
    -t, --team-config DIR   Team config directory name (default: auto-detect)
    -f, --firewall          Enable firewall in container
    --yolo                  Skip permission prompts in Claude
    --build                 Rebuild container image before starting
    --dry-run               Show what would be done without executing
    -v, --verbose           Verbose output
```

**Key features:**
- Auto-detects team config repo (looks for `claude/config/CLAUDE.md`)
- Uses `$(whoami)` for user identity
- Creates user-specific credential directories automatically
- Attaches to existing container if already running
- `init` command generates a workspace Makefile from template

### Workspace Makefile (Auto-Generated)

The `claude-team init` command generates a Makefile from the template at `~/.dotfiles/local/lib/claude-team-makefile-template`:

```makefile
# Usage
make help              # Show available commands
make workstation       # Start workstation mode
make run PROJECT=X     # Start 2 agents on project X
make run4 PROJECT=X    # Start 4 agents on project X
make shell             # Shell-only container
make validate          # Check workspace structure
make info              # Show workspace info
make build             # Build container image
make clean             # Stop all team containers
make worktrees         # List all worktrees
```

## Workflow Examples

### Setting Up a New Team Workspace

```bash
# On host (macOS)
mkdir -p ~/wc/myproject && cd ~/wc/myproject

# Clone team config repo (must have claude/config/ structure)
git clone git@github.com:myorg/team-dotfiles.git

# Clone project repos
git clone git@github.com:myorg/project-alpha.git
git clone git@github.com:myorg/project-beta.git

# Initialize workspace (generates Makefile)
claude-team init

# Output:
# [claude-team] Generating Makefile...
# [claude-team] ✓ Created: /Users/alice/wc/myproject/Makefile
# [claude-team]
# [claude-team] Available commands:
# [claude-team]   make workstation    - Start team config workspace
# [claude-team]   make run PROJECT=X  - Start 2 agents on project X
# [claude-team]   make run4 PROJECT=X - Start 4 agents on project X
# [claude-team]   make shell          - Start shell container
# [claude-team]   make validate       - Validate workspace
# [claude-team]   make info           - Show workspace info
# [claude-team]
# [claude-team] Projects detected: project-alpha project-beta
```

### Daily Development Flow

```bash
cd ~/wc/myproject

# Using Makefile (recommended)
make workstation                    # Edit team config
make run PROJECT=project-alpha      # 2 agents on project-alpha
make run4 PROJECT=project-beta      # 4 agents on project-beta

# Using claude-team directly
claude-team workstation
claude-team agent -p project-alpha
claude-team agent -p project-alpha -n 4
```

### First-Time Authentication

```bash
# Start shell to authenticate Claude
make shell
# Or: claude-team shell

# Inside container
claude auth login
# Follow OAuth flow in browser

# Credentials saved to mounted volume
# Future containers will have auth automatically
```

### Complete Quick Start

```bash
# 1. Create project folder
mkdir -p ~/wc/project1 && cd ~/wc/project1

# 2. Clone team settings (must have claude/config/CLAUDE.md)
git clone git@github.com:myorg/dotfiles.git

# 3. Clone projects
git clone git@github.com:myorg/FRANK.git

# 4. Initialize (generates Makefile)
claude-team init

# 5. Start container and authenticate
make shell
claude auth login    # One-time OAuth

# 6. Start working
make workstation              # Team config workspace
make run PROJECT=FRANK        # 2 agents on FRANK
```

### Multi-User Scenario

```bash
# Alice starts her agents
CLAUDE_USER=alice claude-team agent project-alpha 2
# Creates worktrees: alice-a.1, alice-a.2

# Bob starts his agents (different machine or terminal)
CLAUDE_USER=bob claude-team agent project-alpha 2
# Creates worktrees: bob-a.1, bob-a.2

# Both can work in parallel without conflicts
```

## Authentication

### GitHub CLI (Mounted from Host)

GitHub authentication is **inherited from the host system** by mounting the gh config directory:

```bash
-v "$HOME/.config/gh:/home/claude/.config/gh:ro"
```

**How it works:**
- The host's `~/.config/gh/` contains `hosts.yml` with OAuth tokens
- Mounted read-only (`:ro`) into the container at the same XDG path
- `gh` CLI in container uses these credentials automatically

**Verification:**
```bash
# On host - ensure you're authenticated
gh auth status

# In container - should show same auth
gh auth status
```

**Requirements:**
- Host must have `gh auth login` completed before starting container
- Token scopes needed: `repo`, `read:org`, `workflow` (for PR/issue management)

**Security note:** Mounting read-only prevents the container from modifying or leaking credentials. The token is never written to container-local storage.

### Anthropic/Claude Code (In-Container Login)

Claude Code authentication **must be performed inside the container** — there is currently no way to pre-provision or mount Anthropic credentials from the host.

**First-time setup:**
```bash
# Start container in shell mode
claude-team shell

# Inside container, authenticate
claude auth login
# Follow OAuth flow in browser
# Credentials stored in ~/.config/claude/ (container-local)
```

**Credential persistence options:**

1. **Ephemeral (default):** Credentials lost when container is removed. Re-authenticate each session.

2. **Persistent volume:** Mount a host directory for Claude credentials:
   ```bash
   # Create persistent credential storage on host
   mkdir -p ~/.claude-credentials
   
   # Add to podman run:
   -v "$HOME/.claude-credentials:/home/claude/.config/claude:z"
   ```

3. **Named volume:** Use a Podman named volume for isolation:
   ```bash
   # Create named volume
   podman volume create claude-auth
   
   # Add to podman run:
   -v claude-auth:/home/claude/.config/claude
   ```

**Multi-user considerations:**
- Each user needs their own Anthropic authentication
- Credentials should NOT be shared between users
- Use user-specific volume names: `claude-auth-${USER}`

### Authentication Summary

| Service | Method | Persistence | Source |
|---------|--------|-------------|--------|
| GitHub (`gh`) | Mounted from host | Host filesystem | `~/.config/gh` (read-only) |
| Anthropic (`claude`) | OAuth in container | Volume mount | `~/.config/claude` |

### Updated Wrapper Script (with auth mounts)

```bash
# In claude-team wrapper, updated podman run:
exec podman run --rm -it \
    --name "claude-${MODE}-${PROJECT:-team}-${USER_NAME}" \
    -v "$WORKSPACE:/workspace:z" \
    -v "$HOME/.config/gh:/home/claude/.config/gh:ro" \
    -v "$HOME/.claude-credentials/${USER_NAME}:/home/claude/.config/claude:z" \
    -e "CLAUDE_USER=$USER_NAME" \
    $FIREWALL \
    "$CONTAINER_IMAGE" \
    "$MODE" "$PROJECT" "$AGENTS"
```

**First-run initialization:**
```bash
# Ensure credential directories exist
mkdir -p "$HOME/.claude-credentials/$(whoami)"
```

## Security Considerations

### Firewall Mode

When started with `-f/--firewall`, the container has `NET_ADMIN` capability for firewall rules:

```bash
# In container (if firewall enabled)
iptables -A OUTPUT -p tcp --dport 443 -d api.anthropic.com -j ACCEPT
iptables -A OUTPUT -p tcp --dport 443 -d github.com -j ACCEPT
iptables -A OUTPUT -j DROP
```

### Workspace Isolation

- Each user's worktrees are isolated by naming convention
- Swarm job claiming is atomic (flock-based)
- GitHub branch protection prevents direct pushes

## Configuration Files

### team-settings/settings.json

```json
{
  "permissions": {
    "allow": [
      "Bash(git:*)",
      "Bash(gh:*)",
      "Bash(uv:*)",
      "Bash(npm:*)",
      "Bash(cargo:*)",
      "Bash(go:*)"
    ],
    "deny": []
  },
  "hooks": {
    "SessionStart": [
      {"command": "swarm-hook register"}
    ],
    "PostToolUse": [
      {"command": "swarm-hook hook"}
    ]
  }
}
```

### team-settings/CLAUDE.md

```markdown
# Team Agent Instructions

## Identity
You are part of a collaborative agent team working on multiple projects.

## Coordination
- Use GitHub Issues for tracking work (`gh issue list`, `gh issue view`)
- Use `/take #N` to claim issues and create swarm jobs
- Use `/pr` to create pull requests when work is complete
- Use `/merge` to merge approved PRs and signal other agents

## Worktrees
- Your worktree is your isolated workspace
- Always rebase on main before starting work: `git pull --rebase origin main`
- Never work directly on main

## Multi-Language Support
- Python: Use `uv` for package management
- Node.js: Use `npm` or `pnpm`
- Go: Use `go mod`
- Rust: Use `cargo`
```

## Integration with Agent System

This container setup integrates with the existing agent system:

| Component | Container Location | Host Location |
|-----------|-------------------|---------------|
| Team Settings | `/workspace/team-settings` → `~/.claude` | `~/wc/team-workspace/team-settings` |
| Swarm State | `~/.local/state/agent-context/` | In-container only |
| Job Queue | `~/.local/state/agent-context/{project}/jobs/` | In-container only |
| Events Log | `~/.local/state/agent-context/{project}/events.log` | In-container only |
| Worktrees | `/workspace/worktrees/{project}/{user}-a.{n}/` | `~/wc/team-workspace/worktrees/` |

## Summary

The Claude Team Container provides:

1. **XDG-compliant** containerized development environment
2. **Team settings** shared via symlinked repo at `~/.claude`
3. **Multi-repo** workspace mounted from host macOS
4. **Multi-language** support (Python/UV, Go, Rust, TypeScript, JavaScript)
5. **GitHub-based** external coordination (Issues, PRs)
6. **Worktree-based** internal coordination (swarm jobs, agent isolation)
7. **User-specific** agent naming (`{user}-a.{n}`)
8. **Multiple start modes** (workstation, agent, shell)
9. **Firewall support** for security
10. **Persistent OAuth** authentication

Teams can run multiple containers simultaneously, each in different modes, with isolated worktrees per user while sharing the same codebase and team configuration.
