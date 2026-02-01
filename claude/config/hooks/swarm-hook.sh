#!/usr/bin/env bash
#
# Claude Code hook for swarm-daemon semantic events
#
# Emits semantic events to swarm-daemon when Claude uses tools.
# Fire-and-forget design: runs async, doesn't block Claude.
#
# Input: JSON on stdin with tool call metadata
# Output: JSON with allow/deny decision (always allow)

# Don't use strict error handling - hooks should never fail
set -u
set +m

# =============================================================================
# Determine AGENT_ID (same logic as agent-register.sh)
# =============================================================================

# Check if AGENT_ID is already set
if [[ -z "${AGENT_ID:-}" ]]; then
    # Calculate AGENT_ID from git repo
    if git rev-parse --git-dir >/dev/null 2>&1; then
        REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "")

        if [[ -n "$REPO_ROOT" ]]; then
            # Get repository name (handle worktree paths and leading dots)
            REPO_NAME=$(basename "$REPO_ROOT")
            REPO_PARENT=$(basename "$(dirname "$REPO_ROOT")")

            # Remove leading dot from repo name if present
            REPO_NAME="${REPO_NAME#.}"

            # Handle worktree naming conventions
            if [[ "$REPO_PARENT" == *"-worktree" ]]; then
                REPO_NAME="${REPO_PARENT%-worktree}"
                REPO_NAME="${REPO_NAME#.}"
            elif [[ "$REPO_NAME" == *"-worktree" ]]; then
                REPO_NAME="${REPO_NAME%-worktree}"
            fi

            # Check if we're in a worktree (not the main working tree)
            WORKTREE_DIR=""
            if [[ -f "$REPO_ROOT/.git" ]]; then
                # We're in a worktree - get the worktree directory name
                WORKTREE_DIR=$(basename "$REPO_ROOT")
            fi

            # Build agent ID
            if [[ -n "$WORKTREE_DIR" ]]; then
                # In a worktree: repo-worktree
                AGENT_ID="$REPO_NAME-$WORKTREE_DIR"
            else
                # In main repo: just repo name
                AGENT_ID="$REPO_NAME"
            fi
        fi
    fi

    # Fallback if we couldn't determine it
    if [[ -z "${AGENT_ID:-}" ]]; then
        AGENT_ID="unknown"
    fi
fi

# Export AGENT_ID for swarm-daemon hook command
export AGENT_ID

# Capture process ID
PROCESS_ID="$$"

# Read JSON input
INPUT=$(cat)

# Extract tool name and parameters (handle both old and new Claude Code formats)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // .tool // "unknown"' 2>/dev/null || echo "unknown")
PARAMS=$(echo "$INPUT" | jq -c '.tool_input // .params // {}' 2>/dev/null || echo "{}")

# Determine event type based on tool
EVENT=""
METADATA=""

case "$TOOL" in
    Read)
        EVENT="TOOL_READ"
        FILE=$(echo "$PARAMS" | jq -r '.file_path // "unknown"' 2>/dev/null || echo "unknown")
        METADATA="{\"file\": \"$FILE\", \"pid\": $PROCESS_ID}"
        ;;
    Edit)
        EVENT="TOOL_EDIT"
        FILE=$(echo "$PARAMS" | jq -r '.file_path // "unknown"' 2>/dev/null || echo "unknown")
        # Count lines changed (estimate from old_string/new_string)
        OLD_LINES=$(echo "$PARAMS" | jq -r '.old_string // ""' 2>/dev/null | wc -l || echo "0")
        NEW_LINES=$(echo "$PARAMS" | jq -r '.new_string // ""' 2>/dev/null | wc -l || echo "0")
        LINES_CHANGED=$((OLD_LINES > NEW_LINES ? OLD_LINES : NEW_LINES))
        METADATA="{\"file\": \"$FILE\", \"lines\": $LINES_CHANGED, \"pid\": $PROCESS_ID}"
        ;;
    Write)
        EVENT="TOOL_WRITE"
        FILE=$(echo "$PARAMS" | jq -r '.file_path // "unknown"' 2>/dev/null || echo "unknown")
        LINES=$(echo "$PARAMS" | jq -r '.content // ""' 2>/dev/null | wc -l || echo "0")
        METADATA="{\"file\": \"$FILE\", \"lines\": $LINES, \"pid\": $PROCESS_ID}"
        ;;
    Bash)
        # Detect git operations for specialized events
        COMMAND=$(echo "$PARAMS" | jq -r '.command // ""' 2>/dev/null || echo "")

        if [[ "$COMMAND" =~ ^git[[:space:]]+commit ]]; then
            EVENT="GIT_COMMIT"
            METADATA="{\"command\": \"$COMMAND\", \"pid\": $PROCESS_ID}"
        elif [[ "$COMMAND" =~ ^git[[:space:]]+push ]]; then
            EVENT="GIT_PUSH"
            METADATA="{\"command\": \"$COMMAND\", \"pid\": $PROCESS_ID}"
        elif [[ "$COMMAND" =~ ^git[[:space:]]+rebase ]]; then
            EVENT="GIT_REBASE"
            METADATA="{\"command\": \"$COMMAND\", \"pid\": $PROCESS_ID}"
        elif [[ "$COMMAND" =~ (pytest|npm[[:space:]]+test|make[[:space:]]+test) ]]; then
            # Detect test commands - emit TEST_STARTED now, result will come from PostToolUse
            EVENT="TEST_STARTED"
            METADATA="{\"command\": \"$COMMAND\", \"pid\": $PROCESS_ID}"
        elif [[ "$COMMAND" =~ (ruff|eslint|mypy|pylint) ]]; then
            EVENT="LINT_STARTED"
            METADATA="{\"command\": \"$COMMAND\", \"pid\": $PROCESS_ID}"
        else
            EVENT="TOOL_BASH"
            # Truncate long commands
            SHORT_CMD=$(echo "$COMMAND" | cut -c1-100)
            METADATA="{\"command\": \"$SHORT_CMD\", \"pid\": $PROCESS_ID}"
        fi
        ;;
    Grep)
        EVENT="TOOL_GREP"
        PATTERN=$(echo "$PARAMS" | jq -r '.pattern // "unknown"' 2>/dev/null || echo "unknown")
        METADATA="{\"pattern\": \"$PATTERN\", \"pid\": $PROCESS_ID}"
        ;;
    Glob)
        EVENT="TOOL_GLOB"
        PATTERN=$(echo "$PARAMS" | jq -r '.pattern // "unknown"' 2>/dev/null || echo "unknown")
        METADATA="{\"pattern\": \"$PATTERN\", \"pid\": $PROCESS_ID}"
        ;;
    Task)
        EVENT="TOOL_TASK"
        SUBAGENT=$(echo "$PARAMS" | jq -r '.subagent_type // "unknown"' 2>/dev/null || echo "unknown")
        METADATA="{\"subagent\": \"$SUBAGENT\", \"pid\": $PROCESS_ID}"
        ;;
    *)
        # Unknown tool, skip
        echo '{"decision": "allow"}'
        exit 0
        ;;
esac

# Emit event to swarm-daemon (fire-and-forget, background)
# Use timeout to ensure we don't hang if daemon is slow/stuck
# Redirect all output to /dev/null to prevent any noise
if [[ -n "$EVENT" ]]; then
    (
        timeout 0.2s swarm-daemon hook "$EVENT" "$METADATA" >/dev/null 2>&1 || true
    ) &
fi

# Always allow the operation
echo '{"decision": "allow"}'
exit 0
