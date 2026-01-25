Review codebase, documentation, and issues to identify gaps and verify completeness.

## Usage

```
/review              Full project review
/review code         Code quality and TODOs only
/review docs         Documentation completeness only
/review issues       GitHub issues health only
/review <path>       Review specific file or directory
```

## Process

### 1. Code Review

Scan for incomplete work:

```bash
# Find TODOs, FIXMEs, HACKs
grep -rn "TODO\|FIXME\|HACK\|XXX" src/ --include="*.py" --include="*.ts" --include="*.js"
```

Check for:
- [ ] TODO/FIXME comments (unfinished work)
- [ ] HACK/XXX markers (technical debt)
- [ ] Empty function bodies or `pass`/`...` placeholders
- [ ] Commented-out code blocks
- [ ] Missing error handling (bare `except:`, empty `catch`)
- [ ] Dead code (unused imports, unreachable branches)

### 2. Test Coverage

Analyze test health:

- [ ] Functions/classes without corresponding tests
- [ ] Test files that import non-existent modules
- [ ] Skipped tests (`@skip`, `pytest.mark.skip`)
- [ ] Tests with `# TODO` markers

```bash
# Check for skipped tests
grep -rn "@skip\|pytest.mark.skip\|\.skip(" tests/
```

### 3. Documentation Review

Check docs match reality:

- [ ] README features vs actual implementation
- [ ] API docs vs function signatures
- [ ] CHANGELOG vs recent commits
- [ ] Outdated examples (wrong imports, deprecated APIs)
- [ ] Broken internal links

```bash
# Find documented but potentially missing features
grep -E "^##|^\*\*" README.md | head -20
```

### 4. GitHub Issues Health

```bash
# List open issues
gh issue list --state open --limit 50

# Find stale issues (no activity in 30+ days)
gh issue list --state open --json number,title,updatedAt
```

Check for:
- [ ] Stale issues (no activity, possibly abandoned)
- [ ] Duplicate issues (similar titles/descriptions)
- [ ] Issues already fixed (check if referenced in merged PRs)
- [ ] Issues missing labels or assignees
- [ ] Closed issues that should be reopened

### 5. Cross-Reference

Connect the dots:

- [ ] TODOs that reference non-existent issues
- [ ] Issues that reference deleted code
- [ ] Plans in `docs/plans/` with no corresponding issue
- [ ] Completed work not reflected in CHANGELOG

## Output Format

```
Project Review: <project-name>
═══════════════════════════════════════════════════════════════

Code Quality
────────────────────────────────────────────────────────────────
✗ 5 TODOs found
  - src/api.py:42 — TODO: add rate limiting
  - src/api.py:87 — FIXME: handle timeout
  - src/db.py:15 — TODO: add connection pooling
  ...
✓ No HACK/XXX markers
✗ 2 empty function bodies
  - src/cache.py:23 — invalidate() is empty

Test Coverage
────────────────────────────────────────────────────────────────
✗ 3 modules without tests
  - src/validators.py
  - src/middleware.py
  - src/cache.py
✓ No skipped tests

Documentation
────────────────────────────────────────────────────────────────
✓ README up to date
✗ API docs missing for 2 public functions
  - src/api.py:create_session()
  - src/api.py:refresh_token()

GitHub Issues
────────────────────────────────────────────────────────────────
✓ 12 open issues
✗ 3 stale issues (>30 days)
  - #8: Add dark mode (45 days)
  - #5: Performance optimization (62 days)
  - #3: Mobile support (78 days)
✗ 1 potentially fixed issue
  - #11: Login bug — similar fix merged in PR #24

Summary
────────────────────────────────────────────────────────────────
Issues to create: 3
  → "Add rate limiting to API" (from TODO in src/api.py:42)
  → "Add tests for validators module"
  → "Document create_session() and refresh_token()"

Issues to close: 1
  → #11: Login bug (appears fixed)

Issues to ping: 3
  → #8, #5, #3: Stale, need triage
```

## Actions

After review, offer to:

1. **Create issues** for discovered gaps
   ```bash
   gh issue create --title "Add rate limiting" --body "Found TODO at src/api.py:42"
   ```

2. **Comment on stale issues** asking for status
   ```bash
   gh issue comment 8 --body "Is this still needed? No activity in 45 days."
   ```

3. **Close fixed issues** with explanation
   ```bash
   gh issue close 11 --comment "Fixed in PR #24"
   ```

4. **Queue work** for swarm execution
   ```bash
   swarm-job new "Add missing tests for validators" -c simple -p medium
   ```

## Philosophy

A codebase is never "done" — but it can be **coherent**:
- Every TODO has a tracking issue
- Every issue is actionable or closed
- Every feature is documented and tested
- Every gap is acknowledged

`/review` surfaces the gaps. You decide what to do about them.
