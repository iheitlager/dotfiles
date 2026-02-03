#!/bin/bash
set -euo pipefail

# Parse arguments for session count
NUM_SESSIONS=1
START_COMMAND="claude"

while [[ $# -gt 0 ]]; do
    case $1 in
        -n)
            NUM_SESSIONS="$2"
            shift 2
            ;;
        start)
            START_COMMAND="$1"
            shift
            ;;
        *)
            # Pass remaining args to claude
            break
            ;;
    esac
done

# Copy credentials from host mount (if exists) to agent home
# This ensures credentials are isolated and not shared with host
# XDG-compliant: Uses ~/.config/claude (primary) and ~/.claude.json (legacy)
if [ -d "/tmp/host-claude-creds" ]; then
    echo "Copying Claude credentials from host (XDG-compliant)..."
    mkdir -p /home/agent/.config/claude

    # Copy XDG config directory (contains actual config files)
    if [ -d "/tmp/host-claude-creds/config" ]; then
        cp -r /tmp/host-claude-creds/config/. /home/agent/.config/claude/
        echo "  ✓ Copied ~/.config/claude"
    fi

    # Copy legacy .claude.json file (still used by some versions)
    if [ -f "/tmp/host-claude-creds/claude.json" ]; then
        cp /tmp/host-claude-creds/claude.json /home/agent/.claude.json
        echo "  ✓ Copied ~/.claude.json"
    fi

    # Set proper permissions
    chown -R agent:agent /home/agent/.config /home/agent/.claude.json 2>/dev/null || true
    chmod 600 /home/agent/.claude.json 2>/dev/null || true

    echo "✓ Credentials copied successfully (isolated from host)"
else
    echo "No host credentials found - you'll need to login"
fi

# Set up PATH for agent user (includes ~/.local/bin for Claude)
AGENT_PATH="/home/agent/.cargo/bin:/home/agent/.local/bin:/usr/local/bin:/usr/bin:/bin"

# Initialize firewall if explicitly enabled (disabled by default for compatibility)
# This must run as root, so if we're root, run it, then switch to agent
if [ "${ENABLE_FIREWALL:-0}" = "1" ]; then
    if [ "$(id -u)" -eq 0 ]; then
        echo "Initializing firewall as root..."
        /usr/local/bin/init-firewall.sh

        # Now switch to agent user for running claude
        echo "Switching to agent user..."

        # If only one session, run claude as agent
        if [ "$NUM_SESSIONS" -eq 1 ]; then
            exec su - agent -c "export PATH='$AGENT_PATH' && cd '$(pwd)' && claude $*"
        fi

        # Multi-session mode: start tmux with multiple claude instances
        echo "Starting $NUM_SESSIONS Claude sessions in tmux as agent..."

        # Build tmux command
        TMUX_CMD="export PATH='$AGENT_PATH' && tmux new-session -d -s claude-swarm -n 'claude-1' 'claude $*'"
        for ((i=2; i<=NUM_SESSIONS; i++)); do
            TMUX_CMD="$TMUX_CMD && tmux new-window -t claude-swarm -n 'claude-$i' 'claude $*'"
        done
        TMUX_CMD="$TMUX_CMD && tmux select-window -t claude-swarm:1 && tmux attach-session -t claude-swarm"

        exec su - agent -c "cd '$(pwd)' && $TMUX_CMD"
    else
        echo "ERROR: Container must run as root to initialize firewall"
        echo "Remove --user flag or set ENABLE_FIREWALL=0"
        exit 1
    fi
else
    # Firewall disabled, switch to agent if we're root
    if [ "$(id -u)" -eq 0 ]; then
        echo "Firewall disabled (set ENABLE_FIREWALL=1 to enable)"
        echo "Switching to agent user..."

        # If only one session, run claude as agent
        if [ "$NUM_SESSIONS" -eq 1 ]; then
            exec su - agent -c "export PATH='$AGENT_PATH' && cd '$(pwd)' && claude $*"
        fi

        # Multi-session mode
        echo "Starting $NUM_SESSIONS Claude sessions in tmux as agent..."
        TMUX_CMD="export PATH='$AGENT_PATH' && tmux new-session -d -s claude-swarm -n 'claude-1' 'claude $*'"
        for ((i=2; i<=NUM_SESSIONS; i++)); do
            TMUX_CMD="$TMUX_CMD && tmux new-window -t claude-swarm -n 'claude-$i' 'claude $*'"
        done
        TMUX_CMD="$TMUX_CMD && tmux select-window -t claude-swarm:1 && tmux attach-session -t claude-swarm"
        exec su - agent -c "cd '$(pwd)' && $TMUX_CMD"
    fi
fi

# If we're agent (shouldn't happen with current setup), just run normally
if [ "$(id -u)" -ne 0 ]; then
    # If only one session, just run claude directly
    if [ "$NUM_SESSIONS" -eq 1 ]; then
        exec claude "$@"
    fi

    # Multi-session mode: start tmux with multiple claude instances
    echo "Starting $NUM_SESSIONS Claude sessions in tmux..."

    # Create tmux session with first claude instance
    tmux new-session -d -s claude-swarm -n "claude-1" "claude $*"

    # Create additional windows for remaining sessions
    for ((i=2; i<=NUM_SESSIONS; i++)); do
        tmux new-window -t claude-swarm -n "claude-$i" "claude $*"
    done

    # Select first window
    tmux select-window -t claude-swarm:1

    # Attach to the session
    exec tmux attach-session -t claude-swarm
fi
