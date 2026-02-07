# [System Name] Specification

**Domain:** [Domain Area - e.g., Personal Development Environment, Developer Productivity]
**Version:** 1.0.0
**Status:** [Draft|Proposed|Implemented|Deprecated]
**Date:** [YYYY-MM-DD]

## Overview

[Brief description of the system, its purpose, and key capabilities. Explain what problem it solves and why it exists.]

### Philosophy

- **Principle 1**: [Core design principle - explain the "why"]
- **Principle 2**: [Another guiding principle]
- **Principle 3**: [Third principle if applicable]

### Key Capabilities

- **Capability 1**: [What the system can do]
- **Capability 2**: [Another major feature]
- **Capability 3**: [Third capability]

---

## RFC 2119 Keywords

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

---

## ADDED Requirements

### Requirement: [Requirement Name]

The system MUST/SHALL/SHOULD [clear, actionable statement of what the system must do].

#### Scenario: [Happy Path Name]

- GIVEN [initial state and preconditions - be specific]
- WHEN [action or trigger occurs]
- THEN [expected outcome - testable]
- AND [additional expected outcomes]

#### Scenario: [Edge Case or Error Condition]

- GIVEN [different precondition]
- WHEN [different action or error condition]
- THEN [expected behavior - how system handles it]
- AND [additional outcomes]

### Requirement: [Second Requirement Name]

The system MUST/SHALL/SHOULD [another clear requirement statement].

#### Scenario: [Scenario Name]

- GIVEN [preconditions]
- WHEN [action]
- THEN [expected outcome]

---

## Current Implementation

[Optional: Details about how the requirements are currently implemented]

### Architecture

[Optional: Architecture diagrams, component descriptions, file structure]

```
[ASCII diagram or file structure if applicable]
```

### Key Components

[Optional: Description of main components and their interactions]

---

## Testing Requirements

[How to verify the requirements are met]

- **Manual Testing**: [Steps to manually verify behavior]
- **Automated Testing**: [What should be tested automatically]
- **Acceptance Criteria**: [When is this requirement satisfied]

---

## Dependencies

### Required

- **Dependency 1**: [Required tools, libraries, or systems]
- **Dependency 2**: [Another required dependency]

### Optional

- **Optional 1**: [Optional enhancements]
- **Optional 2**: [Nice-to-have dependencies]

---

## Non-Functional Requirements

### Performance

- [Performance requirements with concrete metrics]
- Example: Response time SHOULD be <100ms

### Reliability

- [Reliability expectations]
- Example: System MUST handle errors gracefully

### Maintainability

- [How easy should it be to maintain and extend]

### Portability

- [Cross-platform requirements if applicable]

---

## References

- **RFC 2119 - Key words for use in RFCs**: https://datatracker.ietf.org/doc/html/rfc2119
- [Additional references, documentation, or related specs]

## Internal Documentation

- [Links to related OpenSpec files]
- [Links to implementation documentation]
- [Links to related ADRs or design documents]

---

**License:** Apache-2.0
**Copyright:** [YYYY] [Author Name]
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
