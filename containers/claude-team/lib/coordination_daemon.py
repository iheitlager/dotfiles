#!/usr/bin/env python3
"""
Coordination Daemon TUI for Claude Team.

Displays real-time view of:
- Registered agents (role, project, model)
- Job queue status (pending, claimed, done)
- Recent events from coordination log

Runs in a dedicated tmux window for monitoring.

Usage:
    python3 coordination_daemon.py
"""

import curses
import time
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import yaml


# State directory
STATE_DIR = Path("/tmp/claude-coordination")
AGENTS_DIR = STATE_DIR / "agents"
JOBS_DIR = STATE_DIR / "jobs"
PENDING_DIR = JOBS_DIR / "pending"
CLAIMED_DIR = JOBS_DIR / "claimed"
DONE_DIR = JOBS_DIR / "done"
EVENT_LOG = STATE_DIR / "events.log"


def load_agents() -> List[Dict[str, Any]]:
    """Load all registered agents."""
    if not AGENTS_DIR.exists():
        return []

    agents = []
    for agent_file in sorted(AGENTS_DIR.glob("*.yaml")):
        try:
            with open(agent_file, "r") as f:
                agent_data = yaml.safe_load(f)
            agents.append(agent_data)
        except Exception:
            continue

    return agents


def load_jobs(directory: Path) -> List[Dict[str, Any]]:
    """Load jobs from a specific directory."""
    if not directory.exists():
        return []

    jobs = []
    for job_file in sorted(directory.glob("*.yaml")):
        try:
            with open(job_file, "r") as f:
                job_data = yaml.safe_load(f)
            jobs.append(job_data)
        except Exception:
            continue

    return jobs


def load_recent_events(count: int = 10) -> List[Dict[str, Any]]:
    """Load recent events from log."""
    if not EVENT_LOG.exists():
        return []

    events = []
    try:
        with open(EVENT_LOG, "r") as f:
            lines = f.readlines()

        # Get last N lines
        for line in lines[-count:]:
            try:
                event = json.loads(line.strip())
                events.append(event)
            except json.JSONDecodeError:
                continue
    except Exception:
        pass

    return events


def format_timestamp(iso_timestamp: str) -> str:
    """Format ISO timestamp to HH:MM:SS."""
    try:
        dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
        return dt.strftime("%H:%M:%S")
    except Exception:
        return "??:??:??"


def truncate_text(text: str, max_len: int) -> str:
    """Truncate text to max length."""
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."


def safe_addstr(stdscr, y: int, x: int, text: str, attr=0, max_width: int = None):
    """Safely add string to screen, catching curses errors."""
    try:
        if max_width:
            text = text[:max_width - 1]
        stdscr.addstr(y, x, text, attr)
    except curses.error:
        pass


def draw_screen(stdscr, agents: List[Dict], pending: List[Dict], claimed: List[Dict], done: List[Dict], events: List[Dict]):
    """Draw the entire TUI screen."""
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # Ensure minimum dimensions
    if height < 10 or width < 40:
        stdscr.addstr(0, 0, "Terminal too small")
        stdscr.refresh()
        return

    # Title
    title = "Claude Team Coordination Dashboard"
    try:
        stdscr.addstr(0, (width - len(title)) // 2, title, curses.A_BOLD)
        stdscr.addstr(1, 0, ("─" * (width - 1))[:width - 1])
    except curses.error:
        pass

    y = 2

    # Agents section
    try:
        stdscr.addstr(y, 0, "╭─ Agents ", curses.A_BOLD)
        if width > 10:
            stdscr.addstr(y, 10, ("─" * (width - 11))[:width - 11])
    except curses.error:
        pass
    y += 1

    if not agents:
        try:
            stdscr.addstr(y, 2, "No agents registered", curses.A_DIM)
        except curses.error:
            pass
        y += 1
    else:
        for agent in agents:
            if y >= height - 3:  # Leave room for footer
                break
            agent_id = agent.get("id", "unknown")
            role = agent.get("role", "unknown")
            project = agent.get("project", "")
            model = agent.get("model", "unknown")

            # Format agent line
            if role == "main":
                line = f"  {agent_id:<20} {role:<12} /workspace       {model:<10}"
            else:
                project_str = project or "unknown"
                line = f"  {agent_id:<20} {role:<12} {project_str:<15} {model:<10}"

            try:
                stdscr.addstr(y, 0, truncate_text(line, width - 1))
            except curses.error:
                pass
            y += 1

    y += 1

    # Jobs section
    try:
        stdscr.addstr(y, 0, "╭─ Jobs ", curses.A_BOLD)
        if width > 7:
            stdscr.addstr(y, 7, ("─" * (width - 8))[:width - 8])
    except curses.error:
        pass
    y += 1

    # Job counts
    counts = f"  Pending: {len(pending)}   Claimed: {len(claimed)}   Done: {len(done)}"
    stdscr.addstr(y, 0, counts, curses.A_BOLD)
    y += 2

    # Show pending jobs
    if pending and y < height - 3:
        for job in pending[:5]:  # Show up to 5
            if y >= height - 3:
                break
            job_id = job.get("id", "unknown")
            desc = job.get("description", "").split('\n')[0]  # First line only
            project = job.get("project", "?")
            line = f"  [PENDING] {job_id} ({project}) - {desc}"
            safe_addstr(stdscr, y, 0, truncate_text(line, width - 1), curses.A_DIM)
            y += 1
        if len(pending) > 5 and y < height - 3:
            safe_addstr(stdscr, y, 0, f"  ... and {len(pending) - 5} more", curses.A_DIM)
            y += 1

    # Show claimed jobs
    if claimed and y < height - 3:
        for job in claimed[:5]:
            if y >= height - 3:
                break
            job_id = job.get("id", "unknown")
            desc = job.get("description", "").split('\n')[0]
            claimed_by = job.get("claimed_by", "?")
            project = job.get("project", "?")
            line = f"  [CLAIMED] {job_id} by {claimed_by} ({project}) - {desc}"
            safe_addstr(stdscr, y, 0, truncate_text(line, width - 1), curses.A_DIM)
            y += 1
        if len(claimed) > 5 and y < height - 3:
            safe_addstr(stdscr, y, 0, f"  ... and {len(claimed) - 5} more", curses.A_DIM)
            y += 1

    if not pending and not claimed and y < height - 3:
        safe_addstr(stdscr, y, 2, "No pending or claimed jobs", curses.A_DIM)
        y += 1

    y += 1

    # Events section
    try:
        stdscr.addstr(y, 0, "╭─ Events ", curses.A_BOLD)
        if width > 9:
            stdscr.addstr(y, 9, ("─" * (width - 10))[:width - 10])
    except curses.error:
        pass
    y += 1

    if not events:
        if y < height - 3:
            safe_addstr(stdscr, y, 2, "No events yet", curses.A_DIM)
            y += 1
    else:
        for event in reversed(events[-10:]):  # Show last 10 events, newest first
            if y >= height - 2:
                break
            timestamp = format_timestamp(event.get("timestamp", ""))
            event_type = event.get("event", "unknown")
            data = event.get("data", {})

            # Format event line based on type
            if event_type == "agent_registered":
                agent_id = data.get("agent_id", "?")
                role = data.get("role", "?")
                line = f"  {timestamp} {agent_id} REGISTERED as {role}"
            elif event_type == "job_pushed":
                job_id = data.get("job_id", "?")
                created_by = data.get("created_by", "?")
                project = data.get("project", "?")
                line = f"  {timestamp} {created_by} PUSHED {job_id} ({project})"
            elif event_type == "job_claimed":
                job_id = data.get("job_id", "?")
                claimed_by = data.get("claimed_by", "?")
                line = f"  {timestamp} {claimed_by} CLAIMED {job_id}"
            elif event_type == "job_completed":
                job_id = data.get("job_id", "?")
                completed_by = data.get("completed_by", "?")
                line = f"  {timestamp} {completed_by} COMPLETED {job_id}"
            elif event_type == "model_changed":
                agent_id = data.get("agent_id", "?")
                new_model = data.get("new_model", "?")
                line = f"  {timestamp} {agent_id} CHANGED MODEL to {new_model}"
            else:
                line = f"  {timestamp} {event_type}"

            safe_addstr(stdscr, y, 0, truncate_text(line, width - 1), curses.A_DIM)
            y += 1

    # Footer
    if y < height - 1:
        try:
            footer = f"Press 'q' to quit | Refresh: 2s | {datetime.now().strftime('%H:%M:%S')}"
            # Draw horizontal line (leave last column empty)
            stdscr.addstr(height - 1, 0, ("─" * (width - 1))[:width - 1], curses.A_DIM)
            # Draw footer text if it fits
            footer_x = max(0, width - len(footer) - 2)
            if footer_x + len(footer) < width:
                stdscr.addstr(height - 1, footer_x, footer[:width - footer_x - 1], curses.A_DIM)
        except curses.error:
            pass

    stdscr.refresh()


def main_loop(stdscr):
    """Main TUI loop."""
    # Setup curses
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(True)  # Non-blocking input
    stdscr.timeout(100)  # Timeout for getch()

    # Setup colors if available
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    last_refresh = 0
    refresh_interval = 2  # seconds

    while True:
        # Check for quit key
        try:
            key = stdscr.getch()
            if key == ord('q') or key == ord('Q'):
                break
        except Exception:
            pass

        # Refresh data periodically
        current_time = time.time()
        if current_time - last_refresh >= refresh_interval:
            agents = load_agents()
            pending = load_jobs(PENDING_DIR)
            claimed = load_jobs(CLAIMED_DIR)
            done = load_jobs(DONE_DIR)
            events = load_recent_events(20)

            try:
                draw_screen(stdscr, agents, pending, claimed, done, events)
            except Exception as e:
                # If drawing fails, try to show error
                stdscr.clear()
                stdscr.addstr(0, 0, f"Error: {e}")
                stdscr.refresh()

            last_refresh = current_time

        time.sleep(0.1)  # Small delay to prevent CPU spinning


def main():
    """Entry point."""
    try:
        curses.wrapper(main_loop)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
