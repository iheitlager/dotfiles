# OpenSpec

**A specification-driven documentation system for codebases**

OpenSpec is a structured approach to documenting software architecture, behavior, and requirements using behavior-driven specifications with RFC 2119 keywords. It provides machine-readable specifications that serve as both documentation and validation criteria for implementations.

---

## Philosophy

OpenSpec follows these core principles:

- **Requirements-First**: Define what the system MUST, SHOULD, and MAY do before implementation
- **Behavior-Driven**: Express requirements as scenarios with Given-When-Then structure
- **RFC 2119 Compliance**: Use standardized requirement keywords (MUST, SHOULD, MAY, etc.)
- **Living Documentation**: Specs evolve with the codebase and stay in sync
- **Discoverable**: Automated tools for browsing, searching, and validating specs

---

## Structure

```
.openspec/
├── README.md                    # This file
└── specs/                       # All specifications
    ├── 001-dotfiles-core/
    │   └── spec.md             # Core dotfiles system spec
    ├── 002-dotfiles-caching/
    │   └── spec.md             # Caching system spec
    └── 003-shortcuts-system/
        └── spec.md             # Keyboard shortcuts spec
```

Each specification follows a standard format:

```markdown
# [System Name] Specification

**Domain:** [Domain/Category]
**Version:** [Semantic Version]
**Status:** [Implemented|Planned|Deprecated]
**Date:** YYYY-MM-DD

## Overview
[High-level description of the system]

## RFC 2119 Keywords
[Standard RFC 2119 compliance statement]

## ADDED Requirements

### Requirement: [Requirement Name]
[Description of the requirement]

#### Scenario: [Scenario Name]
- GIVEN [precondition]
- WHEN [action]
- THEN [expected outcome]
- AND [additional outcomes]
```

---

## Using OpenSpec

### Browse Specifications Interactively

The `spec` command provides an interactive fzf-based browser:

```bash
# Interactive browser with beautiful markdown rendering (glow)
spec

# Interactive browser with raw syntax highlighting (bat)
spec --raw
```

**Features:**
- Browse all specifications and their requirements
- Live preview with syntax highlighting
- Jump to specific requirements
- Navigate with arrow keys, select with Enter

### List All Specifications

```bash
# List all specs with metadata and requirements
spec list
```

**Output includes:**
- File paths and titles
- Domain, version, and status
- All requirements with line numbers

### Show Status Overview

```bash
# Compact table view of all specs
spec status
```

**Output includes:**
- Total number of specifications
- Version, status, and requirement count per spec
- Total requirement count

---

## Creating New Specifications

### 1. Create Directory Structure

```bash
mkdir -p .openspec/specs/my-new-feature
```

### 2. Create spec.md

```bash
touch .openspec/specs/my-new-feature/spec.md
```

### 3. Follow the Template

```markdown
# My New Feature Specification

**Domain:** [Your Domain]
**Version:** 1.0.0
**Status:** Planned
**Date:** 2026-02-07

## Overview

[Describe what this feature does and why it exists]

### Philosophy

- **Principle 1**: [Core design principle]
- **Principle 2**: [Another principle]

### Key Capabilities

- **Capability 1**: [What it can do]
- **Capability 2**: [Another capability]

---

## RFC 2119 Keywords

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

---

## ADDED Requirements

### Requirement: [Requirement Name]

[Detailed description of what this requirement accomplishes]

#### Scenario: [Happy Path Scenario]

- GIVEN [initial state or precondition]
- WHEN [action or trigger]
- THEN [expected outcome]
- AND [additional expected outcomes]

#### Scenario: [Edge Case or Alternative Path]

- GIVEN [different initial state]
- WHEN [different action]
- THEN [different expected outcome]

### Requirement: [Another Requirement]

[Description]

#### Scenario: [Scenario Name]

- GIVEN [precondition]
- WHEN [action]
- THEN [outcome]
```

### 4. Verify Your Spec

```bash
# Check that your spec appears
spec status

# Browse to your new spec
spec
```

---

## RFC 2119 Keyword Reference

| Keyword | Meaning |
|---------|---------|
| **MUST** / **REQUIRED** / **SHALL** | Absolute requirement |
| **MUST NOT** / **SHALL NOT** | Absolute prohibition |
| **SHOULD** / **RECOMMENDED** | May exist valid reasons to ignore, but must understand implications |
| **SHOULD NOT** / **NOT RECOMMENDED** | May exist valid reasons to use, but must understand implications |
| **MAY** / **OPTIONAL** | Truly optional, implementer can choose |

---

## Current Specifications

### Dotfiles System Core
**Location:** `specs/001-dotfiles-core/spec.md`
**Status:** Implemented
**Description:** Complete specification of the modular, XDG-compliant dotfiles management system with topic-based organization, automated bootstrapping, and package management.

### Keyboard Shortcuts System
**Location:** `specs/003-shortcuts-system/spec.md`
**Status:** Implemented
**Description:** Dynamic keyboard shortcuts documentation system that automatically discovers and displays keybindings across all dotfiles modules.

### Dotfiles Caching System
**Location:** `specs/002-dotfiles-caching/spec.md`
**Status:** Implemented
**Description:** Mtime-based caching system for shell integrations that improves shell startup performance through aggressive caching with automatic invalidation.

---

## Tools

### Interactive Browser (`spec`)

The `spec` command is located at `~/.dotfiles/local/bin/spec` and provides:

- **Auto-discovery**: Finds `.openspec/` or `openspec/` directories automatically
- **Search order**: Git root → current directory → `$DOTFILES`
- **Markdown rendering**: Uses `glow` for beautiful rendering or `bat` for syntax highlighting
- **Fuzzy search**: Powered by `fzf` for fast navigation

### Requirements

- `bash` 4.0+
- `fzf` (for interactive mode) - `brew install fzf`
- `glow` (recommended) - `brew install glow`
- `bat` (optional) - `brew install bat`

---

## Benefits

### For Developers

- **Clear Requirements**: Understand what the system must, should, and may do
- **Behavior Examples**: See concrete scenarios for each requirement
- **Quick Reference**: Browse specifications without reading code
- **Onboarding**: New team members can understand architecture quickly

### For Documentation

- **Structured**: Consistent format across all specifications
- **Searchable**: Use `spec` command or grep to find requirements
- **Versioned**: Track specification changes alongside code
- **Validated**: Specs serve as acceptance criteria for features

### For AI Assistants

- **Context**: Architecture references available in system prompts
- **Validation**: AI can check implementations against requirements
- **Consistency**: AI maintains architectural patterns from specs
- **Documentation**: AI can reference specs when making changes

---

## Best Practices

### Writing Specifications

1. **Start with Overview**: Explain the "why" before the "what"
2. **Define Philosophy**: Document core design principles
3. **Use Scenarios**: Every requirement needs concrete examples
4. **Be Specific**: Use RFC 2119 keywords precisely
5. **Keep Updated**: Update specs when implementation changes

### Organizing Specifications

1. **One System per Spec**: Each major system gets its own spec file
2. **Logical Grouping**: Group related specs in subdirectories
3. **Consistent Naming**: Use `spec.md` as the filename
4. **Version Properly**: Bump versions when requirements change

### Maintaining Specifications

1. **Review Regularly**: Ensure specs match implementation
2. **Update Together**: Change specs and code in same PR
3. **Archive Deprecated**: Mark status as "Deprecated" rather than deleting
4. **Cross-Reference**: Link related specs when appropriate

---

## Integration

### With Git

OpenSpec directories are version controlled alongside code:

```bash
# Specs are part of your repository
git add .openspec/
git commit -m "docs: add new feature specification"
```

### With Claude Code

The system prompt includes architecture references:

```markdown
## Architecture References

For understanding the dotfiles system architecture:
- **Core system spec**: `~/.dotfiles/.openspec/specs/001-dotfiles-core/spec.md`
- **Shortcuts system**: `~/.dotfiles/.openspec/specs/003-shortcuts-system/spec.md`
- **XDG integration**: `~/.dotfiles/docs/xdg_setup.md`
```

### With Development Workflow

1. **Planning**: Write spec before implementation
2. **Implementation**: Code against spec requirements
3. **Testing**: Validate scenarios from spec
4. **Review**: Check that changes match spec
5. **Documentation**: Spec serves as documentation

---

## Examples

### Browse all specs

```bash
$ spec
# Opens fzf browser with all specs and requirements
# Use arrows to navigate, Enter to view
```

### View a specific spec

```bash
$ spec
# Type to search for "dotfiles"
# Press Enter to view with markdown rendering
```

### Check spec status

```bash
$ spec status

OpenSpec Status (~/.dotfiles/.openspec)

Files: 3

Specification                              Version   Status        Reqs
──────────────────────────────────────────────────────────────────────
Dotfiles System Core Specification         1.0.0     Implemented   8
Keyboard Shortcuts System Specification    1.0.0     Implemented   6
Dotfiles Caching System Specification      1.0.0     Implemented   4

Total Requirements: 18
```

---

## Contributing

When adding new features to the dotfiles system:

1. **Create a spec** (if adding a major system)
2. **Add requirements** with scenarios
3. **Implement** against the spec
4. **Update status** to "Implemented" when done

When modifying existing features:

1. **Read the spec** first to understand requirements
2. **Update requirements** if behavior changes
3. **Bump version** if requirements change significantly
4. **Maintain scenarios** to reflect new behavior

---

## License

OpenSpec specifications are part of the dotfiles repository.
Copyright 2026 Ilja Heitlager
SPDX-License-Identifier: Apache-2.0

---

*Last updated: 2026-02-07*
