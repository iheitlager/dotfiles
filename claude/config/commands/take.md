Take ownership of a GitHub issue and begin implementation.

## Usage

```
/take #123        Single agent: take and implement directly
/take #123 queue  Multi-agent: load issue into swarm queue as task(s)
/take             Show suggested issues to take
```

## Pre-flight Checks (MANDATORY)

Before taking any issue, run these checks in order. **Stop immediately** if any check fails.

```
┌─────────────────────────────────────────────────────────────┐
│  PRE-FLIGHT CHECKS                                          │
│                                                             │
│  1. Check working state                                     │
│     ├─ On main/agent-N base branch? ─── Continue            │
│     └─ On feature branch?                                   │
│        ├─ Clean (no changes)? ─── Warn, offer to switch     │
│        └─ Dirty (uncommitted)? ─── STOP                     │
│                     │                                       │
│  2. Sync with main                                          │
│     ├─ git fetch origin                                     │
│     └─ git rebase origin/main                               │
│                     │                                       │
│  3. Atomic queue registration (swarm-job take)              │
│     ├─ Issue already in queue? ─── Show who, STOP           │
│     └─ Not in queue? ─── Create + claim atomically          │
│                     │                                       │
│  ✓ Ready to proceed                                         │
└─────────────────────────────────────────────────────────────┘
```

### Check 1: Working State

```bash
# Get current branch
BRANCH=$(git branch --show-current)

# Check for uncommitted changes
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "✗ Uncommitted changes on $BRANCH"
  echo "  Commit or stash changes first, or use /pr to finalize current work"
  # STOP
fi

# Check if on a feature branch (not main, not agent-N base)
if [[ "$BRANCH" != "main" && ! "$BRANCH" =~ ^agent-[0-9]+$ ]]; then
  echo "⚠️  Currently on feature branch: $BRANCH"
  echo "  Options:"
  echo "    1. Switch to main first: git checkout main"
  echo "    2. Finish current work: /pr to create PR"
  echo "    3. Abandon branch: git checkout main && git branch -D $BRANCH"
  # ASK user what to do, or STOP
fi
```

### Check 2: Sync with Main

```bash
git fetch origin
git rebase origin/main
```

**If rebase conflicts:**
```
✗ Rebase conflicts detected
  Your branch has diverged from main. Resolve conflicts first:
    git rebase --abort   # Cancel and keep your changes
    git rebase --continue # After fixing conflicts
```

### Check 3: Atomic Queue Registration

Use `swarm-job take` which atomically:
- Checks if issue already has a job (pending or active)
- Creates the job
- Claims it immediately

```bash
swarm-job take $ISSUE_NUM -t "$TITLE" -p $PRIORITY -c $COMPLEXITY
```

**If already taken:**
```
✗ Issue #123 already in queue

  Job: job-1737500000
  Title: Fix login redirect
  Claimed by: agent-2

Options:
  - Claim existing: swarm-job claim job-1737500000
  - Choose different issue
```

This is atomic (uses `flock`) so no race conditions between agents.

---

## Agent Strategy

The research phase is delegated to an Explore agent, while judgment and implementation stay interactive.

```
┌─────────────────────────────────────────────────────────────┐
│  /take #123                                                 │
│                                                             │
│  0. Pre-flight checks (see above)                           │
│                     │                                       │
│  1. Fetch issue (gh issue view)                             │
│                     │                                       │
│                     ▼                                       │
│  ┌──────────────────────────────────┐                       │
│  │ Explore Agent                    │                       │
│  │                                  │                       │
│  │ - Find relevant code             │                       │
│  │ - Understand patterns            │                       │
│  │ - Identify files to change       │                       │
│  │ - Check for similar past fixes   │                       │
│  └──────────────┬───────────────────┘                       │
│                 │                                           │
│                 ▼                                           │
│  2. Validate issue (interactive)                            │
│     "Does this make sense?"                                 │
│                 │                                           │
│                 ▼                                           │
│  3. Present plan (interactive)                              │
│     "Here's my approach..."                                 │
│                 │                                           │
│                 ▼                                           │
│  4. Implement (main conversation)                           │
└─────────────────────────────────────────────────────────────┘
```

## Modes

### Direct Mode (default)

For single-agent work. You take the issue and implement it yourself.

### Queue Mode

For multi-agent swarms. Loads the issue into the swarm queue so any capable agent can claim it.

```bash
# Queue mode creates swarm job(s) from the issue:
swarm-job new "Issue title" \
  -p <priority from labels> \
  -c <complexity estimate> \
  -d "From #123: <issue description summary>"
```

**Priority mapping from labels:**
- `priority:urgent`, `critical`, `P0` → urgent
- `priority:high`, `important`, `P1` → high
- `priority:low`, `minor`, `P3` → low
- Default → medium

**Complexity estimation:**
- Small issues, docs, typos → simple (haiku)
- Standard features, bug fixes → moderate (sonnet)
- Architecture, multi-file, design → complex (opus)

**Output:** Reports created job ID and suggests `swarm-job list` to verify.

## Process (Direct Mode)

### 1. Fetch Issue

```bash
gh issue view #N
```

Read the full issue including comments and linked discussions.

### 2. Research via Agent

Spawn an Explore agent to understand the codebase context:

```
Task tool:
  subagent_type: Explore
  prompt: |
    Research context for implementing GitHub issue #N:

    Issue summary: <paste issue title and key details>

    Find:
    1. Files most relevant to this issue (by name, imports, functionality)
    2. Existing patterns for similar features/fixes in the codebase
    3. Related tests that might need updates
    4. Any prior attempts or related PRs (check git log for keywords)

    For bugs: Look for where the problematic behavior originates
    For features: Look for where similar features are implemented

    Output:
    - Key files to examine (with brief explanation why)
    - Relevant patterns to follow
    - Suggested approach based on codebase conventions
```

### 3. Validate Issue (Interactive)

With research in hand, make a judgment call:

**Critical check**: Does this issue make sense?
- Is the bug real? Can it be reproduced?
- Is the feature well-defined? Are the requirements clear?
- Are there unanswered questions in the comments?

If the issue is unclear or flawed, **stop and report back**:
> "This issue seems problematic because [X]. Should I:
> a) Comment asking for clarification
> b) Close it with an explanation
> c) Proceed with my interpretation: [describe]"

### 4. Present Plan (Interactive)

Based on agent research, present a brief implementation plan:

```
Files to modify:
- src/foo.ts - Add new handler
- tests/foo.test.ts - Add test cases

Approach: [1-2 sentences]
Estimated complexity: [trivial/small/medium/large]

Test plan:
- [ ] Unit tests for new handler
- [ ] Integration test for end-to-end flow
- [ ] Existing tests still pass

Based on: [reference similar patterns found by agent]
```

Wait for user approval before proceeding.

### 5. Implement

- Create a feature branch: `git checkout -b fix/#123-short-description` or `feat/#123-...`
- Make changes following project conventions
- Write or update tests for changed code

### 6. Verify Tests & Coverage (MANDATORY)

Before preparing for review, **tests must pass**:

```bash
# Run tests (use project's test command)
uv run pytest tests/ -x --tb=short   # Python
npm test                              # Node
make test                             # If Makefile exists
```

**Coverage requirements:**
- New code should have test coverage
- Bug fixes should include a regression test
- Check coverage if available: `uv run pytest --cov=src/`

**If tests fail:**
```
✗ Tests failing - DO NOT proceed to PR

Fix failing tests before continuing:
  - Read test output to understand failures
  - Fix implementation or update tests
  - Re-run until green
```

**If no tests exist for changed code:**
```
⚠️  No test coverage for changes

Options:
  a) Write tests now (recommended)
  b) Proceed without tests (must justify in PR)
  c) Create follow-up issue for tests
```

Run `/check` to verify linting, types, and formatting as well.

### 7. Prepare for Review

- Stage changes and create commit following project conventions
- Reference the issue: `fix: resolve hover bug in sidebar (#123)`
- Summarize what was done and any follow-up needed

### 8. Complete Swarm Job

After PR is created or merged, mark the job as done:

```bash
swarm-job complete "$JOB_ID" -r "PR #$PR_NUM created"
```

This is handled automatically by `/pr` and `/merge` commands.

## Process (Queue Mode)

### 1. Fetch & Validate Issue

```bash
gh issue view #N
```

- Confirm the issue is actionable (not stale, not blocked)
- Check for linked PRs (maybe already in progress)

### 2. Research via Agent (optional for complex issues)

For complex issues, spawn an Explore agent first to inform task breakdown:

```
Task tool:
  subagent_type: Explore
  prompt: |
    Analyze issue #N for task decomposition:

    1. What distinct pieces of work does this require?
    2. What are the dependencies between them?
    3. Which parts could be parallelized?
    4. Estimate complexity of each part (simple/moderate/complex)
```

### 3. Create Swarm Job(s)

For simple issues — one job:
```bash
swarm-job new "Issue title" -p medium -c moderate \
  -d "From #123: <brief description>"
```

For complex issues — break into subtasks:
```bash
swarm-job new "Design API interface (#123)" -p high -c complex
swarm-job new "Implement API handler (#123)" -p high -c moderate -D job-XXX
swarm-job new "Add API tests (#123)" -p medium -c simple -D job-YYY
```

### 4. Report

Output the created job(s):
```
Queued issue #123 as swarm job(s):
  job-1737500000 [high/complex] Design API interface
  job-1737500001 [high/moderate] Implement API handler (blocked by above)
  job-1737500002 [medium/simple] Add API tests (blocked by above)

Run: swarm-job list pending
```

## Philosophy

From the tldraw blog: "If writing the code is the easy part, why would I want someone else to write it?"

The value of `/take` is not the code—it's the **judgment**:
- Validating the issue makes sense
- Choosing the right approach
- Knowing the codebase well enough to do it idiomatically

**Agents handle research. You handle decisions.**

**Never take an issue without first confirming it's worth solving.**

## Output

After taking an issue, provide:
- Summary of changes made
- Any open questions or follow-ups
- Command to create PR: `gh pr create --title "..." --body "Closes #123"`

---

*Inspired by: [Stay away from my trash!](https://tldraw.dev/blog/stay-away-from-my-trash) by Steve Ruiz (tldraw), Jan 2026 and my colleague Nick de Wijer - Graafstra*
