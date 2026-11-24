---
description: Capture and compare outputs from all AI clients under test
allowed-tools: Bash(tmux:*)
---

Collect experiment results from the AI client test rig.

The clients under test are the ones listed in the pane map in the
test-rig section of CLAUDE.md.

Steps:
1. Pick one shared run timestamp in YYYYMMDD-HHMMSS format.
2. For each client in the pane map in CLAUDE.md:
   - Capture: tmux capture-pane -p -t <pane> -S -200
   - Save the raw output to .test-ai/<client>-<timestamp>.md
   - Judge its state: idle (input box visible), still working, permission
     prompt, or dead pane.
3. Write .test-ai/report-<timestamp>.md comparing the clients:
   - completion state per client
   - key differences in their answers or approach
   - anomalies (errors, crashes, permission prompts)
4. Summarize the comparison for the user and point to the report file.
