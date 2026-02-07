# OpenSpec Generator Skill

## Overview

This skill helps you create **OpenSpec** specification files—lightweight, behavior-driven documentation that describes systems using the ADDED (Architecture Driven Development by Example) methodology. OpenSpec combines the clarity of RFC-style specifications with executable examples through scenarios.

## What is OpenSpec?

OpenSpec is a specification format that captures system behavior through:
- **RFC 2119 Keywords**: Formal requirement levels (MUST, SHALL, SHOULD, etc.)
- **ADDED Requirements**: Architecture-driven, example-based requirements
- **Gherkin-Style Scenarios**: Given-When-Then format for concrete examples
- **Living Documentation**: Specs that evolve with the system

**Philosophy**: Specs are living documents that guide development and serve as authoritative system documentation.

## When to Use This Skill

Invoke this skill when:
- Creating a new specification for a system or subsystem
- Documenting a component's behavior and requirements
- Need guidance on OpenSpec structure and patterns
- Want to scan existing specs for conventions

## OpenSpec Repository Structure

OpenSpec files are organized in a `.openspec/` or `openspec/` directory:

```
.openspec/
├── specs/
│   ├── system-name/
│   │   └── spec.md          # Individual specification
│   ├── subsystem-name/
│   │   └── spec.md
│   └── component-name/
│       └── spec.md
└── README.md                 # Optional: OpenSpec documentation guide
```

## How This Skill Works

When you invoke `/spec`, the skill will:

1. **Scan for Existing Specs**: Check `.openspec/` or `openspec/` directories for patterns
2. **Analyze Structure**: Extract common patterns, formatting, and conventions
3. **Guide Spec Creation**: Walk you through creating a new spec file
4. **Generate Template**: Create a properly structured spec.md file

## OpenSpec File Structure

Each spec.md follows this structure:

```markdown
# [System Name] Specification

**Domain:** [Domain Area]
**Version:** [Semantic Version]
**Status:** [Draft | Proposed | Implemented | Deprecated]
**Date:** [YYYY-MM-DD]

## Overview

[Brief description of the system, its purpose, and key capabilities]

### Philosophy

[Core principles and design philosophy]

### Key Capabilities

[Bullet list of major features and capabilities]

---

## RFC 2119 Keywords

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

---

## ADDED Requirements

### Requirement: [Requirement Name]

[Brief description of what the system MUST/SHALL/SHOULD do]

#### Scenario: [Scenario Name]

- GIVEN [preconditions and context]
- WHEN [action or event occurs]
- THEN [expected behavior]
- AND [additional expected behavior]

[Additional scenarios...]

---

## Current Implementation

[Optional: Details about how the requirement is currently implemented]

### Architecture

[Optional: Diagrams, code structure, component interactions]

---

## Testing Requirements

[How to verify the requirements are met]

---

## Dependencies

### Required
[Required dependencies]

### Optional
[Optional dependencies]

---

## Non-Functional Requirements

### Performance
### Reliability
### Maintainability
### Portability

---

## References

- **RFC 2119 - Key words for use in RFCs**: https://datatracker.ietf.org/doc/html/rfc2119
[Additional references...]

## Internal Documentation

[Links to related specs and documentation]

---

**License:** [License]
**Copyright:** [Copyright Info]
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
```

## Requirement Writing Guidelines

### Structure

Each requirement follows this pattern:

```markdown
### Requirement: [Clear, Actionable Name]

[1-2 sentence description using RFC 2119 keywords]

#### Scenario: [Specific Use Case]

- GIVEN [initial state and preconditions]
- WHEN [action or trigger]
- THEN [expected outcome]
- AND [additional expected outcomes]
```

### RFC 2119 Keywords Usage

- **MUST / SHALL**: Absolute requirement (use interchangeably)
- **SHOULD**: Recommended but not mandatory
- **MAY**: Optional / implementation choice
- **MUST NOT / SHALL NOT**: Absolute prohibition

### Writing Effective Scenarios

**Good Scenario** (Specific and Testable):
```markdown
#### Scenario: Cache Hit on Subsequent Runs

- GIVEN valid cache exists at ${XDG_CACHE_HOME}/dotfiles/bash_aliases.sh
- WHEN the shell starts
- THEN it SHALL check cache mtime against source files
- IF cache is fresh (newer than all sources)
- THEN it SHALL source cache directly without scanning filesystem
- AND startup SHALL be <100ms faster than uncached
```

**Bad Scenario** (Vague and Untestable):
```markdown
#### Scenario: Fast Loading

- GIVEN the system is running
- WHEN the user does something
- THEN it should be fast
```

### Scenario Best Practices

1. **Be Specific**: Use concrete values, paths, and conditions
2. **Be Testable**: Should be verifiable through manual or automated testing
3. **Show Context**: GIVEN clause provides all necessary preconditions
4. **Focus on Behavior**: Describe what happens, not how it's implemented
5. **Use AND for Multiple Outcomes**: Chain related expected behaviors
6. **Include Edge Cases**: Document error conditions and boundary cases

## Example Requirements

### Example 1: Discovery Requirement

```markdown
### Requirement: Dynamic Discovery

The system MUST automatically discover all keyboard shortcut documentation files
across the dotfiles repository without requiring manual registration.

#### Scenario: New Module Added

- GIVEN a developer creates a new module directory in dotfiles
- WHEN they create an executable `bash_shortcuts` file in that module
- THEN the shortcuts system SHALL automatically include it in the available
  topics list without code changes

#### Scenario: Module Removed

- GIVEN a module with `bash_shortcuts` exists in the system
- WHEN the module directory is deleted
- THEN the shortcuts system SHALL automatically remove it from available
  topics on next cache refresh
```

### Example 2: Performance Requirement

```markdown
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
```

## Workflow for Creating a Spec

### Step 1: Identify the System

What are you specifying?
- Component name
- Domain area
- Scope and boundaries

### Step 2: Define Key Capabilities

What are the 3-5 most important things this system does?

### Step 3: Write Requirements

For each capability:
1. State the requirement clearly with RFC 2119 keyword
2. Write 2-4 scenarios that demonstrate the requirement
3. Cover happy path, edge cases, and error conditions

### Step 4: Document Implementation

Optional but recommended:
- Architecture diagrams
- Code structure
- Integration points

### Step 5: Add Testing and Non-Functional Requirements

How do you verify it works? What about performance, reliability, etc.?

## Common Patterns

### Pattern: File Discovery

```markdown
### Requirement: Automatic Discovery

The system MUST automatically discover [files/components] without manual registration.

#### Scenario: New Item Added
- GIVEN a new [item] is created in [location]
- WHEN [discovery process runs]
- THEN the system SHALL automatically include it

#### Scenario: Item Removed
- GIVEN an existing [item] is removed
- WHEN [discovery process runs]
- THEN the system SHALL automatically exclude it
```

### Pattern: Caching

```markdown
### Requirement: Smart Caching

The system MUST cache [data] to minimize [expensive operation] while automatically
invalidating stale caches.

#### Scenario: Cache Hit
- GIVEN the cache exists and is fresh
- WHEN [operation occurs]
- THEN the system SHALL load from cache in <Xms

#### Scenario: Cache Miss
- GIVEN no cache exists or cache is stale
- WHEN [operation occurs]
- THEN the system SHALL regenerate cache

#### Scenario: Automatic Invalidation
- GIVEN a cached [data] exists
- WHEN source [data] is modified
- THEN the system SHALL detect stale cache and regenerate
```

### Pattern: Validation

```markdown
### Requirement: Input Validation

The system MUST validate [input] before [operation].

#### Scenario: Valid Input
- GIVEN valid [input]
- WHEN [operation] is performed
- THEN the system SHALL [succeed]

#### Scenario: Invalid Input
- GIVEN invalid [input]
- WHEN [operation] is attempted
- THEN the system SHALL reject with error message
- AND SHALL exit with status code 1
```

## Tips for Great Specs

### Do:
- ✅ Use RFC 2119 keywords consistently
- ✅ Write testable scenarios with concrete examples
- ✅ Include both success and failure cases
- ✅ Reference actual file paths, commands, and values
- ✅ Document dependencies and environment requirements
- ✅ Keep scenarios focused and atomic

### Don't:
- ❌ Mix implementation details into requirements
- ❌ Write vague scenarios that can't be tested
- ❌ Skip the RFC 2119 section
- ❌ Forget to specify error conditions
- ❌ Leave out preconditions in GIVEN clauses
- ❌ Use ambiguous language like "should work well"

## Spec Generation Process

When you use this skill, I will:

1. **Scan Existing Specs**
   - Check for `.openspec/` or `openspec/` directories
   - Analyze existing spec structure and patterns
   - Identify conventions used in your project

2. **Gather Information**
   - System name and domain
   - Version and status
   - Key capabilities
   - Main requirements

3. **Generate Spec File**
   - Create directory structure
   - Generate spec.md with proper formatting
   - Include RFC 2119 reference
   - Add template requirements with scenarios

4. **Guide You Through**
   - Suggest requirement patterns based on system type
   - Help structure scenarios effectively
   - Ensure consistency with existing specs

## Example: Invoking the Skill

```
User: /spec
or
User: Create a new OpenSpec for the hotkey system
```

I will then:
1. Scan for existing specs
2. Ask clarifying questions about the system
3. Generate a properly structured spec file
4. Guide you through adding requirements

## Related Skills

- **ADR Documentation** (`/adr`): For architectural decisions (different from OpenSpec)
- **Testing Strategy**: OpenSpec scenarios inform test cases
- **Project Structure**: Where to place OpenSpec files

## References

- **RFC 2119 - Key words for use in RFCs**: https://datatracker.ietf.org/doc/html/rfc2119
- **Gherkin Language**: https://cucumber.io/docs/gherkin/reference/
- **Behavior-Driven Development**: https://en.wikipedia.org/wiki/Behavior-driven_development
- **XDG Base Directory Specification**: https://specifications.freedesktop.org/basedir-spec/

---

**Note**: This skill follows the OpenSpec convention itself—it's meta-documentation for creating OpenSpecs!

---

**License:** Apache-2.0
**Copyright:** 2026 Ilja Heitlager
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
