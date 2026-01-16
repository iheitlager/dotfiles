# ADR Documentation Strategy

## Overview

This skill provides a comprehensive approach to documenting **Architecture Decision Records (ADRs)**—lightweight, living documents that capture significant architectural decisions and their rationale.

## What is an ADR?

An ADR is a concise document that records a significant architectural, technical, or design decision, including:
- **Context**: Why the decision was needed (problem/constraint)
- **Decision**: What was decided and why
- **Consequences**: Impacts (positive, negative, tradeoffs)
- **Alternatives Considered**: Other options evaluated and why they were rejected
- **Status**: Proposed/Accepted/Superseded/Deprecated
- **Validation**: How/when the decision was validated or will be validated

**Philosophy**: ADRs are living documentation—updated as understanding evolves and decisions are validated through implementation and testing.

## Recommended ADR Repository Structure

```
docs/adr/
├── README.md                 # ADR documentation guide and index
├── index.md                  # Summary table of all ADRs with status
├── 0001-<decision-name>.md   # Individual ADRs (zero-padded numbering)
├── 0002-<decision-name>.md
├── ... (continue numbering) ...
├── templates/
│   ├── adr-template.md       # Blank ADR template for new decisions
│   └── implementation-template.md  # Optional: Implementation plan template
└── CONTRIBUTING.md           # Guidelines for writing/updating ADRs
```

## ADR Template Structure

Each ADR follows a consistent structure:

```markdown
# ADR-NNNN: Brief Title of Decision

## Status
[Proposed | Accepted | Superseded | Deprecated]

## Context
Describe the issue or requirement that necessitated this decision.
Include constraints, background, and what triggered the need for this decision.

## Decision
State the decision clearly and concisely.
Explain why this approach was chosen over alternatives.

## Consequences
Describe the impacts of this decision:
- Positive consequences / Benefits
- Negative consequences / Drawbacks
- Tradeoffs involved

## Alternatives Considered
Document other options that were evaluated:
- Alternative 1: Why rejected
- Alternative 2: Why rejected
- etc.

## Validation
How was/will this decision be validated?
- Testing approach
- Empirical evidence
- Metrics for success
- Review/approval process

## Related ADRs
- Supersedes: [link if any]
- Related to: [other relevant ADRs]
- Superceded by: [if status is Superseded]

## Implementation Notes
Optional: Links to implementation, affected code, deployment info.
```

## Best Practices

### Writing ADRs

1. **Keep it concise**: 1-2 pages maximum
2. **Use clear language**: Avoid jargon; be understandable to team members unfamiliar with the decision
3. **Document tradeoffs**: Show you considered alternatives
4. **Make it future-proof**: Write as if someone will read this in 2 years
5. **Link related decisions**: Help readers understand the broader architecture

### Organizing ADRs

1. **Number sequentially**: Use zero-padded numbers (0001, 0002, etc.)
2. **Group by category**: Consider organizing by architectural layer or domain
3. **Create a master index**: Maintain `index.md` with all ADRs and current status
4. **Timestamp decisions**: Include decision date for context
5. **Use consistent formatting**: Enforce template structure across all ADRs

### Maintenance

1. **Update status regularly**: Mark as Superseded when decisions change
2. **Link superseding decisions**: Show progression of thinking
3. **Add validation results**: Update with empirical evidence as it accumulates
4. **Review periodically**: Flag decisions that need revisiting
5. **Keep rationale**: Even superseded ADRs provide historical context

## When to Write an ADR

Write an ADR when:
- Making a significant architectural choice
- Selecting between major technologies/frameworks
- Establishing patterns that will be reused
- Making decisions that affect multiple teams/systems
- Choosing between approaches with different tradeoffs

Don't write ADRs for:
- Trivial implementation details
- Temporary workarounds
- Decisions that only affect one isolated component

## Indexing and Referencing

Create an `index.md` with a table of all ADRs:

| ADR | Title | Status | Category | Date |
|-----|-------|--------|----------|------|
| 0001 | Example Decision | Accepted | Architecture | 2026-01-16 |
| 0002 | Example Decision | Proposed | Technology | 2026-01-16 |
| 0003 | Example Decision | Superseded | Pattern | 2026-01-15 |

## Implementation Plan Template (Optional)

For decisions requiring structured rollout, optionally create implementation plans:

```markdown
# ADR-NNNN Implementation Plan

## Timeline
- Phase 1: [Description] (Week X-Y)
- Phase 2: [Description] (Week Y-Z)
- etc.

## Acceptance Criteria
- [ ] Requirement 1
- [ ] Requirement 2
- [ ] etc.

## Risk Mitigation
- Risk: [Description] → Mitigation: [Approach]
- etc.
## Success Metrics
- Metric 1: [Target]
- Metric 2: [Target]
```

## How ADRs Guide Development

### 1. **Decision Recording**

When facing an architectural choice:
1. Create new ADR (next sequential number)
2. Document context, decision, consequences
3. Mark as "Proposed"
4. Request feedback from stakeholders

### 2. **Validation & Experimentation**

Before finalizing decisions:
1. Create experimental/spike phase to test hypothesis
2. Implement proof-of-concept
3. Write tests to validate assumptions
4. Gather empirical evidence
5. Update ADR status to "Accepted"

### 3. **Implementation**

Once validated:
1. Implement in production code
2. Cross-reference ADR in docstrings
3. Reference ADR in commit messages and PR descriptions
4. Link implementation files to ADR

### 4. **Evolution**

As requirements change:
1. Update ADR status (Superseded/Deprecated)
2. Create new ADR for revised decision
3. Cross-link old and new ADRs to show evolution
4. Preserve old ADRs for historical context

## Creating an ADR Index

Maintain a master index (`docs/adr/index.md`) with all ADRs:

```markdown
# Architecture Decision Records

## Accepted & Validated
| ADR | Title | Status | Category | Date |
|-----|-------|--------|----------|------|
| 0001 | Title | ✅ Accepted | Architecture | 2026-01-16 |
| 0002 | Title | ✅ Accepted | Technology | 2026-01-16 |

## Proposed (Under Review)
| ADR | Title | Status | Category | Date |
|-----|-------|--------|----------|------|
| 0003 | Title | 📋 Proposed | Pattern | 2026-01-16 |

## Superseded
| ADR | Title | Replaced By |
|-----|-------|------------|
| 0004 | Old Decision | ADR-0005 |
```

## Querying and Finding ADRs

### By Status
```bash
# Find all accepted ADRs
grep -r "Status: ✅" docs/adr/

# Find proposed ADRs
grep -r "Status: 📋" docs/adr/
```

### By Topic
```bash
# Find ADRs mentioning a specific technology
grep -r "PostgreSQL" docs/adr/

# Find related ADRs
grep -r "Related ADRs:" docs/adr/0001-*.md
```

### Organization Tips

1. **Organize by domain**: Group related ADRs together
   - 0001-0010: Architecture decisions
   - 0011-0020: Technology choices
   - 0021-0030: Process decisions

2. **Use consistent naming**: `NNNN-descriptive-title.md`

3. **Create README**: `docs/adr/README.md` explains the ADR process to new team members

## Workflow Integration

### 1. During Planning
- Review existing ADRs when starting new projects
- Identify if a similar decision was already made
- Reuse validated approaches

### 2. During Development
- Reference ADRs in code comments and docstrings
- Link to relevant ADRs in PR descriptions
- Update ADRs if implementation reveals new information

### 3. During Reviews
- Check if new decisions should be ADRs
- Validate that decisions follow established ADRs
- Suggest ADR updates if approach has changed

### 4. During Retrospectives
- Review ADRs that didn't work out
- Mark as Superseded when decisions change
- Extract lessons learned

## Common Pitfalls to Avoid

1. **Too Much Detail**: Keep ADRs at architectural level, not implementation level
2. **No Alternatives**: Always document options considered
3. **Incomplete Context**: Future readers may not know current situation
4. **Never Updated**: Mark superseded ADRs, don't just ignore them
5. **No Validation**: Always include how/when the decision was validated
6. **Hidden ADRs**: Store in standard location (`docs/adr/`) for visibility

## Advanced Features (Optional)

### ADR Templates
Create domain-specific templates:
- `adr-template-architecture.md`
- `adr-template-technology-selection.md`
- `adr-template-process.md`

### ADR Lifecycle Tracking
Track when each ADR:
- Was created (proposed date)
- Was accepted (acceptance date)
- Became relevant (implementation start)
- Was superseded (retirement date)

### ADR Metrics
Monitor ADR effectiveness:
- How many ADRs are currently active?
- What's the supersession rate? (Rate of changes to decisions)
- Which categories have most decisions?
- How long do decisions typically hold?

## Tools & Platforms

### Manual (Recommended for small teams)
- Store ADRs in Git alongside code
- Use Markdown format
- Maintain index manually

### For Large Teams
- Adr-tools: Command-line tools for managing ADRs
- Custom templates and automation
- Integration with issue tracking
- Automated index generation from files

## References

- [ADR GitHub Org](https://adr.github.io/): Official ADR standards
- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions): Original ADR article
- [ADR Examples](https://github.com/topics/adr): Real-world examples from various projects
- **Spike Tests**: `tests/spikes/`
- **Implementation**: `src/code_analyzer/`
- **External**: https://adr.github.io/ (ADR standard)
