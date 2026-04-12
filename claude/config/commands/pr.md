---
model: haiku
---
Create and document a pull request. In the workflow `/review → /pr → /fix → /merge`,
this step creates the PR and records review findings in the body so `/fix` has a clear target.

## Usage

```
/pr                  Create PR from current branch to main
/pr draft            Create as draft PR
/pr <base>           Create PR targeting specific base branch
/pr list             List open PRs with status
/pr #123             Show details for specific PR
```

---

## Create Mode (default)

### 0. Pre-flight: Validate Branch

Never create a PR from `agent-XX` base branches (worktree bases) or from `main` with no new commits.

```bash
BRANCH=$(git branch --show-current)

if [[ "$BRANCH" =~ ^agent-[0-9]+$ ]]; then
  echo "✗ Cannot create PR from agent-XX base branch."
  echo "  Create a feature branch first: git checkout -b feat/your-feature"
  exit 1
fi

if [[ "$BRANCH" == "main" ]]; then
  COMMITS_AHEAD=$(git rev-list --count origin/main..HEAD)
  if [[ "$COMMITS_AHEAD" -eq 0 ]]; then
    echo "✗ No commits ahead of main. Create a feature branch first."
    exit 1
  fi
fi
```

Also warn if:
- Uncommitted changes exist (`git status --short`)
- Branch not pushed to remote (`git log origin/$(git branch --show-current)..HEAD`)
- PR already exists for this branch (`gh pr view 2>/dev/null`)

### 1. Gather Context

```bash
git branch --show-current
git log origin/main..HEAD --oneline
git diff origin/main...HEAD --stat
git diff origin/main...HEAD
```

### 2. Generate Title

Follow conventional commit format: `type(scope): concise description`

Derive from branch name:
- `feat/add-dark-mode` → `feat(ui): add dark mode support`
- `fix/123-login-bug` → `fix(auth): resolve login redirect issue`

### 3. Generate PR Body

Include findings from any prior `/review` run in the current session as actionable items.

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
🤖 *Generated with [Claude Code](https://claude.ai/code)*
```

### 4. Detect Related Issues

Check branch name, commit messages, and TODO comments for `#N` references.
Use `Closes #N` for auto-close on merge, `Related to #N` otherwise.

### 5. Create PR

```bash
gh pr create \
  --title "type(scope): description" \
  --body "$(cat <<'EOF'
...
EOF
)"
```

Add `--draft` for work-in-progress. Add `--base <branch>` for non-main targets.

**Output:**

```
PR Created
═══════════════════════════════════════════════════════════════

PR #124: feat(auth): add OAuth support
URL: https://github.com/owner/repo/pulls/124

Review findings documented: 2 warnings, 3 suggestions
Linked issues: Closes #101, #98

Next: /fix — address the review findings
```

---

## List Mode (`/pr list`)

```bash
gh pr list --state open --json number,title,author,createdAt,reviewDecision,isDraft,labels
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

```bash
gh pr view 123 --json title,body,commits,files,reviews,comments,statusCheckRollup
```

Show: title, description, commits, files changed, review status, CI status.

---

## Safety

- Never creates PRs from `agent-XX` branches
- Never creates PRs from `main` with no new commits
- Warns before creating if tests failing or uncommitted changes exist
