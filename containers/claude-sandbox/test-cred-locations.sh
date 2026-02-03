#!/bin/bash
# Test different credential storage locations for Claude Code on Linux

echo "Testing credential storage locations..."

# Common Electron app credential locations on Linux:
LOCATIONS=(
    "$HOME/.config/Claude Code/credentials.json"
    "$HOME/.config/Claude Code/Local Storage/leveldb"
    "$HOME/.config/claude/credentials.json"
    "$HOME/.config/claude/oauth.json"
    "$HOME/.local/share/Claude Code/credentials.json"
)

for loc in "${LOCATIONS[@]}"; do
    echo "  - $loc"
done
