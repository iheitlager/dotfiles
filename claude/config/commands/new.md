Help create a well-structured GitHub issue from a user description.

## Process

1. **Parse the request** - Understand what the user wants to report or request
2. **Assess complexity** - Estimate effort (trivial/small/medium/large/epic)
3. **Ask clarifying questions** if the request is ambiguous or missing critical details
4. **Generate the issue** with proper formatting

## Issue Title Format

Use conventional prefixes:
- `fix:` - Bug fixes, corrections
- `feat:` - New features, enhancements  
- `docs:` - Documentation changes
- `chore:` - Maintenance, cleanup, tooling
- `refactor:` - Code restructuring without behavior change

Example: `feat: add support for XDG config directories`

## Issue Body Template

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

## Label Suggestions

Based on issue type, suggest appropriate labels:
- `bug` - Something isn't working
- `enhancement` - New feature or improvement
- `help wanted` - Extra attention needed
- `question` - Further information requested

## Output

After gathering information, provide:
1. The complete `gh issue create` command
2. Preview of title and body for review

```bash
gh issue create --title "type: title" --body "..." --label "label1,label2"
```

Ask user to confirm before executing.
