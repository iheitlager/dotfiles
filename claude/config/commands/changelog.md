Generate CHANGELOG entries from commits since the last release.

## Usage

```
/changelog                Generate entries for unreleased changes
/changelog preview        Show what would be added (no file changes)
/changelog <version>      Generate entries for specific version
```

## Process

### 1. Determine Version Context

```bash
# Find latest tag
git describe --tags --abbrev=0

# Find commits since last tag
git log $(git describe --tags --abbrev=0)..HEAD --oneline

# If no tags exist
git log --oneline
```

### 2. Parse Commits

Extract from conventional commit messages:

| Prefix | CHANGELOG Section |
|--------|-------------------|
| `feat:` | Added |
| `fix:` | Fixed |
| `perf:` | Changed (Performance) |
| `refactor:` | Changed |
| `docs:` | Documentation |
| `BREAKING CHANGE:` | Breaking Changes |
| `!` in type | Breaking Changes |

**Ignore for CHANGELOG:**
- `chore:` — Internal maintenance
- `test:` — Test changes only
- `style:` — Formatting only
- `ci:` — CI/CD changes

### 3. Group and Format

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Breaking Changes
- **scope**: Description of breaking change

### Added
- **scope**: New feature description (#123)

### Changed
- **scope**: What was modified

### Fixed
- **scope**: Bug that was fixed (#456)

### Documentation
- Updated X documentation
```

### 4. Enhance Entries

For each commit:
- Extract scope from `type(scope): message`
- Find linked issues: `#123`, `Closes #456`
- Detect breaking changes from footer or `!`
- Clean up message (remove type prefix, capitalize)

**Transform:**
```
feat(parser): add Python 3.12 support (#89)
```
**Into:**
```
- **parser**: Add Python 3.12 support (#89)
```

### 5. Check Existing CHANGELOG

```bash
# Read current changelog
head -50 CHANGELOG.md
```

**Detect format:**
- Keep-a-Changelog style: `## [version] - date`
- Simple style: `## version`
- Match existing conventions

### 6. Generate Output

**Preview mode** (`/changelog preview`):
Show generated entries without modifying files.

**Normal mode**:
1. Generate the new version block
2. Insert after the header/before previous version
3. Show diff of changes
4. Ask for confirmation before saving

## Entry Guidelines

**Good entries:**
- User-focused: What changed for the user?
- Actionable: What do they need to know/do?
- Linked: Reference issues/PRs where relevant

**Bad entries:**
- Implementation details
- Internal refactoring (unless affects behavior)
- Commit noise ("fix typo", "wip", "cleanup")

**Combine related commits:**
```
# Multiple commits about the same feature
feat(auth): add login endpoint
feat(auth): add logout endpoint
feat(auth): add session management

# Combine into:
- **auth**: Add authentication system with login, logout, and session management
```

## Breaking Changes

Breaking changes get special treatment:

```markdown
### Breaking Changes

- **config**: Configuration file format changed from JSON to TOML

  **Migration**: Run `myapp migrate-config` to convert your config file.

  **Before**:
  ```json
  {"key": "value"}
  ```

  **After**:
  ```toml
  key = "value"
  ```
```

## Output Format

```
CHANGELOG Generation
═══════════════════════════════════════════════════════════════

Version: 0.7.0 (from 0.6.0)
Commits analyzed: 15
Entries generated: 8

Preview:
────────────────────────────────────────────────────────────────

## [0.7.0] - 2026-01-26

### Added
- **cli**: Add `--verbose` flag for detailed output (#45)
- **parser**: Support Python 3.12 match statements (#52)

### Fixed
- **auth**: Handle expired refresh tokens gracefully (#48)
- **cache**: Prevent race condition in cache invalidation

### Changed
- **models**: Improve query performance for large datasets

────────────────────────────────────────────────────────────────

Skipped commits (internal):
- chore: update dependencies
- test: add parser edge cases
- ci: fix release workflow

Write to CHANGELOG.md? [y/N]
```

## Integration

After generating changelog:
- Suggest `/version check` to validate consistency
- Suggest `/version bump` if ready to release
- Remind to commit the CHANGELOG update
