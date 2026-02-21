Set up and operate a 3-role in-window agent swarm (agent-1 + reviewer + merger) for sequential issue resolution with review gates.

## Overview

The **trio** pattern runs three Claude agents as panes within the current tmux window:

```
┌─────────────────────────┬─────────────────────────┐
│  ⚙️  AGENT-1 (sonnet)    │  🐚 SHELL               │
│  Implementer            │                         │
│  Coordinates the queue  ├─────────────────────────┤
│                         │  🔍 REVIEWER (sonnet)   │
│                         │  Code + assurance review│
│                         ├─────────────────────────┤
│                         │  🔀 MERGER (haiku)      │
│                         │  Semantic gate + merge  │
└─────────────────────────┴─────────────────────────┘
```

## Usage

```
/trio setup              Spin up reviewer + merger panes in this window
/trio status             Show pane status and current queue
/trio issue #N           Load and implement a single issue through full review+merge cycle
/trio queue #N #M ...    Load multiple issues, work sequentially
/trio shutdown           Gracefully close reviewer and merger panes
```

## Roles

### agent-1 — Implementer (you)
- Reads issue, implements fix on a `feat/` or `fix/` branch
- Runs tests before PR creation
- Coordinates reviewer and merger via tmux send-keys
- Works **strictly sequentially** — never starts next issue until merger confirms DONE

### reviewer — Sonnet pane 3
- Triggered by agent-1 with: `Review PR #N for issue #M. Check: ...`
- Checks: code correctness, test coverage, assurance scenario linkage (spec→test), spec compliance
- Replies via tmux: `REVIEWER: APPROVED` or `REVIEWER: REQUEST CHANGES — <list>`
- Does NOT merge

### merger — Haiku pane 4
- Triggered by agent-1 after REVIEWER APPROVED
- Semantic scan: PR → issue → spec requirement → scenario → test (full chain)
- Pre-flight: `gh pr view --json mergeable,mergeStateStatus,statusCheckRollup`
- Merges via: `gh api repos/<owner>/<repo>/pulls/<N>/merge -X PUT -f merge_method=squash`
- Runs: `git fetch --prune` in worktree
- Replies via tmux: `MERGER: DONE #N` or `MERGER: BLOCKED — <reason>`

## Setup Process

```bash
SESSION="claude-sheerpower"   # adjust to your session name
WORKTREE="/path/to/worktree"  # adjust to your worktree

# 1. Split pane 2 (shell) vertically twice to create reviewer + merger
tmux split-window -v -t $SESSION:agent-1.2 -c "$WORKTREE"
tmux split-window -v -t $SESSION:agent-1.3 -c "$WORKTREE"

# 2. Color pane titles
tmux select-pane -t $SESSION:agent-1.1 -T "⚙️  AGENT-1"
tmux select-pane -t $SESSION:agent-1.2 -T "🐚 SHELL"
tmux select-pane -t $SESSION:agent-1.3 -T "🔍 REVIEWER"
tmux select-pane -t $SESSION:agent-1.4 -T "🔀 MERGER"
tmux set-option -t $SESSION:agent-1 pane-border-status top
tmux set-option -t $SESSION:agent-1 pane-border-format \
  "#{?pane_active,#[fg=colour226 bold],#[fg=colour244]} #{pane_title} #[default]"

# 3. Start reviewer (sonnet)
tmux send-keys -t $SESSION:agent-1.3 \
  "claude --model claude-sonnet-4-6 --add-dir . --append-system-prompt \
  'REVIEWER for sheerpower: review PRs when asked. Check: (1) code correctness, \
  (2) test coverage for changed code, (3) assurance — every new scenario must link to \
  a spec requirement AND a test, (4) spec compliance — if issue acceptance criteria \
  mention updating spec, verify it was done. Reply to agent-1: \
  tmux send-keys -t $SESSION:agent-1.1 \"REVIEWER: APPROVED\" Enter \&\& \
  tmux send-keys -t $SESSION:agent-1.1 Enter'" Enter

# 4. Start merger (haiku)
tmux send-keys -t $SESSION:agent-1.4 \
  "claude --model claude-haiku-4-5-20251001 --add-dir . --append-system-prompt \
  'MERGER for sheerpower: merge PRs after reviewer approval. Steps: \
  (1) verify reviewer said APPROVED, \
  (2) semantic scan: does PR reference issue? does issue reference spec req? does req have scenario? does scenario have test? report any gap, \
  (3) pre-flight: gh pr view --json mergeable,mergeStateStatus,statusCheckRollup, \
  (4) merge: gh api repos/iheitlager/sheerpower/pulls/N/merge -X PUT -f merge_method=squash, \
  (5) git fetch --prune in worktree, \
  (6) reply: tmux send-keys -t $SESSION:agent-1.1 \"MERGER: DONE #N\" Enter \&\& \
  tmux send-keys -t $SESSION:agent-1.1 Enter'" Enter
```

## Per-Issue Workflow

For each issue, agent-1 follows this exact sequence:

```
1.  git checkout agent-N && git fetch origin && git rebase origin/main
2.  git checkout -b fix/<N>-short-description
3.  Implement fix
4.  uv run pytest tests/unit/ -q --tb=no   # must be all green
5.  git add <files> && git commit && git push -u origin fix/<N>-...
6.  gh pr create ...
7.  → tmux: ask REVIEWER to review PR #N
8.  Wait for REVIEWER response
    ├─ APPROVED → step 9
    └─ REQUEST CHANGES → fix, amend/push, go back to step 7
9.  → tmux: ask MERGER to merge PR #N (include reviewer's verdict)
10. Wait for MERGER: DONE #N
11. git checkout agent-N && git fetch --prune && git rebase origin/main
12. git branch -D fix/<N>-...
13. Mark issue done, proceed to next
```

**Sequential rule:** Never create a new feature branch while another is open.
Working in parallel requires separate worktrees.

## Reviewer Checklist (send with request)

```
Review PR #N for issue #M (<title>). Check:
(1) Code correctness — does it do what the issue says?
(2) Tests — are new/changed code paths covered?
(3) Assurance linkage — does each new test reference a spec scenario?
(4) Spec update — did the issue acceptance criteria require updating a spec file?
    If yes, confirm it was done.
(5) Edge cases from issue description — are they all handled?
Reply via: tmux send-keys -t claude-sheerpower:agent-1.1 'REVIEWER: <verdict>' Enter &&
tmux send-keys -t claude-sheerpower:agent-1.1 Enter
```

## Merger Semantic Scan

Merger always checks the full traceability chain before merging:

```
PR #N
  └─ Closes issue #M ✓/✗
       └─ Issue references spec requirement ✓/✗
            └─ Spec requirement has scenario ✓/✗
                 └─ Scenario has test reference ✓/✗
                      └─ Test file exists ✓/✗
```

Any broken link → `MERGER: BLOCKED — <gap description>` → agent-1 fixes before retry.

## Communication Protocol

Agent-1 → Reviewer:
```bash
tmux send-keys -t claude-sheerpower:agent-1.3 "Review PR #N ..." Enter
tmux send-keys -t claude-sheerpower:agent-1.3 "" Enter
```

Agent-1 → Merger:
```bash
tmux send-keys -t claude-sheerpower:agent-1.4 "Merge PR #N. Reviewer approved. ..." Enter
tmux send-keys -t claude-sheerpower:agent-1.4 "" Enter
```

Reviewer/Merger → Agent-1 (they run this themselves):
```bash
tmux send-keys -t claude-sheerpower:agent-1.1 "REVIEWER: APPROVED" Enter
tmux send-keys -t claude-sheerpower:agent-1.1 Enter
```

## Shutdown

```bash
# Close reviewer and merger panes (panes 3 and 4)
tmux send-keys -t claude-sheerpower:agent-1.3 "/exit" Enter
tmux send-keys -t claude-sheerpower:agent-1.4 "/exit" Enter
# Or kill panes directly
tmux kill-pane -t claude-sheerpower:agent-1.4
tmux kill-pane -t claude-sheerpower:agent-1.3
```

## Notes

- **Model cost**: reviewer (sonnet) for judgment calls, merger (haiku) for deterministic checklist — right cost/capability split
- **Why sequential**: feature branches in the same worktree conflict; parallel work needs `git worktree add`
- **Pane numbering**: pane 1 = agent-1 (claude), pane 2 = shell, pane 3 = reviewer, pane 4 = merger
- **Session name**: defaults to `claude-<project>` — adjust to your session
