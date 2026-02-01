#!/usr/bin/env bash
#
# Agent registration hook for swarm-daemon
#
# Registers agent with swarm-daemon at session startup.
# Emits AGENT_WORK_START to mark agent as active.
# Only registers if in a git repository.

set -euo pipefail

# Check if AGENT_ID is already set
if [[ -n "${AGENT_ID:-}" ]]; then
    # Already set, just register
    (
        timeout 0.1s swarm-daemon hook "AGENT_WORK_START" 2>/dev/null || true
    ) &

    cat <<EOF
{
  "decision": "allow",
  "env": {
    "AGENT_ID": "$AGENT_ID"
  }
}
EOF
    exit 0
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir >/dev/null 2>&1; then
    # Not in a git repo, don't register
    echo '{"decision": "allow"}'
    exit 0
fi

# Get repository root
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "")
if [[ -z "$REPO_ROOT" ]]; then
    echo '{"decision": "allow"}'
    exit 0
fi

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
# In worktrees, .git is a file; in main repo, .git is a directory
WORKTREE_DIR=""
GIT_DIR=$(git rev-parse --git-dir 2>/dev/null)

if [[ -f "$REPO_ROOT/.git" ]]; then
    # We're in a worktree - get the worktree directory name
    WORKTREE_DIR=$(basename "$REPO_ROOT")
fi

# Build agent ID
# Examples: dotfiles-agent-1, code-analyzer-agent-2, or just dotfiles for main
if [[ -n "$WORKTREE_DIR" ]]; then
    # In a worktree: repo-worktree
    AGENT_ID="$REPO_NAME-$WORKTREE_DIR"
else
    # In main repo: just repo name
    AGENT_ID="$REPO_NAME"
fi

# Export for child processes
export AGENT_ID

# Register with swarm-daemon (fire-and-forget, background)
(
    timeout 0.1s swarm-daemon hook "AGENT_WORK_START" 2>/dev/null || true
) &

# Return success with agent ID in environment
cat <<EOF
{
  "decision": "allow",
  "env": {
    "AGENT_ID": "$AGENT_ID"
  }
}
EOF
