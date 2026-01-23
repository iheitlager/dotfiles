Create a new git branch following conventional naming.

## Branch Naming Convention

Use prefixes matching commit types:
- `feat/` - New features, enhancements
- `fix/` - Bug fixes, corrections
- `docs/` - Documentation changes
- `chore/` - Maintenance, cleanup, tooling
- `refactor/` - Code restructuring
- `spike/` - Experimental explorations
- `test/` - Test additions or changes

## Process

1. **Parse the request** - Understand what work the user wants to do
2. **Suggest branch name** - Use format: `type/short-description`
3. **Check for related issue** - If issue exists, include number: `feat/123-add-feature`
4. **Create the branch** from current HEAD or specified base

## Branch Name Rules

- Lowercase only
- Use hyphens for spaces
- Keep it short but descriptive (3-5 words max)
- Include issue number if applicable

## Examples

| Request | Branch Name |
|---------|-------------|
| "Add XDG support" | `feat/add-xdg-support` |
| "Fix issue #42 about history" | `fix/42-bash-history-location` |
| "Update README" | `docs/update-readme` |
| "Explore postgres performance" | `spike/postgres-performance` |

## Output

```bash
# Create and switch to new branch
git checkout -b type/branch-name

# Or from specific base
git checkout -b type/branch-name origin/main
```

If there's a related GitHub issue, suggest linking:
```bash
# After first push
gh issue develop 42 --checkout  # Alternative: creates branch from issue
```

Ask user to confirm the branch name before creating.
