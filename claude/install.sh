#!/usr/bin/env bash
# Setup XDG compliant Claude config directory and symlinks
mkdir -p "$HOME/.claude"

# Symlink versionable items INTO ~/.claude
# These cannot by infered from naming conventions alone
mkdir -p "$XDG_CONFIG_HOME/claude"  2>/dev/null
ln -sf "$XDG_CONFIG_HOME/claude/CLAUDE.md" "$HOME/.claude/CLAUDE.md"
ln -sf "$XDG_CONFIG_HOME/claude/settings.json" "$HOME/.claude/settings.json"
ln -sfn "$XDG_CONFIG_HOME/claude/skills" "$HOME/.claude/skills"
ln -sfn "$XDG_CONFIG_HOME/claude/commands" "$HOME/.claude/commands"