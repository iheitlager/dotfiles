# OpenSpec Specification Format

**Domain:** Software Development Process
**Version:** 1.0.0
**Status:** Implemented
**Date:** 2026-02-08
**Owner:** Ilja Heitlager

## Overview

OpenSpec is a structured specification format for documenting system requirements with built-in validation, traceability, and test coverage tracking. It provides a standardized way to capture requirements, scenarios, and acceptance criteria in Markdown format with automated validation tools.

### Philosophy

- **Behavior-Driven Documentation**: Requirements are expressed as scenarios with Given-When-Then format, making them immediately testable and unambiguous
- **Traceability First**: Every requirement can be linked to ADRs, tests, and source code, ensuring documentation stays synchronized with implementation
- **Validation-Aware**: Specs are validated automatically using configurable rules, catching documentation issues early
- **Developer-Friendly**: Plain Markdown format stored in version control, reviewed alongside code changes
- **Progressive Enhancement**: Start simple with basic requirements, add metadata and traceability as projects mature

### Key Capabilities

- **Structured Requirements**: RFC 2119 keywords (MUST/SHALL/SHOULD) with testable scenarios
- **Automated Validation**: Python-based validator checks metadata, sections, requirements, and references
- **Reference Integrity**: Validates links to ADRs, tests, source files with project-root-relative paths
- **Configurable Rules**: TOML-based rules engine with strict/standard/lenient profiles
- **Coverage Tracking**: Track which requirements are covered by tests and documentation
- **CI/CD Integration**: JSON output format for automated validation pipelines
- **Project Initialization**: Quick setup with templates and local validator copies

---

## RFC 2119 Keywords

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

---

## Requirements

### Requirement: Structured Specification Format

OpenSpec specifications MUST follow a defined Markdown structure with metadata frontmatter and required sections.

#### Scenario: Valid Spec with All Required Sections

- GIVEN a specification file following the OpenSpec template
- WHEN the validator parses the file
- THEN it MUST extract metadata from the frontmatter (Domain, Version, Status, Date)
- AND it MUST identify all required sections (Overview, RFC 2119 Keywords, ADDED Requirements)
- AND validation MUST pass without errors

#### Scenario: Missing Required Metadata

- GIVEN a specification file missing required metadata fields
- WHEN the validator runs
- THEN it MUST report ERROR-level issues for each missing required field
- AND it MUST report WARNING-level issues for missing recommended fields

#### Scenario: Missing Required Sections

- GIVEN a specification file missing required sections
- WHEN the validator runs
- THEN it MUST report ERROR-level issues for each missing required section
- AND it MUST report WARNING-level issues for missing recommended sections

### Requirement: RFC 2119 Requirement Statements

Each requirement MUST include an RFC 2119 keyword (MUST, SHALL, SHOULD, MAY) to indicate obligation level.

#### Scenario: Requirement with RFC 2119 Keyword

- GIVEN a requirement statement containing "MUST", "SHALL", or "SHOULD"
- WHEN the validator checks the requirement
- THEN it MUST recognize the requirement as properly formatted
- AND validation MUST pass for that requirement

#### Scenario: Requirement Missing RFC 2119 Keyword

- GIVEN a requirement statement without RFC 2119 keywords
- WHEN the validator checks the requirement
- THEN it MUST report a WARNING-level issue
- AND it SHOULD suggest adding an RFC 2119 keyword

### Requirement: Given-When-Then Scenarios

Each requirement SHOULD include one or more scenarios in Given-When-Then format for testability.

#### Scenario: Complete Given-When-Then Scenario

- GIVEN a requirement with a scenario section
- WHEN the scenario includes GIVEN, WHEN, and THEN steps
- THEN the validator MUST recognize it as complete
- AND validation MUST pass for that scenario

#### Scenario: Incomplete Scenario

- GIVEN a requirement with a scenario missing GIVEN, WHEN, or THEN steps
- WHEN the validator checks the scenario
- THEN it MUST report an INFO-level issue indicating incomplete scenario
- AND it SHOULD specify which steps are missing

#### Scenario: Requirement Without Scenarios

- GIVEN a requirement with no scenario sections
- WHEN the validator runs with must_have_scenarios enabled
- THEN it MUST report a WARNING-level issue
- AND validation SHOULD suggest adding at least one scenario

### Requirement: Project-Root-Relative References

All file references in specifications MUST use project-root-relative paths, not spec-relative paths.

#### Scenario: Project-Root-Relative ADR Link

- GIVEN a specification with a link to `docs/adr/001-decision.md`
- WHEN the validator resolves the reference with --project-folder set
- THEN it MUST resolve the path from the project root
- AND it MUST check if the file exists
- AND it MUST report a WARNING if the file is not found

#### Scenario: External URL Reference

- GIVEN a specification with an HTTPS URL reference
- WHEN the validator checks the reference
- THEN it MUST classify it as 'external'
- AND it MUST skip existence checking
- AND validation MUST pass

#### Scenario: Relative Path with ../../

- GIVEN a specification with a reference like `../../docs/file.md`
- WHEN the validator checks the reference
- THEN it MAY attempt to resolve it for backward compatibility
- AND it SHOULD warn that project-root-relative paths are preferred

### Requirement: Validation Profiles

The validator MUST support configurable validation profiles (strict, standard, lenient) via TOML rules.

#### Scenario: Standard Profile (Default)

- GIVEN no rules.toml file exists
- WHEN the validator runs
- THEN it MUST use the "standard" profile with default rules
- AND it MUST require Domain, Version, Status, Date metadata
- AND it MUST require Overview, RFC 2119 Keywords, ADDED Requirements sections

#### Scenario: Strict Profile

- GIVEN rules.toml with profile = "strict"
- WHEN the validator runs
- THEN it MUST require all recommended fields (including Owner)
- AND it MUST require all recommended sections
- AND it MUST fail on warnings (fail_on_warning = true)

#### Scenario: Lenient Profile

- GIVEN rules.toml with profile = "lenient"
- WHEN the validator runs
- THEN it MUST require only minimal fields (Domain, Status)
- AND it MUST require only minimal sections (Overview, ADDED Requirements)
- AND it MAY not require scenarios for requirements

#### Scenario: Custom Project Rules

- GIVEN a rules.toml file with custom validation rules
- WHEN the validator loads rules
- THEN it MUST merge project rules with defaults
- AND project rules MUST override default rules
- AND the validator MUST use the merged ruleset

### Requirement: Project Initialization

The openspec init command MUST create a complete OpenSpec directory structure for new projects.

#### Scenario: Initialize in Empty Project

- GIVEN an empty project directory
- WHEN running `openspec init`
- THEN it MUST create `.openspec/` directory
- AND it MUST create `.openspec/specs/` subdirectory
- AND it MUST copy template.md to `.openspec/template.md`
- AND it MUST create `.openspec/validate.py` (copy of openspec)
- AND it MUST create `.openspec/rules.toml.example`
- AND it MUST create `.openspec/README.md`
- AND all files MUST be created successfully

#### Scenario: Initialize with Custom Directory Name

- GIVEN a project directory
- WHEN running `openspec init --dir custom-specs`
- THEN it MUST create `custom-specs/` directory
- AND it MUST follow the same structure as `.openspec/`

#### Scenario: Initialize Existing Directory

- GIVEN `.openspec/` already exists
- WHEN running `openspec init`
- THEN it MUST not fail
- AND it MUST update or overwrite existing files
- AND it MUST preserve existing specs in `specs/` subdirectory

### Requirement: Template Exclusion

The validator MUST exclude template files from validation scans.

#### Scenario: Template.md in Spec Directory

- GIVEN `.openspec/template.md` exists
- WHEN running `openspec validate`
- THEN it MUST not include template.md in validation results
- AND it MUST only validate files in `specs/` subdirectory

#### Scenario: Files with "template" in Name

- GIVEN a file named `_template.spec.md` or `template-example.md`
- WHEN the validator scans for specs
- THEN it MUST exclude files with "template" in lowercase name
- AND it MUST exclude files in directories named "template"

### Requirement: Multiple Output Formats

The validator MUST support both terminal (human-readable) and JSON (machine-readable) output formats.

#### Scenario: Terminal Output (Default)

- GIVEN validation results with errors and warnings
- WHEN running `openspec validate` without --format flag
- THEN it MUST display results using rich terminal formatting
- AND it MUST show spec status (PASSED/WARNINGS/FAILED) with colors
- AND it MUST show summary with error/warning counts
- AND output MUST be human-readable

#### Scenario: JSON Output for CI/CD

- GIVEN validation results
- WHEN running `openspec validate --format json`
- THEN it MUST output valid JSON to stdout
- AND JSON MUST include all validation results
- AND JSON MUST include summary statistics
- AND JSON MUST be parseable by CI/CD tools

#### Scenario: Exit Codes

- GIVEN validation completes
- WHEN specs have errors
- THEN the validator MUST exit with code 1
- WHEN specs have warnings and --fail-on-warning is set
- THEN the validator MUST exit with code 2
- WHEN all specs are valid
- THEN the validator MUST exit with code 0

### Requirement: Statistics and Coverage

The validator MUST provide commands to analyze specifications and track coverage.

#### Scenario: Statistics Command

- GIVEN multiple specification files
- WHEN running `openspec stats`
- THEN it MUST display total specs, requirements, scenarios, and references
- AND it MUST show specs grouped by status
- AND it MUST calculate totals across all specs

#### Scenario: Rules Display

- GIVEN active validation rules
- WHEN running `openspec rules show`
- THEN it MUST display the current profile name
- AND it MUST list required metadata fields
- AND it MUST list required sections
- AND output MUST be human-readable

### Requirement: Change Directory Support

The system MUST support delta specs in `.openspec/changes/` directory for tracking proposed modifications.

#### Scenario: Delta Spec Discovery

- GIVEN a delta spec exists in `.openspec/changes/001-feature/specs/`
- WHEN openspec discovers specs
- THEN it SHALL include the delta spec
- AND it SHALL mark it with spec_type=delta
- AND it SHALL extract the change_id from the directory name

#### Scenario: Delta Spec Validation

- GIVEN a delta spec with lifecycle markers
- WHEN openspec validates it
- THEN it SHALL validate metadata and structure
- AND it SHALL check that at least one lifecycle marker exists
- AND it SHALL not require "ADDED Requirements" section (other markers allowed)

### Requirement: Lifecycle Markers

Delta specs MUST use lifecycle markers to indicate the nature of changes to requirements.

#### Scenario: ADDED Requirements

- GIVEN a delta spec with "## ADDED Requirements" section
- WHEN the validator parses it
- THEN it SHALL extract all new requirements
- AND each requirement SHALL have scenarios
- AND requirements SHALL follow normal validation rules

#### Scenario: MODIFIED Requirements

- GIVEN a delta spec with "## MODIFIED Requirements" section
- WHEN the validator parses it
- THEN it SHALL extract modified requirements
- AND requirements SHALL indicate what changed from the original

#### Scenario: REMOVED Requirements

- GIVEN a delta spec with "## REMOVED Requirements" section
- WHEN the validator parses it
- THEN it SHALL list requirements being deprecated
- AND SHALL include rationale for removal

#### Scenario: RENAMED Requirements

- GIVEN a delta spec with "## RENAMED Requirements" section
- WHEN the validator parses it
- THEN it SHALL map old names to new names
- AND SHALL preserve requirement content

#### Scenario: No Lifecycle Markers

- GIVEN a delta spec with no lifecycle marker sections
- WHEN the validator runs
- THEN it MUST report an ERROR
- AND it MUST indicate that delta specs require at least one lifecycle marker

### Requirement: Proposal Workflow

The system MUST support a proposal-based change workflow with structured artifacts.

#### Scenario: Complete Change Structure

- GIVEN a change directory `.openspec/changes/001-feature/`
- WHEN it contains proposal.md, specs/, and tasks.md
- THEN it represents a complete change proposal
- AND proposal.md SHALL document intent, scope, and approach
- AND specs/ SHALL contain delta specs with lifecycle markers
- AND tasks.md SHALL provide implementation checklist

#### Scenario: Proposal Template

- GIVEN openspec init has run
- WHEN a developer creates a new change manually
- THEN they SHALL follow the proposal template structure
- AND include Intent, Scope, Approach sections
- AND include Alternatives Considered
- AND include Impact Analysis

### Requirement: Project Context Documentation

The system MUST support project.md and AGENTS.md for providing context to developers and AI assistants.

#### Scenario: Project Context (project.md)

- GIVEN openspec init creates `.openspec/project.md`
- WHEN a developer or AI reads it
- THEN it SHALL document tech stack, architecture, and conventions
- AND it SHALL include project-specific patterns
- AND it SHALL guide implementation decisions

#### Scenario: AI Agent Instructions (AGENTS.md)

- GIVEN openspec init creates `.openspec/AGENTS.md`
- WHEN an AI assistant works with the project
- THEN it SHALL understand OpenSpec workflow
- AND it SHALL follow project-specific guidelines
- AND it SHALL use correct lifecycle markers for changes

#### Scenario: Context Consistency

- GIVEN project.md and AGENTS.md exist
- WHEN they're updated
- THEN they SHALL remain consistent with each other
- AND they SHALL reflect actual project structure

---

## Current Implementation

### Architecture

OpenSpec is implemented as two complementary tools:

1. **spec** (Bash): Interactive spec browser using fzf for navigation and basic validation
2. **openspec** (Python): Advanced validator with structured validation, reference checking, and rules engine

```
OpenSpec System Architecture:

┌─────────────────────────────────────────────────────┐
│                    User                              │
└──────────────┬─────────────────┬────────────────────┘
               │                 │
       ┌───────▼────────┐  ┌────▼─────────┐
       │ spec (Bash)    │  │ openspec (Python)│
       │ - Interactive  │  │ - Validation  │
       │ - Quick browse │  │ - CI/CD       │
       │ - fzf UI       │  │ - Analysis    │
       └───────┬────────┘  └────┬─────────┘
               │                │
    ┌──────────▼────────────────▼──────────┐
    │      .openspec/ Directory             │
    │  ├── specs/                           │
    │  │   └── 001-feature/spec.md          │
    │  ├── changes/                         │
    │  │   ├── 001-proposal/                │
    │  │   │   ├── proposal.md              │
    │  │   │   ├── specs/                   │
    │  │   │   │   └── 001-feature/spec.md  │
    │  │   │   └── tasks.md                 │
    │  │   └── archive/                     │
    │  ├── project.md                       │
    │  ├── AGENTS.md                        │
    │  ├── template.md                      │
    │  ├── validate.py (local copy)        │
    │  ├── rules.toml (optional)           │
    │  └── README.md                        │
    └───────────────────────────────────────┘
```

### Key Components

#### openspec Python Validator

- **Single File**: `local/bin/openspec` (~2150 LOC)
- **Dependencies**: Uses PEP 723 inline dependencies (rich library)
- **Execution**: Run with `uv run --script openspec` for automatic dependency management

#### Validation Pipeline

1. **Spec Discovery**: Find all `spec.md` files in specs/, changes/, and changes/archive/ (configurable)
2. **Type Detection**: Classify specs as main, delta, or archive based on location
3. **Parsing**: Extract metadata, sections, requirements, scenarios, references, and lifecycle markers
4. **Rule Loading**: Load default rules, merge with project rules.toml, apply profile
5. **Validation**: Run metadata, section, requirement, reference, and lifecycle validators
6. **Reporting**: Format results as terminal output or JSON

#### Directory Patterns

OpenSpec supports three directory types:

1. **Main Specs**: `.openspec/specs/NNN-feature-name/spec.md` - Current system truth
2. **Delta Specs**: `.openspec/changes/NNN-proposal/specs/NNN-feature/spec.md` - Proposed changes
3. **Archive**: `.openspec/changes/archive/NNN-proposal/` - Completed changes

Within each, files can use:
- **Directory-based**: `001-feature-name/spec.md`
- **Named files**: `category/feature.spec.md`

#### Change Management Workflow

1. **Create Proposal**: Create `changes/NNN-name/` with proposal.md, specs/, and tasks.md
2. **Develop**: Implement changes following tasks.md checklist
3. **Merge**: Integrate delta specs into main specs (manual or automated)
4. **Archive**: Move completed change to `changes/archive/`

---

## Testing Requirements

### Manual Testing

- Create test project with `openspec init`
- Create sample spec from template
- Validate with different profiles (standard, strict, lenient)
- Test reference integrity with real and broken links
- Test JSON output format

### Automated Testing

- Unit tests for parsing functions (extract_metadata, parse_sections)
- Unit tests for validation functions (validate_metadata, validate_requirements)
- Integration tests with fixture specs (valid, invalid, missing-metadata)
- CI/CD integration tests with JSON output parsing

### Acceptance Criteria

- All commands execute without Python errors
- Validation detects missing metadata and broken references
- JSON output is valid and parseable
- Template exclusion works correctly
- Project initialization creates all required files

---

## Dependencies

### Required

- **Python 3.11+**: For stdlib tomllib and modern type hints
- **uv**: Fast Python package manager for inline dependency management
- **rich**: Terminal formatting library for beautiful output

### Optional

- **spec (Bash)**: Interactive spec browser (complementary tool)
- **fzf**: Fuzzy finder for interactive spec navigation

---

## Non-Functional Requirements

### Performance

- Spec validation SHOULD complete in <200ms per spec
- Full validation of 10 specs SHOULD complete in <2 seconds
- Project initialization SHOULD complete in <500ms

### Reliability

- Validator MUST handle malformed specs gracefully without crashing
- Validator MUST provide clear error messages with line numbers
- File operations MUST not corrupt existing specs

### Maintainability

- Single-file implementation SHOULD remain under 2000 LOC
- Code SHOULD use type hints for all functions
- Functions SHOULD be self-documenting with clear names
- Validation rules SHOULD be easily configurable via TOML

### Portability

- Validator MUST work on macOS and Linux
- Validator SHOULD work on Windows with Python 3.11+
- No platform-specific dependencies beyond Python stdlib

---

## Metadata [for project tracking]

### Related Documentation

- [Bash spec command](local/bin/spec) - Interactive spec browser
- [Template file](local/share/spec/template.md) - Specification template
- [Python validator](local/bin/openspec) - Validation tool

### Test Coverage

- **Manual Testing**: Full end-to-end workflow testing
- **Real-world Usage**: Validates dotfiles specs (001, 002, 003)
- **Integration Test**: Tested with test project initialization

### Related Issues

- Initial implementation request: Enhance spec command with Python validator
- Design decisions documented in implementation plan

### Related Specifications

- [OpenSpec: Dotfiles Core](.openspec/specs/001-dotfiles-core/spec.md)
- [OpenSpec: Shortcuts System](.openspec/specs/003-shortcuts-system/spec.md)

---

## References

- **RFC 2119 - Key words for use in RFCs**: https://datatracker.ietf.org/doc/html/rfc2119
- **PEP 723 - Inline script metadata**: https://peps.python.org/pep-0723/
- **Given-When-Then**: https://martinfowler.com/bliki/GivenWhenThen.html
- **Behavior-Driven Development**: https://en.wikipedia.org/wiki/Behavior-driven_development

## Internal Documentation

- **Implementation Plan**: Located in conversation transcript
- **Design Decisions**: Documented in commit messages

---

**License:** Apache-2.0
**Copyright:** 2026 Ilja Heitlager
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
