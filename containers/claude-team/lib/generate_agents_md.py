#!/usr/bin/env python3
"""
Generate AGENTS.md content for main or subagents.

Outputs to stdout for use with `--append-system-prompt`.

Usage:
    # For main agent
    python3 generate_agents_md.py main-agent-1

    # For subagent (requires AGENT_PROJECT env var)
    AGENT_PROJECT=backend python3 generate_agents_md.py alice-a.1

Template Variables:
    {{AGENT_ID}}       - Agent identifier from argument
    {{AGENT_ROLE}}     - "main" or "sub" based on ID pattern
    {{PROJECT}}        - From AGENT_PROJECT env var (subagents only)
    {{WORKTREE_PATH}}  - Derived from project and agent ID
    {{BRANCH}}         - Git current branch
    {{PEER_LIST}}      - Discovered from /tmp/claude-coordination/agents/
    {{SESSION}}        - tmux session name from TMUX_SESSION or derived
"""

import os
import sys
from pathlib import Path
import yaml


def get_agent_role(agent_id: str) -> str:
    """Determine agent role from ID pattern."""
    if agent_id.startswith("main-agent-"):
        return "main"
    else:
        return "sub"


def get_project() -> str:
    """Get project name from environment."""
    return os.environ.get("AGENT_PROJECT", "unknown")


def get_worktree_path(project: str, agent_id: str) -> str:
    """Derive worktree path from project and agent ID."""
    if project == "unknown":
        return "/workspace"
    return f"/workspace/.worktrees/{project}/{agent_id}"


def get_current_branch() -> str:
    """Get current git branch."""
    try:
        result = os.popen("git branch --show-current 2>/dev/null").read().strip()
        return result or "unknown"
    except Exception:
        return "unknown"


def get_session_name() -> str:
    """Get tmux session name."""
    # Try TMUX_SESSION env var first
    session = os.environ.get("TMUX_SESSION")
    if session:
        return session

    # Derive from CLAUDE_USER
    user = os.environ.get("CLAUDE_USER", os.environ.get("USER", "user"))
    return f"claude-team-{user}"


def discover_peers() -> str:
    """Discover other agents from coordination state."""
    agents_dir = Path("/tmp/claude-coordination/agents")

    if not agents_dir.exists():
        return "No other agents currently registered."

    agent_files = sorted(agents_dir.glob("*.yaml"))

    if not agent_files:
        return "No other agents currently registered."

    peers = []
    for agent_file in agent_files:
        try:
            with open(agent_file, "r") as f:
                agent_data = yaml.safe_load(f)

            agent_id = agent_data.get("id", "unknown")
            role = agent_data.get("role", "unknown")
            project = agent_data.get("project")

            if role == "main":
                peers.append(f"- **{agent_id}** (main orchestrator)")
            elif role == "sub" and project:
                peers.append(f"- **{agent_id}** (subagent for {project})")
            else:
                peers.append(f"- **{agent_id}** ({role})")
        except Exception:
            continue

    if not peers:
        return "No other agents currently registered."

    return "\n".join(peers)


def generate_main_agent(agent_id: str, session: str, branch: str, peer_list: str) -> str:
    """Generate AGENTS.md for main agent."""
    template_path = Path(__file__).parent / "templates" / "main-agent.md"

    if not template_path.exists():
        return f"# Error: Template not found at {template_path}"

    with open(template_path, "r") as f:
        template = f.read()

    # Substitute variables
    content = template.replace("{{AGENT_ID}}", agent_id)
    content = content.replace("{{SESSION}}", session)
    content = content.replace("{{BRANCH}}", branch)
    content = content.replace("{{PEER_LIST}}", peer_list)

    return content


def generate_sub_agent(
    agent_id: str,
    project: str,
    worktree_path: str,
    branch: str,
    session: str,
    peer_list: str
) -> str:
    """Generate AGENTS.md for subagent."""
    template_path = Path(__file__).parent / "templates" / "sub-agent.md"

    if not template_path.exists():
        return f"# Error: Template not found at {template_path}"

    with open(template_path, "r") as f:
        template = f.read()

    # Substitute variables
    content = template.replace("{{AGENT_ID}}", agent_id)
    content = content.replace("{{PROJECT}}", project)
    content = content.replace("{{WORKTREE_PATH}}", worktree_path)
    content = content.replace("{{BRANCH}}", branch)
    content = content.replace("{{SESSION}}", session)
    content = content.replace("{{PEER_LIST}}", peer_list)

    return content


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: generate_agents_md.py <agent-id>", file=sys.stderr)
        print("", file=sys.stderr)
        print("Examples:", file=sys.stderr)
        print("  python3 generate_agents_md.py main-agent-1", file=sys.stderr)
        print("  AGENT_PROJECT=backend python3 generate_agents_md.py alice-a.1", file=sys.stderr)
        sys.exit(1)

    agent_id = sys.argv[1]
    role = get_agent_role(agent_id)
    branch = get_current_branch()
    session = get_session_name()
    peer_list = discover_peers()

    if role == "main":
        content = generate_main_agent(agent_id, session, branch, peer_list)
    else:
        project = get_project()
        worktree_path = get_worktree_path(project, agent_id)
        content = generate_sub_agent(agent_id, project, worktree_path, branch, session, peer_list)

    # Output to stdout for --append-system-prompt
    print(content)


if __name__ == "__main__":
    main()
