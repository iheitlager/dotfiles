#!/bin/bash
# Setup ~/.claude symlinks from team config
# Called from entrypoint or can be run standalone

TEAM_CONFIG="${1:-$CLAUDE_TEAM_CONFIG}"

if [[ -z "$TEAM_CONFIG" ]]; then
    # Auto-detect
    for dir in /workspace/*/; do
        if [[ -f "${dir}claude/config/CLAUDE.md" ]]; then
            TEAM_CONFIG=$(basename "$dir")
            break
        fi
    done
fi

if [[ -z "$TEAM_CONFIG" ]]; then
    echo "No team config found"
    exit 1
fi

config_path="/workspace/$TEAM_CONFIG/claude/config"

if [[ ! -d "$config_path" ]]; then
    echo "Config path not found: $config_path"
    exit 1
fi

echo "Setting up ~/.claude from $TEAM_CONFIG"

# Ensure ~/.claude exists
mkdir -p "$HOME/.claude"

# Symlink main files
for file in CLAUDE.md settings.json; do
    if [[ -f "$config_path/$file" ]]; then
        ln -sf "$config_path/$file" "$HOME/.claude/$file"
        echo "  ✓ $file"
    fi
done

# Symlink directories
for dir in "$config_path"/*/; do
    if [[ -d "$dir" ]]; then
        name=$(basename "$dir")
        ln -sfn "$dir" "$HOME/.claude/$name"
        echo "  ✓ $name/"
    fi
done

echo "Done"
