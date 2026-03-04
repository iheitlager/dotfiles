List and manage GitHub issues for the current repository.

## Usage

```
/issue                     List open issues
/issue <description>       Quick create from informal input (auto-detects contract)
/issue new                 Structured create with template
/issue #123                Show details for specific issue
```

## List Mode (default)

Run `gh issue list` and show a summary including:
- Issue number and title
- Labels and assignees
- Age (when created)

If there are many issues, group them by label or priority.
Suggest which issues might be good to work on next based on labels like "good first issue" or priority indicators.

## Contract Mode (auto-detected)

When the input contains any of these keywords — `GOAL:`, `CONSTRAINTS:`, `FORMAT:`, `FAILURE CONDITIONS:` — treat it as a **prompt contract** rather than an informal description.

A prompt contract is a structured specification used by `/take` to formalize into a C4 context doc before coding.

**Detection:**

```
if input contains GOAL: or CONSTRAINTS: or FORMAT: or FAILURE CONDITIONS:
  → Contract Mode
else
  → Quick Create Mode
```

**Process:**

1. **Parse the contract** — Extract each section. Flag any that are missing.
2. **Validate completeness** — All four sections must be present:
   - `GOAL` — What to build and why (user value)
   - `CONSTRAINTS` — Technical stack, libraries, patterns that must be used
   - `FORMAT` — Exact file paths, naming, structure expected
   - `FAILURE CONDITIONS` — Explicit conditions that would make the implementation wrong
3. **Ask for missing sections** before proceeding.
4. **Draft the issue** with:
   - Title: `feat: <short description from GOAL>`
   - Body: the full contract preserved verbatim under a `## Prompt Contract` heading, plus a `## Context` section with brief background
   - Label: `prompt-contract` (create if it doesn't exist)
5. **Present for review** — Show the draft before creating. Allow editing.

**Issue body template:**

```markdown
## Context
[1-3 sentence background extracted from GOAL]

## Prompt Contract

**GOAL:**
[verbatim]

**CONSTRAINTS:**
[verbatim]

**FORMAT:**
[verbatim]

**FAILURE CONDITIONS:**
[verbatim]
```

**Why prompt contracts?** They give `/take` enough signal to generate a C4 architecture doc before writing any code — making the implementation plan verifiable before it starts.

---

## Quick Create Mode

When given a brief, informal description (fire-and-forget style), transform it into a well-researched issue:

**Examples:**
- `/issue fix that weird hover bug in the sidebar`
- `/issue feat: add dark mode toggle`
- `/issue config loading is slow on startup`

**Process:**

1. **Interpret the vague input** - Extract intent, affected area, type (bug/feature/chore)
2. **Investigate the codebase** - Find relevant files, understand current behavior
3. **Research root cause** (for bugs) or **design approach** (for features)
4. **Draft a well-formed issue** with:
   - Clear title with conventional prefix (`fix:`, `feat:`, `docs:`, `chore:`)
   - Description that captures the real problem
   - Steps to reproduce (for bugs)
   - Suggested implementation approach
   - Acceptance criteria

5. **Present for review** - Show the draft BEFORE creating
   - Ask: "Does this capture what you meant?"
   - Allow refinement or rejection

**Important:** Slop is lubrication — quick, half-formed thoughts have value. But always validate assumptions and never auto-create without human approval.

## Structured Create Mode (`/issue new`)

For when you want a thorough, templated issue with clarifying questions.

**Process:**

1. **Parse the request** - Understand what the user wants to report or request
2. **Assess complexity** - Estimate effort (trivial/small/medium/large/epic)
3. **Ask clarifying questions** if the request is ambiguous
4. **Generate the issue** with proper formatting

**Title format** (conventional prefixes):
- `fix:` - Bug fixes, corrections
- `feat:` - New features, enhancements
- `docs:` - Documentation changes
- `chore:` - Maintenance, cleanup, tooling
- `refactor:` - Code restructuring without behavior change

**Body template:**

```markdown
## Description
[Clear description of the issue or feature request]

## Complexity
**Estimate:** [trivial|small|medium|large|epic]
**Reasoning:** [Why this complexity level]

## Context
[Any relevant background, related issues, or motivation]

## Acceptance Criteria
- [ ] [Specific, testable criteria]
- [ ] [Another criterion]

## Additional Notes
[Optional: technical considerations, alternatives considered, etc.]
```

**Label suggestions:**
- `bug` - Something isn't working
- `enhancement` - New feature or improvement
- `help wanted` - Extra attention needed

## Output

After any operation, show available actions:
- `/take #123` - Start working on an issue
- `/take #123 queue` - Load issue to swarm queue
- `/issue` - Refresh the list

---

*Inspired by: [Stay away from my trash!](https://tldraw.dev/blog/stay-away-from-my-trash) by Steve Ruiz (tldraw), Jan 2026 and my colleague Nick de Wijer - Graafstra*