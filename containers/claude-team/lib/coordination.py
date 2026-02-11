#!/usr/bin/env python3
"""
Coordination library for Claude Team multi-agent system.

Provides file-based coordination via YAML job queue and agent registry.
State directory: /tmp/claude-coordination/

Commands:
- register: Announce agent startup (SessionStart hook)
- hook: Track tool usage (PostToolUse hook)
- model: Track model changes (ModelChange hook)
- push_job: Create job in pending queue (main agents)
- claim_job: Move job from pending to claimed (subagents)
- complete_job: Move job from claimed to done (subagents)

All commands return {} JSON to continue Claude execution.
"""

import json
import os
import sys
import fcntl
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
import yaml


# State directory structure
STATE_DIR = Path("/tmp/claude-coordination")
AGENTS_DIR = STATE_DIR / "agents"
JOBS_DIR = STATE_DIR / "jobs"
PENDING_DIR = JOBS_DIR / "pending"
CLAIMED_DIR = JOBS_DIR / "claimed"
DONE_DIR = JOBS_DIR / "done"
EVENT_LOG = STATE_DIR / "events.log"


def ensure_state_dirs():
    """Ensure all state directories exist."""
    for directory in [AGENTS_DIR, PENDING_DIR, CLAIMED_DIR, DONE_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    if not EVENT_LOG.exists():
        EVENT_LOG.touch()


def log_event(event_type: str, data: Dict[str, Any]):
    """Append event to audit log with file locking."""
    ensure_state_dirs()

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event_type,
        "data": data
    }

    with open(EVENT_LOG, "a") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            f.write(json.dumps(event) + "\n")
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def atomic_write_yaml(path: Path, data: Dict[str, Any]):
    """Write YAML file atomically using rename."""
    temp_path = path.with_suffix(".tmp")
    with open(temp_path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    temp_path.rename(path)


def atomic_move(src: Path, dst: Path):
    """Move file atomically."""
    src.rename(dst)


def get_agent_id() -> str:
    """Get agent ID from environment or generate from tmux pane."""
    agent_id = os.environ.get("AGENT_ID")
    if agent_id:
        return agent_id

    # Fallback: derive from tmux pane
    tmux_pane = os.environ.get("TMUX_PANE", "unknown")
    return f"agent-{tmux_pane}"


def get_agent_role() -> str:
    """Get agent role from environment."""
    return os.environ.get("AGENT_ROLE", "unknown")


def get_agent_project() -> Optional[str]:
    """Get agent project from environment (subagents only)."""
    return os.environ.get("AGENT_PROJECT")


def get_working_directory() -> str:
    """Get current working directory."""
    return os.getcwd()


def get_model() -> str:
    """Get Claude model from environment or default."""
    return os.environ.get("CLAUDE_MODEL", "unknown")


def cmd_register():
    """Register agent startup (SessionStart hook)."""
    ensure_state_dirs()

    agent_id = get_agent_id()
    agent_file = AGENTS_DIR / f"{agent_id}.yaml"

    agent_data = {
        "id": agent_id,
        "role": get_agent_role(),
        "project": get_agent_project(),
        "working_directory": get_working_directory(),
        "model": get_model(),
        "registered_at": datetime.now(timezone.utc).isoformat(),
        "last_seen": datetime.now(timezone.utc).isoformat()
    }

    atomic_write_yaml(agent_file, agent_data)

    log_event("agent_registered", {
        "agent_id": agent_id,
        "role": agent_data["role"],
        "project": agent_data["project"]
    })

    return {}


def cmd_hook():
    """Track tool usage (PostToolUse hook)."""
    agent_id = get_agent_id()
    agent_file = AGENTS_DIR / f"{agent_id}.yaml"

    # Update last_seen timestamp
    if agent_file.exists():
        with open(agent_file, "r") as f:
            agent_data = yaml.safe_load(f)

        agent_data["last_seen"] = datetime.now(timezone.utc).isoformat()
        atomic_write_yaml(agent_file, agent_data)

    return {}


def cmd_model():
    """Track model changes (ModelChange hook)."""
    agent_id = get_agent_id()
    agent_file = AGENTS_DIR / f"{agent_id}.yaml"

    # Update model and last_seen
    if agent_file.exists():
        with open(agent_file, "r") as f:
            agent_data = yaml.safe_load(f)

        new_model = get_model()
        old_model = agent_data.get("model", "unknown")

        agent_data["model"] = new_model
        agent_data["last_seen"] = datetime.now(timezone.utc).isoformat()
        atomic_write_yaml(agent_file, agent_data)

        log_event("model_changed", {
            "agent_id": agent_id,
            "old_model": old_model,
            "new_model": new_model
        })

    return {}


def cmd_push_job(description: str, project: str, priority: str = "normal"):
    """Create job in pending queue (main agents)."""
    ensure_state_dirs()

    agent_id = get_agent_id()

    # Generate job ID
    timestamp = int(time.time() * 1000)
    job_id = f"job-{timestamp}"

    job_data = {
        "id": job_id,
        "created": datetime.now(timezone.utc).isoformat(),
        "created_by": agent_id,
        "project": project,
        "priority": priority,
        "description": description,
        "acceptance_criteria": "All tests pass, no linting errors",
        "claimed_by": None,
        "claimed_at": None,
        "completed_at": None,
        "result": None
    }

    job_file = PENDING_DIR / f"{job_id}.yaml"
    atomic_write_yaml(job_file, job_data)

    log_event("job_pushed", {
        "job_id": job_id,
        "created_by": agent_id,
        "project": project,
        "description": description
    })

    print(f"Job created: {job_id}", file=sys.stderr)
    return {}


def cmd_claim_job():
    """Claim job from pending queue (subagents)."""
    ensure_state_dirs()

    agent_id = get_agent_id()
    agent_project = get_agent_project()

    if not agent_project:
        print("Error: AGENT_PROJECT not set", file=sys.stderr)
        return {}

    # Find first pending job for this project
    pending_jobs = sorted(PENDING_DIR.glob("*.yaml"))

    for job_file in pending_jobs:
        with open(job_file, "r") as f:
            job_data = yaml.safe_load(f)

        if job_data.get("project") == agent_project:
            # Claim the job
            job_data["claimed_by"] = agent_id
            job_data["claimed_at"] = datetime.now(timezone.utc).isoformat()

            claimed_file = CLAIMED_DIR / job_file.name
            atomic_write_yaml(claimed_file, job_data)

            # Remove from pending (atomic)
            try:
                job_file.unlink()
            except FileNotFoundError:
                # Another agent claimed it first
                claimed_file.unlink()
                continue

            log_event("job_claimed", {
                "job_id": job_data["id"],
                "claimed_by": agent_id,
                "project": agent_project
            })

            print(f"Claimed job: {job_data['id']}", file=sys.stderr)
            print(f"Description: {job_data['description']}", file=sys.stderr)
            return {}

    print("No pending jobs for this project", file=sys.stderr)
    return {}


def cmd_complete_job(job_id: str, result: str):
    """Complete job and move to done queue (subagents)."""
    ensure_state_dirs()

    agent_id = get_agent_id()
    claimed_file = CLAIMED_DIR / f"{job_id}.yaml"

    if not claimed_file.exists():
        print(f"Error: Job {job_id} not found in claimed queue", file=sys.stderr)
        return {}

    with open(claimed_file, "r") as f:
        job_data = yaml.safe_load(f)

    # Verify this agent claimed the job
    if job_data.get("claimed_by") != agent_id:
        print(f"Error: Job {job_id} not claimed by this agent", file=sys.stderr)
        return {}

    # Mark as complete
    job_data["completed_at"] = datetime.now(timezone.utc).isoformat()
    job_data["result"] = result

    done_file = DONE_DIR / f"{job_id}.yaml"
    atomic_write_yaml(done_file, job_data)

    # Remove from claimed
    claimed_file.unlink()

    log_event("job_completed", {
        "job_id": job_id,
        "completed_by": agent_id,
        "result": result
    })

    print(f"Job completed: {job_id}", file=sys.stderr)
    return {}


def main():
    """Main entry point for coordination commands."""
    if len(sys.argv) < 2:
        print("Usage: coordination.py <command> [args...]", file=sys.stderr)
        print("Commands: register, hook, model, push_job, claim_job, complete_job", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]

    try:
        if command == "register":
            result = cmd_register()
        elif command == "hook":
            result = cmd_hook()
        elif command == "model":
            result = cmd_model()
        elif command == "push_job":
            if len(sys.argv) < 4:
                print("Usage: coordination.py push_job <description> <project> [priority]", file=sys.stderr)
                sys.exit(1)
            description = sys.argv[2]
            project = sys.argv[3]
            priority = sys.argv[4] if len(sys.argv) > 4 else "normal"
            result = cmd_push_job(description, project, priority)
        elif command == "claim_job":
            result = cmd_claim_job()
        elif command == "complete_job":
            if len(sys.argv) < 4:
                print("Usage: coordination.py complete_job <job_id> <result>", file=sys.stderr)
                sys.exit(1)
            job_id = sys.argv[2]
            result_text = sys.argv[3]
            result = cmd_complete_job(job_id, result_text)
        else:
            print(f"Unknown command: {command}", file=sys.stderr)
            sys.exit(1)

        # Always output {} JSON to continue Claude execution
        print(json.dumps(result))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        print(json.dumps({}))
        sys.exit(1)


if __name__ == "__main__":
    main()
