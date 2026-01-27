#!/usr/bin/env bash
# Setup VS Code global settings and keybindings

VSCODE_USER_DIR="$HOME/Library/Application Support/Code/User"

# Ensure directory exists
mkdir -p "$VSCODE_USER_DIR"

# Update settings.json - add/update terminal.external.osxExec
SETTINGS_FILE="$VSCODE_USER_DIR/settings.json"
if [ -f "$SETTINGS_FILE" ]; then
    # Merge our settings into existing
    python3 -c "
import json
import sys

with open('$SETTINGS_FILE', 'r') as f:
    settings = json.load(f)

# Add our settings
settings['terminal.external.osxExec'] = 'Ghostty.app'

with open('$SETTINGS_FILE', 'w') as f:
    json.dump(settings, f, indent=2)
    f.write('\n')
"
    echo "  Updated VS Code settings.json"
else
    # Create new settings file
    cat > "$SETTINGS_FILE" << 'EOF'
{
  "terminal.external.osxExec": "Ghostty.app"
}
EOF
    echo "  Created VS Code settings.json"
fi

# Create/update keybindings.json
KEYBINDINGS_FILE="$VSCODE_USER_DIR/keybindings.json"
if [ ! -f "$KEYBINDINGS_FILE" ]; then
    cat > "$KEYBINDINGS_FILE" << 'EOF'
[
  {
    "key": "ctrl+alt+t",
    "command": "workbench.action.terminal.openNativeConsole"
  }
]
EOF
    echo "  Created VS Code keybindings.json"
else
    # Check if keybinding already exists
    if ! grep -q "workbench.action.terminal.openNativeConsole" "$KEYBINDINGS_FILE"; then
        echo "  WARNING: keybindings.json exists, manually add:"
        echo '    { "key": "ctrl+alt+t", "command": "workbench.action.terminal.openNativeConsole" }'
    else
        echo "  VS Code keybindings.json already configured"
    fi
fi
