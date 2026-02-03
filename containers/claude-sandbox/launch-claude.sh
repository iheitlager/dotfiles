#!/bin/bash
set -euo pipefail

# Helper function: Run single Claude session
run_single_session() {
    exec claude "$@"
}

# Helper function: Setup tmux swarm with multiple Claude sessions
setup_tmux_swarm() {
    local num_sessions=$1
    shift
    local args="$*"

    echo "Starting $num_sessions Claude sessions in tmux..."

    # Create tmux session with first claude instance
    tmux new-session -d -s claude-swarm -n "claude-1" "claude $args"

    # Create additional windows for remaining sessions
    for ((i=2; i<=num_sessions; i++)); do
        tmux new-window -t claude-swarm -n "claude-$i" "claude $args"
    done

    # Select first window and attach
    tmux select-window -t claude-swarm:1
    exec tmux attach-session -t claude-swarm
}

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

# Handle Claude credentials (XDG-compliant + OAuth tokens)
# Modern Claude Code uses ~/.config/claude for settings
# OAuth tokens need to be injected from host's macOS Keychain

if [ -d "/home/agent/.config/claude" ] && [ "$(ls -A /home/agent/.config/claude 2>/dev/null)" ]; then
    # XDG config directory mounted - modern approach
    echo "✓ Claude config mounted (XDG-compliant)"
    echo "  → ~/.config/claude stays in sync with host"

    # Inject OAuth credentials from keychain if available
    # Try multiple locations where Electron/Claude Code might look for credentials
    if [ -f "/tmp/host-claude-oauth.json" ]; then
        # Location 1: XDG config (most likely for Linux Electron apps)
        mkdir -p /home/agent/.config/claude
        cp /tmp/host-claude-oauth.json /home/agent/.config/claude/oauth-credentials.json
        chmod 600 /home/agent/.config/claude/oauth-credentials.json

        # Location 2: Claude Code specific directory (Electron app data)
        mkdir -p "/home/agent/.config/Claude Code"
        cp /tmp/host-claude-oauth.json "/home/agent/.config/Claude Code/credentials.json"
        chmod 600 "/home/agent/.config/Claude Code/credentials.json"

        # Fix ownership
        chown -R agent:agent /home/agent/.config/claude "/home/agent/.config/Claude Code" 2>/dev/null || true

        echo "  → OAuth credentials injected from keychain"
        echo "     (placed in multiple locations for compatibility)"
    else
        echo "  ⚠ No OAuth credentials - will need to authenticate"
    fi
elif [ -d "/tmp/host-claude-creds" ]; then
    # Legacy copy-on-start approach for backward compatibility
    echo "Copying Claude credentials from host (legacy mode)..."
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
    echo "⚠ No credentials found - you'll need to login"
    echo "  Run 'claude' on your host first to authenticate"
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

        # Single or multi-session mode
        if [ "$NUM_SESSIONS" -eq 1 ]; then
            exec su - agent -c "export PATH='$AGENT_PATH' && cd '$(pwd)' && claude $*"
        else
            # Build tmux command and execute
            TMUX_CMD="export PATH='$AGENT_PATH' && tmux new-session -d -s claude-swarm -n 'claude-1' 'claude $*'"
            for ((i=2; i<=NUM_SESSIONS; i++)); do
                TMUX_CMD="$TMUX_CMD && tmux new-window -t claude-swarm -n 'claude-$i' 'claude $*'"
            done
            TMUX_CMD="$TMUX_CMD && tmux select-window -t claude-swarm:1 && tmux attach-session -t claude-swarm"
            echo "Starting $NUM_SESSIONS Claude sessions in tmux as agent..."
            exec su - agent -c "cd '$(pwd)' && $TMUX_CMD"
        fi
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

        # Single or multi-session mode
        if [ "$NUM_SESSIONS" -eq 1 ]; then
            exec su - agent -c "export PATH='$AGENT_PATH' && cd '$(pwd)' && claude $*"
        else
            # Build tmux command and execute
            TMUX_CMD="export PATH='$AGENT_PATH' && tmux new-session -d -s claude-swarm -n 'claude-1' 'claude $*'"
            for ((i=2; i<=NUM_SESSIONS; i++)); do
                TMUX_CMD="$TMUX_CMD && tmux new-window -t claude-swarm -n 'claude-$i' 'claude $*'"
            done
            TMUX_CMD="$TMUX_CMD && tmux select-window -t claude-swarm:1 && tmux attach-session -t claude-swarm"
            echo "Starting $NUM_SESSIONS Claude sessions in tmux as agent..."
            exec su - agent -c "cd '$(pwd)' && $TMUX_CMD"
        fi
    fi
fi

# If we're agent (shouldn't happen with current setup), just run normally
if [ "$(id -u)" -ne 0 ]; then
    if [ "$NUM_SESSIONS" -eq 1 ]; then
        run_single_session "$@"
    else
        setup_tmux_swarm "$NUM_SESSIONS" "$@"
    fi
fi
