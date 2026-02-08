# [System Name] Specification (Delta)

**Domain:** [Domain Area]
**Version:** [New Version - e.g., 1.1.0]
**Status:** Proposed
**Date:** [YYYY-MM-DD]
**Change ID:** [NNN-change-name]

## Overview

This delta spec proposes changes to [System Name] to [brief summary of what's changing and why].

**Parent Spec:** `.openspec/specs/NNN-system-name/spec.md` (version X.X.X)

### Changes Summary

- **Added**: [New features or capabilities]
- **Modified**: [Changes to existing requirements]
- **Removed**: [Deprecated features]
- **Renamed**: [Requirement name changes]

---

## RFC 2119 Keywords

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

---

## ADDED Requirements

Use this section for **brand new** requirements that don't exist in the parent spec.

### Requirement: [New Feature Name]

The system MUST/SHALL/SHOULD [clear statement of new requirement].

#### Scenario: [Happy Path]

- GIVEN [precondition]
- WHEN [action]
- THEN [expected new behavior]
- AND [additional outcomes]

#### Scenario: [Edge Case]

- GIVEN [error condition]
- WHEN [action]
- THEN [expected error handling]

---

## MODIFIED Requirements

Use this section for **changes** to existing requirements. Include the original requirement name and clearly indicate what changed.

### Requirement: [Existing Requirement Name] (Modified)

The system MUST/SHALL/SHOULD [updated requirement statement].

**Changes from vX.X.X:**
- **Added**: [New aspects of this requirement]
- **Changed**: [What behavior changed]
- **Rationale**: [Why this change is needed]

#### Scenario: [Updated Behavior] (NEW)

- GIVEN [precondition]
- WHEN [action]
- THEN [new expected behavior]
- AND [how this differs from before]

#### Scenario: [Existing Behavior] (UNCHANGED)

- GIVEN [precondition]
- WHEN [action]
- THEN [behavior that stays the same]

---

## REMOVED Requirements

Use this section for requirements being **deprecated** or **removed**.

### Requirement: [Feature Being Removed]

This requirement is being removed.

**Rationale**: [Why is this being removed? What problem does removal solve?]

**Original Requirement**: [Quote the original requirement text for reference]

**Migration Path**: [How should users adapt? What replaces this functionality?]

**Deprecation Timeline**: [If phased removal, specify timeline]

---

## RENAMED Requirements

Use this section for requirements that are being **renamed** without substantive changes.

### Requirement: [New Name] (formerly: [Old Name])

The system MUST/SHALL/SHOULD [same requirement, just renamed].

**Reason for Rename**: [Why is the name changing? Better clarity? Consistency?]

**Impact**: [Minimal - just a name change, no behavioral changes]

---

## Impact Analysis

### Breaking Changes

- [ ] **Change 1**: [Description and impact]
  - **Affects**: [What users/systems are affected]
  - **Migration**: [How to adapt]

### Dependencies

- **New Dependencies**: [Any new tools, libraries, or systems required]
- **Changed Dependencies**: [Version updates or configuration changes]
- **Removed Dependencies**: [What's no longer needed]

### Testing Strategy

- [ ] Unit tests for new requirements
- [ ] Integration tests for modified behavior
- [ ] Migration tests for removed features
- [ ] Backward compatibility tests (if applicable)

---

## Rollout Plan

### Phase 1: Implementation
- [ ] Implement ADDED requirements
- [ ] Update code for MODIFIED requirements
- [ ] Deprecate REMOVED requirements (if phased)

### Phase 2: Testing
- [ ] All tests pass
- [ ] Manual testing completed
- [ ] Performance benchmarks met

### Phase 3: Documentation
- [ ] Update main spec (merge delta)
- [ ] Update README/docs
- [ ] Update CHANGELOG

### Phase 4: Deployment
- [ ] Deploy to staging
- [ ] Monitor for issues
- [ ] Deploy to production

---

## References

- **Parent Spec**: `.openspec/specs/NNN-system-name/spec.md`
- **Proposal**: `.openspec/changes/NNN-change-name/proposal.md`
- **Tasks**: `.openspec/changes/NNN-change-name/tasks.md`
- **RFC 2119**: https://datatracker.ietf.org/doc/html/rfc2119

---

**License:** Apache-2.0
**Copyright:** [YYYY] [Author Name]
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
