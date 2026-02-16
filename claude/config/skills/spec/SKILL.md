---
name: spec
description: Use when the user asks to "browse specs", "view specifications", "create a spec", "list specs", "edit spec", "validate spec", "format spec", "check spec", "show requirements", "spec to issues", "convert spec", "create proposal", "propose changes", mentions "openspec", or discusses system specifications and requirements documentation.
version: 2.0.0
---

# OpenSpec Management Skill

## Overview

This skill helps you work with **OpenSpec** specifications—behavior-driven documentation that describes systems using RFC 2119 keywords and Given-When-Then scenarios. Supports creating, browsing, editing, and managing specs.

## Understanding OpenSpec: Main Specs vs. Delta Specs

OpenSpec uses two types of specifications to track system evolution:

### Main Specs (`.openspec/specs/`)

**Source of truth** describing your system's **current behavior** ("what is").

- Located in `.openspec/specs/NNN-name/spec.md`
- Use standard section headers: `## Requirements`
- Document what the system actually does NOW
- These are the permanent record of system capabilities

**Key Point**: Main specs use `## Requirements` (NOT lifecycle markers like ADDED/MODIFIED/REMOVED).

### Delta Specs (`.openspec/changes/`)

**Proposed modifications** describing **what's changing** relative to the current specs.

- Located in `.openspec/changes/[change-name]/specs/`
- Use lifecycle marker headers: `## ADDED Requirements`, `## MODIFIED Requirements`, `## REMOVED Requirements`
- Document changes being planned or developed
- Self-contained within change folders for parallel work

**Lifecycle Markers:**
- `## ADDED Requirements` = Brand new requirements being proposed
- `## MODIFIED Requirements` = Changes to existing requirements (note previous value)
- `## REMOVED Requirements` = Features being deprecated
- `## RENAMED Requirements` = Requirement name changes (if supported)

**Workflow**: Delta specs are created for new features → implemented → archived → merged into main specs (lifecycle markers removed during merge).

### The Critical Distinction

| Aspect | Main Specs | Delta Specs |
|--------|-----------|-------------|
| **Location** | `.openspec/specs/` | `.openspec/changes/[change-name]/specs/` |
| **Purpose** | Document current state | Document proposed changes |
| **Section Header** | `## Requirements` | `## ADDED Requirements`, etc. |
| **Lifecycle Markers** | ❌ Not used | ✅ Required |
| **Represents** | "What is" | "What's changing" |

### Why This Matters

**When creating specs:**
1. **Main specs** (finalized) → use `## Requirements`
2. **Delta specs** (proposals) → use `## ADDED Requirements`, `## MODIFIED Requirements`, etc.

**When merging changes:**
- ADDED sections get appended to main spec's Requirements
- MODIFIED sections replace corresponding requirements
- REMOVED sections delete requirements
- Lifecycle markers are stripped during merge

This distinction prevents confusion about what's current versus what's proposed.

**Official Sources**:
- [OpenSpec Concepts](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md)
- [OpenSpec Repository](https://github.com/Fission-AI/OpenSpec)
- [OpenSpec Getting Started](https://github.com/Fission-AI/OpenSpec/blob/main/docs/getting-started.md)

## When to Use This Skill

Invoke this skill when the user wants to:
- **Browse specs**: View existing specifications interactively
- **List specs**: See available specifications and their status
- **Create specs**: Generate new specification files
- **Edit specs**: Modify existing specifications
- **Validate specs**: Check if specs follow the proper structure
- **Format specs**: Reformat specs to match expected template
- **Convert specs**: Transform spec requirements into GitHub issues
- **View requirements**: Examine specific requirements and scenarios

## Available Commands

### Browse Specs Interactively

Use the `spec` command for interactive browsing with fzf:

```bash
spec                    # Interactive browser (default)
spec --raw              # Use bat instead of glow for rendering
```

**Features**:
- Auto-scroll to selected requirements
- `Ctrl-/`: Toggle zoom (60% ↔ 80% width)
- `Ctrl-D/Ctrl-U`: Scroll down/up in preview
- Line counter shows position in file
- Press Enter to view full spec

### List All Specs

```bash
spec list               # Show all specs with metadata and requirements
spec status             # Compact overview table
```

**Output includes**:
- Spec titles and file paths
- Domain, version, and status
- All requirements with line numbers
- Total requirement count

### View Spec Locations

OpenSpec uses a structured directory layout:

```
.openspec/
├── specs/                          # Main specs (current truth)
│   ├── 001-dotfiles-core/spec.md
│   ├── 002-dotfiles-caching/spec.md
│   └── 003-shortcuts-system/spec.md
├── adr/                            # Architectural Decision Records
│   ├── index.md                    # Summary table of all ADRs
│   └── 0001-<decision-name>.md    # Individual ADRs (zero-padded)
├── changes/                        # Delta specs (proposed changes)
│   ├── 001-feature-proposal/
│   │   ├── proposal.md             # Intent, scope, approach
│   │   ├── specs/                  # Delta specs with lifecycle markers
│   │   │   └── 002-caching/spec.md
│   │   └── tasks.md                # Implementation checklist
│   └── archive/                    # Completed changes
│       └── 001-feature-proposal/
├── project.md                      # Project context for AI/developers
├── AGENTS.md                       # AI assistant instructions
├── template.md                     # Spec template
├── validate.py                     # Local validator (copy of openspec)
├── rules.toml                      # Validation rules (optional)
└── README.md                       # OpenSpec documentation
```

### Project Context Files

**project.md**: Documents tech stack, architecture, patterns, and conventions
- Read this first when starting work on a project
- Provides context for making implementation decisions

**AGENTS.md**: Instructions for AI assistants
- Explains OpenSpec workflow
- Documents project-specific guidelines
- Shows how to use lifecycle markers

## Creating New Specs

When the user asks to create a spec, follow this workflow:

### Step 1: Gather Information

Ask the user:
1. **System name**: What are you specifying?
2. **Domain**: What area does this cover?
3. **Key capabilities**: What are the 3-5 main things it does?
4. **Current status**: Draft, Proposed, or Implemented?

### Step 2: Determine Directory Number

Check existing specs to find the next number:

```bash
ls ~/.dotfiles/.openspec/specs/
```

Use the next sequential number (e.g., if last is `003-`, use `004-`).

### Step 3: Create Directory and File

```bash
mkdir -p ~/.dotfiles/.openspec/specs/004-system-name
```

### Step 4: Generate Spec File

Create `spec.md` with this structure:

```markdown
# System Name Specification

**Domain:** [Domain Area]
**Version:** 1.0.0
**Status:** [Draft|Proposed|Implemented]
**Date:** YYYY-MM-DD

## Overview

[Brief description of the system and its purpose]

### Philosophy

- **Principle 1**: [Core design principle]
- **Principle 2**: [Another principle]

### Key Capabilities

- **Capability 1**: [What it does]
- **Capability 2**: [Another capability]

---

## RFC 2119 Keywords

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

---

## Requirements

### Requirement: [Requirement Name]

The system MUST [clear statement of requirement].

#### Scenario: [Happy Path]

- GIVEN [precondition and context]
- WHEN [action or trigger]
- THEN [expected outcome]
- AND [additional outcomes]

#### Scenario: [Edge Case]

- GIVEN [different precondition]
- WHEN [different action]
- THEN [expected behavior]

### Requirement: [Another Requirement]

[Continue with more requirements...]

---

## References

- **RFC 2119**: https://datatracker.ietf.org/doc/html/rfc2119

## Internal Documentation

[Links to related specs]

---

**License:** Apache-2.0
**Copyright:** YYYY [Author]
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
```

### Step 5: Verify

```bash
spec status             # Verify new spec appears
spec                    # Browse to new spec
```

## Editing Existing Specs

When the user wants to edit a spec:

1. **Find the spec**: Use `spec` or `spec list` to locate it
2. **Read the current content**: Use Read tool to load the file
3. **Make targeted edits**: Use Edit tool for specific changes
4. **Maintain structure**: Keep RFC 2119 keywords and scenario format
5. **Update version**: If requirements change significantly, bump version

## Linking Requirements to Implementation Code

OpenSpec supports **implementation traceability**—linking requirements to actual code. This enables tracking which requirements are implemented, finding code for requirements, and measuring coverage.

### Why Code References Matter

1. **Traceability**: Engineers can quickly locate implementation code
2. **Coverage Tracking**: `openspec coverage` command counts references
3. **Maintenance**: Know what code to update when requirements change
4. **Verification**: Code reviewers can verify requirements are implemented
5. **Documentation**: New contributors understand the architecture

### Method 1: Inline Implementation References

Add an **Implementation:** section to each requirement showing where it's implemented in code.

**Format:**
```markdown
### Requirement: Feature Name

The system MUST provide [capability].

**Implementation:**
- `path/to/file.ext` - Brief description of what this file does
- `path/to/file.ext::function_name` - Specific function implementation
- `path/to/file.ext::function_name()` (lines 42-58) - With line numbers
- `path/to/script` (lines 10-25) - Shell script section

#### Scenario: Happy Path
...
```

**Example from dotfiles specs:**
```markdown
### Requirement: Topic-Based Organization

The system MUST organize dotfiles into topic directories.

**Implementation:**
- `bash/bashrc.symlink` - Sources bash_aliases and bash_completion from all topics
- `bash/bash_profile.symlink` - Sources bash_env from all topics
- `local/bin/dot::list` (lines 82-94) - Lists topics with install.sh scripts
- `local/bin/dot::status` (lines 96-243) - Shows topic features (I=install, B=brew, etc.)
- `script/bootstrap::run_installers()` (lines 318-333) - Executes install.sh for each topic
```

**Syntax Rules:**
- Use **relative paths** from project root
- Format: `file::function` or `file::function()` for functions
- Format: `(lines X-Y)` for precise location (optional)
- Add brief description after `-` explaining what it does
- Group related files with bullet points

### Method 2: Metadata Section

Add a **Metadata** section at the end of the spec (after References, before License) with structured categories and **markdown links**.

**Why Markdown Links?**
The `openspec coverage` command parses markdown links in the format `[text](path)` to count:
- Source code references
- Test file references
- Internal documentation links

**Structure:**
```markdown
## Metadata

This section provides project-specific links for tracking and traceability.

### Implementation Files

**Category Name:**
- [path/to/file.ext](path/to/file.ext) - Description

**Another Category:**
- [path/to/other.ext](path/to/other.ext) - Description

### Test Coverage

**Unit Tests:**
- [tests/unit/test_feature.py](tests/unit/test_feature.py) - Feature unit tests

**Integration Tests:**
- [tests/integration/test_workflow.sh](tests/integration/test_workflow.sh) - End-to-end tests

**Manual Testing:**
- Test procedure 1: Steps to verify requirement
- Test procedure 2: Steps to verify edge cases

### Related Specifications

- [001-core-system](../001-core-system/spec.md) - Core system specification
- [002-related-feature](../002-related-feature/spec.md) - Related feature

---

**License:** Apache-2.0
**Copyright:** 2026 Author
```

**Example from spec 001:**
```markdown
## Metadata

This section provides project-specific links for tracking and traceability.

### Implementation Files

**Bootstrap Process:**
- [script/bootstrap](script/bootstrap) - Main bootstrap script with 8-step installation

**Package Management:**
- [local/bin/dot](local/bin/dot) - Homebrew package manager, topic installer
- [homebrew/brew_install.sh](homebrew/brew_install.sh) - Homebrew installation

**Shell Integration:**
- [bash/bash_profile.symlink](bash/bash_profile.symlink) - Login shell init
- [bash/bashrc.symlink](bash/bashrc.symlink) - Interactive shell init

### Test Coverage

**Manual Testing:**
- Bootstrap idempotency: Run `script/bootstrap` twice, verify no errors
- Topic discovery: Add new topic with bash_aliases, verify auto-discovery

### Related Specifications

- [002-dotfiles-caching](../002-dotfiles-caching/spec.md) - Caching system
- [003-shortcuts-system](../003-shortcuts-system/spec.md) - Shortcuts
```

### Which Method to Use?

**Use Inline Implementation** when:
- Requirement maps to specific functions/files
- You want direct traceability at requirement level
- Code is well-organized and easy to reference

**Use Metadata Section** when:
- You want a consolidated reference list
- Multiple requirements share the same files
- You want to track test coverage separately
- You want structured categories for clarity

**Use Both** when:
- Inline for specific requirement-to-code mapping
- Metadata for comprehensive file list and test coverage

### Coverage Tracking

The `openspec coverage` command parses markdown links to categorize and count references:

```bash
openspec coverage

# Output:
                      Reference Coverage
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━┳━━━━━━━━┳━━━━━━━┓
┃ Spec                       ┃ ADRs ┃ Tests ┃ Source ┃ Total ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━╇━━━━━━━━╇━━━━━━━┩
│ 001-dotfiles-core          │    0 │     0 │      5 │     5 │
│ 002-dotfiles-caching       │    0 │     0 │      4 │     4 │
│ 003-shortcuts-system       │    0 │     0 │      1 │     1 │
└────────────────────────────┴──────┴───────┴────────┴───────┘
```

**Reference Categorization (from actual code):**
- **ADRs**: Links containing `/adr/` or starting with `adr/` (Architectural Decision Records)
- **Tests**: Links containing `/test` or starting with `test` (test files, spec directories)
- **Source**: Links to source code files:
  - Extensions: `.py`, `.js`, `.ts`, `.java`, `.go`, `.rs`, `.sh`, `.bash`, `.symlink`
  - Paths: `script/`, `/bin/`, `bin/`, `/brew_install`
- **External**: Links starting with `http://`, `https://`, `ftp://` (not counted in table)
- **Internal**: Other links like `.md` files, internal docs (not counted in table)

**Note**: Only ADRs, Tests, and Source appear in the coverage table. External and internal links are parsed but not displayed.

### Best Practices

**DO:**
- ✅ Use relative paths from project root
- ✅ Use markdown link format: `[text](path)`
- ✅ Group files by category in Metadata section
- ✅ Include line numbers for large files
- ✅ Update references when code moves
- ✅ Link to tests for each requirement

**DON'T:**
- ❌ Use absolute paths (`/Users/name/project/file.py`)
- ❌ Link to external URLs for internal code
- ❌ Forget to update links when refactoring
- ❌ Include implementation details in requirement text (use Implementation section)

### Example: Adding Traceability to Existing Spec

**Before:**
```markdown
### Requirement: User Authentication

The system MUST authenticate users via OAuth.

#### Scenario: Successful Login
- GIVEN a valid OAuth token
- WHEN user attempts login
- THEN grant access to protected resources
```

**After:**
```markdown
### Requirement: User Authentication

The system MUST authenticate users via OAuth.

**Implementation:**
- `src/auth/oauth.py::OAuthHandler` (lines 45-120) - OAuth flow implementation
- `src/auth/session.py::create_session()` (lines 23-35) - Session creation
- `src/middleware/auth.py::require_auth` (lines 10-18) - Auth middleware decorator

#### Scenario: Successful Login
- GIVEN a valid OAuth token
- WHEN user attempts login
- THEN grant access to protected resources
```

**And at end of spec:**
```markdown
## Metadata

### Implementation Files

**Authentication:**
- [src/auth/oauth.py](src/auth/oauth.py) - OAuth provider integration
- [src/auth/session.py](src/auth/session.py) - Session management
- [src/middleware/auth.py](src/middleware/auth.py) - Auth middleware

### Test Coverage

**Unit Tests:**
- [tests/unit/test_oauth.py](tests/unit/test_oauth.py) - OAuth handler tests
- [tests/unit/test_session.py](tests/unit/test_session.py) - Session tests

**Integration Tests:**
- [tests/integration/test_auth_flow.py](tests/integration/test_auth_flow.py) - End-to-end auth
```

## Creating Proposals for Changes

When the user wants to propose changes to existing specs or add new features, use the proposal workflow:

### Proposal Workflow

1. **Create Change Directory**:
   ```bash
   mkdir -p ~/.dotfiles/.openspec/changes/NNN-proposal-name/specs
   ```

2. **Create proposal.md**:
   - **Intent**: Why is this change needed? What problem does it solve?
   - **Scope**: What's in scope vs. out of scope?
   - **Approach**: How will this be implemented?
   - **Alternatives**: What other approaches were considered?
   - **Impact**: Breaking changes, dependencies, testing strategy

3. **Create Delta Specs** with lifecycle markers:
   - Use `## ADDED Requirements` for brand new requirements
   - Use `## MODIFIED Requirements` for changes to existing requirements
   - Use `## REMOVED Requirements` for deprecating features
   - Use `## RENAMED Requirements` for renaming requirements

4. **Create tasks.md**:
   - Implementation checklist
   - Pre-implementation, implementation, testing, review phases
   - Track progress as tasks are completed

### Example Delta Spec Structure

```markdown
# Feature Name (Delta)

**Domain:** [Domain]
**Version:** [Version]
**Status:** Proposed
**Date:** YYYY-MM-DD

## Overview

This delta spec proposes [summary of changes].

## RFC 2119 Keywords

[Standard boilerplate]

## ADDED Requirements

### Requirement: New Feature

The system MUST support [new functionality].

#### Scenario: New Behavior
- GIVEN [context]
- WHEN [action]
- THEN [expected new behavior]

## MODIFIED Requirements

### Requirement: Existing Feature (Modified)

The system MUST support [updated functionality].

**Changes from v1.0:**
- Added: [What's new]
- Changed: [What changed]
- Removed: [What was removed]

#### Scenario: Updated Behavior (NEW)
- GIVEN [context]
- WHEN [action]
- THEN [new expected behavior]

## REMOVED Requirements

### Requirement: Deprecated Feature

This requirement is being removed because [rationale].

**Migration path**: [How to adapt to removal]
```

### When to Use Proposals

- Adding significant new features
- Making breaking changes
- Removing functionality
- Major refactoring that affects behavior
- Any change that requires team discussion/approval

For small bug fixes or minor improvements, you can update main specs directly.

## Validating Specs

When the user asks to validate a spec, check for required sections and proper structure.

### Required Sections

Every main spec MUST include:

1. **Title** - `# [System Name] Specification`
2. **Frontmatter** - Domain, Version, Status, Date (Owner is recommended)
3. **Overview** - Brief description
4. **RFC 2119 Keywords** - Standard compliance statement
5. **Requirements** - At least one requirement (note: use "Requirements", NOT "ADDED Requirements" in main specs)

### Validation Checklist

Run through this checklist and report findings:

```markdown
✅ Has proper title format
✅ Has frontmatter (Domain, Version, Status, Date required; Owner recommended)
✅ Has Overview section
✅ Has Philosophy subsection (recommended)
✅ Has Key Capabilities subsection (recommended)
✅ Has RFC 2119 Keywords section
✅ Has Requirements section (NOT "ADDED Requirements" for main specs)
✅ Has at least one Requirement
✅ Each requirement has at least one Scenario
✅ Scenarios use proper Given-When-Then format
✅ Uses RFC 2119 keywords (MUST, SHALL, SHOULD, MAY)
✅ Has References section (recommended)
✅ Has license/copyright info (recommended)
```

### Validation Example

```
User: "Validate the caching spec"

Claude: I'll validate the dotfiles caching spec...

✅ Title: "Dotfiles Caching System Specification"
✅ Frontmatter: All fields present (Domain, Version, Status, Date)
✅ Overview: Present with Philosophy and Key Capabilities
✅ RFC 2119 Keywords: Present
✅ Requirements: 4 requirements found
✅ Scenarios: All requirements have scenarios
✅ Given-When-Then: Proper format used
✅ RFC 2119 Keywords: Used correctly (MUST, SHALL)
✅ References: Present
✅ License: Apache-2.0

Summary: Spec is valid! No issues found.
```

### Common Issues

Report these if found:

❌ **Missing RFC 2119 section**: Required for standards compliance
❌ **Wrong section header**: Using "## ADDED Requirements" in main specs (should be "## Requirements")
❌ **Vague scenarios**: Missing GIVEN/WHEN/THEN or too abstract
❌ **No requirements**: Spec must have at least one requirement
❌ **Missing frontmatter**: Need Domain, Version, Status, Date (Owner recommended)
❌ **Weak keywords**: Using "should" instead of RFC 2119 SHOULD
❌ **No scenarios**: Requirements must have concrete examples
❌ **Implementation details**: Scenarios should describe behavior, not code

## Formatting Specs

When the user asks to format a spec, restructure it to match the template.

### Formatting Process

1. **Read the current spec**: Load the file completely
2. **Identify sections**: Find existing content
3. **Reorganize**: Match standard template order
4. **Add missing sections**: Insert template sections with placeholders
5. **Preserve content**: Keep all existing text, just reorganize
6. **Fix formatting**: Ensure proper markdown structure

### Standard Section Order (Main Specs)

```markdown
1. Title (# System Name Specification)
2. Frontmatter (Domain, Version, Status, Date)
3. Overview
   - Brief description
   - Philosophy (subsection)
   - Key Capabilities (subsection)
4. RFC 2119 Keywords (standard boilerplate)
5. Requirements
   - Multiple requirements
   - Each with scenarios
6. Current Implementation (optional)
7. Testing Requirements (optional)
8. Dependencies (optional)
9. Non-Functional Requirements (optional)
10. References
11. Internal Documentation
12. License/Copyright
```

**Note**: For delta specs in `.openspec/changes/`, use lifecycle markers: `## ADDED Requirements`, `## MODIFIED Requirements`, `## REMOVED Requirements`

### Formatting Example

```
User: "Format the hotkey spec"

Claude: I'll reformat the hotkey spec to match the standard template...

Changes made:
- Moved Overview before RFC 2119 section
- Added missing Philosophy subsection
- Added Key Capabilities subsection
- Reorganized requirements into Requirements section
- Added RFC 2119 Keywords section (was missing)
- Added References section
- Added license/copyright footer
- Standardized requirement headers
- Formatted scenarios with proper indentation

The spec now follows the standard OpenSpec structure.
```

### Formatting Guidelines

**Do**:
- ✅ Preserve all existing content
- ✅ Add section dividers (`---`)
- ✅ Standardize heading levels (## for sections, ### for requirements)
- ✅ Format scenarios with proper bullets and indentation
- ✅ Add missing required sections with `[TODO]` placeholders
- ✅ Keep line length reasonable (~80-100 chars for text)

**Don't**:
- ❌ Delete or modify existing requirements
- ❌ Change the meaning of scenarios
- ❌ Remove implementation details (move to proper section instead)
- ❌ Alter RFC 2119 keywords
- ❌ Remove references or links

## Converting Specs to Issues

When the user wants to create GitHub issues from spec requirements:

### Approach 1: One Issue Per Requirement

```bash
# Extract requirements from spec
grep "^### Requirement:" spec.md

# For each requirement, create issue with:
# - Title: Requirement name
# - Body: Requirement description + scenarios
# - Labels: spec, requirement
```

### Approach 2: One Issue Per Scenario

For complex requirements, create separate issues per scenario:

```bash
# Title: [Requirement Name] - [Scenario Name]
# Body: Given-When-Then scenario
# Labels: spec, scenario, requirement-name
```

### Using gh CLI

```bash
gh issue create \
  --title "Requirement: [Name]" \
  --body "[Full requirement text with scenarios]" \
  --label "spec,requirement"
```

## Writing Effective Requirements

### Requirement Format

Requirements support both numbered and unnumbered formats:

**Unnumbered (standard):**
```markdown
### Requirement: Topic-Based Organization
```

**Numbered (optional):**
```markdown
### Requirement 8: Serialization Methods
### Requirement 10: Validation Rules
```

Use numbered requirements when:
- You need explicit ordering
- Requirements will be referenced by number
- Multiple specs need aligned numbering

### Formatting Rules

**❌ PROHIBITED:**
- **NO color codes** - No ANSI escape sequences, no `\033[`, no terminal colors
- **NO HTML** - No `<span>`, `<div>`, or any HTML tags
- **NO emoji in requirements** - Keep formal and searchable
- **NO special characters** - Stick to markdown syntax

**✅ ALLOWED:**
- Plain markdown formatting (`**bold**`, `*italic*`, `` `code` ``)
- Standard markdown lists, headings, links
- Code blocks with language specifiers
- Numbered requirement format (`### Requirement 8:`)

### RFC 2119 Keywords

- **MUST/SHALL**: Absolute requirement (mandatory)
- **SHOULD**: Recommended but not mandatory
- **MAY**: Optional feature or behavior
- **MUST NOT/SHALL NOT**: Absolute prohibition

### Scenario Best Practices

✅ **Good Scenario** (Specific and testable):
```markdown
#### Scenario: Cache Hit on Subsequent Shell Start

- GIVEN valid cache exists at ${XDG_CACHE_HOME}/dotfiles/bash_aliases.sh
- AND cache mtime is newer than all source files
- WHEN a new bash shell starts
- THEN it SHALL source the cache directly without filesystem scanning
- AND shell startup SHALL complete in <100ms
```

❌ **Bad Scenario** (Vague and untestable):
```markdown
#### Scenario: Fast Loading

- GIVEN the system is running
- WHEN user does something
- THEN it should be fast
```

### Key Principles

1. **Be Specific**: Use concrete values, paths, and conditions
2. **Be Testable**: Should be verifiable through testing
3. **Show Context**: GIVEN clause provides all preconditions
4. **Focus on Behavior**: Describe what happens, not implementation
5. **Include Edge Cases**: Document error conditions and boundaries

## Common Patterns

### Pattern: Discovery

```markdown
### Requirement: Automatic Discovery

The system MUST automatically discover [items] without manual registration.

#### Scenario: New Item Added
- GIVEN a new [item] is created
- WHEN [discovery runs]
- THEN system SHALL include it automatically

#### Scenario: Item Removed
- GIVEN [item] is deleted
- WHEN [discovery runs]
- THEN system SHALL exclude it automatically
```

### Pattern: Caching

```markdown
### Requirement 5: Smart Caching

The system MUST cache [data] with automatic invalidation.

#### Scenario: Cache Hit
- GIVEN cache exists and is fresh
- WHEN [operation occurs]
- THEN load from cache in <Xms

#### Scenario: Automatic Invalidation
- GIVEN cached data exists
- WHEN source data changes
- THEN system SHALL regenerate cache
```

### Pattern: Numbered Requirements

Use numbered requirements for explicit ordering:

```markdown
### Requirement 1: Data Input
The system MUST accept input from multiple sources.

### Requirement 2: Data Validation
The system MUST validate input before processing (depends on Req 1).

### Requirement 3: Data Storage
The system MUST persist validated data (depends on Req 2).
```

## Integration with Workflow

### After Creating a Spec

1. **Browse it**: `spec` to verify it appears
2. **Commit it**: Add to git with `/commit`
3. **Reference it**: Link from CLAUDE.md if relevant

### Spec-Driven Development

1. **Write spec first**: Define requirements before implementation
2. **Implement features**: Code against spec requirements
3. **Update status**: Change from Draft → Implemented when done
4. **Keep in sync**: Update spec when behavior changes

## Quick Reference

```bash
# Browse specs interactively
spec

# List all specs with details
spec list

# Show compact overview
spec status

# Create new spec (use /spec skill)
/spec create [system-name]

# Validate a spec (use /spec skill)
/spec validate [spec-file]

# Format a spec (use /spec skill)
/spec format [spec-file]

# Find spec directory
cd ~/.dotfiles/.openspec/specs/

# Count requirements across all specs (both formats)
grep -r "^### Requirement" ~/.dotfiles/.openspec/specs/ | wc -l

# Check if spec has RFC 2119 section
grep -l "RFC 2119 Keywords" ~/.dotfiles/.openspec/specs/*/spec.md
```

## Example Workflow

**User**: "Create a spec for the hotkey system"

**Claude**:
1. Ask about system details (name, domain, capabilities)
2. Check next available number: `ls ~/.dotfiles/.openspec/specs/`
3. Create directory: `mkdir -p .openspec/specs/004-hotkey-system/`
4. Generate spec.md with proper structure
5. Prompt user to add specific requirements
6. Run `spec status` to verify

**User**: "Show me the caching spec"

**Claude**:
1. Run `spec` to open interactive browser
2. Or read the file directly: `Read ~/.dotfiles/.openspec/specs/002-dotfiles-caching/spec.md`

**User**: "Validate the shortcuts spec"

**Claude**:
1. Read the spec file
2. Check for all required sections
3. Verify RFC 2119 compliance
4. Check requirement structure
5. Report validation results with ✅/❌

**User**: "Format the hotkey spec"

**Claude**:
1. Read the current spec
2. Identify existing sections
3. Reorganize to match standard template
4. Add missing sections with placeholders
5. Preserve all existing content
6. Write the reformatted spec

**User**: "Convert the caching spec requirements to issues"

**Claude**:
1. Read the spec file
2. Extract all requirements (grep for `### Requirement`)
3. For each requirement, create issue with `gh issue create`
4. Include scenarios in issue body

## Important Guidelines

When creating or editing specs, **ALWAYS follow these rules**:

### ✅ DO:
- Use plain markdown formatting only
- Use numbered requirements when ordering matters (`### Requirement 8:`)
- Keep text clean and searchable
- Use RFC 2119 keywords (MUST, SHALL, SHOULD, MAY)
- Write specific, testable scenarios with Given-When-Then

### ❌ DON'T:
- **NO color codes** - No `\033[31m`, no ANSI escape sequences
- **NO HTML** - No `<span style="color:red">`, no HTML tags
- **NO emoji in requirements** - Keep professional and greppable
- **NO special terminal formatting** - Plain markdown only
- **NO implementation details** - Focus on behavior, not code

These rules ensure specs remain:
- **Searchable** with grep/ripgrep
- **Portable** across editors and viewers
- **Version-control friendly** with clean diffs
- **Professional** and formal in tone

---

**License:** Apache-2.0
**Copyright:** 2026 Ilja Heitlager
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
