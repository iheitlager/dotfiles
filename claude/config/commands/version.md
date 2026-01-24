Validate version consistency and release readiness across the project.

## Usage

```
/version                 Full validation check
/version check           Same as above
/version bump <type>     Bump version (patch|minor|major)
```

## Validation Checks

### 1. Version Number Sync

Find all version declarations and verify they match:

```bash
# Common locations
grep -r "__version__" src/
grep -r "version" pyproject.toml package.json Cargo.toml
grep -r "## Version" README.md
```

**Check for:**
- [ ] `src/*/__init__.py` — `__version__ = "X.Y.Z"`
- [ ] `pyproject.toml` — `version = "X.Y.Z"`
- [ ] `package.json` — `"version": "X.Y.Z"`
- [ ] `README.md` — Version badge or header
- [ ] All versions match

### 2. CHANGELOG Sync

Compare CHANGELOG.md with git history:

```bash
# Latest version in CHANGELOG
head -20 CHANGELOG.md

# Recent commits since last tag
git log $(git describe --tags --abbrev=0)..HEAD --oneline
```

**Check for:**
- [ ] CHANGELOG has entry for current version
- [ ] Recent commits are reflected in CHANGELOG
- [ ] No "[Unreleased]" section with shipped changes
- [ ] Date matches release date (if releasing today)

### 3. Git State

```bash
git status --short
git log --oneline -5
git describe --tags --always
```

**Check for:**
- [ ] No untracked files that should be committed
- [ ] No uncommitted changes
- [ ] Current commit is tagged (if checking a release)
- [ ] Branch is up to date with remote

### 4. Dependencies

```bash
# Python
uv pip list --outdated 2>/dev/null || pip list --outdated

# Node
npm outdated 2>/dev/null

# Check lock file freshness
git diff --name-only HEAD~10 | grep -E "lock|\.lock"
```

**Check for:**
- [ ] Lock file is committed
- [ ] No critical security updates pending
- [ ] Dependencies resolve without conflicts

## Output Format

```
Version Check: <project-name>
═══════════════════════════════════════════════════════════════

Version Numbers
────────────────────────────────────────────────────────────────
✓ src/myproject/__init__.py    → 0.6.0
✓ pyproject.toml               → 0.6.0
✓ README.md                    → 0.6.0
✓ All versions match

CHANGELOG
────────────────────────────────────────────────────────────────
✓ CHANGELOG.md has entry for 0.6.0
✗ 3 commits not in CHANGELOG:
  - abc1234 feat: add swarm-task CLI
  - def5678 fix: watcher broadcast
  - ghi9012 docs: update commands.md

Git State
────────────────────────────────────────────────────────────────
✓ Working directory clean
✓ No untracked files
✗ Not tagged (latest tag: v0.5.0)
✓ Up to date with origin/main

Dependencies
────────────────────────────────────────────────────────────────
✓ Lock file committed
✓ No critical updates

Summary
────────────────────────────────────────────────────────────────
Status: NOT READY for release

Issues:
  1. Update CHANGELOG with recent commits
  2. Create tag v0.6.0

Run: /version bump patch  (after fixing issues)
```

## Bump Mode (`/version bump`)

Increment version and update all locations:

```
/version bump patch      0.6.0 → 0.6.1  (bug fixes)
/version bump minor      0.6.0 → 0.7.0  (new features)
/version bump major      0.6.0 → 1.0.0  (breaking changes)
```

### Bump Process

1. **Validate current state** — Run checks first
2. **Calculate new version** — Based on bump type
3. **Update all version locations** — Edit files
4. **Update CHANGELOG** — Add new version header with date
5. **Show diff** — Preview changes before committing
6. **Offer to commit** — `chore: bump version to X.Y.Z`
7. **Offer to tag** — `git tag vX.Y.Z`

### Semver Guidelines

| Change Type | Bump | Example |
|------------|------|---------|
| Bug fix, patch | patch | `fix:` commits |
| New feature, backwards compatible | minor | `feat:` commits |
| Breaking change | major | API changes, removals |
| Docs, chore, refactor | none | No version change |

## Philosophy

A version number is a promise:
- **Patch**: "This fixes bugs, safe to upgrade"
- **Minor**: "This adds features, safe to upgrade"
- **Major**: "This changes things, read the notes"

`/version` ensures you keep that promise by validating everything is in sync before release.
