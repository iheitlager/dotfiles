# Keyboard Shortcuts System Specification

**Domain:** Developer Productivity / Documentation
**Version:** 1.0.0
**Status:** Implemented
**Date:** 2026-02-07

## Overview

A dynamic, modular keyboard shortcuts documentation system that automatically discovers and displays keyboard shortcuts across all dotfiles modules, providing developers with instant access to keybindings without searching through configuration files.

---

## RFC 2119 Keywords

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

---

## ADDED Requirements

### Requirement: Dynamic Discovery
The system MUST automatically discover all keyboard shortcut documentation files across the dotfiles repository without requiring manual registration.

#### Scenario: New Module Added
- GIVEN a developer creates a new module directory in dotfiles
- WHEN they create an executable `bash_shortcuts` file in that module
- THEN the shortcuts system SHALL automatically include it in the available topics list without code changes

#### Scenario: Module Removed
- GIVEN a module with `bash_shortcuts` exists in the system
- WHEN the module directory is deleted
- THEN the shortcuts system SHALL automatically remove it from available topics on next cache refresh

### Requirement: Smart Caching
The system MUST cache discovered topics to minimize filesystem scanning while automatically invalidating stale caches.

#### Scenario: Cache Hit
- GIVEN the topics cache exists and is fresh
- WHEN a user runs `shortcuts`
- THEN the system SHALL load topics from cache in <50ms

#### Scenario: Cache Miss
- GIVEN no cache exists or cache is stale
- WHEN a user runs `shortcuts`
- THEN the system SHALL scan filesystem, rebuild cache, and save for future use

#### Scenario: File Modified
- GIVEN a cached topics list exists
- WHEN any `bash_shortcuts` file is modified (newer mtime than cache)
- THEN the system SHALL automatically invalidate and regenerate the cache

### Requirement: Multiple Access Interfaces
The system MUST provide multiple ergonomic ways to access shortcut documentation.

#### Scenario: Direct Command
- GIVEN a user wants to see shortcuts
- WHEN they type `shortcuts` or `shortcuts bash`
- THEN the system SHALL display all shortcuts or filtered shortcuts

#### Scenario: Short Alias
- GIVEN a user wants quick access
- WHEN they type `sc bash`
- THEN the system SHALL display bash shortcuts (equivalent to `shortcuts bash`)

#### Scenario: Help Integration
- GIVEN a user expects help system integration
- WHEN they type `help shortcuts`
- THEN the system SHALL display usage information
- AND WHEN they type `help shortcuts bash`
- THEN the system SHALL display bash shortcuts

### Requirement: Topic Filtering
The system MUST allow users to view shortcuts for specific topics or all topics.

#### Scenario: All Shortcuts
- GIVEN multiple topics exist (bash, tmux, nvim, ghostty)
- WHEN a user runs `shortcuts` with no arguments
- THEN the system SHALL display shortcuts for all topics in alphabetical order

#### Scenario: Single Topic
- GIVEN multiple topics exist
- WHEN a user runs `shortcuts tmux`
- THEN the system SHALL display only tmux shortcuts
- AND SHALL NOT display other topics

#### Scenario: Invalid Topic
- GIVEN a user specifies a non-existent topic
- WHEN they run `shortcuts invalid_topic`
- THEN the system SHALL display an error message
- AND SHALL show usage information with available topics
- AND SHALL exit with status code 1

### Requirement: Cache Management
The system MUST integrate with the dotfiles cache management infrastructure.

#### Scenario: Cache Invalidation via dot Command
- GIVEN the shortcuts cache exists
- WHEN a user runs `dot invalidate`
- THEN the system SHALL remove the shortcuts cache file
- AND SHALL display confirmation of removal

#### Scenario: Manual Cache Refresh
- GIVEN stale or outdated cache
- WHEN a user runs `shortcuts --refresh`
- THEN the system SHALL force full discovery scan
- AND SHALL rebuild cache from scratch
- AND SHALL display count of discovered topics

### Requirement: Extensible Module Format
The system MUST support a simple, consistent format for module-specific shortcut documentation.

#### Scenario: Standard Format
- GIVEN a module wants to document shortcuts
- WHEN they create a `bash_shortcuts` file with:
  - Executable permissions (chmod +x)
  - Bash shebang (#!/usr/bin/env bash)
  - Helper functions (shortcut, note)
  - Organized sections with echo statements
- THEN the shortcuts system SHALL automatically parse and display it

#### Scenario: Formatted Output
- GIVEN a `bash_shortcuts` file outputs formatted text
- WHEN the shortcuts command executes it
- THEN the output MUST include:
  - Section headers (plain text)
  - Colored key names (green, 25-char width)
  - Descriptions (plain text)
  - Optional notes (cyan)

### Requirement: Performance Constraints
The system MUST maintain fast response times for interactive use.

#### Scenario: Cached Execution
- GIVEN a valid cache exists
- WHEN a user runs `shortcuts bash`
- THEN the total execution time SHALL be <100ms

#### Scenario: Cold Start
- GIVEN no cache exists
- WHEN a user runs `shortcuts bash` for the first time
- THEN the total execution time SHALL be <200ms

### Requirement: Cross-Module Consistency
All module `bash_shortcuts` files MUST follow a consistent structure and format.

#### Scenario: Helper Functions
- GIVEN any module's `bash_shortcuts` file
- WHEN it defines shortcuts
- THEN it SHALL use standardized helper functions:
  - `shortcut(key, description)` for key bindings
  - `note(message)` for explanatory notes
  - Color codes: GREEN for keys, CYAN for notes, RESET for normal

#### Scenario: Section Organization
- GIVEN a module with multiple shortcut categories
- WHEN organizing the documentation
- THEN it SHALL use clear section headers with echo statements
- AND SHALL group related shortcuts together
- AND SHALL order sections logically (most common first)

---

## Current Implementation

### Architecture

```yaml
components:
  cli: local/bin/shortcuts (224 lines)
  cache: ${XDG_CACHE_HOME}/dotfiles/shortcuts.cache
  modules:
    - bash/bash_shortcuts (Bash + FZF)
    - config/ghostty/bash_shortcuts (Terminal)
    - nvim/bash_shortcuts (Editor)
    - tmux/bash_shortcuts (Multiplexer)
  integration:
    - bash/bash_aliases (sc alias, help function)
    - local/bin/dot (invalidate command)
```

### Supported Topics

| Topic | File | Categories | Shortcuts |
|-------|------|------------|-----------|
| bash | bash/bash_shortcuts | Navigation, Editing, History, FZF | ~30 |
| ghostty | config/ghostty/bash_shortcuts | Window, Font, Tabs | ~15 |
| nvim | nvim/bash_shortcuts | Navigation, Copy/Paste, Buffers, LSP | ~35 |
| tmux | tmux/bash_shortcuts | Sessions, Windows, Panes, Copy Mode | ~25 |

### Discovery Algorithm

```
1. Scan ${DOTFILES} for files named "bash_shortcuts"
2. Extract relative paths from dotfiles root
3. Derive topic names:
   - config/*/bash_shortcuts → basename of subdirectory
   - */bash_shortcuts → basename of parent directory
4. Build associative array: topic → path
5. Sort topics alphabetically
6. Cache results to shortcuts.cache
```

### Cache Format

```
# ${XDG_CACHE_HOME}/dotfiles/shortcuts.cache
bash=bash/bash_shortcuts
ghostty=config/ghostty/bash_shortcuts
nvim=nvim/bash_shortcuts
tmux=tmux/bash_shortcuts
```

---

## Usage Examples

### View All Shortcuts
```bash
$ shortcuts
# Displays all shortcuts for all topics

$ sc
# Same as above (short alias)
```

### View Topic Shortcuts
```bash
$ shortcuts bash
# Shows bash and FZF shortcuts

$ sc nvim
# Shows neovim keybindings

$ help shortcuts tmux
# Shows tmux shortcuts via help system
```

### Cache Management
```bash
$ shortcuts --refresh
# Force rescan and rebuild cache

$ dot invalidate
# Clear all dotfiles caches including shortcuts
```

### Getting Help
```bash
$ shortcuts --help
$ shortcuts -h
$ help shortcuts
# All show usage information
```

---

## Extension Guide

### Adding Shortcuts for New Module

#### Step 1: Create bash_shortcuts File
```bash
#!/usr/bin/env bash
# Copyright 2026 Your Name
# SPDX-License-Identifier: Apache-2.0

GREEN='\033[32m'
CYAN='\033[36m'
RESET='\033[0m'

shortcut() {
    printf "  ${GREEN}%-25s${RESET} %s\n" "$1" "$2"
}

note() {
    printf "  ${CYAN}Note: %s${RESET}\n" "$1"
}

echo "Section Name:"
shortcut "Ctrl+X" "Description of what it does"
shortcut "Alt+F" "Another shortcut"
note "Additional context or tips"

echo ""
echo "Another Section:"
shortcut "F1" "Help system"
```

#### Step 2: Make Executable
```bash
chmod +x ~/.dotfiles/mymodule/bash_shortcuts
```

#### Step 3: Refresh and Test
```bash
shortcuts --refresh
shortcuts mymodule
```

---

## Testing Requirements

### Test: Discovery
```bash
# Verify all bash_shortcuts files are found
find ~/.dotfiles -name "bash_shortcuts" -type f
# Expected: 4 files (bash, ghostty, nvim, tmux)
```

### Test: Cache Invalidation
```bash
# Populate cache
shortcuts bash

# Modify a shortcuts file
touch ~/.dotfiles/bash/bash_shortcuts

# Verify auto-invalidation
shortcuts bash
# Expected: cache should regenerate automatically
```

### Test: Aliases
```bash
# Short alias
sc --help
# Expected: shows usage

# Help integration
help shortcuts
# Expected: shows usage

help shortcuts bash
# Expected: shows bash shortcuts
```

### Test: Performance
```bash
# Cold start
rm -f ~/.cache/dotfiles/shortcuts.cache
time shortcuts bash
# Expected: <200ms

# Cached
time shortcuts bash
# Expected: <100ms
```

---

## Dependencies

### Required
- bash ≥4.0
- find (POSIX compliant)
- stat (BSD or GNU)
- chmod (for setting executable permissions)

### Optional
- bat (for syntax highlighted help, fallback: cat)

### Environment
- `$DOTFILES` → defaults to `${HOME}/.dotfiles`
- `$XDG_CACHE_HOME` → defaults to `${HOME}/.cache`

---

## Future Enhancements

### Potential: Interactive Search
- GIVEN a user wants to search across all shortcuts
- WHEN they run `shortcuts --search "paste"`
- THEN the system SHALL use fzf to provide interactive filtering

### Potential: Export Formats
- GIVEN a user wants external documentation
- WHEN they run `shortcuts --export pdf`
- THEN the system SHALL generate a PDF with all shortcuts

### Potential: Config File Parsing
- GIVEN modules with config files (tmux.conf, init.lua)
- WHEN shortcuts are updated in config
- THEN the system COULD auto-generate bash_shortcuts from config annotations

---

## Non-Functional Requirements

### Maintainability
- Code SHALL be commented with clear explanations
- Functions SHALL have single responsibilities
- Error handling SHALL provide helpful messages

### Portability
- System SHALL work on macOS and Linux
- System SHALL gracefully handle missing optional dependencies
- System SHALL follow XDG Base Directory specification

### User Experience
- Output SHALL use consistent formatting and colors
- Error messages SHALL be clear and actionable
- Help text SHALL include examples

---

## References

- **RFC 2119 - Key words for use in RFCs**: https://datatracker.ietf.org/doc/html/rfc2119
- **XDG Base Directory Specification**: https://specifications.freedesktop.org/basedir-spec/
- **Bash Scripting Best Practices**: https://google.github.io/styleguide/shellguide.html

## Internal Documentation

- [Dotfiles System Core Specification](../001-dotfiles-core/spec.md) - Main dotfiles system
- [Dotfiles Caching Specification](../002-dotfiles-caching/spec.md) - Caching system (shortcuts uses this)

---

**License:** Apache-2.0
**Copyright:** 2026 Ilja Heitlager
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
