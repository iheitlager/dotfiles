#!/bin/bash
# Claude Team Container - Entrypoint
# Handles mode switching and tmux session setup
set -e

# Get user from environment or default
USER_NAME="${CLAUDE_USER:-claude}"
MODE="${1:-workstation}"
PROJECT="${2:-}"
AGENTS="${3:-2}"
TEAM_CONFIG="${CLAUDE_TEAM_CONFIG:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[entrypoint]${NC} $*"; }
warn() { echo -e "${YELLOW}[entrypoint]${NC} $*"; }
error() { echo -e "${RED}[entrypoint]${NC} $*" >&2; exit 1; }

# Setup ~/.claude symlinks from team config
setup_claude_config() {
    if [[ -z "$TEAM_CONFIG" ]]; then
        # Auto-detect team config
        for dir in /workspace/*/; do
            if [[ -f "${dir}claude/config/CLAUDE.md" ]]; then
                TEAM_CONFIG=$(basename "$dir")
                break
            fi
        done
    fi

    if [[ -z "$TEAM_CONFIG" ]]; then
        warn "No team config found, ~/.claude will be empty"
        return
    fi

    local config_path="/workspace/$TEAM_CONFIG/claude/config"
    
    if [[ ! -d "$config_path" ]]; then
        warn "Team config path not found: $config_path"
        return
    fi

    log "Setting up ~/.claude from $TEAM_CONFIG"

    # Symlink main files
    for file in CLAUDE.md settings.json; do
        if [[ -f "$config_path/$file" ]]; then
            ln -sf "$config_path/$file" "$HOME/.claude/$file"
            log "  ✓ $file"
        fi
    done

    # Symlink directories
    for dir in "$config_path"/*/; do
        if [[ -d "$dir" ]]; then
            local name=$(basename "$dir")
            ln -sfn "$dir" "$HOME/.claude/$name"
            log "  ✓ $name/"
        fi
    done
}

# Ensure state directories exist
setup_state_dirs() {
    mkdir -p "$XDG_STATE_HOME/agent-context"
    if [[ -n "$PROJECT" ]]; then
        mkdir -p "$XDG_STATE_HOME/agent-context/$PROJECT/jobs/pending"
        mkdir -p "$XDG_STATE_HOME/agent-context/$PROJECT/jobs/active"
        mkdir -p "$XDG_STATE_HOME/agent-context/$PROJECT/jobs/done"
    fi
}

# Create worktree for an agent
create_worktree() {
    local project="$1"
    local agent_num="$2"
    local worktree_name="${USER_NAME}-a.${agent_num}"
    local worktree_path="/workspace/worktrees/${project}/${worktree_name}"
    local project_path="/workspace/${project}"

    if [[ ! -d "$project_path/.git" ]]; then
        error "Project not a git repo: $project_path"
    fi

    if [[ ! -d "$worktree_path" ]]; then
        log "Creating worktree: $worktree_name"
        mkdir -p "/workspace/worktrees/${project}"
        cd "$project_path"
        git worktree add "$worktree_path" -b "$worktree_name" 2>/dev/null || \
            git worktree add "$worktree_path" "$worktree_name" 2>/dev/null || \
            git worktree add "$worktree_path" HEAD
    fi
    
    echo "$worktree_path"
}

# Build claude command with options
claude_cmd() {
    local cmd="claude"
    if [[ -n "$CLAUDE_YOLO" ]]; then
        cmd="$cmd --dangerously-skip-permissions"
    fi
    echo "$cmd"
}

# Mode: workstation
# Left pane: claude in team-config, Right pane: shell
run_workstation() {
    local team_path="/workspace/${TEAM_CONFIG}"
    
    if [[ ! -d "$team_path" ]]; then
        team_path="/workspace"
    fi

    log "Starting workstation mode"
    log "  Team config: $team_path"

    exec tmux new-session -s "ws-${TEAM_CONFIG:-team}" \
        "cd '$team_path' && $(claude_cmd); exec bash" \; \
        split-window -h "cd /workspace && exec bash" \; \
        select-pane -t 0
}

# Mode: agent
# N panes, each with claude in a worktree
run_agent() {
    if [[ -z "$PROJECT" ]]; then
        error "PROJECT is required for agent mode"
    fi

    if [[ ! -d "/workspace/$PROJECT" ]]; then
        error "Project not found: /workspace/$PROJECT"
    fi

    log "Starting agent mode"
    log "  Project: $PROJECT"
    log "  Agents: $AGENTS"
    log "  User: $USER_NAME"

    # Create worktrees
    local worktrees=()
    for i in $(seq 1 "$AGENTS"); do
        worktrees+=("$(create_worktree "$PROJECT" "$i")")
    done

    # Build tmux session
    local session="claude-${PROJECT}-${USER_NAME}"
    local first_worktree="${worktrees[0]}"
    local agent_id="${USER_NAME}-a.1"

    # Start first pane
    tmux new-session -d -s "$session" -c "$first_worktree" \
        "AGENT_ID=$agent_id $(claude_cmd); exec bash"

    # Add remaining panes
    for i in $(seq 2 "$AGENTS"); do
        local idx=$((i - 1))
        local wt="${worktrees[$idx]}"
        local aid="${USER_NAME}-a.${i}"
        tmux split-window -t "$session" -c "$wt" \
            "AGENT_ID=$aid $(claude_cmd); exec bash"
    done

    # Arrange layout
    if [[ "$AGENTS" -eq 2 ]]; then
        tmux select-layout -t "$session" even-horizontal
    elif [[ "$AGENTS" -ge 4 ]]; then
        tmux select-layout -t "$session" tiled
    fi

    # Attach
    exec tmux attach -t "$session"
}

# Mode: shell
run_shell() {
    log "Starting shell mode"
    cd /workspace
    exec bash
}

# Main
setup_claude_config
setup_state_dirs

case "$MODE" in
    workstation)
        run_workstation
        ;;
    agent)
        run_agent
        ;;
    shell)
        run_shell
        ;;
    *)
        error "Unknown mode: $MODE (use: workstation, agent, shell)"
        ;;
esac
