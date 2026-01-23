Create a feature plan document in `./docs/plans/`.

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

1. Check existing plans: `ls docs/plans/`
2. Use next sequential number
3. Use lowercase, hyphenated name

## Output

After gathering info:
1. Show plan preview
2. Create file at `./docs/plans/NNN-feature-name.md`
3. Suggest creating related branch: `feat/feature-name`
4. Suggest creating GitHub issue if none exists

Ask user to confirm before creating.
