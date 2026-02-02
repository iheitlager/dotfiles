#!/usr/bin/env python3
"""
Agent registration hook for swarm-daemon (SessionStart)

Registers agent with swarm-daemon at session startup.
Emits AGENT_STARTUP event.
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def get_git_repo_context():
    """Get git repository name as context identifier."""
    try:
        # Get repo root
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True
        )
        repo_root = Path(result.stdout.strip())

        # Get repo name (handle worktrees and leading dots)
        repo_name = repo_root.name.lstrip('.')

        # Check if this is a worktree
        git_dir = repo_root / ".git"
        if git_dir.is_file():
            # In a worktree - use parent directory logic
            parent_name = repo_root.parent.name
            if parent_name.endswith("-worktree"):
                repo_name = parent_name.replace("-worktree", "").lstrip('.')

        return repo_name
    except subprocess.CalledProcessError:
        return None


def get_agent_id():
    """Determine agent ID from environment or generate it."""
    # Check if already set
    agent_id = os.environ.get("AGENT_ID")
    if agent_id:
        return agent_id

    # Get context (repo name)
    context = get_git_repo_context()
    if not context:
        return "unknown"

    # Simple agent ID: just the repo name for now
    # In multi-agent setups, this could be extended to context.agent-N
    return context


def register_agent(agent_id, context):
    """Register agent with swarm-daemon."""
    try:
        subprocess.run(
            ["swarm-daemon", "hook", "AGENT_STARTUP", f'{{"context":"{context}"}}'],
            env={**os.environ, "AGENT_ID": agent_id, "AGENT_CONTEXT": context},
            capture_output=True,
            timeout=0.2,
            check=False
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass  # Daemon not running or slow - that's OK


def main():
    """Main hook execution."""
    # Determine agent ID and context
    context = get_git_repo_context()
    if not context:
        # Not in a git repo - allow but don't register
        print(json.dumps({"decision": "allow"}))
        return

    agent_id = get_agent_id()

    # Register with daemon (fire-and-forget)
    register_agent(agent_id, context)

    # Return response with agent ID in environment
    response = {
        "decision": "allow",
        "env": {
            "AGENT_ID": agent_id,
            "AGENT_CONTEXT": context
        }
    }
    print(json.dumps(response))


if __name__ == "__main__":
    main()
