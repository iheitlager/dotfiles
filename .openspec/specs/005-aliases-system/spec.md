# Aliases Documentation System Specification

**Domain:** Developer Productivity / Documentation
**Version:** 1.0.0
**Status:** Proposed
**Date:** 2026-02-09
**Owner:** Ilja Heitlager

## Overview

A dynamic, modular aliases documentation system that automatically discovers and displays shell aliases across all dotfiles topics, providing developers with instant access to available shortcuts without searching through bash_aliases files.

### Philosophy

- **Zero-Maintenance Documentation**: Aliases are extracted directly from bash_aliases files where they're defined
- **Discoverable by Default**: All aliases are automatically indexed and searchable without manual registration
- **Topic-Aware Display**: Group aliases by topic (bash, git, docker) for easy reference
- **Cache for Speed**: Smart caching ensures instant access while staying fresh

### Key Capabilities

- **Automatic Discovery**: Scans all topic directories for bash_aliases files
- **Multiple Access Methods**: Direct command (aliases), short alias (al)
- **Topic Filtering**: View all aliases or filter by specific topic
- **Smart Caching**: mtime-based cache with automatic invalidation
- **Alias Extraction**: Parses bash_aliases files to extract alias definitions

---

## RFC 2119 Keywords

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

---

## ADDED Requirements

### Requirement: Dynamic Discovery

The system MUST automatically discover all bash_aliases files across the dotfiles repository without requiring manual registration.

#### Scenario: New Topic Added

- GIVEN a developer creates a new topic directory in dotfiles
- WHEN they create a bash_aliases file in that topic
- THEN the aliases system SHALL automatically include it in the available topics list without code changes

#### Scenario: Topic Removed

- GIVEN a topic with bash_aliases exists in the system
- WHEN the topic directory is deleted
- THEN the aliases system SHALL automatically remove it from available topics on next cache refresh

### Requirement: Smart Caching

The system MUST cache discovered topics to minimize filesystem scanning while automatically invalidating stale caches.

#### Scenario: Cache Hit

- GIVEN the topics cache exists and is fresh
- WHEN a user runs aliases
- THEN the system SHALL load topics from cache in less than 50ms

#### Scenario: Cache Miss

- GIVEN no cache exists or cache is stale
- WHEN a user runs aliases
- THEN the system SHALL scan filesystem, rebuild cache, and save for future use

#### Scenario: File Modified

- GIVEN a cached topics list exists
- WHEN any bash_aliases file is modified (newer mtime than cache)
- THEN the system SHALL automatically invalidate and regenerate the cache

### Requirement: Alias Extraction

The system MUST parse bash_aliases files to extract alias definitions and display them in readable format.

#### Scenario: Simple Alias Extraction

- GIVEN a bash_aliases file with line "alias gs='git status'"
- WHEN the system parses the file
- THEN it SHALL extract alias name "gs" and command "git status"
- AND it SHALL display them in formatted output

#### Scenario: Function Extraction

- GIVEN a bash_aliases file with function definitions
- WHEN the system parses the file
- THEN it SHALL extract function names
- AND it SHALL display them alongside aliases

#### Scenario: Comment Preservation

- GIVEN a bash_aliases file with comments above aliases
- WHEN the system parses the file
- THEN it MAY extract comments as descriptions
- AND it SHALL associate comments with the following alias

### Requirement: Multiple Access Interfaces

The system MUST provide multiple ergonomic ways to access alias documentation.

#### Scenario: Direct Command

- GIVEN a user wants to see aliases
- WHEN they type aliases or aliases bash
- THEN the system SHALL display all aliases or filtered aliases

#### Scenario: Short Alias

- GIVEN a user wants quick access
- WHEN they type al bash
- THEN the system SHALL display bash aliases (equivalent to aliases bash)

### Requirement: Topic Filtering

The system MUST allow users to view aliases for specific topics or all topics.

#### Scenario: All Aliases

- GIVEN multiple topics exist (bash, git, docker, python)
- WHEN a user runs aliases with no arguments
- THEN the system SHALL display aliases for all topics in alphabetical order

#### Scenario: Single Topic

- GIVEN multiple topics exist
- WHEN a user runs aliases git
- THEN the system SHALL display only git aliases
- AND it SHALL NOT display other topics

#### Scenario: Invalid Topic

- GIVEN a user specifies a non-existent topic
- WHEN they run aliases invalid_topic
- THEN the system SHALL display an error message
- AND it SHALL show usage information with available topics
- AND it SHALL exit with status code 1

### Requirement: Cache Management

The system MUST integrate with the dotfiles cache management infrastructure.

#### Scenario: Cache Invalidation via dot Command

- GIVEN the aliases cache exists
- WHEN a user runs dot invalidate
- THEN the system SHALL remove the aliases cache file
- AND it SHALL display confirmation of removal

#### Scenario: Manual Cache Refresh

- GIVEN stale or outdated cache
- WHEN a user runs aliases --refresh
- THEN the system SHALL force full discovery scan
- AND it SHALL rebuild cache from scratch
- AND it SHALL display count of discovered topics

### Requirement: Performance Constraints

The system MUST maintain fast response times for interactive use.

#### Scenario: Cached Execution

- GIVEN a valid cache exists
- WHEN a user runs aliases bash
- THEN the total execution time SHALL be less than 100ms

#### Scenario: Cold Start

- GIVEN no cache exists
- WHEN a user runs aliases bash for the first time
- THEN the total execution time SHALL be less than 200ms

---

## Current Implementation

### Architecture

```
components:
  cli: local/bin/aliases (TBD)
  cache: ${XDG_CACHE_HOME}/dotfiles/aliases/topics.cache
  sources:
    - bash/bash_aliases
    - git/bash_aliases
    - docker/bash_aliases
    - python/bash_aliases
    - [all other topics with bash_aliases]
  integration:
    - bash/bash_aliases (al alias)
    - local/bin/dot (invalidate command)
```

### Discovery Algorithm

```
1. Scan ${DOTFILES} for files named "bash_aliases"
2. Extract relative paths from dotfiles root
3. Derive topic names from parent directory
4. Build associative array: topic → path
5. Sort topics alphabetically
6. Cache results to aliases/topics.cache
```

### Cache Format

```
# ${XDG_CACHE_HOME}/dotfiles/aliases/topics.cache
bash=bash/bash_aliases
docker=docker/bash_aliases
git=git/bash_aliases
python=python/bash_aliases
```

---

## Usage Examples

### View All Aliases

```bash
$ aliases
# Displays all aliases for all topics

$ al
# Same as above (short alias)
```

### View Topic Aliases

```bash
$ aliases bash
# Shows bash aliases

$ al git
# Shows git aliases
```

### Cache Management

```bash
$ aliases --refresh
# Force rescan and rebuild cache

$ dot invalidate
# Clear all dotfiles caches including aliases
```

### Getting Help

```bash
$ aliases --help
$ aliases -h
# Show usage information
```

---

## Metadata

This section provides project-specific links for tracking and traceability.

### Implementation Files

**Main Command:**
- [local/bin/aliases](local/bin/aliases) - Aliases command with discovery, caching, and filtering (TBD)

**Source Files:**
- [bash/bash_aliases](bash/bash_aliases) - Bash shell aliases
- [git/bash_aliases](git/bash_aliases) - Git aliases
- [docker/bash_aliases](docker/bash_aliases) - Docker aliases
- [python/bash_aliases](python/bash_aliases) - Python aliases
- [All topics with bash_aliases files]

**Shell Integration:**
- [bash/bash_aliases](bash/bash_aliases) - Defines al alias for aliases command (TBD)

### Test Coverage

**Manual Testing:**
- Discovery: Add new bash_aliases file, run aliases, verify it appears
- Caching: Run aliases twice, verify second run uses cache
- Filtering: Run aliases bash, verify only bash aliases shown
- Invalidation: Run dot invalidate, verify aliases cache removed

**Test Procedures:** Documented in requirements scenarios

### Related Specifications

- [001-dotfiles-core](../001-dotfiles-core/spec.md) - Core dotfiles system
- [002-dotfiles-caching](../002-dotfiles-caching/spec.md) - Caching infrastructure used by aliases
- [003-shortcuts-system](../003-shortcuts-system/spec.md) - Similar system for keyboard shortcuts

---

## References

- **RFC 2119 - Key words for use in RFCs**: https://datatracker.ietf.org/doc/html/rfc2119
- **Bash Aliases**: https://www.gnu.org/software/bash/manual/html_node/Aliases.html
- **XDG Base Directory Specification**: https://specifications.freedesktop.org/basedir-spec/

## Internal Documentation

- [Dotfiles System Core Specification](../001-dotfiles-core/spec.md) - Main dotfiles system
- [Dotfiles Caching Specification](../002-dotfiles-caching/spec.md) - Caching system (aliases uses this)
- [Shortcuts System Specification](../003-shortcuts-system/spec.md) - Parallel system for keyboard shortcuts

---

**License:** Apache-2.0
**Copyright:** 2026 Ilja Heitlager
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
