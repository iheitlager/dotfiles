# Claude Sandbox Container

Podman container for running Claude CLI in an isolated environment with Python 3.12 + UV support.

## Quick Start

```bash
# Build
make build

# Run
make run              # Single session
make run-multi N=3    # Three sessions

# Or use commands
cs                    # Single session (alias)
cs3                   # Three sessions (alias)
```

## Documentation

See **[~/.dotfiles/docs/claude-sandbox.md](../../docs/claude-sandbox.md)** for complete documentation.

## Features

- Python 3.12 with UV package manager
- Node.js + Claude CLI
- Multi-agent tmux sessions
- Optional network firewall
- Auto-mounted credentials
