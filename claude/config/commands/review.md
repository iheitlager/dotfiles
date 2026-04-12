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

**Aspects:** `code` `security` `tests` `docs` `types` `simplify` `all` (default)

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

### 2. Fetch Linked Issues

Extract issue references from the PR body (`Closes #N`, `Fixes #N`, `Resolves #N`, `#N`) and fetch each:

```bash
# Extract issue numbers from PR body (covers common keywords + bare #N)
echo "$BODY" | grep -oE '([Cc]loses?|[Ff]ixes?|[Rr]esolves?|[Rr]elated to)?\s*#[0-9]+' | grep -oE '[0-9]+'

# Fetch each linked issue
gh issue view $ISSUE_NUMBER --json number,title,body,labels,comments
```

Build a **Requirements context** block from all linked issues:

```
Requirements (from linked issues):
─────────────────────────────────
Issue #42: Add OAuth login support
  Labels: enhancement, auth
  Description: <issue body>
  Comments (acceptance criteria, decisions): <relevant comments>

Issue #51: Fix token refresh on expiry
  ...
```

If no issues are linked, note "No linked issues found" and proceed.

### 3. Load Project Conventions

Read `CLAUDE.md` (or `.dotfiles/claude/config/CLAUDE.md`) and include in every agent prompt:

```
Project conventions (apply what's relevant to this project's language):
- Python: ruff (linting), pyright (types), pytest (>80% coverage), uv, isort, type hints required
- Rust: clippy -D warnings, rustfmt, cargo test, cargo check
- All: ADRs in .openspec/adr/, specs in .openspec/specs/
- All: Conventional commits (feat/fix/chore/refactor/docs)
- All: No markdown files unless explicitly requested
```

### 3. Determine Applicable Agents

Based on changed files and diff content:

| Condition | Agent |
|-----------|-------|
| Always | `code-reviewer` — bugs, logic errors, project conventions, missing error handling |
| Always | `security-reviewer` — OWASP, injection, secrets, silent failures, auth |
| Test files changed OR logic-heavy diff | `test-writer` — coverage gaps, missing edge cases, test quality |
| Docstrings/comments added or modified | `docs-generator` — comment accuracy, docstring rot, outdated docs |
| Type annotations added or modified | `type-design-analyzer` — invariants, encapsulation, type correctness |
| Diff > 50 lines | `refactor-helper` — code smells, simplification, duplication |

Run all applicable agents in parallel.

### 4. Launch Agents

Pass each agent the PR diff, context, and project conventions:

```
Agent tool:
  subagent_type: code-reviewer   (or other applicable agent)
  prompt: |
    Review PR #$PR: $TITLE

    Project conventions (apply what's relevant to this project's language):
    - Python: ruff, pyright, pytest (>80% coverage), uv, isort, type hints required
    - Rust: clippy -D warnings, rustfmt, cargo test, cargo check
    - All: Conventional commits; no gratuitous markdown files
    - All: ADRs document architectural decisions (.openspec/adr/)

    Requirements (from linked issues):
    $REQUIREMENTS_CONTEXT

    PR Description:
    $BODY

    Files changed:
    $FILE_LIST

    Diff:
    $DIFF

    Report findings with file:line references, severity (critical/warning/suggestion),
    and a concrete suggested fix for each issue.
    Also flag any requirements from the linked issues that appear unaddressed or incomplete.
    Focus only on the changed code, not the entire codebase.
```

### 5. Aggregate & Present

Combine agent results into a unified report, deduplicating overlapping findings:

```
PR Review: #123 feat(auth): add OAuth support
═══════════════════════════════════════════════════════════════

Critical (0)
────────────────────────────────────────────────────────────────
None

Warnings (2)
────────────────────────────────────────────────────────────────
[security-reviewer] src/auth/oauth.py:78
  Token stored in plain text in session.
  Fix: Encrypt sensitive session data before storage.

[code-reviewer] src/auth/oauth.py:45
  Missing error handling for token refresh failure.
  Fix: Wrap in try/except, raise AuthError on failure.

Suggestions (3)
────────────────────────────────────────────────────────────────
[type-design-analyzer] src/auth/oauth.py:23
  Return type is `Optional[str]` but None is never returned.
  Fix: Change to `-> str`.

[test-writer] tests/test_oauth.py
  Missing test for token expiry edge case.

[refactor-helper] src/auth/oauth.py:12
  Magic string "oauth_callback" repeated 3 times — extract as constant.

Unaddressed Requirements (1)
────────────────────────────────────────────────────────────────
[#42] Token refresh on expiry — issue mentions handling 401 responses,
  no code path found for this in the diff.

Strengths
────────────────────────────────────────────────────────────────
✓ Good separation of concerns
✓ Comprehensive happy-path tests
✓ Clear commit messages

Summary: 0 critical, 2 warnings, 3 suggestions, 1 unaddressed requirement
```

### 6. Document Findings in the PR (automatic)

After presenting the report, **always** post findings as a PR comment without asking:

```bash
gh pr comment $PR --body "$(cat <<'EOF'
## Review Findings

### Critical (N)
...

### Warnings (N)
...

### Suggestions (N)
...

### Unaddressed Requirements (N)
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
