Take ownership of a GitHub issue and begin implementation.

## Usage

```
/take #123        Single agent: take and implement directly
/take #123 queue  Multi-agent: load issue into swarm queue as task(s)
/take             Show suggested issues to take
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

### 1. Understand the Issue

- Fetch full issue details with `gh issue view #N`
- Read all comments and linked discussions
- **Critical check**: Does this issue make sense?
  - Is the bug real? Can it be reproduced?
  - Is the feature well-defined? Are the requirements clear?
  - Are there unanswered questions in the comments?

If the issue is unclear or flawed, **stop and report back**:
> "This issue seems problematic because [X]. Should I:
> a) Comment asking for clarification
> b) Close it with an explanation
> c) Proceed with my interpretation: [describe]"

### 2. Research & Plan

- Search codebase for relevant code
- Understand existing patterns and conventions
- Identify files that need changes
- Consider edge cases and tests needed

Present a brief implementation plan:
```
Files to modify:
- src/foo.ts - Add new handler
- tests/foo.test.ts - Add test cases

Approach: [1-2 sentences]
Estimated complexity: [trivial/small/medium/large]
```

### 3. Implement

- Create a feature branch: `git checkout -b fix/#123-short-description` or `feat/#123-...`
- Make changes following project conventions
- Write or update tests
- Ensure checks pass

### 4. Prepare for Review

- Stage changes and create commit following project conventions
- Reference the issue: `fix: resolve hover bug in sidebar (#123)`
- Summarize what was done and any follow-up needed

## Process (Queue Mode)

### 1. Fetch & Validate Issue

```bash
gh issue view #N
```

- Confirm the issue is actionable (not stale, not blocked)
- Check for linked PRs (maybe already in progress)

### 2. Assess Complexity

Estimate based on:
- Number of files likely affected
- Architectural impact
- Testing requirements
- Dependencies on other work

### 3. Create Swarm Task(s)

For simple issues — one task:
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

**Never take an issue without first confirming it's worth solving.**

## Output

After taking an issue, provide:
- Summary of changes made
- Any open questions or follow-ups
- Command to create PR: `gh pr create --title "..." --body "Closes #123"`

---

*Inspired by: [Stay away from my trash!](https://tldraw.dev/blog/stay-away-from-my-trash) by Steve Ruiz (tldraw), Jan 2026 and my colleague Nick de Wijer - Graafstra*
