Create a new git branch following conventional naming.

## Usage

```
/br                           Interactive branch creation
/br <description>             Create branch from description
/br feat <description>        Shorthand: create feature branch
/br fix <description>         Shorthand: create fix branch
/br fix #123 <description>    Include issue number
```

## Shorthand Examples

```
/br feat add user auth        → feat/add-user-auth
/br fix login redirect        → fix/login-redirect
/br fix #42 token expiry      → fix/42-token-expiry
/br docs update readme        → docs/update-readme
/br refactor models           → refactor/models
/br spike postgres perf       → spike/postgres-perf
```

## Branch Naming Convention

Use prefixes matching commit types:
- `feat/` — New features, enhancements
- `fix/` — Bug fixes, corrections
- `docs/` — Documentation changes
- `chore/` — Maintenance, cleanup, tooling
- `refactor/` — Code restructuring
- `spike/` — Experimental explorations
- `test/` — Test additions or changes

## Process

1. **Parse the request** — Understand what work the user wants to do
2. **Suggest branch name** — Use format: `type/short-description`
3. **Check for related issue** — If issue exists, include number: `feat/123-add-feature`
4. **Create the branch** from current HEAD or specified base

## Branch Name Rules

- Lowercase only
- Use hyphens for spaces
- Keep it short but descriptive (3-5 words max)
- Include issue number if applicable
- No special characters except hyphens

## Full Examples

| Request | Branch Name |
|---------|-------------|
| "Add XDG support" | `feat/add-xdg-support` |
| "Fix issue #42 about history" | `fix/42-bash-history-location` |
| "Update README" | `docs/update-readme` |
| "Explore postgres performance" | `spike/postgres-performance` |
| `/br feat dark mode` | `feat/dark-mode` |
| `/br fix #99 memory leak` | `fix/99-memory-leak` |

## Output

```bash
# Create and switch to new branch
git checkout -b type/branch-name

# Or from specific base
git checkout -b type/branch-name origin/main
```

If there's a related GitHub issue, suggest linking:
```bash
# Alternative: create branch from issue (includes issue metadata)
gh issue develop 42 --checkout
```

## Workflow Integration

After creating branch:
- `/plan` — Create a feature plan if complex
- `/take #N` — If working on a specific issue
- Start coding!

When done:
- `/commit` — Create conventional commit
- `/pr` — Open pull request

Ask user to confirm the branch name before creating.
