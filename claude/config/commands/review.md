---
model: sonnet
---
Review a pull request using specialized agents. In the workflow `/review → /pr → /fix → /merge`,
this step generates the findings that get documented in the PR.

## Usage

```
/review              Review current branch's PR
/review #123         Review specific PR by number
/review #123 tests   Review only specific aspects
```

**Aspects:** `code` `tests` `errors` `comments` `types` `simplify` `all` (default)

---

## Process

### 1. Identify PR

```bash
# Current branch
gh pr view --json number,title,body,files,commits

# Or specific PR
gh pr view 123 --json number,title,body,files,commits

# Get the diff
gh pr diff $PR
```

### 2. Determine Applicable Agents

Based on changed files:

| Condition | Agent |
|-----------|-------|
| Always | `code-reviewer` — bugs, quality, project conventions |
| Test files changed | `pr-test-analyzer` — coverage gaps, test quality |
| Comments/docs added | `comment-analyzer` — comment accuracy, rot |
| Error handling changed | `silent-failure-hunter` — silent failures, bare excepts |
| Types added/modified | `type-design-analyzer` — invariants, encapsulation |
| After passing review | `code-simplifier` — polish and clarity |

Skip agents that don't apply. Run applicable ones in parallel.

### 3. Launch Agents

Pass each agent the PR diff and context:

```
Task tool:
  subagent_type: code-reviewer   (or other applicable agent)
  prompt: |
    Review PR #$PR: $TITLE

    PR Description:
    $BODY

    Files changed:
    $FILE_LIST

    Diff:
    $DIFF

    Report findings with file:line references, severity (critical/warning/suggestion),
    and suggested fix for each issue.
```

### 4. Aggregate & Present

Combine agent results into a unified report:

```
PR Review: #123 feat(auth): add OAuth support
═══════════════════════════════════════════════════════════════

Critical (0)
────────────────────────────────────────────────────────────────
None

Warnings (2)
────────────────────────────────────────────────────────────────
[code-reviewer] src/auth/oauth.py:45
  Missing error handling for token refresh failure.
  Fix: Wrap in try/except, raise AuthError on failure.

[silent-failure-hunter] src/auth/oauth.py:78
  Token stored in plain text in session.
  Fix: Encrypt sensitive session data.

Suggestions (3)
────────────────────────────────────────────────────────────────
[code-reviewer] src/auth/oauth.py:23
  Magic string "oauth_callback" should be a constant.

[pr-test-analyzer] tests/test_oauth.py
  Missing test for token expiry edge case.

[comment-analyzer] src/auth/oauth.py:12
  Docstring says "returns bool" but function returns None.

Strengths
────────────────────────────────────────────────────────────────
✓ Good separation of concerns
✓ Comprehensive happy-path tests
✓ Clear commit messages

Summary: 0 critical, 2 warnings, 3 suggestions
```

### 5. Document Findings in the PR (automatic)

After presenting the report, **always** post the findings as a PR comment without asking:

```bash
gh pr comment $PR --body "$(cat <<'EOF'
## Review Findings

### Critical (N)
...

### Warnings (N)
...

### Suggestions (N)
...

### Strengths
...

---
🤖 *Review by Claude*
EOF
)"
```

If the PR doesn't exist yet (no open PR for the branch), skip this step and note that findings
will be documented when `/pr` is run.

After posting, confirm:
```
✓ Findings posted to PR #123
Next: /fix — address the findings
```
