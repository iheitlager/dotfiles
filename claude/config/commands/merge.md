---
model: haiku
---
Merge a GitHub PR after review findings have already been documented and fixed.

Assumes the workflow: `/pr` (document) → `/fix` (fix findings) → `/merge` (this).

## Usage

```
/merge              Merge current branch's PR
/merge #123         Merge specific PR by number
/merge --dry-run    Show what would happen without merging
```

## Process

### 1. Identify PR

```bash
# Current branch's PR
gh pr view --json number,title,headRefName,baseRefName

# Or specific PR
gh pr view 123 --json number,title,headRefName,baseRefName
```

### 2. Pre-flight Checks

```bash
gh pr view $PR --json mergeable,mergeStateStatus,reviewDecision,statusCheckRollup,isDraft
```

| Check | Must Be |
|-------|---------|
| `isDraft` | `false` |
| `mergeable` | `MERGEABLE` |
| `mergeStateStatus` | `CLEAN` or `UNSTABLE` |
| `reviewDecision` | `APPROVED` (if required) |
| `statusCheckRollup` | All `SUCCESS` or `NEUTRAL` |

Stop and report if any check fails — do not proceed.

**Output when ready:**

```
Pre-flight Check Passed
═══════════════════════════════════════════════════════════════

PR #123: feat(auth): add OAuth support

✓ Not a draft
✓ No merge conflicts
✓ Approved
✓ CI passing (5/5)

Linked issues that will close: #101, #98
Branch to delete: feat/oauth-support

Proceed? [Y/n]
```

### 3. Update Changelog & Version, Commit

Determine version bump from branch type:
- `feat/*` → minor bump (0.X.0)
- `fix/*` → patch bump (0.0.X)
- All others → skip version bump

```bash
# Get commits since last tag
git log $(git describe --tags --abbrev=0 2>/dev/null || git rev-list --max-parents=0 HEAD)..HEAD \
  --pretty=format:"- %s" --no-merges
```

Update `CHANGELOG.md` and bump version in the appropriate locations for the project type:

**Python:**
1. `src/<package>/__init__.py` — `__version__ = "X.Y.Z"`
2. `pyproject.toml` — `version = "X.Y.Z"`
3. `README.md` — version badge or `## Version: X.Y.Z`
4. `CHANGELOG.md` — new `## [X.Y.Z] - YYYY-MM-DD` section

**Rust:**
1. `Cargo.toml` — `version = "X.Y.Z"` (workspace root if applicable)
2. `README.md` — version badge or `## Version: X.Y.Z`
3. `CHANGELOG.md` — new `## [X.Y.Z] - YYYY-MM-DD` section

If no version files exist, only update `CHANGELOG.md`.

```bash
# Python
git add CHANGELOG.md README.md src/*/ pyproject.toml

# Rust
git add CHANGELOG.md README.md Cargo.toml Cargo.lock

git commit -m "chore: release vX.Y.Z"
git push
```

### 4. Detect Linked Issues

```bash
gh pr view $PR --json body,commits --jq '
  [.body, (.commits[].messageBody // "")] |
  join(" ") |
  match("(closes?|fixes?|resolves?)\\s*#([0-9]+)"; "gi") |
  .captures[1].string
' | sort -u
```

Warn if no linked issues found.

### 5. Merge the PR

Always use the GitHub API — `gh pr merge` fails with worktrees:

```bash
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)

gh api -X PUT repos/$REPO/pulls/$PR/merge \
  -f merge_method=merge

# Delete remote branch
BRANCH=$(gh pr view $PR --json headRefName -q .headRefName)
gh api -X DELETE repos/$REPO/git/refs/heads/$BRANCH 2>/dev/null || true
```

### 6. Sync Local Repository

```bash
BRANCH=$(gh pr view $PR --json headRefName -q .headRefName)

# Find worktree with this branch checked out
WORKTREE=$(git worktree list --porcelain | grep -B2 "branch refs/heads/$BRANCH" | grep "^worktree" | awk '{print $2}')

git fetch --prune

# Pull main in whichever worktree has it
BASE_WORKTREE=$(git worktree list --porcelain | grep -B2 "branch refs/heads/main" | grep "^worktree" | awk '{print $2}')
if [[ -n "$BASE_WORKTREE" ]]; then
  git -C "$BASE_WORKTREE" pull origin main
fi

# Delete local feature branch
if [[ -n "$WORKTREE" ]]; then
  AGENT_BRANCH=$(git -C "$WORKTREE" branch --show-current | grep agent || echo "main")
  git -C "$WORKTREE" checkout "$AGENT_BRANCH" 2>/dev/null && \
    git branch -D "$BRANCH" 2>/dev/null || true
else
  git branch -D "$BRANCH" 2>/dev/null || true
fi
```

### 7. Verify Linked Issues

```bash
for ISSUE in $LINKED_ISSUES; do
  gh issue view $ISSUE --json number,state,stateReason -q \
    '"Issue #\(.number): \(.state) (\(.stateReason // "N/A"))"'
done
```

If an issue is still open, offer to close it manually:

```bash
gh issue close $ISSUE --reason completed --comment "Closed via PR #$PR"
```

## Output

```
PR Merged Successfully
═══════════════════════════════════════════════════════════════

✓ CHANGELOG.md updated — [0.4.0] section added
✓ Version bumped: 0.3.1 → 0.4.0
✓ Release commit: abc1233 chore: release v0.4.0
✓ PR #123 merged into main
✓ Remote branch 'feat/oauth-support' deleted
✓ Local branch 'feat/oauth-support' deleted
✓ main pulled and up to date
✓ Stale refs pruned

Linked Issues:
  ✓ #101 closed (completed)
  ✓ #98 closed (completed)

Repository is clean and up to date.
```

## Dry Run

```
/merge --dry-run

Dry Run: PR #123
═══════════════════════════════════════════════════════════════

Would perform:
  1. Update CHANGELOG.md + bump version to 0.4.0
  2. Commit: chore: release v0.4.0
  3. Merge PR #123 into main
  4. Delete remote branch: origin/feat/oauth-support
  5. Delete local branch: feat/oauth-support
  6. Pull main, prune stale refs

Issues that would close: #101, #98

No changes made. Run without --dry-run to execute.
```

## Edge Cases

**Local branch has unpushed commits:** warn and ask before deleting.

**PR from fork:** skip remote branch deletion (no permission).

**Protected branch / squash not allowed:** fall back to merge commit.

## Safety

- Never merges draft PRs
- Never merges with failing required checks
- Never merges with unresolved conflicts
- Never force-deletes unmerged local branches
- Always confirms before proceeding
