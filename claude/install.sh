mkdir -p "$HOME/.claude"

# Symlink versionable items INTO ~/.claude
# These cannot by infered from naming conventions alone
ln -sf ~/.config/claude/CLAUDE.md "$HOME/.claude/CLAUDE.md"
ln -sf ~/.config/claude/settings.json "$HOME/.claude/settings.json"
ln -sfn ~/.config/claude/skills "$HOME/.claude/skills"
ln -sfn ~/.config/claude/commands "$HOME/.claude/commands"