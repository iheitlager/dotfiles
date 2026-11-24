# Spec: Replace fragile sed with tmux format strings (issue #44)

## Problem

Two identical lines in `local/bin/launch-agents` extract a window name using
a 3-command pipeline that is both fragile and incorrect:

```bash
# Lines 1001 and 1019 (identical pattern):
local window_name=$(tmux list-windows -t "$target_session" \
  | grep "^${window_id}:" \
  | sed 's/^[0-9]*: \([^ ]*\).*/\1/')
```

**Defects:**
1. `tmux list-windows` default output includes status flags (`*`, `-`) and
   layout info after the name — the sed pattern stops at the first space,
   so it captures `agent-1*` or `workspace*` instead of `agent-1` / `workspace`.
2. The pipeline breaks if the window name contains characters the sed BRE
   doesn't expect (e.g. spaces, brackets).
3. Three external processes for what tmux can do natively in one call.

Both occurrences are used only for debug logging:
- Line 1001: `debug "Stopping window: $window_name"`
- Line 1019: `debug "Graceful shutdown to window: $window_name"`

## Fix

### R1: Replace both sed pipelines with a tmux format string call

```bash
local window_name=$(tmux list-windows -t "$target_session" \
  -F "#{window_index} #{window_name}" \
  | awk -v id="$window_id" '$1==id {print $2; exit}')
```

- `-F "#{window_index} #{window_name}"` — native tmux format, no status flags
- `awk -v id="$window_id" '$1==id {print $2; exit}'` — exact index match,
  no regex, handles any window name without spaces (all names in this script
  are `agent-N`, `workspace`, `monitors`, `daemon`)

### R2: Both occurrences must be replaced (they are identical)

- `local/bin/launch-agents:1001` — force-kill path
- `local/bin/launch-agents:1019` — graceful shutdown path

### R3: No other changes

- Do not touch surrounding code, other functions, or other files
- The `agent_windows` pipeline above the loop (line ~994) is out of scope

## Acceptance

1. `grep "sed 's/\^" local/bin/launch-agents` returns no matches
2. Both debug lines still present with `window_name` variable
3. `bash -n local/bin/launch-agents` passes (syntax check)
