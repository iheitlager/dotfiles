Take ownership of a GitHub issue and begin implementation.

## Usage

`/take #123` - Take issue number 123 and start working on it
`/take` - Show suggested issues to take (from `/issues` output)

## Process

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
