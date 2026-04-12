Take ownership of a GitHub issue and begin implementation.

## Usage

```
/take #123        Single agent: take and implement directly
/take #123 queue  Multi-agent: load issue into swarm queue as task(s)
/take             Show suggested issues to take
```

**Epic detection:** If the issue has the `epic` label or links to sub-issues, `/take` automatically enters Epic Mode — one branch, one PR, one commit per sub-ticket.

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
  # If on an epic branch and taking a sub-issue of that epic, continue (Epic Mode)
  # Otherwise warn
  echo "⚠️  Currently on feature branch: $BRANCH"
  echo "  Options:"
  echo "    1. Switch to main first: git checkout main"
  echo "    2. Finish current work: /pr to create PR"
  echo "    3. Abandon branch: git checkout main && git branch -D $BRANCH"
  echo "    4. Continue on this branch (Epic Mode — sub-ticket of current epic)"
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
JOB_OUTPUT=$(swarm-job take $ISSUE_NUM -t "$TITLE" -p $PRIORITY -c $COMPLEXITY)
JOB_ID=$(echo "$JOB_OUTPUT" | grep "Job ID:" | awk '{print $3}')

# Record job claim event (Phase 2)
swarm-daemon hook JOB_CLAIMED "$JOB_ID" --issue $ISSUE_NUM --title "$TITLE"
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
│  2.5 If prompt contract detected:                           │
│      └─ Write C4 context doc to .openspec/adr/              │
│         (lightweight: context + containers + contract)      │
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

### Epic Mode (auto-detected)

For issues labeled `epic` or that have sub-issues. One branch, one PR, one commit per sub-ticket.

**Detection:**
```
if issue has label "epic" OR issue body contains task list with #N references
  → Epic Mode
else
  → Direct Mode (or Queue Mode if "queue" arg)
```

**Key principle:** The epic branch stays open across all sub-tickets. Each sub-ticket gets its own commit (not its own branch/PR). The PR is created once at the end, referencing all closed sub-issues.

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

### 2.5 Formalize Prompt Contract → C4 Context Doc (if applicable)

**Trigger:** The issue body contains a `## Prompt Contract` section (created by `/issue` in contract mode) or raw GOAL/CONSTRAINTS/FORMAT/FAILURE CONDITIONS keywords.

**If no prompt contract is detected, skip this step entirely.**

**Process:**

1. **Extract the four contract sections** from the issue body.

2. **Determine the next ADR number:**
   ```bash
   ls .openspec/adr/ | grep -E '^[0-9]{4}-' | sort | tail -1
   # Increment by 1
   ```

3. **Write the C4 context doc** at `.openspec/adr/NNNN-c4-<feature-slug>.md`:

```markdown
# C4 Context: <Feature Name>

> Source: #<issue-number> — <issue title>

## System Context

<1-2 sentences: who uses this, what system it belongs to, what external systems it interacts with — derived from GOAL and FORMAT sections>

## Containers

<derived from FORMAT section: list each file/component specified, its role, and technology>

| Container | Path | Role |
|-----------|------|------|
| <name> | <path from FORMAT> | <role inferred from GOAL/CONSTRAINTS> |

## Constraints

<verbatim CONSTRAINTS section from the contract>

## Failure Conditions

<verbatim FAILURE CONDITIONS section from the contract>

## Full Prompt Contract

```
GOAL:
<verbatim>

CONSTRAINTS:
<verbatim>

FORMAT:
<verbatim>

FAILURE CONDITIONS:
<verbatim>
```
```

4. **Reference the ADR** in the plan presentation (step 3): "Architecture formalized in `.openspec/adr/NNNN-c4-<feature>.md`"

5. **During implementation**, use the FORMAT section as the authoritative file structure. Use FAILURE CONDITIONS as a checklist before marking the issue done.

---

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
make test                             # If Makefile exists
uv run pytest tests/ -x --tb=short   # Python
cargo test                            # Rust
npm test                              # Node
```

**Coverage requirements:**
- New code should have test coverage
- Bug fixes should include a regression test
- Check coverage if available:
  - Python: `uv run pytest --cov=src/`
  - Rust: `cargo llvm-cov 2>/dev/null || cargo tarpaulin`

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

## Process (Epic Mode)

When an epic is detected, the workflow changes: one branch holds all sub-ticket work, each sub-ticket is a commit, and one PR closes everything.

### 1. Setup Epic Branch

```bash
# Create a single branch for the entire epic
git checkout -b feat/#48-epic-short-description
```

### 2. Identify Sub-Tickets

```bash
# List sub-issues from the epic body or linked issues
gh issue view #48
# Parse task list or find issues referencing this epic
gh issue list --search "epic:#48" --state open
```

Present the ordered list of sub-tickets to the user:
```
Epic #48: Grounded C4 Architecture Modeling System

Sub-tickets (in suggested order):
  1. #62 - Generate UML Sequence and State Diagrams
  2. #63 - Model Dotfiles Sequences
  3. #64 - Implement Reverse Engineering
  4. #65 - Implement Coverage Tracking
  5. #67 - Dependency and Impact Analysis

Proceed with this order? (reorder/skip/go)
```

### 3. Work Through Sub-Tickets Sequentially

For each sub-ticket on the **same branch**:

1. **Research** — Explore agent for context (same as Direct Mode step 2)
2. **Validate** — Does this sub-ticket make sense given prior work on this branch?
3. **Implement** — Make changes on the epic branch
4. **Test** — Run tests, verify nothing broke
5. **Commit** — One commit per sub-ticket, referencing the sub-issue:
   ```bash
   git commit -m "feat: generate UML sequence diagrams (#62)"
   ```
6. **Close sub-ticket** — Comment and close:
   ```bash
   gh issue close #62 -c "Implemented in epic branch feat/#48-..., commit <sha>"
   ```
7. **Report progress** — Show what's done vs remaining:
   ```
   Epic #48 progress: [2/5]
     ✅ #62 - Generate UML Sequence and State Diagrams
     ✅ #63 - Model Dotfiles Sequences
     🔄 #64 - Implement Reverse Engineering (next)
     ⬜ #65 - Implement Coverage Tracking
     ⬜ #67 - Dependency and Impact Analysis
   ```
8. **Ask before continuing** — User may want to pause, review, or reorder

### 4. Finalize Epic

After all sub-tickets are done (or user decides to stop):

1. **Run full test suite** — All tests must pass
2. **Push the epic branch** — `git push -u origin feat/#48-...`
3. **Create one PR** referencing all sub-issues:
   ```
   gh pr create --title "feat: Grounded C4 Architecture Modeling System" --body "
   ## Summary
   Implements epic #48 across N sub-tickets.

   ## Sub-tickets
   - Closes #62 — Generate UML diagrams
   - Closes #63 — Model sequences
   - Closes #64 — Reverse engineering
   ...

   ## Test plan
   - [ ] All existing tests pass
   - [ ] New tests for each sub-ticket
   "
   ```
4. **Close the epic** after PR is merged

### Resuming an Epic

If the conversation ends mid-epic (context limit, user pauses):
- The branch and commits are preserved
- Next session: `/take #48` detects the existing epic branch and resumes
- Check: `git log --oneline main..HEAD` to see what's already done
- Cross-reference with open sub-tickets to find where to continue

### Epic Pre-flight (when already on an epic branch)

When `/take #N` is called and you're already on an epic branch:
1. Check if `#N` is a sub-ticket of the current epic — if yes, continue on this branch
2. If `#N` is a different issue — warn and offer to switch or finish current epic first

---

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
