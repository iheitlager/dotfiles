# Teaching Your AI Agent Where It Lives

*Triple-layer config architecture for Claude Code*

*Part 2 of a series on building an agentic development environment*

---

> "All problems in computer science can be solved by another level of indirection."
>
> — David Wheeler

---

In the [previous article](https://stories.lab271.io/the-agents-are-coming-clean-your-home-c8ae7e026c51), we cleaned up our home directory with XDG-compliant dotfiles. Now we face a new challenge: AI coding agents have opinions about where their config lives, and those opinions don't always align with ours.

Claude Code expects `~/.claude/`. We want version control. We want XDG compliance. We want a single source of truth.

The solution? Another level of indirection.

## The Challenge

Claude Code stores its configuration in `~/.claude/`:

```
~/.claude/
├── CLAUDE.md          # Global instructions (the AI reads this)
├── settings.json      # Permissions, preferences
├── commands/          # Custom slash commands
└── skills/            # Reusable skill definitions
```

This creates three problems:

1. **Version control** — You want `CLAUDE.md` in git, but `~/.claude/` isn't your dotfiles repo
2. **XDG compliance** — Config should live in `~/.config/`, not another dotfile in `~/`
3. **Machine portability** — Clone dotfiles, get your agent instructions everywhere

Sound familiar? It's the same problem we solved for vim and tmux — but with a twist. Claude Code doesn't support XDG paths, and we need to version control files that directly instruct an AI.

## The Triple-Layer Architecture

The solution chains three symlinks:

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
│  ~/.config/claude/  ───► symlink to ~/.dotfiles/claude/config/          │
│       │                                                                 │
│       │  claude/install.sh                                              │
│       ▼                                                                 │
│  Layer 3: APPLICATION EXPECTATION                                       │
│  ~/.claude/  ─────────► symlinks to ~/.config/claude/*                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

Each layer serves a purpose:

| Layer | Location | Why it exists |
|-------|----------|---------------|
| **1** | `~/.dotfiles/claude/config/` | Version control, backup, portability |
| **2** | `~/.config/claude/` | XDG compliance, standards, tool interop |
| **3** | `~/.claude/` | What Claude Code actually reads |

Edit in one place. Git tracks it. Claude reads it.

## Implementation

### Layer 1 → 2: The Bootstrap

The dotfiles bootstrap script (from part 1) handles this automatically:

```bash
link_config_files () {
  for src in $(find "$DOTFILES" -maxdepth 2 -type d -name 'config'); do
    local topic=$(basename $(dirname "$src"))
    local dst="$HOME/.config/$topic"
    link_file "$src" "$dst"
  done
}
```

Any `config/` directory inside a topic becomes `~/.config/<topic>/`. For Claude:

```
~/.dotfiles/claude/config/ → ~/.config/claude/
```

### Layer 2 → 3: The Install Script

Claude Code doesn't check `~/.config/`. It wants `~/.claude/`. The topic's `install.sh` bridges the gap:

```bash
#!/usr/bin/env bash
mkdir -p "$HOME/.claude"

# Symlink files
ln -sf "$XDG_CONFIG_HOME/claude/CLAUDE.md" "$HOME/.claude/CLAUDE.md"
ln -sf "$XDG_CONFIG_HOME/claude/settings.json" "$HOME/.claude/settings.json"

# Symlink directories
for dir in "$XDG_CONFIG_HOME/claude"/*/; do
    [ -d "$dir" ] && ln -sfn "$dir" "$HOME/.claude/$(basename "$dir")"
done
```

The `-n` flag on `ln -sfn` is crucial for directories — it replaces existing symlinks correctly.

## What to Version Control

Not everything in `~/.claude/` should be versioned. Here's the split:

| File/Directory | Version Control | Why |
|----------------|-----------------|-----|
| `CLAUDE.md` | ✅ Yes | Your global AI instructions |
| `settings.json` | ✅ Yes | Permissions and preferences |
| `commands/` | ✅ Yes | Custom slash commands |
| `skills/` | ✅ Yes | Reusable skill definitions |
| `projects/` | ❌ No | Project-specific state |
| `todos/` | ❌ No | Session state |
| `.credentials` | ❌ No | Auth tokens (never commit) |

The dotfiles repo only contains `config/` — the versionable parts. Runtime state stays in `~/.claude/` proper (or better: `~/.local/state/claude/`).

## The CLAUDE.md File

This is where it gets interesting. `CLAUDE.md` is a markdown file that Claude Code reads at startup. It's your global instructions to the AI:

```markdown
# Claude Code Instructions

## Code Quality Standards
- Python 3.12+, use modern type hints
- Linter: ruff
- Testing: pytest with >80% coverage

## Workflow Preferences
- Use Bash and Git freely
- Read files before modifying
- Create branches following naming conventions

## What NOT To Do
- Never generate markdown docs unless asked
- No force pushes or hard resets
- Don't commit .env files
```

This file travels with your dotfiles. New machine? Clone, bootstrap, and Claude already knows your preferences.

## The settings.json File

Claude Code's permission system lives here. You can allowlist and denylist specific commands:

```json
{
  "permissions": {
    "allow": [
      "Read(*)",
      "Edit",
      "Bash(git *)",
      "Bash(uv *)",
      "Bash(gh *)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(sudo*)",
      "Bash(curl*|*sh)",
      "Write(~/.ssh/*)",
      "Read(~/.aws/*)"
    ]
  }
}
```

This is security configuration for your AI agent. Version control it. Review changes carefully. The deny list in particular is your safety net.

## Skills and Commands

The `skills/` and `commands/` directories extend Claude Code's capabilities:

```
~/.dotfiles/claude/config/
├── commands/
│   ├── commit.md        # /commit slash command
│   ├── review-pr.md     # /review-pr slash command
│   └── ...
└── skills/
    ├── adr-writing/     # ADR documentation skill
    ├── testing/         # Test writing skill
    └── ...
```

These are reusable instructions and workflows. Version control them, share them across machines, evolve them over time.

## Verification

After running `script/bootstrap`, verify the chain:

```bash
# Layer 1 → Layer 2
$ ls -la ~/.config/claude
lrwxr-xr-x  claude -> /Users/you/.dotfiles/claude/config

# Layer 2 → Layer 3
$ ls -la ~/.claude/
lrwxr-xr-x  CLAUDE.md -> ~/.config/claude/CLAUDE.md
lrwxr-xr-x  settings.json -> ~/.config/claude/settings.json
lrwxr-xr-x  commands -> ~/.config/claude/commands
lrwxr-xr-x  skills -> ~/.config/claude/skills

# Full chain
$ readlink -f ~/.claude/CLAUDE.md
/Users/you/.dotfiles/claude/config/CLAUDE.md
```

One file. Three paths. Full traceability.

## Why This Matters

This isn't just about organization. It's about treating AI agent configuration as first-class infrastructure:

1. **Auditability** — Git history shows every change to your AI's instructions
2. **Portability** — Your agent setup travels with your dotfiles
3. **Security** — Permission settings are version controlled and reviewable
4. **Consistency** — Same instructions across all your machines

When you start running multiple agents (which we'll cover in part 3), this foundation becomes critical. Each agent reads from the same source of truth.

## What's Next

In part 3, we'll scale up: running multiple Claude agents in parallel using git worktrees, shared task queues, and the agent coordination system. The triple-layer config ensures they all start with identical instructions.

But first: go version control your `CLAUDE.md`. Your future self will thank you.

---

*My dotfiles are available at [github.com/iheitlager/dotfiles](https://github.com/iheitlager/dotfiles). The full Claude config setup is in the `claude/` topic directory.*

## References

- [Part 1: The Agents Are Coming. Clean Your $HOME.](https://stories.lab271.io/the-agents-are-coming-clean-your-home-c8ae7e026c51)
- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code)
- [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/latest/)
