Clean up merged git branches (both local and remote).

## Usage

```
/purge                Clean both local and remote merged branches
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

**Local merged branches:**
```bash
git branch --merged main | grep -vE '^\*|main|master|develop'
```

**Remote merged branches:**
```bash
git branch -r --merged origin/main | grep -vE 'main|master|develop|HEAD'
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
  main, master, develop, current branch
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

## Safety Checks

**Never delete:**
- Current branch (`*` in branch list)
- `main`, `master`, `develop` branches
- Branches with uncommitted work
- Unmerged branches (use `-d` not `-D`)

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

Your repository is clean!
```

## Examples

**Quick cleanup:**
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
This means the branch has commits not in main. Check if work was lost or use `git branch -D` manually if certain.

**Permission denied on remote:**
```
remote: Permission denied
```
You may not have push access to delete remote branches. Ask a maintainer.
