# Pipeline: 3-Pane PR Review Team

Manage the reviewer + merger sub-agents that live as panes inside this window.

## Usage

```
/pipeline start       Add reviewer + merger panes to this window
/pipeline review #N   Send PR to reviewer
/pipeline status      Check pane layout
/pipeline stop        Kill reviewer + merger panes
```

## Layout (after start)

```
┌─────────────────┬─────────────────┐
│                 │   reviewer      │
│   coder (you)   │   sonnet        │
│   pane 1        │   pane 2        │
│                 ├─────────────────┤
│                 │   merger        │
│                 │   haiku         │
│                 │   pane 3        │
└─────────────────┴─────────────────┘
```

---

## `/pipeline start`

Run:
```bash
bash ~/.claude/pipeline/start.sh
```

Verify with:
```bash
tmux list-panes -t claude-sheerpower:agent-1 -F 'pane #{pane_index}: #{pane_current_command}'
```

Expected: 3 panes, pane 2 and 3 running `claude`.

---

## `/pipeline review #N`

Send the PR to the reviewer:
```bash
tmux send-keys -t claude-sheerpower:agent-1.2 "Review PR #N" Enter
```

Then wait. The reviewer will signal this pane (pane 1) with one of:
- `"PR #N APPROVED — merging"` — reviewer auto-triggers merger
- `"PR #N REJECTED: <reasons>"` — fix the issues, run `/pr` again

Do not merge manually — the merger handles it after reviewer approval.

---

## `/pipeline status`

```bash
tmux list-panes -t claude-sheerpower:agent-1 -F 'pane #{pane_index} (#{pane_width}x#{pane_height}): #{pane_current_command} — active=#{pane_active}'
```

---

## `/pipeline stop`

Remove reviewer and merger panes (highest index first):
```bash
tmux kill-pane -t claude-sheerpower:agent-1.3 2>/dev/null || true
tmux kill-pane -t claude-sheerpower:agent-1.2 2>/dev/null || true
echo "Pipeline stopped — back to 2-pane layout"
```

---

## Communication Reference

| From | To | Command |
|------|----|---------|
| You | Reviewer | `tmux send-keys -t claude-sheerpower:agent-1.2 "Review PR #N" Enter` |
| You | Merger | `tmux send-keys -t claude-sheerpower:agent-1.3 "Merge PR #N" Enter` |
| Reviewer | You | `tmux send-keys -t claude-sheerpower:agent-1.1 "..." Enter` |
| Reviewer | Merger | `tmux send-keys -t claude-sheerpower:agent-1.3 "Merge PR #N" Enter` |
| Merger | You | `tmux send-keys -t claude-sheerpower:agent-1.1 "..." Enter` |

---

## Full Workflow

```
1. Write code + /pr  →  creates PR #N

2. /pipeline review #N
   → tmux send to pane 2 (reviewer)

3. Reviewer checks spec/ADR/quality → signals pane 1 + pane 3

4. Merger runs pre-flight → merge → sync → signals pane 1

5. "PR #N MERGED" → /swarm complete job or continue
```

## Role Files

- `~/.claude/pipeline/REVIEWER.md` — reviewer instructions
- `~/.claude/pipeline/MERGER.md`   — merger instructions
- `~/.claude/pipeline/start.sh`    — startup script
