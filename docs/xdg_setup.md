# XDG Base Directory Compliance

This document describes the XDG Base Directory Specification implementation in this dotfiles repository, with a focus on the purposeful triple-layer approach for managing configuration.

## XDG Base Directory Specification

The [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/latest/) defines standard locations for user files:

| Variable | Default | Purpose |
|----------|---------|---------|
| `XDG_CONFIG_HOME` | `~/.config` | User configuration files |
| `XDG_DATA_HOME` | `~/.local/share` | User data files |
| `XDG_STATE_HOME` | `~/.local/state` | User state (logs, history, runtime) |
| `XDG_CACHE_HOME` | `~/.cache` | Non-essential cached data |

These are exported in [bash_profile.symlink](../bash/bash_profile.symlink#L4-L9):

```bash
export XDG_CONFIG_HOME=~/.config          # User configuration files
export XDG_DATA_HOME=~/.local/share       # User data files
export XDG_STATE_HOME=~/.local/state      # User state (logs, history)
export XDG_CACHE_HOME=~/.cache            # Non-essential cached data
```

Additionally, `~/.local/bin` is used for user executables (a common convention, though not in the XDG spec).

## Bootstrap XDG Setup

The [script/bootstrap](../script/bootstrap) creates the XDG directory structure:

```bash
setup_xdg_dirs () {
  local xdg_dirs=(
    "$HOME/.config"       # XDG_CONFIG_HOME
    "$HOME/.local/share"  # XDG_DATA_HOME
    "$HOME/.local/state"  # XDG_STATE_HOME
    "$HOME/.cache"        # XDG_CACHE_HOME
    "$HOME/.local/bin"    # User executables
  )
  for dir in "${xdg_dirs[@]}"; do
    mkdir -p "$dir"
  done
}
```

---

## The Triple-Layer Approach

For applications like Claude Code that don't fully support XDG conventions, we use a purposeful triple-layer symlink strategy:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        TRIPLE-LAYER ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Layer 1: SOURCE OF TRUTH                                               │
│  ~/.dotfiles/claude/config/                                             │
│  ├── CLAUDE.md                                                          │
│  ├── settings.json                                                      │
│  ├── commands/                                                          │
│  └── skills/                                                            │
│       │                                                                 │
│       │  bootstrap: link_config_files()                                 │
│       ▼                                                                 │
│  Layer 2: XDG CONVENTION                                                │
│  ~/.config/claude/  ──────► symlink to ~/.dotfiles/claude/config/       │
│  ├── CLAUDE.md                                                          │
│  ├── settings.json                                                      │
│  ├── commands/                                                          │
│  └── skills/                                                            │
│       │                                                                 │
│       │  claude/install.sh                                              │
│       ▼                                                                 │
│  Layer 3: APPLICATION EXPECTATION                                       │
│  ~/.claude/  ───────────────► symlinks to ~/.config/claude/*            │
│  ├── CLAUDE.md ──────────────► ~/.config/claude/CLAUDE.md               │
│  ├── settings.json ──────────► ~/.config/claude/settings.json           │
│  ├── commands/ ──────────────► ~/.config/claude/commands/               │
│  └── skills/ ────────────────► ~/.config/claude/skills/                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Why Three Layers?

| Layer | Location | Purpose |
|-------|----------|---------|
| **1. Dotfiles** | `~/.dotfiles/claude/config/` | Version control, backup, portability |
| **2. XDG** | `~/.config/claude/` | Standards compliance, tool interoperability |
| **3. Application** | `~/.claude/` | Application compatibility (Claude Code expects this) |

### Benefits

1. **Version Control**: All configuration lives in `~/.dotfiles/` under git
2. **XDG Compliance**: Standard location for other tools that respect XDG
3. **Application Compatibility**: Works with apps that use hardcoded paths
4. **Single Source of Truth**: Edit in one place, changes propagate everywhere

---

## Implementation Details

### Bootstrap: Dotfiles → XDG

The `link_config_files()` function in [script/bootstrap](../script/bootstrap#L91-L100) links any `config/` directory inside a topic to `~/.config/<topic>/`:

```bash
link_config_files () {
  for src in $(find "$DOTFILES" -maxdepth 2 -type d -name 'config')
  do
    local topic=$(basename $(dirname "$src"))
    local dst="$HOME/.config/$topic"
    link_file "$src" "$dst"
  done
}
```

This creates:
```
~/.config/claude/ → ~/.dotfiles/claude/config/
~/.config/tmux/   → ~/.dotfiles/tmux/config/
```

### Topic Install: XDG → Application

The [claude/install.sh](../claude/install.sh) creates the final symlinks from the application's expected location to the XDG location:

```bash
#!/usr/bin/env bash
mkdir -p "$HOME/.claude"

# Symlink versionable items INTO ~/.claude
# These cannot be inferred from naming conventions alone
ln -sf ~/.config/claude/CLAUDE.md "$HOME/.claude/CLAUDE.md"
ln -sf ~/.config/claude/settings.json "$HOME/.claude/settings.json"
ln -sfn ~/.config/claude/skills "$HOME/.claude/skills"
ln -sfn ~/.config/claude/commands "$HOME/.claude/commands"
```

> **Note**: `ln -sfn` is used for directories to replace existing symlinks correctly.

---

## Verification

After running `script/bootstrap`, verify the symlink chain:

```bash
# Layer 1 → Layer 2 (dotfiles → XDG)
$ ls -la ~/.config/claude
lrwxr-xr-x  claude -> /Users/user/.dotfiles/claude/config

# Layer 2 → Layer 3 (XDG → Application)
$ ls -la ~/.claude/
lrwxr-xr-x  CLAUDE.md -> /Users/user/.config/claude/CLAUDE.md
lrwxr-xr-x  settings.json -> /Users/user/.config/claude/settings.json
lrwxr-xr-x  commands -> /Users/user/.config/claude/commands
lrwxr-xr-x  skills -> /Users/user/.config/claude/skills

# Full chain verification
$ readlink -f ~/.claude/CLAUDE.md
/Users/user/.dotfiles/claude/config/CLAUDE.md
```

---

## XDG-Compliant Applications

Many modern CLI tools support XDG out of the box:

| Application | Config Location | Notes |
|-------------|-----------------|-------|
| tmux | `~/.config/tmux/tmux.conf` | Since tmux 3.1 |
| bat | `~/.config/bat/config` | Automatic |
| ripgrep | `~/.config/ripgrep/config` | Via `RIPGREP_CONFIG_PATH` |
| git | `~/.config/git/config` | Fallback only |
| nvim | `~/.config/nvim/` | Automatic |

For these, only layers 1 and 2 are needed.

---

## Adding a New Topic with XDG Support

1. **Create the topic structure**:
   ```bash
   mkdir -p ~/.dotfiles/newtopic/config
   ```

2. **Add configuration files**:
   ```bash
   # Files go in config/ subdirectory
   touch ~/.dotfiles/newtopic/config/settings.conf
   ```

3. **Run bootstrap** (or manually link):
   ```bash
   # Bootstrap will create: ~/.config/newtopic/ → ~/.dotfiles/newtopic/config/
   script/bootstrap
   ```

4. **If application needs non-XDG location**, create `install.sh`:
   ```bash
   # ~/.dotfiles/newtopic/install.sh
   mkdir -p "$HOME/.newtopic"
   ln -sf ~/.config/newtopic/settings.conf "$HOME/.newtopic/settings.conf"
   ```

---

## State vs Configuration

The XDG spec separates configuration from state:

| Type | Location | Examples | Version Control |
|------|----------|----------|-----------------|
| **Config** | `~/.config/` | Settings, preferences | ✅ Yes |
| **State** | `~/.local/state/` | History, logs, runtime data | ❌ No |
| **Data** | `~/.local/share/` | User data, databases | ❌ Usually no |
| **Cache** | `~/.cache/` | Temporary, regenerable | ❌ No |

The agent system uses this separation:
- **Config**: `~/.config/claude/` (versioned skills, settings)
- **State**: `~/.local/state/agent-context/` (task queues, runtime data)

---

## References

- [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/latest/)
- [Arch Wiki: XDG Base Directory](https://wiki.archlinux.org/title/XDG_Base_Directory)
- [dotfiles philosophy](https://dotfiles.github.io/)
