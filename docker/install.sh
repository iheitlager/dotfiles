#!/bin/bash

# Simple script to setup Docker config with buildx support

DOCKER_DIR="$HOME/.docker"
CONFIG_FILE="$DOCKER_DIR/config.json"

# Create directory if it doesn't exist
mkdir -p "$DOCKER_DIR"

# Create or update config file
if [ ! -f "$CONFIG_FILE" ]; then
    # Create new config
    cat > "$CONFIG_FILE" << EOF
{
  "cliPluginsExtraDirs": [
    "\$HOMEBREW_PREFIX/lib/docker/cli-plugins"
  ]
}
EOF
else
    # Update existing config - only add if not already present
    if ! grep -q "cliPluginsExtraDirs" "$CONFIG_FILE"; then
        cp "$CONFIG_FILE" "$CONFIG_FILE.bak"
        sed -i.tmp '$s/}//' "$CONFIG_FILE"
        cat >> "$CONFIG_FILE" << EOF
  ,
  "cliPluginsExtraDirs": [
    "\$HOMEBREW_PREFIX/lib/docker/cli-plugins"
  ]
}
EOF
    fi
fi
