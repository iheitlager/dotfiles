#!/usr/bin/env python3
"""
Swarm event hook for swarm-daemon (PostToolUse)

Emits events to swarm-daemon when Claude uses tools.
Currently tracking: REQUEST_START, REQUEST_END

Future events (commented out for now):
- Tool-specific events (TOOL_READ, TOOL_EDIT, etc.)
- Git operations (GIT_COMMIT, GIT_PUSH, etc.)
- Test/lint events
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def get_git_repo_context():
    """Get git repository name as context identifier."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True
        )
        repo_root = Path(result.stdout.strip())
        repo_name = repo_root.name.lstrip('.')

        # Check if this is a worktree
        git_dir = repo_root / ".git"
        if git_dir.is_file():
            parent_name = repo_root.parent.name
            if parent_name.endswith("-worktree"):
                repo_name = parent_name.replace("-worktree", "").lstrip('.')

        return repo_name
    except subprocess.CalledProcessError:
        return None


def get_agent_id(context):
    """Get agent ID from environment or generate from context."""
    agent_id = os.environ.get("AGENT_ID")
    if agent_id:
        return agent_id
    return context if context else "unknown"


def emit_event(agent_id, context, event_type, metadata):
    """Emit event to swarm-daemon (fire-and-forget)."""
    try:
        metadata_json = json.dumps(metadata)
        subprocess.run(
            ["swarm-daemon", "hook", event_type, metadata_json],
            env={**os.environ, "AGENT_ID": agent_id, "AGENT_CONTEXT": context or ""},
            capture_output=True,
            timeout=0.2,
            check=False
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass  # Daemon not running or slow - that's OK


def main():
    """Main hook execution."""
    # Read JSON input from stdin
    try:
        hook_input = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        print(json.dumps({"decision": "allow"}))
        return

    # Get context and agent ID
    context = get_git_repo_context()
    if not context:
        print(json.dumps({"decision": "allow"}))
        return

    agent_id = get_agent_id(context)

    # Extract tool information
    tool_name = hook_input.get("tool_name") or hook_input.get("tool", "unknown")

    # Simple request tracking for now
    # We emit REQUEST_START and REQUEST_END as markers
    # In the future, we can add more granular tool-specific events

    # For now, just emit a simple request event
    metadata = {
        "tool": tool_name,
        "pid": os.getpid(),
        "context": context
    }

    # Emit REQUEST event (can be enhanced later to distinguish START/END)
    emit_event(agent_id, context, "REQUEST", metadata)

    # Future: Add tool-specific event logic here
    # if tool_name == "Read":
    #     emit_event(agent_id, context, "TOOL_READ", {...})
    # elif tool_name == "Edit":
    #     emit_event(agent_id, context, "TOOL_EDIT", {...})
    # etc.

    # Always allow the operation
    print(json.dumps({"decision": "allow"}))


if __name__ == "__main__":
    main()
