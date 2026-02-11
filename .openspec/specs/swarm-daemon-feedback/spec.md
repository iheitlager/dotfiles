# Spec: swarm-daemon daemon foreground feedback

## Problem

`swarm-daemon daemon` runs silently after 4 startup lines. Hooks from Claude Code
fire events via `swarm-daemon hook EVENT` → writes to `events.log`, but the
daemon never displays these. Running in a terminal gives no confirmation that
the swarm system is alive and receiving hook events.

## Root Cause

`SwarmDaemon.run()` (swarm-daemon:1128) only:
1. Checks stale agents every poll interval (disabled by default via config)
2. Detects patterns every 12 loops (~1 min)

It never reads `events.log`. So hook events land invisibly.

## Requirements

### R1: Live event tail in foreground mode

When the daemon is started in a terminal (stdout/stderr is a tty), it MUST
display new events from `events.log` as they arrive (tail-follow behavior).

**Format** (one line per event):
```
HH:MM:SS  EVENT_TYPE          agent-id   [data summary]
```

Color coding (ANSI):
- GREEN: AGENT_STARTUP, REQUEST_START, TEST_PASSED, LINT_PASSED
- YELLOW: AGENT_SHUTDOWN, JOB_PR_READY
- RED: TEST_FAILED, LINT_FAILED, AGENT_ERROR
- DIM: REQUEST, REQUEST_END (high-frequency, don't dominate)
- Default: everything else

### R2: Startup status line

After the 4 existing startup lines, print the current agent count:
```
Agents: 1 registered (dotfiles: working)
```

### R3: Periodic heartbeat

Every 30s with no new events, print a dim status line:
```
[HH:MM:SS] -- no new events (1 agent working) --
```
This confirms the daemon is alive.

### R4: No change to background (non-tty) behavior

If `not sys.stderr.isatty()`, keep current behavior: log to file only.

## Implementation Notes

- Add `tail_events_log()` method to `SwarmDaemon` that seeks to EOF on open,
  then non-blocking reads new lines, yields them
- In `SwarmDaemon.run()` loop: check for new events every poll interval;
  display using existing `_print_event`-style formatting from `SwarmREPL`
- Reuse `SwarmREPL` color constants and `_print_event` logic (avoid duplication)
- The poll loop already runs every 5s (stale_check_interval) — use same loop

## Acceptance Tests

1. `swarm-daemon daemon` in terminal shows events as Claude Code tools fire
2. `swarm-daemon daemon` piped to file shows no ANSI color codes
3. Existing `swarm-daemon log -f` still works independently
4. `swarm-daemon status` / `swarm-daemon agents` unaffected

## Files to Change

- `/Users/iheitlager/.dotfiles/local/bin/swarm-daemon` — `SwarmDaemon` class only
  - Add `_is_foreground()` helper
  - Add `_init_event_tail()` and `_drain_new_events()` methods
  - Modify `run()` to call drain + heartbeat logic when foreground

## Out of Scope

- No change to hook firing frequency
- No new config options
- No change to REPL mode
