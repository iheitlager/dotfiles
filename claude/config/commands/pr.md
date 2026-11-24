---
model: haiku
---
Create and document a pull request (GitHub) or merge request (GitLab). In the workflow
`/review → /pr → /fix → /merge`, this step creates the PR and records review findings in the
body, so `/fix` has a clear target. Below, "PR" means a GitHub PR or a GitLab MR.

## Usage

```
/pr                  Create a PR from the current branch to main
/pr draft            Create it as a draft
/pr <base>           Create a PR targeting a specific base branch
/pr list             List open PRs with their status
/pr #123             Show details for a PR (GitLab: !123 or 123)
```

---

## Detect the Forge (all modes)

```bash
HOST=$(git remote get-url origin | sed -E 's#^[a-z+]+://##; s#^[^@/]*@##; s#[:/].*##')
case "$HOST" in
  github.com) FORGE=github ;;
  *) glab auth status --hostname "$HOST" >/dev/null 2>&1 && FORGE=gitlab || FORGE=unknown ;;
esac
echo "$HOST → $FORGE"
```

- `github` → use `gh`. `gitlab` → use `glab`. `unknown` → stop and ask.
- GitLab behind a network allow-list returns **HTTP 403 with an HTML page** ("Access to Gitlab
  is not allowed from your IP-address"). Stop and ask the user to connect the VPN.

---

## Create Mode (default)

### 0. Pre-flight: Validate the Branch

Never create a PR from an `agent-XX` base branch (worktree base), or from `main` with no new commits.

```bash
BRANCH=$(git branch --show-current)

if [[ "$BRANCH" =~ ^agent-[0-9]+$ ]]; then
  echo "✗ Cannot create PR from agent-XX base branch."
  echo "  Create a feature branch first: git checkout -b feat/your-feature"
  exit 1
fi

if [[ "$BRANCH" == "main" ]]; then
  git fetch -q origin
  if [[ "$(git rev-list --count origin/main..HEAD)" -eq 0 ]]; then
    echo "✗ Nothing to open a PR for: main has no commits ahead of origin/main."
    exit 1
  fi
  echo "✗ On main with new commits. Move them to a feature branch first."
  exit 1
fi
```

Also check, and warn:
- **Uncommitted changes** (`git status --short`): commit or stash first.
- **Branch not pushed** (`git log origin/$BRANCH..HEAD`, or no upstream): push with `git push -u origin "$BRANCH"`. Never force-push without asking.
- **A PR already exists for this branch:** show it instead of creating a second one.
  - GitHub: `gh pr view 2>/dev/null`
  - GitLab: `glab mr list --source-branch "$BRANCH"`
- **The project gate fails** (`make check`, or `cargo test` / `uv run pytest` plus lint): say so in the body, or fix it first.

### 1. Gather Context

```bash
git branch --show-current
git log origin/main..HEAD --oneline
git diff origin/main...HEAD --stat
git diff origin/main...HEAD
```

### 2. Generate the Title

Follow conventional commit format: `type(scope): concise description`

Derive it from the branch name:
- `feat/add-dark-mode` → `feat(ui): add dark mode support`
- `fix/123-login-bug` → `fix(auth): resolve login redirect issue`

### 3. Generate the PR Body

Include findings from any prior `/review` run in the current session as actionable items.

Do NOT bump versions or edit `CHANGELOG.md` in the PR: `/merge` does that. The
`<!-- changelog -->` block in the body is its input, so always fill it, even for one line.

**Every number in the body is counted by a command in the same step** (test counts, files,
requirements), never written from memory. In a **public** repository, check the body for
client or customer names before creating it.

```markdown
## Summary

[2-3 bullet points: what and why]

## Changes

### Added
- ...

### Changed
- ...

### Fixed
- ...

## Changelog

<!-- changelog -->
- One line per user-visible change (consumed by `/merge` for the CHANGELOG.md section)
<!-- /changelog -->

## Review Findings

[If `/review` was run: list findings by severity for `/fix` to address.
 If no prior review: omit this section.]

| Severity | File | Issue |
|----------|------|-------|
| warning  | src/foo.py:42 | Missing error handling |
| suggestion | tests/ | Add edge case for X |

## Testing

- [ ] Unit tests added/updated
- [ ] Manual testing performed
- [ ] Edge cases considered

## Related Issues

Closes #N

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

### 4. Detect Related Issues

Check the branch name, commit messages and TODO comments for `#N` references.
Write `Closes #N` only when every acceptance criterion of #N is met; otherwise `Related to #N`.
Never put close/fix/resolve before `#N` in a negated sentence: both forges ignore the negation.
GitLab issues are `#N` too; GitLab MRs are `!N`.

### 5. Create the PR

Write the body to a file first, so quoting can't break it.

**GitHub:**
```bash
gh pr create --title "type(scope): description" --body-file /path/to/body.md
```
Add `--draft` for work in progress, and `--base <branch>` for a non-main target.

**GitLab:**
```bash
glab mr create --title "type(scope): description" --description-file /path/to/body.md \
  --target-branch main --yes
```
Add `--draft` for work in progress. `--yes` skips the interactive prompt. `glab` pushes the
branch first by default; push it yourself beforehand (step 0) so nothing surprising happens.

The command prints the URL. Check it was created: `gh pr view`, or `glab mr list --source-branch "$BRANCH"`.

**Output:**

```
PR Created
═══════════════════════════════════════════════════════════════

PR #124: feat(auth): add OAuth support              (GitLab: MR !124)
URL: https://github.com/owner/repo/pull/124

Review findings documented: 2 warnings, 3 suggestions
Linked issues: Closes #101, #98

Next: /fix to address the review findings, or /merge
```

---

## List Mode (`/pr list`)

**GitHub:**
```bash
gh pr list --state open --json number,title,author,createdAt,reviewDecision,isDraft,labels
```

**GitLab:**
```bash
glab mr list -F json | jq -r '.[] | "!\(.iid) \(.title) | \(.author.username) | \(.created_at[:10]) | draft=\(.draft) | \(.detailed_merge_status)"'
```

**Output:**

```
Open Pull Requests
═══════════════════════════════════════════════════════════════

#124 feat(auth): add OAuth support                @me
     Created: just now | Draft | 2 warnings to fix

#138 fix(api): handle timeout errors              @bob
     Created: 1 week ago | Changes requested

Summary: 2 open PRs
```

---

## View Mode (`/pr #123`)

**GitHub:**
```bash
gh pr view 123 --json title,body,commits,files,reviews,comments,statusCheckRollup
```

**GitLab:**
```bash
glab mr view 123 --comments
glab mr view 123 -F json | jq '{iid, title, state, draft, detailed_merge_status, pipeline: .head_pipeline.status}'
```

Show: title, description, commits, files changed, review status, CI status.

---

## Safety

- Never creates PRs from `agent-XX` branches
- Never creates PRs from `main`
- Never creates a second PR for a branch that already has one
- Never force-pushes without asking
- Warns before creating if tests fail or uncommitted changes exist
