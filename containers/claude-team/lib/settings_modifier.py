#!/usr/bin/env python3
"""
Settings.json modifier for Claude Team containers.

Reads team config settings.json, preserves most fields, but replaces
the hooks section with container-specific coordination hooks.

The modified settings.json is written to ~/.claude/settings.json,
breaking the symlink and creating a local copy.

Usage:
    python3 settings_modifier.py
"""

import json
import os
import shutil
from pathlib import Path


# Coordination hooks for container
COORDINATION_HOOKS = {
    "SessionStart": [
        {
            "matcher": "startup|resume",
            "hooks": [
                {
                    "type": "command",
                    "command": "python3 /opt/claude-team/lib/coordination.py register"
                }
            ]
        }
    ],
    "PostToolUse": [
        {
            "matcher": "Read|Edit|Write|Bash|Grep|Glob|Task",
            "hooks": [
                {
                    "type": "command",
                    "command": "python3 /opt/claude-team/lib/coordination.py hook"
                }
            ]
        }
    ],
    "ModelChange": [
        {
            "matcher": ".*",
            "hooks": [
                {
                    "type": "command",
                    "command": "python3 /opt/claude-team/lib/coordination.py model"
                }
            ]
        }
    ]
}


def find_team_config_settings() -> Path:
    """Find team config settings.json in /workspace."""
    workspace = Path("/workspace")
    team_config = os.environ.get("CLAUDE_TEAM_CONFIG", "")

    # Try explicit team config
    if team_config:
        settings_path = workspace / team_config / "claude" / "config" / "settings.json"
        if settings_path.exists():
            return settings_path

    # Auto-detect by looking for claude/config/CLAUDE.md
    for item in workspace.iterdir():
        if item.is_dir():
            claude_md = item / "claude" / "config" / "CLAUDE.md"
            if claude_md.exists():
                settings_path = item / "claude" / "config" / "settings.json"
                if settings_path.exists():
                    return settings_path

    raise FileNotFoundError("Could not find team config settings.json in /workspace")


def clear_coordination_state():
    """Clear ephemeral coordination state directory."""
    state_dir = Path("/tmp/claude-coordination")

    # Remove and recreate
    if state_dir.exists():
        shutil.rmtree(state_dir)

    # Create directory structure
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "agents").mkdir(exist_ok=True)
    (state_dir / "jobs" / "pending").mkdir(parents=True, exist_ok=True)
    (state_dir / "jobs" / "claimed").mkdir(exist_ok=True)
    (state_dir / "jobs" / "done").mkdir(exist_ok=True)
    (state_dir / "events.log").touch()


def modify_settings():
    """Main function to modify settings.json."""
    # Find team config settings.json
    try:
        team_settings_path = find_team_config_settings()
        print(f"Found team settings: {team_settings_path}")
    except FileNotFoundError as e:
        print(f"Warning: {e}")
        print("Using default settings with coordination hooks only")
        team_settings = {}
    else:
        # Read team settings
        with open(team_settings_path, "r") as f:
            team_settings = json.load(f)

    # Prepare modified settings
    modified_settings = {}

    # Preserve these fields from team settings
    preserve_fields = [
        "permissions",
        "additionalDirectories",
        "model",
        "defaultModel",
        "disableTelemetry",
        "enableChatPreviews"
    ]

    for field in preserve_fields:
        if field in team_settings:
            modified_settings[field] = team_settings[field]

    # Replace hooks section
    modified_settings["hooks"] = COORDINATION_HOOKS

    # Write to ~/.claude/settings.json
    claude_config_dir = Path.home() / ".claude"
    claude_config_dir.mkdir(parents=True, exist_ok=True)

    output_path = claude_config_dir / "settings.json"

    # Remove existing file/symlink
    if output_path.exists() or output_path.is_symlink():
        output_path.unlink()

    # Write modified settings
    with open(output_path, "w") as f:
        json.dump(modified_settings, f, indent=2)

    print(f"Modified settings written to: {output_path}")

    # Clear coordination state
    clear_coordination_state()
    print("Coordination state cleared")


def main():
    """Entry point."""
    try:
        modify_settings()
        print("Settings modification complete")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
