# VS Code Dev Container Configuration

This directory provides VS Code Dev Containers support for the Claude Sandbox.

## Quick Start with VS Code

1. **Install Prerequisites**:
   - [Visual Studio Code](https://code.visualstudio.com/)
   - [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
   - Docker or Podman

2. **Open in Container**:
   - Open this directory in VS Code
   - Click "Reopen in Container" when prompted
   - Or: `Cmd+Shift+P` → "Dev Containers: Reopen in Container"

3. **Start Claude**:
   ```bash
   claude
   ```

## Configuration Details

- **Base Image**: Same Containerfile used by Podman setup
- **User**: Runs as `agent` (non-root)
- **Mounts**:
  - `~/.config/claude` → `/home/agent/.config/claude` (credentials)
  - `~/.cache/uv` → `/home/agent/.cache/uv` (Python packages)
- **Firewall**: Disabled by default (set `ENABLE_FIREWALL=1` in devcontainer.json to enable)
- **Shell**: zsh with oh-my-zsh
- **Python**: 3.12 with UV package manager

## VS Code Extensions

Pre-installed extensions:
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Ruff (charliermarsh.ruff)

## Firewall Security

⚠️ **Important**: Firewall is disabled by default for compatibility. To enable:

1. Edit `devcontainer.json`:
   ```json
   "containerEnv": {
     "ENABLE_FIREWALL": "1"
   }
   ```

2. Add to `devcontainer.json`:
   ```json
   "runArgs": ["--privileged"]
   ```

3. Rebuild container

## Differences from Podman Setup

| Feature | Podman (make run) | VS Code DevContainer |
|---------|-------------------|----------------------|
| Multi-session | ✅ tmux support | ❌ Single session only |
| Firewall | Optional | Optional |
| Credential sync | 3 strategies | Mount only |
| OAuth injection | ✅ From Keychain | ❌ Not supported |
| Startup speed | Fast | Slower (VS Code overhead) |
| IDE integration | Manual | ✅ Native VS Code |

## Customization

Edit `devcontainer.json` to:
- Add VS Code extensions (`extensions` array)
- Change VS Code settings (`settings` object)
- Add environment variables (`containerEnv`)
- Mount additional volumes (`mounts` array)
- Run post-create commands (`postCreateCommand`)

## Troubleshooting

### Container won't start
- Ensure `~/.config/claude` exists: `mkdir -p ~/.config/claude`
- Check Docker/Podman is running
- Try: `Cmd+Shift+P` → "Dev Containers: Rebuild Container"

### Claude authentication fails
- Authenticate on host first: `claude` (outside container)
- Credentials at `~/.config/claude/` will be automatically mounted

### Permission errors
- Check file ownership: `ls -la ~/.config/claude`
- Container runs as `agent` (uid 1000)

## Related Documentation

- [Main Documentation](../../docs/claude-sandbox.md)
- [VS Code Dev Containers Docs](https://code.visualstudio.com/docs/devcontainers/containers)
- [Official Claude Code DevContainer](https://github.com/anthropics/claude-code/tree/main/.devcontainer)
