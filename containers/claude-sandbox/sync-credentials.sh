#!/bin/bash
set -euo pipefail

# Sync Claude Code credentials from macOS Keychain to container format
# This extracts OAuth tokens from keychain and prepares them for container use

echo "Extracting Claude Code credentials from macOS Keychain..."

# Extract credentials from keychain
CREDS=$(security find-generic-password -s "Claude Code-credentials" -a "iheitlager" -w 2>/dev/null)

if [ -z "$CREDS" ]; then
    echo "✗ Failed to extract credentials from keychain"
    echo "  Make sure Claude Code is authenticated on the host"
    exit 1
fi

# Create credential file in container directory (podman can access this)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMP_CREDS="$SCRIPT_DIR/.claude-oauth-creds.json"
echo "$CREDS" > "$TEMP_CREDS"
chmod 600 "$TEMP_CREDS"

echo "✓ Credentials extracted and saved to .claude-oauth-creds.json"
echo "  This file will be mounted into the container at startup"
