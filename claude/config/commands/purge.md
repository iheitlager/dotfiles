---
model: claude-haiku-4-5-20251001
---

Clean up merged git branches (both local and remote), then sync all worktrees and main with origin.

## Usage

```
/purge                Clean branches + sync all worktrees
/purge local          Clean only local merged branches
/purge remote         Clean only remote merged branches
/purge --dry-run      Show what would be deleted without deleting
```

## Process

### 1. Fetch and Prune

```bash
git fetch --prune
```

This removes remote-tracking references to deleted branches.

### 2. Find Merged Branches

**Local merged branches** (excluding protected and worktree base branches):
```bash
git branch --merged main | grep -vE '^\*|main|master|develop|agent-[0-9]+'
```

**Remote merged branches:**
```bash
git branch -r --merged origin/main | grep -vE 'main|master|develop|HEAD|agent-[0-9]+'
```

### 3. Show Preview

Display branches that would be deleted:

```
Branch Cleanup Preview
═══════════════════════════════════════════════════════════════

Local branches to delete (3):
  feat/add-login          merged 5 days ago
  fix/header-alignment    merged 2 weeks ago
  chore/update-deps       merged 1 month ago

Remote branches to delete (2):
  origin/feat/add-login         merged 5 days ago
  origin/fix/header-alignment   merged 2 weeks ago

Protected (will not delete):
  main, master, develop, agent-XX branches, current branch
```

### 4. Confirm and Delete

Ask for confirmation before any deletion.

**Delete local:**
```bash
git branch -d <branch>
```

**Delete remote:**
```bash
git push origin --delete <branch>
```

If a branch is "not fully merged" but you confirm it should be deleted (e.g., it was squash-merged), force delete it:
```bash
git branch -D <branch>
```

### 5. Sync Main and All Worktrees

After branch cleanup, find all worktrees and rebase each onto origin/main:

```bash
# List all worktrees
git worktree list
```

For each worktree (including the main repo):
1. If it's on `main` — rebase onto `origin/main`
2. If it's on an `agent-XX` branch — rebase onto `origin/main`
3. Skip worktrees with uncommitted changes (warn the user)

```bash
# For each worktree path discovered above:
cd <worktree-path>
BRANCH=$(git branch --show-current)
if git diff --quiet && git diff --cached --quiet; then
    git fetch origin
    git rebase origin/main
    echo "✓ Synced $BRANCH in <worktree-path>"
else
    echo "⚠ Skipped $BRANCH in <worktree-path> — uncommitted changes"
fi
```

Then go back to the original directory.

## Safety Checks

**Never delete:**
- Current branch (`*` in branch list)
- `main`, `master`, `develop` branches
- `agent-XX` worktree base branches
- Branches with uncommitted work
- Unmerged branches (use `-d` not `-D`, ask user before force-deleting)

**Warn before deleting:**
- Branches less than 1 day old
- Branches with recent commits
- More than 10 branches at once

## Output

```
Branch Cleanup Summary
═══════════════════════════════════════════════════════════════

Deleted local branches: 3
  ✓ feat/add-login
  ✓ fix/header-alignment
  ✓ chore/update-deps

Deleted remote branches: 2
  ✓ origin/feat/add-login
  ✓ origin/fix/header-alignment

Skipped: 0
Errors: 0

Worktree Sync Summary
═══════════════════════════════════════════════════════════════

  ✓ main        /path/to/repo               → rebased on origin/main
  ✓ agent-1     /path/to/worktree/agent-1   → rebased on origin/main
  ✓ agent-2     /path/to/worktree/agent-2   → rebased on origin/main
  ⚠ agent-3     /path/to/worktree/agent-3   → skipped (uncommitted changes)

Your repository is clean!
```

## Examples

**Full cleanup (branches + sync all worktrees):**
```
/purge
```

**Preview only:**
```
/purge --dry-run
```

**Clean up after feature work:**
```
# After merging a PR
/purge local
```

**Clean up stale remote branches:**
```
/purge remote
```

## Troubleshooting

**Branch not fully merged:**
```
error: The branch 'feat/x' is not fully merged.
```
This can happen with squash-merges. Check `git log main..feat/x` — if empty, it's safe to force-delete with `git branch -D feat/x`. Ask the user before proceeding.

**Rebase conflict in worktree:**
```
CONFLICT (content): Merge conflict in src/foo.py
```
Stop the rebase (`git rebase --abort`), report the conflict to the user, and skip that worktree.

**Permission denied on remote:**
```
remote: Permission denied
```
You may not have push access to delete remote branches. Ask a maintainer.
