# Claude Sandbox Container

Podman container for running Claude CLI in an isolated environment with Python 3.12 + UV support.

## ⚠️ Security Notice

**Firewall is disabled by default** for rootless Podman compatibility. This means the container has full network access to all domains.

- ✅ **Trusted workloads**: Use `make run` (default, no firewall)
- ⚠️ **Untrusted workloads**: Use `make run-firewall` (requires root Podman + `--privileged`)

For maximum security with untrusted code, enable the firewall to restrict network access to only approved domains (GitHub, PyPI, Anthropic API, etc.).

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
- Claude CLI (native binary, no Node.js)
- Multi-agent tmux sessions
- Optional network firewall
- Direct credential mounting (XDG-compliant)
