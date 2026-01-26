Look at the staged changes (git diff --cached) and write a conventional commit message.

## Usage

```
/commit              Generate commit message for staged changes
/commit --amend      Amend the previous commit (use carefully)
```

## Commit Format

```
type(scope): description

[optional body]

[optional footer]
```

## Types

| Type | Description | Version Impact |
|------|-------------|----------------|
| `feat` | New feature | Minor bump |
| `fix` | Bug fix | Patch bump |
| `docs` | Documentation only | None |
| `refactor` | Code restructuring | None |
| `test` | Adding/updating tests | None |
| `chore` | Maintenance, tooling | None |
| `perf` | Performance improvement | Patch bump |
| `style` | Formatting, whitespace | None |

## Process

1. **Read staged changes**
   ```bash
   git diff --cached --stat
   git diff --cached
   ```

2. **Analyze the changes**
   - What type of change is this?
   - What's the primary scope (module/component)?
   - Is this a breaking change?
   - Does it close any issues?

3. **Determine scope** from file paths:
   - `src/cli/*` → `cli`
   - `src/core/*` → `core`
   - `tests/*` → `test`
   - `docs/*` → `docs`
   - Multiple areas → omit scope or use broader term

4. **Check for breaking changes**
   - API signature changes
   - Removed public functions/classes
   - Changed return types
   - Configuration format changes
   - Database schema changes

5. **Generate message**

## Breaking Changes

If the change is breaking, add `!` after type and include footer:

```
feat(api)!: change authentication flow

BREAKING CHANGE: The login() function now requires a config object
instead of individual parameters.

Migration:
- Before: login(user, pass)
- After: login({user, pass, options})
```

## Multi-File Commits

**When to combine** (one commit):
- Related changes that form a single logical unit
- Refactoring that touches many files
- Feature with its tests

**When to split** (separate commits):
- Unrelated changes staged together
- Formatting/style mixed with logic changes
- Multiple distinct features

If changes should be split, suggest:
```bash
git reset HEAD <file>  # Unstage specific files
```

## Examples

**Simple feature:**
```
feat(parser): add support for Python 3.12 syntax
```

**Bug fix with issue reference:**
```
fix(auth): handle expired tokens gracefully

Previously, expired tokens caused a 500 error. Now returns 401
with a clear message prompting re-authentication.

Closes #42
```

**Refactoring:**
```
refactor(models): extract validation logic into separate module

No functional changes. Moves validation from User and Project
models into shared validators.py for reuse.
```

**Breaking change:**
```
feat(config)!: switch to TOML configuration format

BREAKING CHANGE: JSON config files are no longer supported.
Run `myapp migrate-config` to convert existing configs.
```

## Output

After generating the message:
1. Show the proposed commit message
2. Ask for confirmation or edits
3. Execute: `git commit -m "message"`

If the commit includes a Co-Authored-By, add it to the footer.
