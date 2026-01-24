List and manage GitHub issues for the current repository.

## Default: List Issues

Run `gh issue list` and show a summary including:
- Issue number and title
- Labels and assignees
- Age (when created)

If there are many issues, group them by label or priority.
Suggest which issues might be good to work on next based on labels like "good first issue" or priority indicators.

## Quick Issue Creation Mode

When given a brief, informal description (fire-and-forget style), transform it into a well-researched issue:

### Input Examples
- `/issues fix that weird hover bug in the sidebar`
- `/issues feat: I want a dark mode toggle somewhere accessible`
- `/issues the config file loading is slow on startup`

### Process

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

### Important

**Slop is lubrication** - Quick, half-formed thoughts have value. But always:
- Validate assumptions before creating
- Mark speculative analysis clearly
- Never auto-create without human approval

This prevents the "AI-to-AI telephone game" where a vague issue spawns a vague PR.

## Output

After listing issues OR after creating a new issue, summarize what actions are available:
- `/take #123` - Start working on an issue
- `/issue` - Refresh the list

---

*Inspired by: [Stay away from my trash!](https://tldraw.dev/blog/stay-away-from-my-trash) by Steve Ruiz (tldraw), Jan 2026 and my colleague Nick de Wijer - Graafstra*