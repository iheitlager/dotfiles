Create, list, review, and manage pull requests.

## Usage

```
/pr                  Create PR from current branch to main
/pr draft            Create as draft PR
/pr <base>           Create PR targeting specific base branch
/pr list             List open PRs with status
/pr #123             Show details for specific PR
/pr #123 review      Code review with agent
/pr #123 checkout    Checkout PR branch locally
/pr #123 continue    Checkout and continue working on PR
/pr #123 merge       Merge PR and clean up branches
```

## Agent Strategy

PR review delegates to the code-reviewer agent for thorough analysis.

```
┌─────────────────────────────────────────────────────────────┐
│  /pr #123 review                                            │
│                                                             │
│  1. Fetch PR details (gh pr view)                           │
│                     │                                       │
│                     ▼                                       │
│  ┌──────────────────────────────────────┐                   │
│  │ code-reviewer Agent                  │                   │
│  │                                      │                   │
│  │ - Analyze all changed files          │                   │
│  │ - Check for bugs, security issues    │                   │
│  │ - Verify test coverage               │                   │
│  │ - Check project conventions          │                   │
│  └──────────────┬───────────────────────┘                   │
│                 │                                           │
│                 ▼                                           │
│  2. Present findings (interactive)                          │
│     "Here's my review..."                                   │
│                 │                                           │
│                 ▼                                           │
│  3. Offer actions                                           │
│     - Post comments to PR                                   │
│     - Approve / Request changes                             │
└─────────────────────────────────────────────────────────────┘
```

---

## List Mode (`/pr list`)

Show open PRs with useful context:

```bash
gh pr list --state open --json number,title,author,createdAt,reviewDecision,isDraft,labels
```

**Output format:**

```
Open Pull Requests
═══════════════════════════════════════════════════════════════

#142 feat(auth): add OAuth support                    @alice
     Created: 3 days ago | Reviews: Approved | Ready to merge
     Labels: enhancement, needs-review

#138 fix(api): handle timeout errors                  @bob
     Created: 1 week ago | Reviews: Changes requested
     Labels: bug, priority:high

#135 [DRAFT] refactor(models): simplify data layer   @carol
     Created: 2 weeks ago | Draft
     Labels: refactor

Summary: 3 open PRs (1 draft, 1 approved, 1 needs work)

Actions:
  /pr #142           View PR details
  /pr #142 review    Review this PR
  /pr #138 checkout  Checkout to continue work
```

**Filter options:**

```bash
# By author
gh pr list --author @me

# By review status
gh pr list --search "review:required"

# By label
gh pr list --label "priority:high"
```

---

## View Mode (`/pr #123`)

Show detailed PR information:

```bash
gh pr view 123
gh pr view 123 --json title,body,commits,files,reviews,comments
```

**Output includes:**
- Title and description
- Commits in the PR
- Files changed (with diff stats)
- Review status and comments
- CI/check status

---

## Review Mode (`/pr #123 review`)

Perform a thorough code review using the code-reviewer agent.

### Process

1. **Fetch PR context**
   ```bash
   gh pr view 123 --json title,body,files,commits
   gh pr diff 123
   ```

2. **Spawn code-reviewer agent**
   ```
   Task tool:
     subagent_type: code-reviewer
     prompt: |
       Review PR #123: <title>

       PR Description:
       <body>

       Files changed:
       <file list>

       Analyze this PR for:
       1. **Bugs & Logic Errors** - Off-by-one, null checks, race conditions
       2. **Security Issues** - Injection, auth bypass, data exposure
       3. **Code Quality** - Complexity, duplication, naming
       4. **Test Coverage** - Are changes adequately tested?
       5. **Project Conventions** - Style, patterns, architecture fit

       For each issue found, report:
       - File and line number
       - Severity (critical/warning/suggestion)
       - Description and suggested fix

       Also note what's done well.
   ```

3. **Present findings**
   ```
   PR Review: #123 feat(auth): add OAuth support
   ═══════════════════════════════════════════════════════════════

   Overall: 👍 Approve with minor suggestions

   Critical Issues (0)
   ────────────────────────────────────────────────────────────────
   None found

   Warnings (2)
   ────────────────────────────────────────────────────────────────
   src/auth/oauth.py:45
     Missing error handling for token refresh failure.
     Suggestion: Wrap in try/except and handle gracefully.

   src/auth/oauth.py:78
     Token stored in plain text in session.
     Suggestion: Consider encrypting sensitive session data.

   Suggestions (3)
   ────────────────────────────────────────────────────────────────
   src/auth/oauth.py:23
     Magic string "oauth_callback" could be a constant.

   tests/test_oauth.py:15
     Consider adding test for token expiry edge case.

   docs/auth.md
     Update docs to include new OAuth flow.

   Positive Notes
   ────────────────────────────────────────────────────────────────
   ✓ Good separation of concerns
   ✓ Comprehensive happy-path tests
   ✓ Clear commit messages
   ```

4. **Offer actions**
   - Post review comments to PR
   - Submit review (approve/request changes)
   - Checkout to fix issues yourself

### Post Review Comments

```bash
# Post individual comment
gh pr comment 123 --body "Great work on the OAuth implementation!

A few suggestions:
- Consider adding error handling at line 45
- Token storage could be more secure

---
🤖 *Review by Claude*"

# Or submit formal review
gh pr review 123 --approve --body "LGTM with minor suggestions"
gh pr review 123 --request-changes --body "Please address security concerns"
```

---

## Checkout Mode (`/pr #123 checkout`)

Checkout a PR branch locally to review or test:

```bash
gh pr checkout 123
```

After checkout:
- Run tests locally
- Explore the changes
- Add commits if needed

---

## Continue Mode (`/pr #123 continue`)

Checkout and continue working on a PR (yours or collaborative):

### Process

1. **Checkout the PR**
   ```bash
   gh pr checkout 123
   ```

2. **Understand context**
   ```bash
   gh pr view 123
   git log --oneline -10
   ```

3. **Spawn Explore agent** for context
   ```
   Task tool:
     subagent_type: Explore
     prompt: |
       Understand PR #123 to continue work:

       1. What is this PR trying to accomplish?
       2. What's already done vs remaining?
       3. Are there review comments to address?
       4. What files are being modified?

       Summarize the state and suggest next steps.
   ```

4. **Present status**
   ```
   PR #123: feat(auth): add OAuth support
   ═══════════════════════════════════════════════════════════════

   Status: Changes requested
   Author: @alice (you're helping)

   Done:
   ✓ OAuth provider integration
   ✓ Token refresh logic
   ✓ Basic tests

   To address (from reviews):
   - [ ] Add error handling for token refresh (src/auth/oauth.py:45)
   - [ ] Encrypt token in session (src/auth/oauth.py:78)
   - [ ] Add token expiry test

   Ready to continue. What would you like to work on?
   ```

---

## Merge Mode (`/pr #123 merge`)

Merge a PR and clean up both local and remote branches.

### Process

1. **Pre-merge checks**
   ```bash
   # Verify PR is mergeable
   gh pr view 123 --json mergeable,mergeStateStatus,reviewDecision
   ```

   **Check for:**
   - PR is approved (or no reviews required)
   - No merge conflicts
   - CI checks passing
   - Not a draft

   **Warn if:**
   - Changes requested but not addressed
   - Failing CI checks
   - Merge conflicts exist

2. **Confirm merge**
   ```
   PR #123: feat(auth): add OAuth support
   ═══════════════════════════════════════════════════════════════

   Status: Ready to merge
   Branch: feat/oauth-support → main
   Reviews: 2 approved
   Checks: All passing

   Merge method options:
   1. Squash and merge (recommended) - Single commit
   2. Create merge commit - Preserve history
   3. Rebase and merge - Linear history

   Proceed with squash merge? [y/N]
   ```

3. **Merge the PR**
   ```bash
   # Squash merge (default, cleaner history)
   gh pr merge 123 --squash --delete-branch

   # Or merge commit
   gh pr merge 123 --merge --delete-branch

   # Or rebase
   gh pr merge 123 --rebase --delete-branch
   ```

   The `--delete-branch` flag removes the remote branch automatically.

4. **Clean up local branch**
   ```bash
   # Get the branch name before it's gone
   BRANCH=$(gh pr view 123 --json headRefName -q .headRefName)

   # Switch to main if on the merged branch
   CURRENT=$(git branch --show-current)
   if [ "$CURRENT" = "$BRANCH" ]; then
     git checkout main
   fi

   # Update main
   git pull origin main

   # Delete local branch
   git branch -d "$BRANCH"
   ```

5. **Prune stale remote refs**
   ```bash
   git fetch --prune
   ```

### Output

```
PR Merged Successfully
═══════════════════════════════════════════════════════════════

✓ PR #123 merged into main (squash)
✓ Remote branch 'feat/oauth-support' deleted
✓ Local branch 'feat/oauth-support' deleted
✓ Switched to main
✓ Pulled latest changes

Commit: abc1234 feat(auth): add OAuth support (#123)

Next:
  /pr list          See remaining PRs
  /version check    Validate for release
  /changelog        Update changelog
```

### Merge Methods

| Method | When to Use |
|--------|-------------|
| **Squash** | Default. Clean single commit. Good for feature branches. |
| **Merge** | Preserve full commit history. Good for long-running branches. |
| **Rebase** | Linear history without merge commits. Good for small changes. |

### Edge Cases

**On the branch being merged:**
```bash
# Automatically switch to main first
git checkout main
git pull
# Then delete
```

**Branch has unpushed local commits:**
```
Warning: Local branch has 2 commits not in the PR.
These will be lost if you delete the local branch.

Options:
1. Delete anyway (lose local commits)
2. Keep local branch
3. Cancel merge
```

**PR already merged:**
```bash
# Just clean up branches
git fetch --prune
git branch -d feat/old-branch 2>/dev/null
```

---

## Create Mode (default)

Create a new PR from current branch.

### 0. Pre-flight Check: Validate Branch Type

**CRITICAL**: Never create a PR from `agent-XX` base branches (worktree bases).

```bash
BRANCH=$(git branch --show-current)

# Block PR creation from agent-XX base branches
if [[ "$BRANCH" =~ ^agent-[0-9]+$ ]]; then
  echo "✗ Cannot create PR from agent-XX base branch"
  echo ""
  echo "  agent-XX branches are worktree bases, not feature branches."
  echo ""
  echo "  To create a PR from this worktree:"
  echo "    1. Sync to main: git fetch && git rebase origin/main"
  echo "    2. Create feature branch: git checkout -b feat/your-feature"
  echo "    3. Make your changes and commit"
  echo "    4. Create PR: /pr"
  echo ""
  exit 1
fi

# Also block from main if no commits ahead
if [[ "$BRANCH" == "main" ]]; then
  COMMITS_AHEAD=$(git rev-list --count origin/main..HEAD)
  if [[ "$COMMITS_AHEAD" -eq 0 ]]; then
    echo "✗ No commits ahead of main"
    echo ""
    echo "  Create a feature branch first:"
    echo "    /br feat <description>"
    echo ""
    exit 1
  fi
fi
```

### 1. Gather Context

```bash
# Current branch and remote status
git branch --show-current
git log origin/main..HEAD --oneline

# Full diff against base
git diff origin/main...HEAD --stat
git diff origin/main...HEAD
```

### 2. Analyze Changes

- **Commits**: Review all commits being merged (not just the latest)
- **Files changed**: Identify affected areas/modules
- **Type of change**: Feature, fix, refactor, docs, etc.
- **Breaking changes**: API changes, schema changes, config changes
- **Related issues**: Look for issue references in commits or branch name

### 3. Generate PR Title

Follow conventional commit format:

```
type(scope): concise description
```

**From branch name patterns:**
- `feat/add-dark-mode` → `feat(ui): add dark mode support`
- `fix/123-login-bug` → `fix(auth): resolve login redirect issue`
- `refactor/cleanup-models` → `refactor(models): simplify data layer`

### 4. Generate PR Body

```markdown
## Summary

[2-3 bullet points describing what this PR does and why]

## Changes

[Grouped list of significant changes]

### Added
- New feature X

### Changed
- Modified behavior Y

### Fixed
- Bug Z

## Testing

[How was this tested? What should reviewers check?]

- [ ] Unit tests added/updated
- [ ] Manual testing performed
- [ ] Edge cases considered

## Related Issues

Closes #123
Related to #456

---
Generated with [Claude Code](https://claude.ai/code)
```

### 5. Detect Related Issues

Look for issue references in:
- Branch name: `fix/123-description` → #123
- Commit messages: `Closes #123`, `Fixes #456`
- TODO comments mentioning issues

Include appropriate keywords:
- `Closes #N` — Auto-close when merged
- `Fixes #N` — Auto-close when merged (bugs)
- `Related to #N` — Link without closing

### 6. Check PR Readiness

Before creating, verify:

```bash
# Tests pass
make test  # or appropriate test command

# No uncommitted changes
git status --short

# Branch is pushed
git log origin/$(git branch --show-current)..HEAD
```

**Warn if:**
- Tests are failing
- Uncommitted changes exist
- Branch not pushed to remote
- No commits ahead of base
- PR already exists for this branch

### 7. Create PR

```bash
gh pr create \
  --title "type(scope): description" \
  --body "$(cat <<'EOF'
## Summary
...

## Changes
...

## Testing
...

---
Generated with [Claude Code](https://claude.ai/code)
EOF
)"
```

**Options:**
- `--draft` for work-in-progress
- `--base <branch>` for non-main targets
- `--reviewer <user>` if reviewers identified
- `--label <label>` based on change type

---

## Reviewer Suggestions

Suggest reviewers based on:
- CODEOWNERS file (if exists)
- Git blame for modified files
- Recent contributors to affected areas

```bash
# Find contributors to changed files
git diff origin/main...HEAD --name-only | \
  xargs -I{} git log --format='%an' -- {} | \
  sort | uniq -c | sort -rn | head -5
```

---

## Output

After any operation, suggest relevant next actions:

**After create:**
- Add reviewers: `gh pr edit --add-reviewer @user`
- Add labels: `gh pr edit --add-label "enhancement"`
- View in browser: `gh pr view --web`

### Complete Swarm Job

If this PR was created from a `/take` workflow, record the PR ready event (Phase 2):

```bash
# Find job for this issue (from PR body "Closes #N")
JOB_ID=$(swarm-job list active | grep "#$ISSUE_NUM" | awk '{print $1}')
if [[ -n "$JOB_ID" ]]; then
  # Record PR ready event (Phase 2)
  swarm-daemon hook JOB_PR_READY "$JOB_ID" "$PR_NUM"
fi
```

**After review:**
- Post comments: `gh pr comment 123 --body "..."`
- Approve: `gh pr review 123 --approve`
- Checkout to fix: `/pr #123 checkout`

**After checkout:**
- Make changes and commit
- Push: `git push`
- Back to main: `git checkout main`
