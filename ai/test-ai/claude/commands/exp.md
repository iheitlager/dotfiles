---
description: Send an experiment prompt to the AI clients under test
argument-hint: "[client] <prompt>"
allowed-tools: Bash(tmux:*)
---

Send an experiment to the AI client test rig.

Arguments: $ARGUMENTS

The valid client names are the ones listed in the pane map in the
test-rig section of CLAUDE.md.

Steps:
1. If the first argument is a valid client name, the target is that client
   only and the rest is the prompt. Otherwise the target is ALL clients and
   the full argument string is the prompt.
2. For each target client, look up its pane ID in the pane map in CLAUDE.md.
3. Capture the pane pre-state: tmux capture-pane -p -t <pane> -S -20
4. Send the prompt as a single line:
   tmux send-keys -l -t <pane> "<prompt>"
   tmux send-keys -t <pane> Enter
5. Report which clients received the prompt, plus their pre-state (idle,
   mid-task, permission prompt, or exited).

Notes:
- Keep the prompt exactly as provided; do not rephrase. It must stay single-line.
- Do not wait for completion; the user collects results with /exp-check.
- If a client pane is dead (client exited), report it instead of sending.
