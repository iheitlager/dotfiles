#!/bin/bash
# Graceful shutdown script for claude-team container
# Available as: shutdown, x, stop

set -e

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[shutdown]${NC} $*"; }
warn() { echo -e "${YELLOW}[shutdown]${NC} $*"; }

log "Initiating graceful shutdown..."

# Check if we're in a tmux session
if [[ -n "$TMUX" ]]; then
    log "Detaching from tmux session..."
    tmux detach-client
else
    log "Not in a tmux session, exiting shell..."
fi

# Kill the tmux session if it exists
if tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
    log "Killing tmux session: $TMUX_SESSION"
    tmux kill-session -t "$TMUX_SESSION"
fi

log "Shutdown complete. Container will exit."

# Exit the shell, which will cause the container to stop
exit 0
