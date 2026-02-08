# Dotfiles System Core Specification

**Domain:** Personal Development Environment
**Version:** 1.0.0
**Status:** Implemented
**Date:** 2026-02-07
**Owner:** Ilja Heitlager

## Overview

A modular, XDG-compliant dotfiles management system for macOS that provides topic-based organization, automated bootstrapping, package management, and shell integration. The system follows the Unix philosophy of simple, composable tools with predictable behavior.

### Philosophy

- **Topic-Based Modularization**: Each technology (bash, git, nvim, docker, etc.) is self-contained in its own directory with standardized files
- **XDG Base Directory Compliance**: All configuration follows the XDG specification for portability and cleanliness
- **Scripting Over Configuration Management**: Simple bash scripts instead of complex convergence-based tools (Ansible, Chef, etc.)
- **Version Control First**: All configuration is versioned in git for reproducibility and sharing across machines
- **Aggressive Caching**: Shell integrations are cached with mtime-based invalidation for fast startup times
- **Homebrew-Centric**: Package management through Homebrew with automatic discovery from all topics

### Key Capabilities

- **One-Command Bootstrap**: `script/bootstrap` sets up a new machine from scratch
- **Automatic Discovery**: Topics, packages, and shell configurations are discovered automatically without registration
- **Conflict Prevention**: Validates configuration structure before installation to prevent errors
- **Stale Cleanup**: Detects and removes orphaned symlinks from XDG directories
- **Maintenance Tool**: `dot` command provides package management, cache control, and topic installation

---

## RFC 2119 Keywords

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

---

## Requirements

### Requirement: Topic-Based Organization

The system MUST support modular topic-based organization where each topic is independently installable and discoverable.

#### Scenario: New Topic Added

- GIVEN a developer creates a new topic directory at `~/.dotfiles/newtopic/`
- WHEN they add standard files (bash_aliases, brew_packages, config/, install.sh)
- THEN the system SHALL automatically discover and integrate them on next shell start
- AND `dot list` SHALL include the new topic if install.sh exists
- AND `dot status` SHALL show the topic's features

#### Scenario: Topic Files Sourced in Order

- GIVEN a topic has bash_env, bash_aliases, and bash_completion files
- WHEN the shell starts
- THEN bash_env SHALL be sourced first (in .bash_profile for environment variables)
- AND bash_aliases SHALL be sourced second (in .bashrc for aliases)
- AND bash_completion SHALL be sourced last (in .bashrc for completions)

#### Scenario: Topic Removed

- GIVEN a topic directory is deleted from ~/.dotfiles
- WHEN the shell starts
- THEN the system SHALL continue without errors
- AND the cache SHALL be regenerated without the deleted topic

#### Scenario: Partial Topic Definition

- GIVEN a topic has only brew_packages (no shell integration)
- WHEN bootstrap runs
- THEN the system SHALL install packages without requiring other files
- AND SHALL NOT create empty shell integrations

### Requirement: XDG Base Directory Compliance

The system MUST follow the XDG Base Directory Specification for all configuration, data, state, and cache paths.

#### Scenario: Bootstrap Creates XDG Directories

- GIVEN a fresh Mac installation
- WHEN script/bootstrap runs
- THEN it SHALL create ~/.config (XDG_CONFIG_HOME)
- AND SHALL create ~/.local/share (XDG_DATA_HOME)
- AND SHALL create ~/.local/state (XDG_STATE_HOME)
- AND SHALL create ~/.cache (XDG_CACHE_HOME)
- AND SHALL create ~/.local/bin (user executables)

#### Scenario: Topic Config Symlinked

- GIVEN a topic has a config/ subdirectory (e.g., nvim/config/)
- WHEN bootstrap runs
- THEN it SHALL symlink ~/.dotfiles/<topic>/config/ to ~/.config/<topic>/
- AND the symlink SHALL be validated to point to an existing source

#### Scenario: General Config Symlinked

- GIVEN config/<app>/ exists in the general config directory (e.g., config/bat/)
- WHEN bootstrap runs
- THEN it SHALL symlink ~/.dotfiles/config/<app>/ to ~/.config/<app>/
- AND SHALL process all subdirectories under config/

#### Scenario: XDG Variables Exported

- GIVEN the shell starts
- WHEN bash_profile is sourced
- THEN all XDG variables SHALL be exported with correct defaults
- AND applications SHALL be able to reference them

### Requirement: Bootstrap Installation

The system MUST provide a one-time bootstrap process for new machines that is idempotent and safe.

#### Scenario: Fresh Install

- GIVEN a clean Mac with Homebrew installed
- WHEN script/bootstrap runs
- THEN it SHALL execute in order:
  1. Setup XDG directories
  2. Purge stale symlinks
  3. Validate config structure
  4. Setup local gitconfig
  5. Install brew packages (unless --no-brew)
  6. Install dotfiles (*.symlink)
  7. Link config directories
  8. Run topic installers (install.sh)
- AND SHALL report success/failure for each step

#### Scenario: Idempotent Execution

- GIVEN bootstrap has been run previously
- WHEN script/bootstrap runs again
- THEN it SHALL skip existing symlinks
- AND SHALL prompt for conflicts (overwrite/backup/skip)
- AND SHALL NOT duplicate work

#### Scenario: Conflict Detection

- GIVEN both config/nvim/ and nvim/config/ exist
- WHEN bootstrap runs
- THEN it MUST exit with error code 1
- AND MUST display conflicting topics with resolution instructions
- AND SHALL NOT proceed with installation

#### Scenario: Bootstrap Flags

- GIVEN bootstrap supports command-line flags
- WHEN run with --git flag
- THEN it SHALL force gitconfig regeneration
- WHEN run with --no-brew flag
- THEN it SHALL skip Homebrew package installation

### Requirement: Package Management (Homebrew)

The system MUST automatically discover and install Homebrew packages from all topics.

#### Scenario: Brew Packages Discovery

- GIVEN multiple topics have brew_packages files
- WHEN `dot` command runs
- THEN it SHALL find all brew_packages files using maxdepth 2
- AND SHALL source each brew_packages file in order
- AND SHALL collect all tap, brew, cask commands

#### Scenario: Brewfile Generation

- GIVEN packages have been installed
- WHEN `dot` completes installation
- THEN it SHALL export current state to ${XDG_DATA_HOME}/Brewfile
- AND the Brewfile SHALL include taps, formulae, and casks
- AND SHALL serve as cache for future installations

#### Scenario: Brewfile Usage

- GIVEN a Brewfile exists at ${XDG_DATA_HOME}/Brewfile
- WHEN `dot` runs without --new flag
- THEN it SHALL use `brew bundle --file=Brewfile`
- AND SHALL skip discovery and sourcing of brew_packages

#### Scenario: Force Regeneration

- GIVEN a Brewfile exists but is outdated
- WHEN `dot --new` runs
- THEN it SHALL ignore existing Brewfile
- AND SHALL rediscover all brew_packages
- AND SHALL regenerate Brewfile from scratch

### Requirement: Shell Integration

The system MUST aggregate and load shell configurations from all topics with proper ordering.

**Note**: Performance optimization through caching is detailed in the [Dotfiles Caching System Specification](../002-dotfiles-caching/spec.md).

#### Scenario: bash_env Sourced First

- GIVEN topics have bash_env files
- WHEN the shell starts and sources .bash_profile
- THEN it SHALL load all bash_env files (or cached equivalent)
- AND SHALL export environment variables before aliases load

#### Scenario: bash_aliases Sourced Second

- GIVEN topics have bash_aliases files
- WHEN .bashrc is sourced
- THEN it SHALL load all bash_aliases files (or cached equivalent)
- AND SHALL load after bash_env so aliases can reference environment variables

#### Scenario: bash_completion Sourced Last

- GIVEN topics have bash_completion files
- WHEN .bashrc is sourced
- THEN it SHALL load all bash_completion files (or cached equivalent)
- AND SHALL load after aliases for proper tab completion

### Requirement: Configuration Symlinks

The system MUST support two config directory patterns with conflict detection and validation.

#### Scenario: Topic-Specific Config Pattern

- GIVEN a topic has structure: <topic>/config/
- WHEN bootstrap runs link_config_files()
- THEN it SHALL create symlink: ~/.config/<topic>/ → ~/.dotfiles/<topic>/config/
- AND SHALL handle interactive prompts for conflicts

#### Scenario: General Config Pattern

- GIVEN config/<app>/ exists
- WHEN bootstrap runs link_config_files()
- THEN it SHALL create symlink: ~/.config/<app>/ → ~/.dotfiles/config/<app>/
- AND SHALL process all subdirectories under config/

#### Scenario: Config Conflict Validation

- GIVEN both patterns exist for the same topic (config/nvim and nvim/config)
- WHEN bootstrap runs validate_config_structure()
- THEN it SHALL detect the conflict
- AND SHALL list all conflicts with priorities (topic/config has precedence)
- AND SHALL exit with error code 1 before any installation
- AND SHALL provide resolution command (rm -rf config/<topic>)

#### Scenario: Symlink Overwrite Handling

- GIVEN a symlink target already exists
- WHEN bootstrap attempts to create symlink
- THEN it SHALL check if current symlink points to correct source
- IF correct, SHALL skip
- IF incorrect, SHALL prompt: [s]kip, [S]kip all, [o]verwrite, [O]verwrite all, [b]ackup, [B]ackup all
- AND SHALL respect user choice for remaining conflicts

### Requirement: Topic Installers

The system MUST execute topic-specific install.sh scripts with error handling.

#### Scenario: Install Script Execution

- GIVEN topics have install.sh files (e.g., bash/install.sh, osx/install.sh)
- WHEN bootstrap runs run_installers()
- THEN it SHALL find all install.sh files using maxdepth 2
- AND SHALL execute each with `sh -c "${src}"`
- AND SHALL log output to /tmp/dotfiles-install
- AND SHALL report success for each installer

#### Scenario: Installer Error Handling

- GIVEN an install.sh script exits with non-zero status
- WHEN bootstrap executes it
- THEN it SHALL display failure message
- AND SHALL show last 5 lines of /tmp/dotfiles-install
- AND SHALL exit bootstrap with code 1

#### Scenario: Manual Topic Installation

- GIVEN a topic has install.sh
- WHEN user runs `dot install <topic>`
- THEN it SHALL source the topic's install.sh directly
- AND SHALL report success or failure
- AND SHALL NOT affect other topics

#### Scenario: List Available Topics

- GIVEN multiple topics have install.sh
- WHEN user runs `dot list`
- THEN it SHALL display all topics with install.sh scripts
- AND SHALL show them in a readable list format

### Requirement: Cache Integration

The system MUST integrate with the dotfiles caching system for optimal performance.

**Note**: Detailed caching requirements are specified in the [Dotfiles Caching System Specification](../002-dotfiles-caching/spec.md).

#### Scenario: Cached Shell Integration

- GIVEN the shell starts
- WHEN bash_profile and bashrc are sourced
- THEN they SHALL check for cached shell integrations
- AND SHALL use cached versions when available and fresh
- AND SHALL regenerate caches automatically when stale

#### Scenario: Cache Control via dot Command

- GIVEN the dot command manages caches
- WHEN user runs `dot invalidate`
- THEN all shell integration caches SHALL be removed
- WHEN user runs `dot status`
- THEN cache status SHALL be displayed

### Requirement: Symlink Hygiene

The system MUST detect and remove stale symlinks in XDG directories.

#### Scenario: Stale Symlink Detection

- GIVEN XDG directories contain symlinks
- WHEN `dot purge` runs
- THEN it SHALL scan XDG_CONFIG_HOME, XDG_DATA_HOME, XDG_STATE_HOME, XDG_CACHE_HOME
- AND SHALL find symlinks with maxdepth 2
- AND SHALL test each symlink target for existence
- AND SHALL collect all broken symlinks

#### Scenario: Interactive Removal

- GIVEN stale symlinks are found
- WHEN `dot purge` runs (without --force)
- THEN it SHALL list all stale symlinks with their targets
- AND SHALL prompt "Remove these stale symlinks? [Y/n]"
- AND SHALL remove on confirmation
- AND SHALL skip on rejection

#### Scenario: Force Purge

- GIVEN stale symlinks exist
- WHEN `dot purge --force` runs
- THEN it SHALL remove all stale symlinks without prompting
- AND SHALL display removed symlinks
- AND SHALL be suitable for scripting

#### Scenario: Bootstrap Integration

- GIVEN bootstrap runs
- WHEN purge_stale_symlinks() is called
- THEN it SHALL run `dot purge --force` automatically
- AND SHALL log output to /tmp/dotfiles-purge
- AND SHALL report success/failure

### Requirement: Status Reporting

The system MUST provide comprehensive status information about the dotfiles installation.

#### Scenario: Complete Status Display

- GIVEN dotfiles are installed
- WHEN user runs `dot status`
- THEN it SHALL display:
  1. Shell cache status (files, sizes, ages, source counts)
  2. Brewfile status (path, tap/formula/cask counts)
  3. Homebrew status (prefix, installed counts)
  4. XDG paths (CONFIG, DATA, STATE, CACHE)
  5. Topics summary (with feature indicators: I=install, B=brew, A=aliases, E=env, C=completion, X=config)
  6. Outdated packages (first 5, with timeout)

#### Scenario: Fast Status Display

- GIVEN status is requested
- WHEN `dot status` runs
- THEN it SHALL complete in <2 seconds
- AND SHALL timeout brew outdated after 5 seconds
- AND SHALL use fast operations (grep -c, wc -l) instead of slow brew commands

---

## Current Implementation

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DOTFILES ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  SOURCE: ~/.dotfiles/                                       │
│  ├── <topic>/                    (19 topics)                │
│  │   ├── bash_aliases            → cached to ~/.cache       │
│  │   ├── bash_env                → cached to ~/.cache       │
│  │   ├── bash_completion         → cached to ~/.cache       │
│  │   ├── brew_packages           → aggregated to Brewfile   │
│  │   ├── install.sh              → run by bootstrap         │
│  │   ├── *.symlink               → linked to ~              │
│  │   └── config/                 → linked to ~/.configi     │
│  ├── config/<app>/               → linked to ~/.config      │
│  ├── local/                                                 │
│  │   ├── bin/                    (executables)              │
│  │   ├── lib/                    (shared libraries)         │
│  │   └── share/                  (static data)              │
│  └── script/                                                │
│      └── bootstrap               (one-time setup)           │
│                                                             │
│  COMMANDS:                                                  │
│  ├── script/bootstrap            Setup new machine          │
│  └── local/bin/dot               Package & cache mgmt       │
│                                                             │
│  XDG TARGET: (linked from dotfiles)                         │
│  ├── ~/.config/<topic>/          User configuration         │
│  ├── ~/.local/share/             User data, Brewfile        │
│  ├── ~/.local/state/             Logs, history              │
│  └── ~/.cache/dotfiles/          Shell caches               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
~/.dotfiles/
├── aws/                    # AWS CLI configuration
│   ├── bash_aliases
│   └── bash_env
├── bash/                   # Bash shell configuration
│   ├── bash_aliases
│   ├── bash_completion
│   ├── bash_env
│   ├── bash_profile.symlink
│   ├── bash_shortcuts*
│   ├── bashrc.symlink
│   ├── brew_packages
│   └── install.sh*
├── claude/                 # Claude Code agent system
│   ├── config/
│   │   ├── CLAUDE.md
│   │   ├── settings.json
│   │   ├── commands/
│   │   └── skills/
│   └── install.sh*
├── config/                 # General XDG configs
│   ├── bat/
│   ├── ghostty/
│   ├── pip/
│   ├── ripgrep/
│   └── swarm-daemon/
├── containers/             # Container tools
│   └── bash_aliases
├── docker/                 # Docker/Colima setup
│   ├── bash_aliases
│   ├── bash_env
│   ├── brew_packages
│   └── install.sh*
├── fzf/                    # Fuzzy finder
│   ├── bash_aliases
│   └── install.sh*
├── git/                    # Git configuration
│   ├── bash_aliases
│   ├── bash_completion
│   ├── bash_env
│   ├── brew_packages
│   ├── config/
│   ├── gitconfig.symlink
│   └── gitconfig.template
├── homebrew/               # Homebrew installation
│   └── brew_install.sh*
├── latex/                  # LaTeX tools
│   └── bash_aliases
├── local/                  # User-local files
│   ├── bin/                # Executables (dot, etc.)
│   ├── lib/                # Shared libraries
│   └── share/              # Static data
├── node/                   # Node.js configuration
│   └── bash_env
├── nvim/                   # Neovim configuration
│   ├── bash_shortcuts*
│   ├── config/             # Neovim config files
│   └── install.sh*
├── ollama/                 # Ollama AI configuration
│   └── bash_env
├── osx/                    # macOS system settings
│   ├── brew_packages
│   └── install.sh*
├── python/                 # Python/uv configuration
│   ├── bash_aliases
│   ├── bash_env
│   ├── brew_packages
│   └── install.sh*
├── ruby/                   # Ruby configuration
│   └── bash_env
├── tmux/                   # Tmux multiplexer
│   ├── bash_shortcuts*
│   ├── config/
│   └── install.sh*
├── tofu/                   # OpenTofu/Terraform
│   └── bash_aliases
├── vscode/                 # VS Code configuration
│   ├── bash_aliases
│   └── brew_packages
├── docs/                   # Documentation
│   ├── agent-system.md
│   ├── coloring.md
│   └── xdg_setup.md
├── script/                 # Setup scripts
│   └── bootstrap*
└── README.md
```

### Topic Files Reference

| File Type | Purpose | Loading Mechanism | Cached | Example |
|-----------|---------|-------------------|--------|---------|
| `bash_aliases` | Shell aliases and functions | Sourced by .bashrc | Yes (.cache/dotfiles/bash_aliases.sh) | `alias gs='git status'` |
| `bash_env` | Environment variables | Sourced by .bash_profile | Yes (.cache/dotfiles/bash_env.sh) | `export EDITOR=nvim` |
| `bash_completion` | Tab completion scripts | Sourced by .bashrc | Yes (.cache/dotfiles/bash_completion.sh) | `complete -F _git g` |
| `brew_packages` | Homebrew dependencies | Sourced by dot command | Yes (Brewfile) | `brew "ripgrep"` |
| `install.sh` | Topic-specific setup | Executed by bootstrap or `dot install` | No | Install plugins, set defaults |
| `*.symlink` | Dotfiles to link to $HOME | Symlinked by bootstrap | No | bash_profile.symlink → ~/.bash_profile |
| `config/` | XDG configuration directory | Symlinked by bootstrap | No | nvim/config → ~/.config/nvim |
| `bash_shortcuts` | Keyboard shortcuts docs | Executed by shortcuts command | Yes (.cache/dotfiles/shortcuts/) | Display keybindings |

### Special Directories

#### local/bin/ - User Executables

Contains custom scripts available in PATH:

| Script | Purpose |
|--------|---------|
| `dot` | Package manager, cache control, topic installation |
| `hotkey` | System-wide hotkey daemon (Python) |
| `shortcuts` | Display keyboard shortcuts for topics |
| `launch-agents` | Multi-agent swarm management |
| `swarm-job` | Job queue for agent coordination |
| `git-*` | Git utility scripts |

#### local/lib/ - Shared Libraries

Contains reusable code sourced by scripts:

| Library | Purpose |
|---------|---------|
| `shell-common.sh` | Common shell functions and utilities |
| `templates/` | Script templates for code generation |

#### local/share/ - Static Data

Contains non-executable data files:

| File | Purpose |
|------|---------|
| `Brewfile` | Generated Homebrew package list |
| `WORKSPACE_AGENT.md` | Workspace agent instructions |

#### config/ - General XDG Configs

For applications that don't warrant a dedicated topic:

| Directory | Application |
|-----------|-------------|
| `bat/` | Syntax highlighting cat alternative |
| `ghostty/` | Terminal emulator |
| `pip/` | Python package manager |
| `ripgrep/` | Fast grep alternative |
| `swarm-daemon/` | Agent coordination daemon |

---

## Topic Organization Conventions

### Standard Files

#### bash_aliases

**Purpose**: Define shell aliases and functions available in interactive shells.

**Loading**: Sourced by .bashrc, cached to `~/.cache/dotfiles/bash_aliases.sh`

**Format**:
```bash
# No shebang needed (sourced, not executed)
# Copyright and SPDX header

# Simple alias
alias gs='git status'

# Alias with options
alias ll='eza -la --git --icons'

# Function
function mkcd() {
    mkdir -p "$1" && cd "$1"
}

# Conditional alias
if command -v nvim &> /dev/null; then
    alias vim='nvim'
fi
```

**Rules**:
- No shebang (file is sourced)
- Use single quotes for aliases without variable expansion
- Use functions for complex logic
- Check command existence before aliasing
- Keep aliases short and memorable

#### bash_env

**Purpose**: Export environment variables required by applications.

**Loading**: Sourced by .bash_profile (login shells only), cached to `~/.cache/dotfiles/bash_env.sh`

**Format**:
```bash
# No shebang needed (sourced, not executed)
# Copyright and SPDX header

# Simple export
export EDITOR=nvim

# Path addition
export PATH="$HOME/.local/bin:$PATH"

# XDG override
export DOCKER_CONFIG="${XDG_CONFIG_HOME}/docker"

# Conditional export
if [ -d "$HOME/.cargo/bin" ]; then
    export PATH="$HOME/.cargo/bin:$PATH"
fi
```

**Rules**:
- No shebang (file is sourced)
- Only exports, no aliases or functions
- Loaded before bash_aliases (so aliases can reference env vars)
- Use `${VAR:-default}` for defaults

#### bash_completion

**Purpose**: Provide tab completion for commands and aliases.

**Loading**: Sourced by .bashrc after aliases, cached to `~/.cache/dotfiles/bash_completion.sh`

**Format**:
```bash
# No shebang needed (sourced, not executed)
# Copyright and SPDX header

# Use existing completion for alias
complete -F _git g

# Custom completion function
_my_command() {
    local cur="${COMP_WORDS[COMP_CWORD]}"
    COMPREPLY=( $(compgen -W "start stop restart" -- "$cur") )
}
complete -F _my_command mycommand
```

**Rules**:
- No shebang (file is sourced)
- Loaded after aliases (can reference aliases)
- Use existing completion functions when possible
- Test completions in clean shell

#### brew_packages

**Purpose**: Declare Homebrew dependencies for the topic.

**Loading**: Sourced by `dot` command, aggregated to Brewfile

**Format**:
```bash
# No shebang needed (sourced, not executed)
# Copyright and SPDX header

# Add tap if needed
tap "homebrew/cask-fonts"

# Install formula
brew "ripgrep"
brew "fd"

# Install cask
cask "visual-studio-code"

# Install with options (not common in modern Homebrew)
brew "vim", args: ["with-lua"]
```

**Rules**:
- No shebang (file is sourced)
- Use `tap`, `brew`, `cask` commands
- One package per line
- Comment complex or non-obvious packages
- Don't include dependencies (Homebrew handles this)

#### install.sh

**Purpose**: Perform topic-specific setup that can't be handled by symlinks.

**Loading**: Executed by bootstrap during initial setup, or by `dot install <topic>`

**Format**:
```bash
#!/usr/bin/env bash
# Copyright and SPDX header

# Set strict mode
set -e

# Create directories
mkdir -p "$HOME/.local/state/mytopic"

# Symlink non-convention files
ln -sf "$XDG_CONFIG_HOME/mytopic/config.json" "$HOME/.mytopic/config.json"

# Download external dependencies
if [ ! -d "$HOME/.mytopic/plugins" ]; then
    git clone https://github.com/author/plugin "$HOME/.mytopic/plugins"
fi

# Set macOS defaults
defaults write com.example.app setting -bool true

echo "✓ mytopic installed"
```

**Rules**:
- Must have shebang (executed as script)
- Use `set -e` for early exit on error
- Be idempotent (safe to run multiple times)
- Reference XDG variables
- Print success message
- Don't prompt user (bootstrap may be unattended)

#### *.symlink

**Purpose**: Files that should be symlinked directly to $HOME with a dot prefix.

**Loading**: Symlinked by bootstrap `install_dotfiles()` function

**Format**: Any file type, named with .symlink suffix

**Examples**:
- `bash_profile.symlink` → `~/.bash_profile`
- `bashrc.symlink` → `~/.bashrc`
- `gitconfig.symlink` → `~/.gitconfig`

**Rules**:
- Filename determines target: `<name>.symlink` → `~/.<name>`
- Use for files that MUST be in $HOME (shell init files)
- Prefer config/ for XDG-compliant apps
- Don't commit secrets (use .gitignore)

#### config/

**Purpose**: Configuration files/directories that follow XDG Base Directory spec.

**Loading**: Symlinked by bootstrap `link_config_files()` function

**Format**: Directory containing config files

**Examples**:
- `nvim/config/` → `~/.config/nvim/`
- `tmux/config/` → `~/.config/tmux/`
- `git/config/` → `~/.config/git/`

**Rules**:
- One config/ per topic (under topic directory)
- OR use config/<app>/ for apps without dedicated topic
- Bootstrap validates no conflicts between patterns
- Can contain any file structure (nested dirs, multiple files)

### Topic Examples

#### Full-Featured Topic: bash/

Shows all file types in use:

```
bash/
├── bash_aliases          # Extensive aliases (ll, gs, etc.)
├── bash_completion       # Tab completions for aliases
├── bash_env              # Environment (PATH, EDITOR)
├── bash_profile.symlink  # Login shell initialization
├── bash_shortcuts*       # Keyboard shortcuts documentation
├── bashrc.symlink        # Interactive shell initialization
├── brew_packages         # Terminal tools (bash, bash-completion)
└── install.sh*           # Setup bash completion
```

**Key Patterns**:
- Both .symlink files (shell requires them in ~/)
- All shell integration types (aliases, env, completion)
- Executable scripts (install.sh, bash_shortcuts)
- Package dependencies

#### Config-Heavy Topic: nvim/

Shows XDG config pattern with complex directory structure:

```
nvim/
├── bash_shortcuts*       # Neovim keybindings reference
├── config/               # → ~/.config/nvim/
│   ├── init.lua
│   ├── lazy-lock.json
│   └── lua/
│       ├── config/
│       │   ├── keymaps.lua
│       │   ├── lazy.lua
│       │   └── options.lua
│       └── plugins/
│           ├── colorscheme.lua
│           ├── telescope.lua
│           └── treesitter.lua
└── install.sh*           # Install lazy.nvim plugin manager
```

**Key Patterns**:
- No shell integration (aliases/env/completion)
- Complex nested config structure
- Plugin manager bootstrap in install.sh
- Documentation for keybindings

#### Minimal Topic: node/

Shows minimal topic with only environment:

```
node/
└── bash_env              # Export NODE_OPTIONS, npm config
```

**Key Patterns**:
- Single file sufficient for simple topics
- No packages (Node installed elsewhere)
- Just environment configuration

#### Shell-Integrated Topic: git/

Shows heavy shell integration with XDG config:

```
git/
├── bash_aliases          # Extensive git aliases (gs, ga, gc, etc.)
├── bash_completion       # Completions for aliases
├── bash_env              # GIT_EDITOR, signing config
├── brew_packages         # git, git-delta, gh CLI
├── config/               # → ~/.config/git/
│   └── ignore            # Global gitignore
├── gitconfig.symlink     # Main git config (includes local)
└── gitconfig.template    # Template for local config
```

**Key Patterns**:
- All shell integration types
- Both ~/.gitconfig (symlink) and ~/.config/git/ (XDG)
- Template file for user-specific config
- CLI tools in brew_packages

#### General Config: config/bat/

Shows general config pattern for apps without dedicated topic:

```
config/
├── bat/                  # → ~/.config/bat/
│   └── config
├── ghostty/              # → ~/.config/ghostty/
│   ├── bash_shortcuts*
│   └── config
├── pip/                  # → ~/.config/pip/
│   └── pip.conf
└── ripgrep/              # → ~/.config/ripgrep/
    └── config
```

**Key Patterns**:
- Apps without dedicated topic go under config/
- Each subdirectory becomes ~/.config/<app>/
- Can include bash_shortcuts for documentation
- Simple apps that don't need brew_packages or install.sh

### Naming Rules

#### Reserved Names

| Name | Purpose | Discoverable |
|------|---------|--------------|
| `bash_aliases` | Shell aliases | Yes (cached) |
| `bash_env` | Environment variables | Yes (cached) |
| `bash_completion` | Tab completions | Yes (cached) |
| `bash_shortcuts` | Keyboard shortcuts docs | Yes (cached) |
| `brew_packages` | Homebrew dependencies | Yes (aggregated) |
| `install.sh` | Topic installer | Yes (listed) |
| `config/` | XDG config directory | Yes (symlinked) |
| `*.symlink` | Home directory symlink | Yes (linked) |

#### Custom Files

Files not matching reserved names:
- Not automatically discovered or processed
- Can be referenced by install.sh or other scripts
- Examples: templates, helper scripts, documentation

#### Executable Bit

| File Type | Executable | Reason |
|-----------|------------|--------|
| bash_aliases | No | Sourced by shell |
| bash_env | No | Sourced by shell |
| bash_completion | No | Sourced by shell |
| bash_shortcuts | Yes | Executed by shortcuts command |
| brew_packages | No | Sourced by dot command |
| install.sh | Yes | Executed by bootstrap/dot |
| local/bin/* | Yes | User commands |

---

## Bootstrap Process

### Execution Order

1. **Setup XDG Directories** (`setup_xdg_dirs()`)
   - Creates ~/.config, ~/.local/share, ~/.local/state, ~/.cache, ~/.local/bin
   - Uses `mkdir -p` (idempotent)
   - Reports success for each directory

2. **Purge Stale Symlinks** (`purge_stale_symlinks()`)
   - Calls `dot purge --force` if dot command exists
   - Removes broken symlinks from XDG directories
   - Logs to /tmp/dotfiles-purge

3. **Validate Config Structure** (`validate_config_structure()`)
   - Scans for config/ subdirectories in topics
   - Checks if config/<topic>/ also exists (conflict)
   - Exits with error if conflicts found
   - Provides resolution instructions

4. **Setup Local Gitconfig** (`setup_gitconfig()`)
   - Prompts for name, email, SSH signing key
   - Creates ~/.local/gitconfig (not versioned)
   - Skips if exists (unless --git flag)

5. **Install Brew Packages** (`install_brew_packages()`)
   - Skipped if --no-brew flag
   - Calls `dot --new` to regenerate Brewfile
   - Installs all packages
   - Logs to /tmp/dotfiles-dot

6. **Install Dotfiles** (`install_dotfiles()`)
   - Finds all *.symlink files (maxdepth 2)
   - Links to $HOME with dot prefix
   - Prompts for conflicts (overwrite/backup/skip)

7. **Link Config Files** (`link_config_files()`)
   - Links <topic>/config/ → ~/.config/<topic>/
   - Links config/<app>/ → ~/.config/<app>/
   - Prompts for conflicts (overwrite/backup/skip)

8. **Run Installers** (`run_installers()`)
   - Finds all install.sh files (maxdepth 2)
   - Executes each with `sh -c`
   - Logs to /tmp/dotfiles-install
   - Exits on first failure

### Code Reference

All functions defined in `script/bootstrap`:

```
setup_xdg_dirs          → Line 53
purge_stale_symlinks    → Line 76
validate_config_structure → Line 95
setup_gitconfig         → Line 131
link_config_files       → Line 190
link_file               → Line 216 (helper)
install_dotfiles        → Line 291
install_brew_packages   → Line 303
run_installers          → Line 318
```

Main execution:
```
Line 353-362:
setup_xdg_dirs
purge_stale_symlinks
validate_config_structure
setup_gitconfig $FORCE_GIT
if [ "$SKIP_BREW" != "true" ]; then
  install_brew_packages
fi
install_dotfiles
link_config_files
run_installers
```

### Validation Checks

#### XDG Directory Structure

Bootstrap verifies all XDG directories are created:
- XDG_CONFIG_HOME (default: ~/.config)
- XDG_DATA_HOME (default: ~/.local/share)
- XDG_STATE_HOME (default: ~/.local/state)
- XDG_CACHE_HOME (default: ~/.cache)
- ~/.local/bin (not XDG spec, but convention)

#### Config Conflict Detection

Prevents both patterns for same topic:
```
Conflict Example:
  ❌ config/nvim  (should be removed)
  ✅ nvim/config  (has precedence)

Resolution: rm -rf $DOTFILES/config/nvim
```

#### Symlink Validation

Before creating symlink:
1. Check if target exists
2. If exists, check if it points to correct source
3. If correct, skip
4. If incorrect, prompt user

---

## The dot Command

### Commands Reference

```
Usage: dot [COMMAND] [OPTIONS]

COMMANDS:
  (none)            Install Homebrew packages (default)
  install <topic>   Run install.sh for specific topic
  list              List topics with install.sh scripts
  status            Show installation status and outdated packages
  invalidate        Clear dotfiles caches (shell integration)
  purge [--force]   Remove stale symlinks in XDG directories
  clean             Clean Claude Code config files from home directory

OPTIONS:
  -n, --new         Force Brewfile regeneration and install
  -x, --export      Only create Brewfile without installing
  -s, --skip        Skip brew bundle, force package installation
  -v, --verbose     Show verbose output
  -f, --file PATH   Specify custom Brewfile location
  -h, --help        Show help message
```

### Package Discovery Algorithm

When `dot --new` runs:

```
1. Check DOTFILES variable is set
2. Prompt for sudo early (avoid timeout mid-install)
3. Install Homebrew if missing (via homebrew/brew_install.sh)
4. Scan for all brew_packages files:
   find "$DOTFILES" -maxdepth 2 -name 'brew_packages'
5. For each brew_packages file:
   - Print "Processing installer: <topic>"
   - Source the file (executes tap/brew/cask commands)
   - Exit on error
6. After all packages installed:
   - Export current state: brew bundle dump --force
   - Save to ${XDG_DATA_HOME}/Brewfile
7. Report success
```

When `dot` runs (no --new):

```
1. Check if Brewfile exists at ${XDG_DATA_HOME}/Brewfile
2. If exists and not --new:
   - Use existing Brewfile
   - Run: brew bundle --file="$BREWFILE"
   - Skip discovery and sourcing
3. If not exists or --new:
   - Fall through to discovery algorithm above
```

### Cache Strategy

#### Cache Location

All shell caches stored at:
```
${XDG_CACHE_HOME}/dotfiles/
├── bash_env.sh           # Aggregated bash_env from all topics
├── bash_aliases.sh       # Aggregated bash_aliases from all topics
├── bash_completion.sh    # Aggregated bash_completion from all topics
└── shortcuts/            # Keyboard shortcuts topics cache
    └── topics.cache
```

#### Cache Generation

Handled by shell initialization files (.bash_profile, .bashrc):

```bash
# Example from .bashrc for bash_aliases
CACHE_FILE="${XDG_CACHE_HOME:-$HOME/.cache}/dotfiles/bash_aliases.sh"

# Check if cache is fresh
if [ -f "$CACHE_FILE" ]; then
    cache_valid=true
    # Compare cache mtime against all source files
    for file in "$DOTFILES"/*/bash_aliases; do
        [ "$file" -nt "$CACHE_FILE" ] && cache_valid=false && break
    done
fi

# If cache is stale or missing, regenerate
if [ "$cache_valid" != true ]; then
    mkdir -p "$(dirname "$CACHE_FILE")"
    # Concatenate all bash_aliases files
    cat "$DOTFILES"/*/bash_aliases > "$CACHE_FILE" 2>/dev/null
fi

# Source the cache
[ -f "$CACHE_FILE" ] && source "$CACHE_FILE"
```

#### Invalidation Rules

**Automatic**:
- On shell start, compare cache mtime vs source files
- If any source newer than cache, regenerate

**Manual**:
- `dot invalidate` - removes all cache files
- Bootstrap purge - removes stale caches during setup

#### Cache Performance

| Operation | Uncached | Cached | Improvement |
|-----------|----------|--------|-------------|
| Shell startup (bash_aliases) | ~200ms | ~20ms | 10x faster |
| Shell startup (bash_env) | ~150ms | ~15ms | 10x faster |
| Shell startup (bash_completion) | ~250ms | ~25ms | 10x faster |
| shortcuts command | ~150ms | ~50ms | 3x faster |

---

## XDG Base Directory Integration

### Directory Mapping

The dotfiles system uses XDG Base Directory specification for organization:

| XDG Variable | Default | Dotfiles Usage |
|--------------|---------|----------------|
| `XDG_CONFIG_HOME` | `~/.config` | Topic configs, app settings |
| `XDG_DATA_HOME` | `~/.local/share` | Brewfile, persistent data |
| `XDG_STATE_HOME` | `~/.local/state` | Logs, history, runtime state |
| `XDG_CACHE_HOME` | `~/.cache` | Shell caches, shortcuts cache |
| (not XDG) | `~/.local/bin` | User executables (in PATH) |

### Triple-Layer Architecture

For applications that don't support XDG (like Claude Code):

```
Layer 1: SOURCE OF TRUTH
~/.dotfiles/claude/config/
    ├── CLAUDE.md
    ├── settings.json
    ├── commands/
    └── skills/
         ↓
    bootstrap: link_config_files()
         ↓
Layer 2: XDG CONVENTION
~/.config/claude/ → symlink to ~/.dotfiles/claude/config/
    ├── CLAUDE.md
    ├── settings.json
    ├── commands/
    └── skills/
         ↓
    claude/install.sh
         ↓
Layer 3: APPLICATION EXPECTATION
~/.claude/
    ├── CLAUDE.md → ~/.config/claude/CLAUDE.md
    ├── settings.json → ~/.config/claude/settings.json
    ├── commands/ → ~/.config/claude/commands/
    └── skills/ → ~/.config/claude/skills/
```

**Benefits**:
1. Single source of truth in versioned dotfiles
2. XDG compliance for tool interoperability
3. Application compatibility for non-XDG apps
4. Edit once, changes propagate through symlinks

### Compliance Verification

Verify XDG setup:

```bash
# Check XDG variables
echo $XDG_CONFIG_HOME   # Should be ~/.config
echo $XDG_DATA_HOME     # Should be ~/.local/share
echo $XDG_STATE_HOME    # Should be ~/.local/state
echo $XDG_CACHE_HOME    # Should be ~/.cache

# Check directory structure
ls -la ~/.config        # Should contain topic symlinks
ls -la ~/.local/share   # Should contain Brewfile
ls -la ~/.local/state   # Should contain app state dirs
ls -la ~/.cache         # Should contain dotfiles/ cache

# Verify symlink chain
ls -la ~/.config/nvim           # → ~/.dotfiles/nvim/config/
ls -la ~/.claude/CLAUDE.md      # → ~/.config/claude/CLAUDE.md
readlink -f ~/.claude/CLAUDE.md # → ~/.dotfiles/claude/config/CLAUDE.md
```

---

## Extension Guide

### Adding a New Topic

#### Step 1: Create Topic Directory

```bash
mkdir -p ~/.dotfiles/newtopic
cd ~/.dotfiles/newtopic
```

#### Step 2: Add Standard Files

Choose files based on needs:

**For shell integration**:
```bash
# Environment variables (loaded in login shells)
cat > bash_env << 'EOF'
# Copyright 2026 Your Name
# SPDX-License-Identifier: Apache-2.0

export NEWTOPIC_HOME="${XDG_DATA_HOME}/newtopic"
export PATH="$NEWTOPIC_HOME/bin:$PATH"
EOF

# Aliases (loaded in interactive shells)
cat > bash_aliases << 'EOF'
# Copyright 2026 Your Name
# SPDX-License-Identifier: Apache-2.0

alias nt='newtopic'
alias ntl='newtopic list'
EOF

# Completions (loaded after aliases)
cat > bash_completion << 'EOF'
# Copyright 2026 Your Name
# SPDX-License-Identifier: Apache-2.0

_newtopic() {
    local cur="${COMP_WORDS[COMP_CWORD]}"
    COMPREPLY=( $(compgen -W "list start stop" -- "$cur") )
}
complete -F _newtopic nt
EOF
```

**For Homebrew packages**:
```bash
cat > brew_packages << 'EOF'
# Copyright 2026 Your Name
# SPDX-License-Identifier: Apache-2.0

brew "newtopic-cli"
cask "newtopic-app"
EOF
```

**For XDG config**:
```bash
mkdir -p config
cat > config/config.toml << 'EOF'
[newtopic]
setting = "value"
EOF
```

**For custom setup**:
```bash
cat > install.sh << 'EOF'
#!/usr/bin/env bash
# Copyright 2026 Your Name
# SPDX-License-Identifier: Apache-2.0

set -e

# Create state directory
mkdir -p "${XDG_STATE_HOME}/newtopic"

# Initialize config if needed
if [ ! -f "$XDG_CONFIG_HOME/newtopic/config.toml" ]; then
    echo "Initializing newtopic..."
    newtopic init
fi

echo "✓ newtopic installed"
EOF

chmod +x install.sh
```

#### Step 3: Test Integration

```bash
# Reload shell to test caching
exec bash

# Test environment
echo $NEWTOPIC_HOME

# Test alias
nt --version

# Test completion
nt <TAB>

# Test config symlink
ls -la ~/.config/newtopic

# Check status
dot status
```

#### Step 4: Install Packages and Run Installer

```bash
# Install Homebrew packages
dot --new

# Run topic installer
dot install newtopic
```

### Adding Shell Integration

#### When to Use bash_env vs bash_aliases

**Use bash_env for**:
- Environment variables (export)
- PATH modifications
- Tool configuration via environment
- Variables used by other scripts

**Use bash_aliases for**:
- Command aliases
- Shell functions
- Interactive conveniences
- Shortcuts

**Use bash_completion for**:
- Tab completion for aliases
- Custom completion functions
- Integration with existing completions

#### Example: Adding Environment Variable

```bash
# In <topic>/bash_env
export MYTOOL_CONFIG="${XDG_CONFIG_HOME}/mytool"

# In <topic>/bash_aliases
alias mt='mytool --config $MYTOOL_CONFIG'
```

#### Example: Adding Function

```bash
# In <topic>/bash_aliases
function mytool-reset() {
    rm -rf "${XDG_STATE_HOME}/mytool"
    mytool init
}
```

### Adding Configuration

#### When to Use <topic>/config vs config/<app>

**Use <topic>/config/ when**:
- App is primary focus of topic (nvim, tmux, git)
- Complex config with many files
- Topic has other files (brew_packages, install.sh)

**Use config/<app>/ when**:
- Standalone app without dedicated topic
- Simple config (1-2 files)
- No brew_packages or install.sh needed
- App is a utility (bat, ripgrep, fd)

#### Example: Adding Topic Config

```bash
mkdir -p mytopic/config
cat > mytopic/config/settings.json << 'EOF'
{
  "theme": "catppuccin",
  "editor": "nvim"
}
EOF

# Run bootstrap to create symlink
script/bootstrap
# Creates: ~/.config/mytopic/ → ~/.dotfiles/mytopic/config/
```

#### Example: Adding General Config

```bash
mkdir -p config/newtool
cat > config/newtool/config.yaml << 'EOF'
theme: dark
EOF

# Run bootstrap to create symlink
script/bootstrap
# Creates: ~/.config/newtool/ → ~/.dotfiles/config/newtool/
```

---

## Testing Requirements

### Test: Topic Discovery

```bash
# Verify all topics have expected structure
cd ~/.dotfiles
for topic in */; do
    [ -d "$topic" ] || continue
    topic_name=$(basename "$topic")

    # Skip non-topic dirs
    [[ "$topic_name" =~ ^(\.git|script|docs|\.openspec|\.claude)$ ]] && continue

    echo "Topic: $topic_name"
    [ -f "$topic/bash_aliases" ] && echo "  ✓ bash_aliases"
    [ -f "$topic/bash_env" ] && echo "  ✓ bash_env"
    [ -f "$topic/bash_completion" ] && echo "  ✓ bash_completion"
    [ -f "$topic/brew_packages" ] && echo "  ✓ brew_packages"
    [ -f "$topic/install.sh" ] && echo "  ✓ install.sh"
    [ -d "$topic/config" ] && echo "  ✓ config/"
done
```

### Test: Bootstrap Idempotency

```bash
# Run bootstrap twice, should be safe
script/bootstrap
script/bootstrap

# Verify no duplicate symlinks
ls -la ~/.config/nvim
readlink ~/.config/nvim  # Should point to dotfiles, not be duplicated
```

### Test: Cache Invalidation

```bash
# Generate cache
exec bash

# Check cache exists
ls -la ~/.cache/dotfiles/bash_aliases.sh

# Modify source
touch ~/.dotfiles/git/bash_aliases

# Reload shell
exec bash

# Verify cache was regenerated (newer mtime)
ls -la ~/.cache/dotfiles/bash_aliases.sh
```

### Test: Symlink Validation

```bash
# Create stale symlink
ln -s /nonexistent/path ~/.config/stale

# Run purge
dot purge --force

# Verify removed
[ ! -L ~/.config/stale ] && echo "✓ Stale symlink removed"
```

### Test: Package Installation

```bash
# Export current state
dot --export

# Check Brewfile
cat ~/.local/share/Brewfile

# Verify includes topic packages
grep -q "ripgrep" ~/.local/share/Brewfile || echo "✗ Missing package"

# Test installation from Brewfile
dot
```

---

## Dependencies

### Required

- **bash** ≥4.0 - Shell scripting and runtime
- **Homebrew** - Package management for macOS
- **git** - Version control for dotfiles
- **find** - File discovery (POSIX compliant)
- **ln** - Symlink creation
- **mkdir** - Directory creation

### Optional

- **bat** - Syntax highlighted output (fallback: cat)
- **eza** - Modern ls replacement (fallback: ls)
- **ripgrep** - Fast searching (fallback: grep)
- **fd** - Fast find replacement (fallback: find)
- **fzf** - Fuzzy finder for interactive selection
- **delta** - Git diff viewer

### Environment Variables

| Variable | Default | Required |
|----------|---------|----------|
| `DOTFILES` | `~/.dotfiles` | Yes (set by bootstrap) |
| `XDG_CONFIG_HOME` | `~/.config` | Yes (set by bash_profile) |
| `XDG_DATA_HOME` | `~/.local/share` | Yes (set by bash_profile) |
| `XDG_STATE_HOME` | `~/.local/state` | Yes (set by bash_profile) |
| `XDG_CACHE_HOME` | `~/.cache` | Yes (set by bash_profile) |

---

## Non-Functional Requirements

### Maintainability

**Code Quality**:
- All scripts SHALL include copyright and SPDX headers
- Functions SHALL have single responsibility
- Complex logic SHALL include comments explaining "why" not "what"
- Error handling SHALL provide actionable messages
- Scripts SHALL use `set -e` for early exit on errors

**Documentation**:
- Each topic SHALL have clear purpose
- Non-obvious configuration SHALL be commented
- Breaking changes SHALL be documented in commit messages

**Testing**:
- Bootstrap SHALL be tested on clean macOS installation
- Cache invalidation SHALL be verified with manual tests
- Symlink creation SHALL be verified end-to-end

### Portability

**Platform Support**:
- Primary target: macOS (tested on Apple Silicon and Intel)
- Secondary target: Linux (best effort, may require adjustments)
- Shell scripts SHALL use POSIX-compatible constructs where possible
- Platform-specific code SHALL be guarded with conditionals

**Graceful Degradation**:
- Missing optional tools SHALL NOT cause errors
- Aliases SHALL check command existence before aliasing
- Completions SHALL check function existence before registering

**XDG Compliance**:
- All configuration SHALL follow XDG Base Directory spec
- Fallback to defaults if XDG variables not set
- Triple-layer architecture for non-compliant apps

### Performance

**Shell Startup**:
- Interactive shell startup SHALL be <200ms
- With caching, startup SHALL be <50ms faster
- Cache freshness check SHALL be <10ms

**Command Execution**:
- `dot status` SHALL complete in <2 seconds
- `dot list` SHALL complete in <500ms
- `shortcuts` SHALL complete in <100ms (cached)

**Bootstrap**:
- Initial bootstrap SHALL complete in <10 minutes (with Homebrew install)
- Subsequent bootstrap runs SHALL complete in <2 minutes

**Caching**:
- Cache hits SHALL avoid filesystem scanning
- Cache invalidation SHALL be automatic and transparent
- Manual invalidation SHALL be instant

### User Experience

**Output Formatting**:
- Success messages SHALL use green ✓ prefix
- Error messages SHALL use red ✗ prefix
- Info messages SHALL use blue ℹ️  prefix
- Warnings SHALL use yellow ⚠️  prefix

**Error Messages**:
- Errors SHALL include context (what failed, why)
- Errors SHALL suggest resolution steps
- Errors SHALL reference log files when available

**Help Text**:
- Commands SHALL provide --help flag
- Help SHALL include examples
- Help SHALL list all available options

**Progress Feedback**:
- Long operations SHALL show progress
- Bootstrap SHALL report each step
- Package installation SHALL show counts

---

## References

- **XDG Base Directory Specification**: https://specifications.freedesktop.org/basedir-spec/latest/
- **Holman's dotfiles** (original inspiration): https://github.com/holman/dotfiles
- **Dotfiles community**: https://dotfiles.github.io/
- **Homebrew**: https://brew.sh/
- **Bash Scripting Best Practices**: https://google.github.io/styleguide/shellguide.html

## Internal Documentation

- [README.md](README.md) - Quick start and overview
- [docs/xdg_setup.md](docs/xdg_setup.md) - XDG implementation details
- [docs/coloring.md](docs/coloring.md) - Modern CLI tools and colors
- [.openspec/specs/dotfiles-caching/spec.md](.openspec/specs/002-dotfiles-caching/spec.md) - Shell integration caching system
- [.openspec/specs/shortcuts-system/spec.md](../003-shortcuts-system/spec.md) - Keyboard shortcuts system

---

**License:** Apache-2.0
**Copyright:** 2026 Ilja Heitlager
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
