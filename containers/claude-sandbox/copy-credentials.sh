#!/bin/bash
set -euo pipefail

# Script to copy Claude credentials into a running container
# This is an alternative to mounting credentials

CONTAINER_NAME="${1:-claude-sandbox-instance}"

echo "Copying Claude credentials to container: $CONTAINER_NAME"

# Check if container is running
if ! podman ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo "ERROR: Container '$CONTAINER_NAME' is not running"
    echo "Start it first with: make run"
    exit 1
fi

# Copy credentials
echo "Copying ~/.claude.json..."
podman cp ~/.claude.json "${CONTAINER_NAME}:/home/agent/.claude.json"

echo "Copying ~/.claude/ directory..."
podman exec "$CONTAINER_NAME" mkdir -p /home/agent/.claude
tar -czf - -C ~/.claude . | podman exec -i "$CONTAINER_NAME" tar -xzf - -C /home/agent/.claude

# Fix permissions
echo "Setting permissions..."
podman exec "$CONTAINER_NAME" chown -R agent:agent /home/agent/.claude /home/agent/.claude.json

echo "✓ Credentials copied successfully!"
echo "Note: Credentials will be lost when container is removed (--rm flag)"
