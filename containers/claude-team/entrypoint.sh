#!/bin/bash
# Claude Team Container - Entrypoint v2.0
# Multi-agent architecture with coordination daemon
set -e

# Get user and mode from environment
USER_NAME="${CLAUDE_USER:-claude}"
MODE="${1:-run}"
TEAM_CONFIG="${CLAUDE_TEAM_CONFIG:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[entrypoint]${NC} $*"; }
warn() { echo -e "${YELLOW}[entrypoint]${NC} $*"; }
error() { echo -e "${RED}[entrypoint]${NC} $*" >&2; exit 1; }

# Clear ephemeral coordination state
clear_coordination_state() {
    log "Clearing coordination state..."
    rm -rf /tmp/claude-coordination
    mkdir -p /tmp/claude-coordination/{agents,jobs/{pending,claimed,done}}
    touch /tmp/claude-coordination/events.log
}

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
        warn "No team config found, ~/.claude will be minimal"
        return
    fi

    local config_path="/workspace/$TEAM_CONFIG/claude/config"

    if [[ ! -d "$config_path" ]]; then
        warn "Team config path not found: $config_path"
        return
    fi

    log "Setting up ~/.claude from $TEAM_CONFIG"

    # Symlink CLAUDE.md
    if [[ -f "$config_path/CLAUDE.md" ]]; then
        ln -sf "$config_path/CLAUDE.md" "$HOME/.claude/CLAUDE.md"
        log "  ✓ CLAUDE.md"
    fi

    # Symlink directories
    for dir in commands skills templates agents; do
        if [[ -d "$config_path/$dir" ]]; then
            ln -sfn "$config_path/$dir" "$HOME/.claude/$dir"
            log "  ✓ $dir/"
        fi
    done

    # NOTE: settings.json will be created by settings_modifier.py
}

# Detect all project repos in /workspace
detect_projects() {
    local projects=()
    for dir in /workspace/*/; do
        local name=$(basename "$dir")
        # Skip team config and .worktrees
        if [[ "$name" != "$TEAM_CONFIG" && "$name" != ".worktrees" && -d "${dir}.git" ]]; then
            projects+=("$name")
        fi
    done
    echo "${projects[@]}"
}

# Create worktree for a project
create_worktree() {
    local project="$1"
    local agent_num="$2"
    local worktree_name="${USER_NAME}-a.${agent_num}"
    local worktree_path="/workspace/.worktrees/${project}/${worktree_name}"
    local project_path="/workspace/${project}"

    if [[ ! -d "$project_path/.git" ]]; then
        error "Project not a git repo: $project_path"
    fi

    if [[ ! -d "$worktree_path" ]]; then
        log "Creating worktree: ${project}/${worktree_name}"
        mkdir -p "/workspace/.worktrees/${project}"
        cd "$project_path"

        # Try to create or add existing worktree
        git worktree add "$worktree_path" -b "$worktree_name" 2>/dev/null || \
            git worktree add "$worktree_path" "$worktree_name" 2>/dev/null || \
            git worktree add "$worktree_path" HEAD 2>/dev/null || true
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

# Mode: run (full multi-agent session)
run_multi_agent() {
    log "Starting multi-agent session"
    log "  User: $USER_NAME"
    log "  Team config: ${TEAM_CONFIG:-none}"

    # Detect all projects
    local projects=($(detect_projects))

    if [[ ${#projects[@]} -eq 0 ]]; then
        warn "No projects detected in /workspace"
    else
        log "  Projects: ${projects[*]}"
    fi

    # Create worktrees for each project
    local agent_num=1
    declare -A worktree_map

    for project in "${projects[@]}"; do
        local worktree=$(create_worktree "$project" "$agent_num")
        worktree_map[$project]=$worktree
        ((agent_num++))
    done

    # Build tmux session
    local session="claude-team-${USER_NAME}"
    export TMUX_SESSION="$session"

    log "Building tmux session: $session"

    # Window 1: main (2 orchestrator agents + shell)
    log "  Window: main (2 orchestrators + shell)"
    tmux new-session -d -s "$session" -n "main" -c /workspace \
        "AGENT_ID=main-agent-1 AGENT_ROLE=main $(claude_cmd) --append-system-prompt \"\$(python3 /opt/claude-team/lib/generate_agents_md.py main-agent-1)\"; exec bash"

    tmux split-window -t "$session:main" -h -c /workspace \
        "AGENT_ID=main-agent-2 AGENT_ROLE=main $(claude_cmd) --append-system-prompt \"\$(python3 /opt/claude-team/lib/generate_agents_md.py main-agent-2)\"; exec bash"

    tmux split-window -t "$session:main" -v -c /workspace \
        "exec bash"

    tmux select-layout -t "$session:main" main-vertical

    # Windows 2-N: one per project (subagent in worktree)
    agent_num=1
    for project in "${projects[@]}"; do
        local worktree="${worktree_map[$project]}"
        local agent_id="${USER_NAME}-a.${agent_num}"

        log "  Window: $project (subagent $agent_id)"

        tmux new-window -t "$session" -n "$project" -c "$worktree" \
            "AGENT_ID=$agent_id AGENT_ROLE=sub AGENT_PROJECT=$project $(claude_cmd) --append-system-prompt \"\$(python3 /opt/claude-team/lib/generate_agents_md.py $agent_id)\"; exec bash"

        ((agent_num++))
    done

    # Final window: coordination daemon
    log "  Window: coord (coordination daemon)"
    tmux new-window -t "$session" -n "coord" \
        "python3 /opt/claude-team/lib/coordination_daemon.py"

    # Select main window and attach
    tmux select-window -t "$session:main"

    log "✓ Session ready: $session"
    log ""
    log "Windows:"
    log "  - main:  2 orchestrator agents + shell"
    for project in "${projects[@]}"; do
        log "  - $project:  subagent in worktree"
    done
    log "  - coord: coordination dashboard"
    log ""

    exec tmux attach -t "$session"
}

# Mode: shell (just a shell)
run_shell() {
    log "Starting shell mode"
    cd /workspace
    exec bash
}

# Main entrypoint
main() {
    # Phase 1: Setup
    clear_coordination_state
    setup_claude_config

    # Phase 2: Modify settings.json (replace hooks)
    if [[ -f /opt/claude-team/lib/settings_modifier.py ]]; then
        log "Modifying settings.json..."
        python3 /opt/claude-team/lib/settings_modifier.py
    fi

    # Phase 3: Run mode
    case "$MODE" in
        run)
            run_multi_agent
            ;;
        shell)
            run_shell
            ;;
        *)
            error "Unknown mode: $MODE (use: run, shell)"
            ;;
    esac
}

# Execute main
main
