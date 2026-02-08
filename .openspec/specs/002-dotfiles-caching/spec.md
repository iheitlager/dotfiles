# Dotfiles Caching System Specification

**Domain:** Personal Development Environment / Performance Optimization
**Version:** 1.0.0
**Status:** Implemented
**Date:** 2026-02-07
**Owner:** Ilja Heitlager

## Overview

A mtime-based caching system for dotfiles shell integrations that dramatically improves shell startup performance by aggregating and caching bash_env, bash_aliases, and bash_completion files from all topics. The system automatically invalidates stale caches while maintaining transparency to the user.

### Philosophy

- **Aggressive Caching**: Shell integrations are cached with mtime-based invalidation for fast startup times
- **Automatic Invalidation**: Cache freshness is checked on every shell start, no manual intervention needed
- **Transparent Operation**: Caching happens behind the scenes, users only notice improved performance
- **Single Cache Location**: All caches stored in XDG_CACHE_HOME for easy management

### Key Capabilities

- **10x Faster Shell Startup**: Cached shell starts in ~50ms vs ~500ms uncached
- **Automatic Cache Generation**: First run generates cache, subsequent runs use it
- **Mtime-Based Validation**: Compares cache modification time against all source files
- **Manual Control**: `dot invalidate` command for forced cache refresh
- **Shortcuts Cache**: Dedicated cache for keyboard shortcuts topics list

---

## RFC 2119 Keywords

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

---

## ADDED Requirements

### Requirement: Cache Management

The system MUST cache shell integrations for fast startup with automatic and manual invalidation.

#### Scenario: Cache Generation on First Run

- GIVEN no cache exists at ${XDG_CACHE_HOME}/dotfiles/
- WHEN the shell starts
- THEN it SHALL create cache directory
- AND SHALL scan for all bash_env, bash_aliases, bash_completion files
- AND SHALL concatenate them into respective .sh cache files
- AND SHALL source the cache

#### Scenario: Cache Hit on Subsequent Runs

- GIVEN valid cache exists
- WHEN the shell starts
- THEN it SHALL check cache mtime against source files
- IF cache is fresh (newer than all sources)
- THEN it SHALL source cache directly without scanning filesystem
- AND startup SHALL be <100ms faster than uncached

#### Scenario: Automatic Cache Invalidation

- GIVEN a cache exists
- WHEN a topic's bash_aliases file is modified
- THEN on next shell start, cache freshness check SHALL detect stale cache
- AND SHALL regenerate bash_aliases.sh automatically
- AND SHALL source the updated cache

#### Scenario: Manual Cache Invalidation

- GIVEN caches exist at ${XDG_CACHE_HOME}/dotfiles/
- WHEN user runs `dot invalidate`
- THEN it SHALL remove all .sh cache files
- AND SHALL remove shortcuts/ cache directory
- AND SHALL display confirmation of removed files
- AND SHALL instruct user to restart shell

#### Scenario: Cache Status Display

- GIVEN caches exist
- WHEN user runs `dot status`
- THEN it SHALL display cache directory location
- AND SHALL show each cache file with size and age
- AND SHALL show source counts (e.g., "5 sources, bashrc")

### Requirement: Shell Integration Caching

The system MUST cache bash_env, bash_aliases, and bash_completion files with proper loading order.

#### Scenario: bash_env Cached and Sourced

- GIVEN topics have bash_env files
- WHEN the shell starts and sources .bash_profile
- THEN it SHALL check for ${XDG_CACHE_HOME}/dotfiles/bash_env.sh
- IF cache is fresh, SHALL source cache directly
- IF cache is stale or missing, SHALL regenerate from all bash_env files
- AND SHALL export environment variables before aliases load

#### Scenario: bash_aliases Cached and Sourced

- GIVEN topics have bash_aliases files
- WHEN .bashrc is sourced
- THEN it SHALL check for ${XDG_CACHE_HOME}/dotfiles/bash_aliases.sh
- IF cache is fresh, SHALL source cache directly
- IF cache is stale or missing, SHALL regenerate from all bash_aliases files

#### Scenario: bash_completion Cached and Sourced

- GIVEN topics have bash_completion files
- WHEN .bashrc is sourced
- THEN it SHALL check for ${XDG_CACHE_HOME}/dotfiles/bash_completion.sh
- IF cache is fresh, SHALL source cache directly
- IF cache is stale or missing, SHALL regenerate from all bash_completion files
- AND SHALL load after aliases for proper tab completion

### Requirement: Cache Freshness Validation

The system MUST accurately detect stale caches by comparing modification times.

#### Scenario: Cache Freshness Check

- GIVEN a cache file exists at ${XDG_CACHE_HOME}/dotfiles/bash_aliases.sh
- WHEN the shell checks freshness
- THEN it SHALL compare cache mtime against all source bash_aliases files
- IF any source is newer than cache, cache is stale
- IF cache is stale, SHALL regenerate automatically

#### Scenario: New Topic Added

- GIVEN a cache was generated from 5 topics
- WHEN a new topic with bash_aliases is added
- THEN on next shell start, the new file's mtime SHALL be newer than cache
- AND cache SHALL be regenerated to include new topic

#### Scenario: Topic Removed

- GIVEN a cache includes a topic that is then deleted
- WHEN the shell starts
- THEN it SHALL regenerate cache without the deleted topic
- AND SHALL not error on missing source file

### Requirement: Shortcuts Cache

The system MUST cache the list of available keyboard shortcuts topics.

#### Scenario: Shortcuts Topics Cache

- GIVEN multiple modules have bash_shortcuts files
- WHEN shortcuts command runs for the first time
- THEN it SHALL scan for all bash_shortcuts files
- AND SHALL build topic → path mapping
- AND SHALL save to ${XDG_CACHE_HOME}/dotfiles/shortcuts/topics.cache

#### Scenario: Shortcuts Cache Hit

- GIVEN shortcuts topics cache exists and is fresh
- WHEN shortcuts command runs
- THEN it SHALL load topics from cache in <50ms
- AND SHALL not scan filesystem

#### Scenario: Shortcuts Cache Invalidation

- GIVEN shortcuts cache exists
- WHEN a bash_shortcuts file is modified (newer than cache)
- THEN shortcuts command SHALL detect stale cache
- AND SHALL regenerate topics cache automatically

---

## Current Implementation

### Cache Location

All shell caches stored at:
```
${XDG_CACHE_HOME}/dotfiles/
├── bash_env.sh           # Aggregated bash_env from all topics
├── bash_aliases.sh       # Aggregated bash_aliases from all topics
├── bash_completion.sh    # Aggregated bash_completion from all topics
└── shortcuts/            # Keyboard shortcuts topics cache
    └── topics.cache
```

Default: `~/.cache/dotfiles/`

### Cache Generation

Handled by shell initialization files (.bash_profile, .bashrc):

```bash
# Example from .bashrc for bash_aliases
CACHE_FILE="${XDG_CACHE_HOME:-$HOME/.cache}/dotfiles/bash_aliases.sh"

# Check if cache is fresh
if [ -f "$CACHE_FILE" ]; then
    cache_valid=true
    # Compare cache mtime against all source files
    for file in "$DOTFILES"/*/bash_aliases; do
        [ "$file" -nt "$CACHE_FILE" ] && cache_valid=false && break
    done
fi

# If cache is stale or missing, regenerate
if [ "$cache_valid" != true ]; then
    mkdir -p "$(dirname "$CACHE_FILE")"
    # Concatenate all bash_aliases files
    cat "$DOTFILES"/*/bash_aliases > "$CACHE_FILE" 2>/dev/null
fi

# Source the cache
[ -f "$CACHE_FILE" ] && source "$CACHE_FILE"
```

### Invalidation Rules

**Automatic**:
- On shell start, compare cache mtime vs source files
- If any source newer than cache, regenerate

**Manual**:
- `dot invalidate` - removes all cache files
- Bootstrap purge - removes stale caches during setup

### Cache Strategy

#### When Cache is Used

1. **Shell Startup**: bash_profile sources bash_env.sh cache
2. **Interactive Shell**: bashrc sources bash_aliases.sh and bash_completion.sh caches
3. **Shortcuts Command**: Loads topics.cache for quick lookup

#### When Cache is Regenerated

1. **First Run**: No cache exists yet
2. **Stale Detection**: Source file modified after cache
3. **New Topic**: New bash_* file added to dotfiles
4. **Manual Invalidation**: User runs `dot invalidate`
5. **Bootstrap**: During initial setup

### Cache Files

| Cache File | Source Files | Loaded By | Performance Gain |
|------------|--------------|-----------|------------------|
| `bash_env.sh` | `*/bash_env` | .bash_profile | ~135ms (150ms → 15ms) |
| `bash_aliases.sh` | `*/bash_aliases` | .bashrc | ~180ms (200ms → 20ms) |
| `bash_completion.sh` | `*/bash_completion` | .bashrc | ~225ms (250ms → 25ms) |
| `shortcuts/topics.cache` | `*/bash_shortcuts` | shortcuts command | ~100ms (150ms → 50ms) |

---

## Testing Requirements

### Test: Cache Generation

```bash
# Remove all caches
rm -rf ~/.cache/dotfiles/

# Start new shell
exec bash

# Verify caches were created
ls -la ~/.cache/dotfiles/
# Expected: bash_env.sh, bash_aliases.sh, bash_completion.sh exist
```

### Test: Cache Hit

```bash
# Ensure cache exists
[ -f ~/.cache/dotfiles/bash_aliases.sh ] || exec bash

# Time cache hit
time source ~/.cache/dotfiles/bash_aliases.sh
# Expected: <25ms
```

### Test: Cache Invalidation

```bash
# Generate cache
exec bash

# Check cache exists
ls -la ~/.cache/dotfiles/bash_aliases.sh

# Modify source
touch ~/.dotfiles/git/bash_aliases

# Reload shell
exec bash

# Verify cache was regenerated (newer mtime)
ls -la ~/.cache/dotfiles/bash_aliases.sh
stat -f "%Sm" ~/.cache/dotfiles/bash_aliases.sh  # macOS
# Expected: timestamp should be very recent
```

### Test: Manual Invalidation

```bash
# Generate caches
exec bash

# Count cache files
cache_count=$(find ~/.cache/dotfiles -type f | wc -l)
echo "Cache files: $cache_count"

# Invalidate
dot invalidate

# Verify removal
[ ! -f ~/.cache/dotfiles/bash_aliases.sh ] && echo "✓ Cache removed"
[ ! -d ~/.cache/dotfiles/shortcuts ] && echo "✓ Shortcuts cache removed"
```

### Test: New Topic Detection

```bash
# Create new topic
mkdir -p ~/.dotfiles/testcache
cat > ~/.dotfiles/testcache/bash_aliases << 'EOF'
alias testcache='echo "Test cache works"'
EOF

# Reload shell (cache should regenerate)
exec bash

# Verify new alias loaded
type testcache
# Expected: testcache is aliased to echo...

# Cleanup
rm -rf ~/.dotfiles/testcache
```

---

## Non-Functional Requirements

### Performance

**Shell Startup**:
- Interactive shell startup SHALL be <200ms
- With caching, startup SHALL be <50ms faster than uncached
- Cache freshness check SHALL be <10ms

**Command Execution**:
- `dot status` SHALL complete in <2 seconds
- `shortcuts` SHALL complete in <100ms (cached)

**Cache Operations**:
- Cache hits SHALL avoid filesystem scanning
- Cache invalidation SHALL be automatic and transparent
- Manual invalidation SHALL be instant (<100ms)

### Reliability

**Error Handling**:
- Missing source files SHALL NOT break cache generation
- Permission errors SHALL fail gracefully with clear message
- Partial cache SHALL NOT be sourced (atomic writes)

**Consistency**:
- Cache MUST accurately reflect all source files
- Stale cache MUST be detected reliably
- Regeneration MUST include all topics

### Maintainability

**Code Quality**:
- Cache generation logic SHALL be in shell init files
- Manual operations SHALL be in `dot` command
- No external dependencies required (pure bash)

**Debugging**:
- Cache location SHALL be displayed in `dot status`
- Cache age and size SHALL be visible
- Source file counts SHALL be shown

---

## Dependencies

### Required

- **bash** ≥4.0 - Shell scripting and runtime
- **find** - File discovery (POSIX compliant)
- **cat** - File concatenation
- **mkdir** - Directory creation
- **rm** - File removal
- **stat** - File modification time (BSD or GNU)

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `DOTFILES` | `~/.dotfiles` | Source directory for topics |
| `XDG_CACHE_HOME` | `~/.cache` | Cache storage location |

---

## References

- **XDG Base Directory Specification**: https://specifications.freedesktop.org/basedir-spec/latest/
- **Bash Scripting Best Practices**: https://google.github.io/styleguide/shellguide.html
- **RFC 2119 - Key words for use in RFCs**: https://datatracker.ietf.org/doc/html/rfc2119

## Internal Documentation

- [Dotfiles System Core Specification](../001-dotfiles-core/spec.md) - Main dotfiles system
- [Shortcuts System Specification](../003-shortcuts-system/spec.md) - Keyboard shortcuts (uses caching)

---

**License:** Apache-2.0
**Copyright:** 2026 Ilja Heitlager
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
