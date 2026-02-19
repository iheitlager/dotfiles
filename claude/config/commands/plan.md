Create planning documents: feature plans or architectural decision records (ADRs).

## Usage

```
/plan                    Interactive feature plan
/plan <feature>          Plan specific feature → .openspec/plans/
/plan adr <decision>     Architectural decision → .openspec/adr/
```

## Process

1. **Gather information** about the feature through questions
2. **Assess scope and complexity**
3. **Generate plan** using the template structure
4. **Create file** with sequential numbering

## Required Information

Before creating the plan, gather:

### Basic Info
- **Feature name**: Short descriptive title
- **Problem**: What problem does this solve?
- **Why now**: Why is this important?

### Scope Assessment
- **Complexity**: trivial | small | medium | large | epic
- **Estimated effort**: X days/weeks
- **Dependencies**: What needs to exist first?
- **Blockers**: Known issues or decisions needed?

### Design
- **Key components**: What files/modules are affected?
- **Architecture changes**: Any system design changes?
- **Data models**: New models or schema changes?

## Plan Structure

Follow the template from `0003-feature-plans.md`:

```markdown
# Plan: [Feature Name]

**Branch**: `feat/short-name`
**Date**: [Today's date]
**Status**: Planning
**Owner**: @[username]

---

## Overview
[Problem and approach summary]

## Key Design Decisions
[Critical decisions with rationale]

## Architecture
[Diagram or description]

## Implementation Components
[Files and changes needed]

## Implementation Phases
[Phase breakdown with estimates]

## Testing Strategy
[Unit, integration, spike tests]

## Success Criteria
[Checklist of done conditions]

## Dependencies & Blockers
[Internal/external deps, blockers]

## Timeline & Milestones
[Target dates table]

## Notes & Open Questions
[Outstanding questions]
```

## File Naming

Format: `NNN-short-name.md`

1. Check existing plans: `ls .openspec/plans/`
2. Use next sequential number
3. Use lowercase, hyphenated name

## Output

After gathering info:
1. Show plan preview
2. Create file at `./.openspec/plans/NNN-feature-name.md`
3. Suggest creating related branch: `feat/feature-name`
4. Suggest creating GitHub issue if none exists

Ask user to confirm before creating.

---

## ADR Mode (`/plan adr`)

Create an Architectural Decision Record for significant design decisions.

### When to Write an ADR

- Choosing between technologies or approaches
- Establishing patterns that affect multiple components
- Making decisions that are hard to reverse
- Documenting why something is the way it is

### ADR Template

Use bold metadata fields for parser-compatible frontmatter (NOT heading-level sections):

```markdown
# ADR-NNNN: [Title]

**Status**: Proposed

**Date**: [Today's date, YYYY-MM-DD]

**Decision ID**: NNNN-short-title

---

## Context

[What is the issue that we're seeing that is motivating this decision?
First paragraph should be a concise summary — extracted by parser.]

## Decision

[What is the change that we're proposing and/or doing?
First paragraph should be a concise summary — extracted by parser.]

## Consequences

### Positive
- [benefit 1]
- [benefit 2]

### Negative
- [drawback 1]
- [drawback 2]

## Alternatives Considered

### [Alternative 1]
- Pros: ...
- Cons: ...
- Why rejected: ...

## References

- [Link to relevant documentation]
- [Related ADRs: ADR-XXXX, ADR-YYYY]
```

**Parser-required fields:**
- `**Status**:` — Accepted / Proposed / Deprecated / Superseded
- `**Date**:` — YYYY-MM-DD format
- `**Decision ID**:` — Matches filename stem (e.g., `0019-traceability_metamodel`)
- `**Supersedes**:` — Optional, for `ADR-XXXX` references (creates SUPERSEDES edges)

### ADR Naming

Format: `NNNN-short-title.md`

1. Check existing ADRs: `ls .openspec/adr/`
2. Use next sequential number (4 digits, zero-padded)
3. Use lowercase, hyphenated title

### ADR Output

After gathering context:
1. Show ADR preview
2. Create file at `./.openspec/adr/NNNN-title.md`
3. Update ADR index if one exists
4. Suggest linking from relevant code comments

Ask user to confirm before creating.
