# Claude Sandbox Container

Podman-compatible container for running Claude CLI in an isolated, secure environment with UV and Python support.

## Features

- **Python 3.12** with UV package manager
- **Claude CLI** via native installer (no Node.js/npm dependency)
- **Multi-stage build** with BuildKit cache support for fast rebuilds
- **XDG Base Directory compliant** (`~/.config/claude`, `~/.cache/uv`)
- **Persistent UV cache** mounted from host for instant package installs
- **Network firewall** restricting access to approved domains only (optional)
- **Multi-agent support** via launch script with tmux sessions
- **Development tools**: git, gh, fzf, git-delta, nano, vim
- **Non-root user** (agent) for security
- **Optimized layers** - no build-essential or Node.js in final image

## Architecture

### Multi-Stage Build

The container uses a two-stage build process:

1. **Builder stage**: Downloads Claude CLI, git-delta, and UV installer
2. **Runtime stage**: Copies binaries from builder, installs runtime dependencies

**Benefits**:
- Smaller final image (no build tools in runtime)
- Faster rebuilds with BuildKit layer caching
- Cleaner separation of build vs runtime dependencies

### XDG Base Directory Compliance

The container follows the [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html):

```bash
XDG_CONFIG_HOME=/home/agent/.config    # Configuration files
XDG_CACHE_HOME=/home/agent/.cache      # Cache files
XDG_DATA_HOME=/home/agent/.local/share # Data files
XDG_STATE_HOME=/home/agent/.local/state # State files
```

**Host mappings**:
- `~/.config/claude` → Container config directory
- `~/.cache/uv` → Container UV cache (persistent, fast)
- `~/.claude.json` → Legacy credentials file (backward compatibility)

### BuildKit Cache Optimization

During build, UV uses BuildKit cache mounts for instant package installation:

```dockerfile
RUN --mount=type=cache,target=/home/agent/.cache/uv \
    uv pip install --system pip setuptools wheel
```

This means common Python packages are cached **during image build**, making rebuilds extremely fast.

## Quick Start

### Build & Run (Makefile)

```bash
cd ~/.dotfiles/containers/claude-sandbox

# Build the container
make build

# Run single Claude session (credentials auto-mounted)
make run

# Run 3 Claude sessions in parallel (tmux)
make run-multi N=3

# Run with firewall (requires root podman)
make run-firewall
```

### Command & Aliases

The `claude-sandbox` command is available in `local/bin/`:

```bash
claude-sandbox          # Single session
claude-sandbox -n2      # Two sessions

# Or use aliases from claude/bash_aliases
cs                      # Same as claude-sandbox
cs2                     # Two sessions
cs3                     # Three sessions
cs4                     # Four sessions
```

## Credentials

### Authentication Setup

**Credentials are COPIED, not mounted** - Your host credentials remain isolated and protected!

**First Run**: Authenticate once on your host system:

1. Outside the container, run `claude` on your host to authenticate
2. Credentials are saved to `~/.config/claude/` and `~/.claude.json` on your **host** (XDG-compliant)

**Subsequent Runs**: Credentials are automatically copied into each container instance!

### How It Works (Copy-on-Start, Default ✓)

**Recommended** - Credentials are copied from host into each container at startup:

```bash
make run          # Credentials copied from ~/.config/claude to container
```

**Pros**:
- Host credentials isolated and protected from container changes
- No authentication needed in container
- Safe for parallel instances

**Cons**:
- Changes inside container don't persist (but this is usually what you want!)
- Need to re-authenticate on host if credentials expire

### Manual Copy (Advanced)

If you need to manually copy credentials to a running container:

```bash
# Terminal 1: Start container without credential access
make run-no-mount

# Terminal 2: Copy credentials in
make copy-creds

# Or use the script directly
./copy-credentials.sh container-name
```

### Verify Credentials

Inside the container (XDG-compliant paths):

```bash
ls -la ~/.claude.json            # Legacy credentials file
ls -la ~/.config/claude/         # XDG config directory
```

## Manual Usage (Podman Commands)

### Build the Container

Build with BuildKit support for cache mounts:

```bash
cd ~/.dotfiles/containers/claude-sandbox
BUILDKIT_PROGRESS=plain podman build --layers=true -t claude-sandbox -f Containerfile .

# Or use the Makefile
make build
```

### Run Single Session

XDG-compliant mounts:

```bash
podman run -it --rm \
  -v $(pwd):/workspace/$(basename $(pwd)) \
  -v ~/.config/claude:/tmp/host-claude-creds/config:ro \
  -v ~/.claude.json:/tmp/host-claude-creds/claude.json:ro \
  -v ~/.cache/uv:/home/agent/.cache/uv \
  --network="host" \
  -w /workspace/$(basename $(pwd)) \
  claude-sandbox
```

### Run Multi-Agent Sessions

```bash
podman run -it --rm \
  -v $(pwd):/workspace/$(basename $(pwd)) \
  -v ~/.config/claude:/tmp/host-claude-creds/config:ro \
  -v ~/.claude.json:/tmp/host-claude-creds/claude.json:ro \
  -v ~/.cache/uv:/home/agent/.cache/uv \
  --network="host" \
  -w /workspace/$(basename $(pwd)) \
  claude-sandbox -n2
```

This starts 2 Claude sessions in separate tmux windows. All sessions share the UV cache for instant package installation.

## Python & UV Support

### Basic Usage

The container includes Python 3.12 and UV package manager with **persistent cache** for fast package installation:

```bash
# Inside container
uv --version          # Check UV version
python --version      # Python 3.12

# Create virtual environment
uv venv

# Install packages (cached across container runs!)
uv pip install requests pytest

# Run with uv
uv run pytest tests/
```

**Cache Performance**: The UV cache at `~/.cache/uv` is mounted from your host, so packages are cached across container instances. First install is fast, subsequent installs are nearly instant.

### UV Project Workflow

```bash
# Create project with UV
uv init my-project
cd my-project
uv add requests pytest

# Run with UV
uv run python main.py
uv run pytest

# Sync dependencies
uv sync
```

### UV Cache Details

**Cache Location**: `~/.cache/uv` (host) → `/home/agent/.cache/uv` (container)

**Why This Matters**:
- First `uv add requests`: Downloads and caches package (~1-2s)
- Next time in ANY container: Instant install from cache (~0.1s)
- Cache shared across all your container instances
- Works great for multi-agent workflows

**Cache Size**: UV's cache is typically 100-500MB depending on packages used. This is shared across all projects and container instances.

**Clear Cache** (if needed):
```bash
# On host
rm -rf ~/.cache/uv

# In container
rm -rf ~/.cache/uv
```

## Multi-Session Tmux Navigation

The `launch-claude.sh` script supports:

- **Single session**: `claude-sandbox` (default)
- **Multi-session**: `claude-sandbox -n<NUM>` (e.g., `-n2`, `-n5`)
- **Pass args to Claude**: `claude-sandbox -n2 --model opus`

### Tmux Controls

When running with `-n2` or more:

- `Ctrl-b n` - Next window
- `Ctrl-b p` - Previous window
- `Ctrl-b 1` - Window 1 (first Claude)
- `Ctrl-b 2` - Window 2 (second Claude)
- `Ctrl-b d` - Detach (container keeps running)
- `Ctrl-b &` - Kill current window
- `Ctrl-d` - Exit (in a window, kills that Claude session)
- `tmux attach -t claude-swarm` - Reattach to detached session

## Security Features

### Network Firewall

**Default**: Firewall **disabled** (for rootless Podman compatibility)

**Enable firewall**: Set `ENABLE_FIREWALL=1` and use `--privileged`

When enabled, the firewall restricts outbound traffic to:

- GitHub (web, API, git)
- Anthropic API
- PyPI and pythonhosted.org
- Astral.sh (for UV)
- Sentry, Statsig
- VS Code marketplace

**Note**: The npm registry is still whitelisted in `init-firewall.sh` but can be safely removed since we no longer use npm for Claude CLI installation.

All other domains are blocked.

### Enable Firewall (Requires Root Podman)

```bash
# Using Makefile (recommended)
make run-firewall

# Or manually (XDG-compliant)
podman run -it --rm \
  -e ENABLE_FIREWALL=1 \
  --privileged \
  -v $(pwd):/workspace/$(basename $(pwd)) \
  -v ~/.config/claude:/tmp/host-claude-creds/config:ro \
  -v ~/.claude.json:/tmp/host-claude-creds/claude.json:ro \
  -v ~/.cache/uv:/home/agent/.cache/uv \
  --network="host" \
  -w /workspace/$(basename $(pwd)) \
  claude-sandbox
```

**Firewall requirements**:
- Root Podman (not rootless)
- Linux with iptables/nftables
- `--privileged` flag

### Add Custom Domains

Edit `init-firewall.sh` and add domains to the loop around line 68, then rebuild:

```bash
podman build -t claude-sandbox -f Containerfile .
```

## Troubleshooting

### Container won't start

```bash
# Check if XDG config files exist
ls -la ~/.config/claude ~/.claude.json

# Ensure directories exist (Makefile does this automatically)
mkdir -p ~/.config/claude ~/.cache/uv

# Try without firewall (default)
make run
```

### Permission Errors

Ensure XDG configuration directories and files exist:

```bash
ls -la ~/.config/claude ~/.claude.json ~/.cache/uv
```

### Network Issues

Check if firewall is blocking needed domains. Firewall is disabled by default.

### UV command not found

UV is installed in `/home/agent/.local/bin` and should be in PATH automatically. If not:

```bash
source ~/.local/bin/env
```

### Multi-session tmux issues

```bash
# List sessions
tmux ls

# Attach to existing session
tmux attach -t claude-swarm

# Kill stuck session
tmux kill-session -t claude-swarm
```

## Customization

### Change Claude Version

Edit `Containerfile` line 8 in the builder stage (version without 'v' prefix):

```dockerfile
ARG CLAUDE_CODE_VERSION=2.1.29
```

Claude CLI is installed via native binary from Google Cloud Storage (official distribution).

**Note**: Binaries are **not** on GitHub releases - they're distributed via:
- Google Cloud Storage (used by container)
- Official install script: https://claude.ai/install.sh
- Homebrew Cask (macOS)

### Change Python Version

Edit `Containerfile` lines 6 and 44 (builder and runtime stages):

```dockerfile
FROM python:3.13-slim AS builder  # Line 6
...
FROM python:3.13-slim             # Line 44
```

### Change UV Version

Edit `Containerfile` line 9 in the builder stage:

```dockerfile
ARG UV_VERSION=0.6.0
```

Find UV versions at: https://github.com/astral-sh/uv/releases

### Change git-delta Version

Edit `Containerfile` line 10 in the builder stage:

```dockerfile
ARG GIT_DELTA_VERSION=0.18.2
```

### Pre-cache Additional Python Packages

To pre-install common packages in the image, edit `Containerfile` lines 130-134:

```dockerfile
RUN --mount=type=cache,target=/home/agent/.cache/uv,uid=1000,gid=1000 \
    uv pip install --system \
    pip \
    setuptools \
    wheel \
    pytest \
    ruff \
    mypy
```

These packages will be available immediately in all containers without installation delay.

## Build Performance

### Multi-Stage Benefits

The multi-stage build provides:

- **~250MB smaller images** by excluding build tools from runtime
- **Layer caching** means unchanged stages aren't rebuilt
- **Parallel downloads** in builder stage don't bloat final image

### BuildKit Cache Mounts

UV cache mounts during build provide:

```
First build:     ~120s (downloads binaries + packages)
Rebuild (code):  ~10s  (only copies changed scripts)
Rebuild (deps):  ~30s  (UV uses cache, very fast)
Clean rebuild:   ~90s  (BuildKit cache helps significantly)
```

### Runtime Cache Performance

```
uv pip install requests (first time):  ~1.5s
uv pip install requests (cached):      ~0.08s  (20x faster!)
```

## Files Overview

- `Containerfile` - Multi-stage container definition with BuildKit cache support
- `init-firewall.sh` - Network firewall script (optional, disabled by default)
- `launch-claude.sh` - XDG-compliant entry point with multi-session support
- `copy-credentials.sh` - Copy credentials to running container
- `Makefile` - Build and run shortcuts with BuildKit enabled
- `~/.dotfiles/docs/claude-sandbox.md` - This documentation

## Container Info

- **Base Image**: python:3.12-slim (multi-stage build)
- **User**: agent (non-root, uid 1000)
- **Working Directory**: /workspace
- **Shell**: zsh (with oh-my-zsh and plugins)
- **Timezone**: Europe/Amsterdam (configurable via TZ build arg)
- **XDG Compliant**: Yes (all config in ~/.config, cache in ~/.cache)
- **BuildKit**: Required for cache mount optimization
- **Auto-updates**: Disabled (pinned versions, rebuild to update)
- **Image Size**: ~600MB (optimized, no build tools in final image)

## Migrating from Old Setup

If you have an existing `~/.claude` directory (pre-XDG):

### Option 1: Let Claude Migrate Automatically

Modern Claude versions automatically migrate to XDG. Just run:

```bash
# On host
claude
```

Claude will detect `~/.claude` and migrate to `~/.config/claude` automatically.

### Option 2: Manual Migration

```bash
# On host
mkdir -p ~/.config/claude
cp -r ~/.claude/* ~/.config/claude/
# Keep ~/.claude.json where it is (still used)
```

### Verify Migration

```bash
ls -la ~/.config/claude/
ls -la ~/.claude.json
```

After migration, you can optionally remove the old directory:

```bash
# Only after verifying everything works!
rm -rf ~/.claude
```

## Tips

1. **Use multi-session for parallel work**: `make run-multi N=3`
2. **XDG-compliant by default**: All config in `~/.config`, cache in `~/.cache`
3. **UV cache persists**: Shared across all container instances for speed
4. **Firewall disabled by default**: Works with rootless Podman out of the box
5. **Mount additional volumes**: Add `-v /path/to/dir:/workspace/dir` to podman run
6. **Pass args to Claude**: `claude-sandbox --model opus`
7. **Keep sessions running**: Detach with `Ctrl-b d`, reattach later with `tmux attach -t claude-swarm`
8. **Use aliases**: `cs2` for quick 2-session launch
9. **BuildKit required**: Ensures optimal build performance with cache mounts
10. **Pre-cache packages**: Edit Containerfile to include commonly used Python packages
