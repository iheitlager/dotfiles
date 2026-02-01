Merge a GitHub PR with full pre-flight checks, clean up, and ticket verification.

## Usage

```
/merge              Merge current branch's PR
/merge #123         Merge specific PR by number
/merge --dry-run    Show what would happen without merging
```

## Features

- **Pre-flight checks** — Verify PR is ready (approved, checks passing, no conflicts)
- **Sync & clean** — Update local repo, prune stale refs, delete merged branches
- **Return to main** — Automatically switch back to main branch
- **Ticket verification** — Confirm linked issues will be closed

## Process

### 1. Identify PR

```bash
# Current branch's PR
gh pr view --json number,title,headRefName,baseRefName

# Or specific PR
gh pr view 123 --json number,title,headRefName,baseRefName
```

### 2. Pre-flight Checks

Run all checks before proceeding:

```bash
gh pr view $PR --json mergeable,mergeStateStatus,reviewDecision,statusCheckRollup,isDraft
```

**Required conditions:**

| Check | Command | Must Be |
|-------|---------|---------|
| Not a draft | `isDraft` | `false` |
| Mergeable | `mergeable` | `MERGEABLE` |
| Merge state | `mergeStateStatus` | `CLEAN` or `UNSTABLE` |
| Reviews | `reviewDecision` | `APPROVED` (if required) |
| CI checks | `statusCheckRollup` | All `SUCCESS` or `NEUTRAL` |

**Output on issues:**

```
Pre-flight Check Failed
═══════════════════════════════════════════════════════════════

PR #123: feat(auth): add OAuth support

✗ Draft PR — cannot merge drafts
✗ Merge conflicts — rebase required
✗ Reviews: Changes requested (2 pending comments)
✗ CI: 1 failing check (test-unit)

Resolution:
  gh pr ready 123              # Mark as ready
  git fetch && git rebase      # Fix conflicts
  Address review comments      # Then re-request review
  Fix failing tests            # Push to re-run CI

Run /merge again when resolved.
```

**Output when ready:**

```
Pre-flight Check Passed
═══════════════════════════════════════════════════════════════

PR #123: feat(auth): add OAuth support

✓ Not a draft
✓ No merge conflicts
✓ Reviews: Approved (2 approvals)
✓ CI: All checks passing (5/5)

Linked issues that will close:
  #101 - Add OAuth login option
  #98  - Support third-party authentication

Merge method: squash (default)
Branch to delete: feat/oauth-support

Proceed? [Y/n]
```

### 3. Detect Linked Issues

Find issues that will be closed by this merge:

```bash
# From PR body and commits
gh pr view $PR --json body,commits --jq '
  [.body, (.commits[].messageBody // "")] |
  join(" ") |
  match("(closes?|fixes?|resolves?)\\s*#([0-9]+)"; "gi") |
  .captures[1].string
' | sort -u
```

**Keywords that auto-close:**
- `Closes #N`, `Close #N`
- `Fixes #N`, `Fix #N`
- `Resolves #N`, `Resolve #N`

If no linked issues found, warn:

```
Warning: No linked issues detected.
If this PR should close an issue, consider:
  gh pr edit 123 --body "$(gh pr view 123 --json body -q .body)

Closes #N"
```

### 4. Merge the PR

```bash
# Squash merge (default, cleaner history)
gh pr merge $PR --squash --delete-branch

# Alternative methods if requested:
# gh pr merge $PR --merge --delete-branch    # Merge commit
# gh pr merge $PR --rebase --delete-branch   # Rebase
```

The `--delete-branch` flag removes the remote branch automatically.

### 5. Sync Local Repository

```bash
# Fetch latest and prune deleted remote refs
git fetch --prune

# Get the merged branch name
BRANCH=$(gh pr view $PR --json headRefName -q .headRefName)

# Switch to main if on the merged branch
CURRENT=$(git branch --show-current)
if [ "$CURRENT" = "$BRANCH" ]; then
  git checkout main
fi

# Update main
git pull origin main

# Delete local branch (safe delete, won't delete unmerged)
git branch -d "$BRANCH" 2>/dev/null || true
```

### 6. Verify Linked Issues

After merge, confirm issues were closed:

```bash
# Check each linked issue
for ISSUE in $LINKED_ISSUES; do
  gh issue view $ISSUE --json state,stateReason -q '
    "Issue #\(.number): \(.state) (\(.stateReason // "N/A"))"
  '
done
```

**Expected output:**

```
Verifying linked issues...
  ✓ Issue #101: CLOSED (completed)
  ✓ Issue #98: CLOSED (completed)
```

**If an issue didn't close** (wrong keyword, different repo, etc.):

```
Warning: Issue #99 is still OPEN
This may happen if:
  - The issue is in a different repository
  - The closing keyword was malformed
  - GitHub's linking didn't trigger

To close manually:
  gh issue close 99 --reason completed --comment "Closed via PR #123"
```

### 7. Complete Swarm Job & Notify Agents

After merge, update the swarm queue and signal other agents:

```bash
# Complete any swarm job associated with this PR's issues (Phase 2)
for ISSUE in $LINKED_ISSUES; do
  JOB_ID=$(swarm-job list active 2>/dev/null | grep "#$ISSUE" | awk '{print $1}')
  if [[ -n "$JOB_ID" ]]; then
    # Record PR merged event (Phase 2)
    swarm-daemon hook JOB_PR_MERGED "$JOB_ID" "$PR"
  fi
done

# Signal other agents to sync (reactive action - Phase 2)
# Note: This can also be handled by swarm-daemon automatically
if tmux has-session -t "claude-$PROJECT" 2>/dev/null; then
  # Get all panes and notify them
  for pane in $(tmux list-panes -t "claude-$PROJECT:agents" -F '#{pane_index}'); do
    tmux send-keys -t "claude-$PROJECT:agents.$pane" \
      "[sync] main updated via PR #$PR - run: git fetch && git rebase origin/main" Enter
  done
fi
```

This ensures:
- Swarm queue reflects completed work
- Other agents know to sync their branches

---

## Output

```
PR Merged Successfully
═══════════════════════════════════════════════════════════════

✓ PR #123 merged into main (squash)
✓ Remote branch 'feat/oauth-support' deleted
✓ Local branch 'feat/oauth-support' deleted
✓ Switched to main
✓ Pulled latest changes
✓ Pruned stale remote refs
✓ Swarm job completed (if applicable)
✓ Notified agents to sync (if in swarm mode)

Commit: abc1234 feat(auth): add OAuth support (#123)

Linked Issues:
  ✓ #101 closed (completed)
  ✓ #98 closed (completed)

Repository is clean and up to date.

Next:
  /pr list          See remaining PRs
  /changelog        Update changelog for release
  /version          Check version consistency
```

## Dry Run Mode

With `--dry-run`, show everything that would happen without executing:

```
/merge --dry-run

Dry Run: PR #123
═══════════════════════════════════════════════════════════════

Would perform:
  1. Merge PR #123 into main (squash)
  2. Delete remote branch: origin/feat/oauth-support
  3. Delete local branch: feat/oauth-support
  4. Switch to main branch
  5. Pull latest changes
  6. Prune stale refs

Issues that would close:
  #101 - Add OAuth login option
  #98  - Support third-party authentication

No changes made. Run without --dry-run to execute.
```

## Edge Cases

**On the branch being merged:**
Automatically switches to main first before deleting.

**Local branch has unpushed commits:**
```
Warning: Local branch has commits not in the PR:
  abc1234 WIP: debugging
  def5678 temp changes

These will be lost. Options:
  1. Delete anyway (lose commits)
  2. Keep local branch
  3. Cancel merge

Choose [1/2/3]:
```

**PR from fork:**
```
Note: PR is from a fork (user/repo).
Remote branch deletion will be skipped (no permission).
```

**Protected branch rules:**
If squash isn't allowed, fall back to merge commit:
```
Note: Squash merge not allowed by branch protection.
Using merge commit instead.
```

## Merge Methods

| Method | Flag | When to Use |
|--------|------|-------------|
| **Squash** | `--squash` | Default. Clean single commit. Feature branches. |
| **Merge** | `--merge` | Preserve full history. Long-running branches. |
| **Rebase** | `--rebase` | Linear history. Small changes. |

Override default: `/merge #123 --merge` or `/merge #123 --rebase`

## Safety

- Never merges draft PRs
- Never merges with failing required checks
- Never merges with unresolved conflicts
- Never force-deletes unmerged local branches
- Always confirms before proceeding
- Dry-run available to preview actions
