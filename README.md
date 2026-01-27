# iheitlager does dotfiles

## dotfiles

Your dotfiles are how you personalize your system. These are mine, specific for working on OSX.
My workflow is all about Homebrew, bash, Ghostty, tmux, vscode and Claude. It is also very XDG inspired. 

I believe everything should be versioned and scripted. Your laptop is your personal workstation for which you have to tweak your personal workflow. That way it can also become shareable between various workstations like your private and workmachines. As such I am a fan of the [dotfiles philosophy](https://dotfiles.github.io/). Therefore, I once started with [holmans dotfiles](https://github.com/holman/dotfiles) and did create my own. Mine however, is very much `bash` centric instead of `zsh`. Do not really know the value of another shell. 

This dotfile system is basic scripting with some topical modularization, no fancy agent convergence based config management. Over the years the system became infected by the use of IA. Modern CLI tools (eza, bat, ripgrep, fd, delta, fzf) provide rich colored output and better defaults. And some lengthy scripts where nicely produced by Claude. Nowadays it also contains my agent system.

## Quick Start

```sh
# Install homebrew on a clean Mac
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
eval "$(/opt/homebrew/bin/brew shellenv)"

# Clone and bootstrap
git clone git@github.com:iheitlager/dotfiles.git ~/.dotfiles
~/.dotfiles/script/bootstrap    # Configure dotfiles (run once)
dot                             # Install/upgrade packages
```

## Key Commands

| Command | Description |
|---------|-------------|
| `dot` | Install/upgrade Homebrew packages |
| `dot install <topic>` | Run install.sh for a topic (vim, osx, tmux, etc.) |
| `dot list` | Show available topics with install scripts |
| `dot -h` | Show all dot options |

## Features

### Terminal Stack
- **Ghostty** - GPU-accelerated terminal with Catppuccin colors
- **tmux** - Terminal multiplexer with status bar, git info, session persistence
- **bash** - Configured with modern completions and prompt

### Hotkey Daemon
Custom Python hotkey daemon for system-wide shortcuts:
- **Alt+Enter** - Launch Ghostty
- Runs as LaunchAgent, logs to `~/.local/state/hotkey/`
- Requires Accessibility permissions

### Editor Support
- **Neovim** - Configured with lazy.nvim, telescope, treesitter
- **VS Code** - Global keybindings (Ctrl+Alt+T for terminal)
- **vim** - Classic config with Vundle

### Agent System
Multi-agent swarm for Claude Code:
- `launch-agents` - Start/manage agent swarms
- `swarm-job` - Job queue management
- `swarm-watcher` - Queue monitoring daemon
- See [docs/agent-system.md](docs/agent-system.md) for details

## Topical Organization

Everything is organized by topic (vim, git, python, etc.). Each topic can have:

| File | Purpose |
|------|---------|
| `bash_aliases` | Shell aliases (loaded by .bash_profile) |
| `bash_env` | Environment variables |
| `bash_completion` | Tab completions |
| `brew_packages` | Homebrew packages (run with `dot`) |
| `install.sh` | Setup script (run with `dot install <topic>`) |
| `*.symlink` | Symlinked to `$HOME` |
| `config/` | Symlinked to `~/.config/<topic>/` |

## XDG Base Directory

This setup follows the [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/latest/):

| Variable | Location | Purpose |
|----------|----------|---------|
| `XDG_CONFIG_HOME` | `~/.config` | User configuration |
| `XDG_DATA_HOME` | `~/.local/share` | User data |
| `XDG_STATE_HOME` | `~/.local/state` | Logs, history, runtime state |
| `XDG_CACHE_HOME` | `~/.cache` | Cached data |

Use `xdg-info` to inspect XDG paths and app compliance.

## Directory Structure

```
~/.dotfiles/
├── bash/           # Shell configuration
├── claude/         # Claude Code config, agents, skills
├── config/         # XDG configs (ghostty, bat, ripgrep, tmux)
├── docker/         # Docker/Colima setup
├── git/            # Git config and aliases
├── local/bin/      # Custom scripts (dot, hotkey, launch-agents)
├── osx/            # macOS-specific settings
├── python/         # Python/uv configuration
├── tmux/           # tmux config with TPM plugins
├── vim/            # Vim/Neovim configuration
└── vscode/         # VS Code settings
```

## Secrets

Never commit secrets! Use `~/.config/secrets` (sourced by .bash_profile, excluded from git).
Git credentials go in `~/.local/gitconfig`.

## Credits
- Main inspiration: https://github.com/holman/dotfiles
- Dotfiles community: https://dotfiles.github.io/