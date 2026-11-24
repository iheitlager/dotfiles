---
model: haiku
---
Merge a pull request (GitHub) or merge request (GitLab) after review findings have been documented and fixed.

Assumes the workflow: `/pr` (document) → `/fix` (fix findings) → `/merge` (this).
Below, "PR" means a GitHub pull request or a GitLab merge request (MR).

## Usage

```
/merge              Merge the current branch's PR/MR
/merge #123         Merge a specific PR (GitHub) or MR (GitLab: !123 or 123)
/merge --dry-run    Show what would happen without merging
```

## Process

### 0. Detect the Forge

```bash
HOST=$(git remote get-url origin | sed -E 's#^[a-z+]+://##; s#^[^@/]*@##; s#[:/].*##')
case "$HOST" in
  github.com) FORGE=github ;;
  *) glab auth status --hostname "$HOST" >/dev/null 2>&1 && FORGE=gitlab || FORGE=unknown ;;
esac
echo "$HOST → $FORGE"
```

- `github` → use `gh`. `gitlab` → use `glab`. `unknown` → stop and ask.
- GitLab: `glab api` fills `:id` with the current project, so `projects/:id/...` needs no project ID.
- GitLab behind a network allow-list returns **HTTP 403 with an HTML page** ("Access to Gitlab is not allowed from your IP-address"). Stop and tell the user to connect the VPN. Don't retry in a loop.

### 1. Identify the PR

**GitHub:**
```bash
gh pr view --json number,title,headRefName,baseRefName        # current branch
gh pr view 123 --json number,title,headRefName,baseRefName    # specific PR
```

**GitLab:**
```bash
BRANCH=$(git branch --show-current)
glab mr list --source-branch "$BRANCH"                        # current branch → MR iid
glab api projects/:id/merge_requests/$MR \
  | jq '{iid, title, source_branch, target_branch, draft, has_conflicts, detailed_merge_status, sha}'
```

**No PR/MR for the branch?** Stop and say so: `/pr` creates it. Don't open one silently here.
Exception: when the user explicitly asked for "/pr and /merge" in one go, create it first,
with a `<!-- changelog -->` block (see `/pr`).

**Nothing to merge?** If the branch is `main` with no commits ahead of `origin/main`, stop and report.

### 2. Pre-flight Checks

**GitHub:**
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

**GitLab:**
```bash
glab api projects/:id/merge_requests/$MR \
  | jq '{draft, has_conflicts, detailed_merge_status, pipeline: .head_pipeline.status}'
```

| Field | Must Be |
|-------|---------|
| `draft` | `false` |
| `has_conflicts` | `false` |
| `detailed_merge_status` | `mergeable` |
| `head_pipeline.status` | `success`, or `null` when the project has no CI (see below) |

`detailed_merge_status` is `checking` or `approvals_syncing` for a few seconds after a push.
That is not a failure: poll every 5 s, up to 40 s, before judging it.

```bash
for i in $(seq 1 8); do
  S=$(glab api projects/:id/merge_requests/$MR | jq -r .detailed_merge_status)
  [[ "$S" == "mergeable" ]] && break
  [[ "$S" == "checking" || "$S" == "approvals_syncing" ]] || break
  sleep 5
done
echo "$S"
```

**CI still running** (GitHub `UNSTABLE`, GitLab `ci_still_running` or pipeline `running`/`pending`):
wait 3 minutes up front (CI typically takes 3–5 min), then poll every 30 s. Don't poll in a
tight loop from the start.

```bash
sleep 180
for i in {1..10}; do
  # GitHub
  STATUS=$(gh pr view $PR --json statusCheckRollup -q \
    '[.statusCheckRollup[] | select(.status != "COMPLETED")] | length')
  [[ "$STATUS" == "0" ]] && break
  # GitLab: P=$(glab api projects/:id/merge_requests/$MR | jq -r .head_pipeline.status)
  #         [[ "$P" == "success" || "$P" == "failed" || "$P" == "canceled" ]] && break
  echo "Still waiting... ($i/10)"
  sleep 30
done
```

Stop and report if any check fails. Don't proceed.

**No CI at all** (GitLab `head_pipeline` is `null`; GitHub has no checks): the project's own gate
replaces CI. Run it on the PR head, for example `make check` (or `cargo test` / `uv run pytest`
plus lint), and stop if it fails. Say in the output that the local gate stood in for CI.

**Output when ready:**

```
Pre-flight Check Passed
═══════════════════════════════════════════════════════════════

PR #123: feat(auth): add OAuth support        (GitLab: MR !123)

✓ Not a draft
✓ No merge conflicts
✓ Approved (or: no approval rule)
✓ CI passing (5/5)                            (or: no CI; make check passed locally)

Linked issues that will close: #101, #98
Branch to delete: feat/oauth-support

Proceed? [Y/n]
```

### 3. Release Bump (done here, never in the PR)

A PR carries **no version or changelog change**. `/merge` writes them, so two open PRs
never conflict on version files or `CHANGELOG.md`.

**First check how the project versions.** Read the head of `CHANGELOG.md`, the Makefile (a
`version`/`release`/`bump` target wins over manual edits) and any ADR on versioning. If the
project has **no `CHANGELOG.md` and no release yet**, or an ADR ties versions to a milestone,
ask before bumping: don't start a release scheme on your own.

Pre-check: if the PR diff touches a version file or `CHANGELOG.md`, warn and ask. That defeats this scheme.

```bash
git diff --name-only origin/main...HEAD \
  | grep -E '(^|/)(Cargo\.toml|Cargo\.lock|lib\.rs|pyproject\.toml|package(-lock)?\.json|CHANGELOG\.md)$'
```

**Always rebase before writing the bump.** Other PRs may have merged since you started. If you
bump to X.85 and main already has X.85, you get a conflict and a wasted CI run.

```bash
git restore Cargo.lock 2>/dev/null || true    # discard local lockfile drift
git fetch origin
git rebase origin/main
CURRENT=$(grep -m1 '^version' Cargo.toml | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')  # read, don't assume
echo "Current version on main: $CURRENT"
```

Determine the bump from the branch type:
- `feat/*` → minor bump (0.X.0)
- `fix/*` → patch bump (0.0.X)
- All others → skip the bump and the changelog (no release commit; go to step 4)

**Changelog entry** comes from the PR body, between `<!-- changelog -->` and `<!-- /changelog -->` (written by `/pr`):

```bash
# GitHub
gh pr view $PR --json body -q .body | sed -n '/<!-- changelog -->/,/<!-- \/changelog -->/p' | sed '1d;$d'
# GitLab
glab api projects/:id/merge_requests/$MR | jq -r .description \
  | sed -n '/<!-- changelog -->/,/<!-- \/changelog -->/p' | sed '1d;$d'
```

If the block is missing or empty, stop and ask. Don't invent an entry.
Add it to `CHANGELOG.md` as a new `## [X.Y.Z] - YYYY-MM-DD` section.

Files to update, by project type:

**Rust:**
1. `Cargo.toml`: `version = "X.Y.Z"` (workspace root if applicable)
2. `src/lib.rs`: version constant, if present (skip when it is `env!("CARGO_PKG_VERSION")`)
3. `Cargo.lock`: `cargo update -w` (refreshes the workspace's own entries)
4. `CHANGELOG.md`: new section from the PR body block

**Python:**
1. `src/<package>/__init__.py`: `__version__ = "X.Y.Z"`
2. `pyproject.toml`: `version = "X.Y.Z"`
3. `README.md`: version badge or `## Version: X.Y.Z`
4. `CHANGELOG.md`: new section from the PR body block

**Node / frontend** (also in mixed repos): `npm version X.Y.Z --no-git-tag-version` updates
`package.json` and `package-lock.json` together.

**Generated files that record the version** (an export, a fixture, a SQL dump with an app
version in it): regenerate them with the project's own command, and diff before committing.
Only the version lines may change.

**After the bump, grep the old version repo-wide** and check every hit in `git diff --cached --stat`.
Leave unrelated hits alone (a document's own version, a schema version). Fix the rest:

```bash
git grep -n "$CURRENT" -- ':!CHANGELOG.md'
```

Run the project gate again (`make check` or equivalent) before committing.

```bash
git add CHANGELOG.md <the version files you changed>   # name files; never `git add -A`
# --no-verify: the release commit only touches version and changelog files, not code.
git commit --no-verify -m "chore: release vX.Y.Z"
git push
```

**Pushing after the rebase:** if the rebase rewrote commits that were already pushed, plain
`git push` is rejected. **Don't force-push on your own.** Ask the user first, then use
`git push --force-with-lease`. If the rebase was a no-op, plain `git push` works. Use it.

**Re-run CI after the push.** The release commit changes the head SHA, so earlier results no
longer apply. Go back to the wait loop in step 2 against the new head. Without CI, rerun the
local gate. Only then continue to step 4.

### 4. Detect Linked Issues

**GitHub:**
```bash
gh pr view $PR --json body,commits --jq '
  [.body, (.commits[].messageBody // "")] | join(" ") |
  match("(closes?|fixes?|resolves?)\\s*#([0-9]+)"; "gi") | .captures[1].string
' | sort -u
```

**GitLab** (GitLab reports the issues it will close itself):
```bash
glab api projects/:id/merge_requests/$MR/closes_issues | jq -r '.[].iid'
```

Warn if no linked issues are found.

### 5. Merge

**GitHub:** always use the API. `gh pr merge` fails with worktrees.
```bash
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
gh api -X PUT repos/$REPO/pulls/$PR/merge -f merge_method=merge
BRANCH=$(gh pr view $PR --json headRefName -q .headRefName)
gh api -X DELETE repos/$REPO/git/refs/heads/$BRANCH 2>/dev/null || true
```

**GitLab:** `glab mr merge` goes through the API, so worktrees are fine.
```bash
glab mr merge $MR --remove-source-branch --yes
```
A `405 Method Not Allowed` right after a push means GitLab is still checking. Rerun the
step 2 poll until `detailed_merge_status` is `mergeable`, then retry once.

### 6. Tag the Release

When step 3 made a release commit, tag **that commit** (not the merge commit) and push the tag:

```bash
REL=$(git log origin/main --format=%H --grep='^chore: release v' -1)
git tag -a "vX.Y.Z" "$REL" -m "vX.Y.Z: <one-line summary>"
git push origin "vX.Y.Z"
```

If tag signing fails (1Password needs the user), stop and say so. Don't bypass signing.

### 7. Sync the Local Repository

```bash
BRANCH=<the PR's source branch>
WORKTREE=$(git worktree list --porcelain | grep -B2 "branch refs/heads/$BRANCH" | grep "^worktree" | awk '{print $2}')

git fetch --prune

BASE_WORKTREE=$(git worktree list --porcelain | grep -B2 "branch refs/heads/main" | grep "^worktree" | awk '{print $2}')
if [[ -n "$BASE_WORKTREE" ]]; then
  git -C "$BASE_WORKTREE" pull origin main
fi

if [[ -n "$WORKTREE" ]]; then
  AGENT_BRANCH=$(git -C "$WORKTREE" branch --show-current | grep agent || echo "main")
  git -C "$WORKTREE" checkout "$AGENT_BRANCH" 2>/dev/null && \
    git branch -D "$BRANCH" 2>/dev/null || true
else
  git checkout main 2>/dev/null; git pull -q origin main
  git branch -D "$BRANCH" 2>/dev/null || true
fi
```

If the repository is a **git submodule** of a parent repo, commit the new pointer in the parent
(`git add <path> && git commit -m "store: <name> pointer"`) and push. Do this for each level up.

### 8. Verify Linked Issues

**GitHub:**
```bash
for ISSUE in $LINKED_ISSUES; do
  gh issue view $ISSUE --json number,state,stateReason -q '"Issue #\(.number): \(.state) (\(.stateReason // "N/A"))"'
done
```

**GitLab:**
```bash
for ISSUE in $LINKED_ISSUES; do
  glab issue view $ISSUE | grep -E '^(title|state):'
done
```

If an issue is still open, offer to close it:

```bash
gh issue close $ISSUE --reason completed --comment "Closed via PR #$PR"          # GitHub
glab issue close $ISSUE && glab issue note $ISSUE -m "Closed via !$MR"           # GitLab
```

## Output

```
PR Merged Successfully
═══════════════════════════════════════════════════════════════

✓ CHANGELOG.md updated, [0.4.0] section added
✓ Version bumped: 0.3.1 → 0.4.0 (Cargo.toml, Cargo.lock, package.json)
✓ Release commit: abc1233 chore: release v0.4.0
✓ CI re-run on release commit passed          (or: no CI; make check passed locally)
✓ PR #123 merged into main                    (GitLab: MR !123)
✓ Tag v0.4.0 on abc1233 pushed
✓ Remote branch 'feat/oauth-support' deleted
✓ Local branch 'feat/oauth-support' deleted
✓ main pulled and up to date; stale refs pruned
✓ Parent repo pointer updated                 (submodules only)

Linked Issues:
  ✓ #101 closed (completed)
  ✓ #98 closed (completed)

Repository is clean and up to date.
```

## Dry Run

```
/merge --dry-run

Dry Run: PR #123 (GitHub) / MR !123 (GitLab)
═══════════════════════════════════════════════════════════════

Would perform:
  1. Rebase on main, bump version to 0.4.0, add CHANGELOG.md section from PR body
  2. Commit + push: chore: release v0.4.0
  3. Wait for CI on the new head (or run the local gate when there is no CI)
  4. Merge into main
  5. Tag v0.4.0 on the release commit and push it
  6. Delete remote and local branch: feat/oauth-support
  7. Pull main, prune stale refs, update the parent pointer if this is a submodule

Issues that would close: #101, #98

No changes made. Run without --dry-run to execute.
```

## Edge Cases

**No PR/MR exists for the branch:** stop and point to `/pr`, unless the user asked for both.

**Local branch has unpushed commits:** warn and ask before deleting.

**PR from a fork:** skip remote branch deletion (no permission).

**Protected branch / squash not allowed:** fall back to a merge commit.

**GitLab API returns HTML 403 (IP allow-list):** stop and ask the user to connect the VPN.

**Commit or tag signing fails:** stop; the user has to approve the signature. Never use `--no-gpg-sign`.

## Safety

- Never merges draft PRs/MRs
- Never merges with failing required checks, or without a passing local gate when there is no CI
- Never merges with unresolved conflicts
- Never force-pushes without asking
- Never force-deletes unmerged local branches
- Always confirms before proceeding
