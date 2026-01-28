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

## The Problem

Claude Code stores its configuration in `~/.claude/`:

```
~/.claude/
├── CLAUDE.md          # Global instructions (the AI reads this)
├── settings.json      # Permissions, preferences
├── commands/          # Custom slash commands
└── skills/            # Reusable skill definitions
```

This creates three familiar problems: you want `CLAUDE.md` in git, but `~/.claude/` isn't your dotfiles repo. Config should live in `~/.config/`, not yet another dotfile in `~/`. And you want your agent instructions to travel when you clone your dotfiles on a new machine.

Sound familiar? It's the same pattern we solved for vim and tmux—but with a twist. Claude Code doesn't support XDG paths, and we need to version control files that directly instruct an AI.

## The Triple-Layer Architecture

The solution chains three symlinks:

```
Layer 1: SOURCE OF TRUTH
~/.dotfiles/claude/config/
├── CLAUDE.md, settings.json, commands/, skills/
        │
        │  bootstrap: link_config_files()
        ▼
Layer 2: XDG CONVENTION
~/.config/claude/ ──► symlink to ~/.dotfiles/claude/config/
        │
        │  claude/install.sh
        ▼
Layer 3: APPLICATION EXPECTATION
~/.claude/ ────────► symlinks to ~/.config/claude/*
```

Each layer serves a purpose: Layer 1 gives you version control and portability. Layer 2 maintains XDG compliance and standards. Layer 3 is what Claude Code actually reads.

Edit in one place. Git tracks it. Claude reads it.

## Implementation

**Layer 1 → 2: The Bootstrap.** The dotfiles bootstrap script from part 1 handles this automatically. Any `config/` directory inside a topic becomes `~/.config/<topic>/`:

```bash
link_config_files () {
  for src in $(find "$DOTFILES" -maxdepth 2 -type d -name 'config'); do
    local topic=$(basename $(dirname "$src"))
    link_file "$src" "$HOME/.config/$topic"
  done
}
```

**Layer 2 → 3: The Install Script.** Claude Code doesn't check `~/.config/`. It wants `~/.claude/`. The topic's `install.sh` bridges the gap:

```bash
#!/usr/bin/env bash
mkdir -p "$HOME/.claude"

ln -sf "$XDG_CONFIG_HOME/claude/CLAUDE.md" "$HOME/.claude/CLAUDE.md"
ln -sf "$XDG_CONFIG_HOME/claude/settings.json" "$HOME/.claude/settings.json"

for dir in "$XDG_CONFIG_HOME/claude"/*/; do
    [ -d "$dir" ] && ln -sfn "$dir" "$HOME/.claude/$(basename "$dir")"
done
```

The `-n` flag on `ln -sfn` is crucial for directories—it replaces existing symlinks correctly.

## What to Version Control

Not everything belongs in git. Version control `CLAUDE.md` (your global AI instructions), `settings.json` (permissions and preferences), and the `commands/` and `skills/` directories (custom workflows). Leave `projects/`, `todos/`, and `.credentials` out—these are runtime state and secrets.

## The Key Files

**CLAUDE.md** is where it gets interesting. This markdown file is your global instructions to the AI—code standards, workflow preferences, things to avoid. It travels with your dotfiles. New machine? Clone, bootstrap, and Claude already knows your preferences.

**settings.json** is your security configuration. You can allowlist safe commands (`git`, `uv`, `gh`) and denylist dangerous ones (`rm -rf`, `sudo`, `curl|sh`). Version control this. Review changes carefully. The deny list is your safety net against an overeager agent.

**commands/** and **skills/** extend Claude Code's capabilities with reusable instructions. Custom slash commands, documentation workflows, testing patterns—all versioned, all portable.

## Verification

After running `script/bootstrap`, verify the chain:

```bash
$ ls -la ~/.config/claude
lrwxr-xr-x  claude -> /Users/you/.dotfiles/claude/config

$ ls -la ~/.claude/CLAUDE.md
lrwxr-xr-x  CLAUDE.md -> ~/.config/claude/CLAUDE.md

$ readlink -f ~/.claude/CLAUDE.md
/Users/you/.dotfiles/claude/config/CLAUDE.md
```

One file. Three paths. Full traceability.

## Why This Matters

This isn't just about organization. It's about treating AI agent configuration as first-class infrastructure:

- **Auditability** — Git history shows every change to your AI's instructions
- **Portability** — Your agent setup travels with your dotfiles
- **Security** — Permission settings are version controlled and reviewable
- **Consistency** — Same instructions across all your machines

There's something profound about version-controlling the instructions you give to an AI. When that agent makes a mistake, you can check what guidance you gave it. When you tweak its behavior, you have a record of what changed. When your colleague asks "how did you get Claude to do that?", you point them at a file in git.

When you start running multiple agents in parallel—which we'll cover in part 3—this foundation becomes critical. Each agent reads from the same source of truth, following the same rules, with the same security boundaries.

But first: go version control your `CLAUDE.md`. Your future self will thank you.

---

*My dotfiles are available at [github.com/iheitlager/dotfiles](https://github.com/iheitlager/dotfiles). The full Claude config setup is in the `claude/` topic directory.*

## References

- [Part 1: The Agents Are Coming. Clean Your $HOME.](https://stories.lab271.io/the-agents-are-coming-clean-your-home-c8ae7e026c51)
- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code)
- [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/latest/)
