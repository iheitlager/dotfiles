Review codebase, documentation, and issues to identify gaps and verify completeness.

## Usage

```
/review              Full project review
/review code         Code quality and TODOs only
/review docs         Documentation completeness only
/review issues       GitHub issues health only
/review <path>       Review specific file or directory
```

## Agent Strategy

This skill delegates heavy scanning to agents, then synthesizes results interactively.

```
┌─────────────────────────────────────────────────────────────┐
│  /review                                                    │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Explore      │  │ Explore      │  │ Bash         │      │
│  │ Agent        │  │ Agent        │  │ Agent        │      │
│  │              │  │              │  │              │      │
│  │ Code scan    │  │ Doc scan     │  │ GH issues    │      │
│  │ TODOs, gaps  │  │ Stale docs   │  │ Stale/dupe   │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │               │
│         └────────────┬────┴────────────────┘               │
│                      ▼                                      │
│              Synthesize Report                              │
│              (main conversation)                            │
│                      │                                      │
│                      ▼                                      │
│              Offer Actions                                  │
│              (interactive)                                  │
└─────────────────────────────────────────────────────────────┘
```

## Process

### 1. Spawn Agents (parallel)

Launch these agents in parallel to gather data:

**Agent 1: Code Quality Scan**
```
Task tool:
  subagent_type: Explore
  prompt: |
    Scan the codebase for incomplete work and code quality issues:

    1. Find all TODO, FIXME, HACK, XXX comments
    2. Find empty function bodies (pass, ..., NotImplementedError)
    3. Find commented-out code blocks (3+ consecutive commented lines)
    4. Find bare except clauses or empty catch blocks
    5. Find unused imports

    For each finding, report:
    - File path and line number
    - The marker or issue type
    - Surrounding context (1 line before/after)

    Group by severity: errors > warnings > notes
```

**Agent 2: Test Coverage Scan**
```
Task tool:
  subagent_type: Explore
  prompt: |
    Analyze test coverage gaps:

    1. List all source modules in src/
    2. List all test files in tests/
    3. Identify modules without corresponding test files
    4. Find skipped tests (@skip, pytest.mark.skip)
    5. Find tests with TODO markers

    Report:
    - Modules missing tests
    - Skipped test count and reasons
    - Test files with TODOs
```

**Agent 3: Documentation Scan**
```
Task tool:
  subagent_type: Explore
  prompt: |
    Check documentation freshness:

    1. Compare README features list with actual exports
    2. Check if CHANGELOG has entries for recent commits
    3. Find broken internal links in markdown files
    4. Identify public functions without docstrings

    Report discrepancies with file:line references.
```

**Agent 4: GitHub Issues Health** (if reviewing issues)
```
Task tool:
  subagent_type: Bash
  prompt: |
    Analyze GitHub issues health:

    1. Run: gh issue list --state open --json number,title,labels,updatedAt,assignees
    2. Identify stale issues (no update in 30+ days)
    3. Look for potential duplicates (similar titles)
    4. Cross-reference with recent closed PRs to find potentially fixed issues

    Output a structured summary.
```

### 2. Synthesize Results

Once agents return, combine their findings into a unified report:

- Deduplicate findings
- Prioritize by severity
- Group related items
- Calculate summary statistics

### 3. Present Report

Show the consolidated report (see Output Format below).

### 4. Offer Actions (Interactive)

Ask user which actions to take:
- Create issues for gaps?
- Close stale issues?
- Queue work for swarm?

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

## Prompt

Review this code for bugs, security issues, and improvements. Be concise and actionable.

Focus on:
- Logic errors or potential bugs
- Security vulnerabilities (injection, XSS, secrets)
- Missing error handling
- Type issues
- Performance concerns
- Code clarity

Format: List issues by severity (critical/warning/suggestion) with line references where applicable.
