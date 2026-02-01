#!/usr/bin/env bash
#
# Claude Code hook for swarm-daemon semantic events
#
# Emits semantic events to swarm-daemon when Claude uses tools.
# Fire-and-forget design: runs async, doesn't block Claude.
#
# Input: JSON on stdin with tool call metadata
# Output: JSON with allow/deny decision (always allow)

set -euo pipefail

# Disable job control to prevent background job messages
set +m

# Read JSON input
INPUT=$(cat)

# Extract tool name and parameters (handle both old and new Claude Code formats)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // .tool // "unknown"')
PARAMS=$(echo "$INPUT" | jq -c '.tool_input // .params // {}')
RESULT=$(echo "$INPUT" | jq -c '.tool_response // .result // {}')

# Determine event type based on tool
case "$TOOL" in
    Read)
        EVENT="TOOL_READ"
        FILE=$(echo "$PARAMS" | jq -r '.file_path // "unknown"')
        METADATA="{\"file\": \"$FILE\"}"
        ;;
    Edit)
        EVENT="TOOL_EDIT"
        FILE=$(echo "$PARAMS" | jq -r '.file_path // "unknown"')
        # Count lines changed (estimate from old_string/new_string)
        OLD_LINES=$(echo "$PARAMS" | jq -r '.old_string // ""' | wc -l)
        NEW_LINES=$(echo "$PARAMS" | jq -r '.new_string // ""' | wc -l)
        LINES_CHANGED=$((OLD_LINES > NEW_LINES ? OLD_LINES : NEW_LINES))
        METADATA="{\"file\": \"$FILE\", \"lines\": $LINES_CHANGED}"
        ;;
    Write)
        EVENT="TOOL_WRITE"
        FILE=$(echo "$PARAMS" | jq -r '.file_path // "unknown"')
        LINES=$(echo "$PARAMS" | jq -r '.content // ""' | wc -l)
        METADATA="{\"file\": \"$FILE\", \"lines\": $LINES}"
        ;;
    Bash)
        # Detect git operations for specialized events
        COMMAND=$(echo "$PARAMS" | jq -r '.command // ""')

        if [[ "$COMMAND" =~ ^git[[:space:]]+commit ]]; then
            EVENT="GIT_COMMIT"
            METADATA="{\"command\": \"$COMMAND\"}"
        elif [[ "$COMMAND" =~ ^git[[:space:]]+push ]]; then
            EVENT="GIT_PUSH"
            METADATA="{\"command\": \"$COMMAND\"}"
        elif [[ "$COMMAND" =~ ^git[[:space:]]+rebase ]]; then
            EVENT="GIT_REBASE"
            METADATA="{\"command\": \"$COMMAND\"}"
        elif [[ "$COMMAND" =~ (pytest|npm[[:space:]]+test|make[[:space:]]+test) ]]; then
            # Detect test commands - emit TEST_STARTED now, result will come from PostToolUse
            EVENT="TEST_STARTED"
            METADATA="{\"command\": \"$COMMAND\"}"
        elif [[ "$COMMAND" =~ (ruff|eslint|mypy|pylint) ]]; then
            EVENT="LINT_STARTED"
            METADATA="{\"command\": \"$COMMAND\"}"
        else
            EVENT="TOOL_BASH"
            # Truncate long commands
            SHORT_CMD=$(echo "$COMMAND" | cut -c1-100)
            METADATA="{\"command\": \"$SHORT_CMD\"}"
        fi
        ;;
    Grep)
        EVENT="TOOL_GREP"
        PATTERN=$(echo "$PARAMS" | jq -r '.pattern // "unknown"')
        METADATA="{\"pattern\": \"$PATTERN\"}"
        ;;
    Glob)
        EVENT="TOOL_GLOB"
        PATTERN=$(echo "$PARAMS" | jq -r '.pattern // "unknown"')
        METADATA="{\"pattern\": \"$PATTERN\"}"
        ;;
    Task)
        EVENT="TOOL_TASK"
        SUBAGENT=$(echo "$PARAMS" | jq -r '.subagent_type // "unknown"')
        METADATA="{\"subagent\": \"$SUBAGENT\"}"
        ;;
    *)
        # Unknown tool, skip
        echo '{"decision": "allow"}'
        exit 0
        ;;
esac

# Emit event to swarm-daemon (fire-and-forget, background)
# Use timeout to ensure we don't hang if daemon is slow/stuck
(
    timeout 0.05s swarm-daemon hook "$EVENT" "$METADATA" 2>/dev/null || true
) &

# Always allow the operation
echo '{"decision": "allow"}'
exit 0
