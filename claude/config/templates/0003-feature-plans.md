# Plan Template: Feature Implementation

**Branch**: `feat/xxxxx`  
**Date**: YYYY-MM-DD  
**Status**: Planning | In Progress | Complete  
**Owner**: @username  

---

## Overview

A concise summary of the feature being implemented. Include:
- What problem does this solve?
- Why is it important?
- High-level approach

---

## Key Design Decisions

Document critical decisions made during planning:

1. **Decision 1**: Rationale and impact
2. **Decision 2**: Rationale and impact
3. **Decision 3**: Rationale and impact

Reference relevant ADRs (e.g., ADR-0001, ADR-0009) if applicable.

---

## Architecture

Include a diagram or text description of the system design:

```
┌─────────────────────────────────────┐
│                                     │
│  Component A ──▶ Component B        │
│       │              │              │
│       ▼              ▼              │
│     Data Store                      │
│                                     │
└─────────────────────────────────────┘
```

---

## Implementation Components

### 1. Data Models

**File**: `src/code_analyzer/core/xxxxx_models.py`

```python
# Pydantic/dataclass definitions
@dataclass
class MyModel:
    field1: str
    field2: int
    ...
```

**Database Schema** (if applicable):

```sql
CREATE TABLE xxx (
    id SERIAL PRIMARY KEY,
    field1 TEXT NOT NULL,
    field2 INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, field1)
);

CREATE INDEX idx_xxx_field1 ON xxx(field1);
```

### 2. Core Logic

**File**: `src/code_analyzer/actions/xxxxx_action.py`

- Main action class
- Processing logic
- Integration points with CodeGraph

### 3. Database/Storage

**File**: `src/code_analyzer/db/xxxxx_queries.py`

- SQL queries or ORM operations
- CRUD operations
- Bulk operations if needed

### 4. Configuration

**File**: `src/code_analyzer/config/xxxxx_config.py`

- Configuration parameters
- Constants
- Environment variables

---

## Implementation Phases

### Phase 1: Foundation (Estimate: X days)

**Objectives**
- Define data models
- Set up database schema
- Create basic unit tests

**Deliverables**
- Data models and database schema
- Unit tests (>80% coverage)
- Documentation

### Phase 2: Core Logic (Estimate: X days)

**Objectives**
- Implement main action/processor
- Integrate with existing systems
- Integration tests

**Deliverables**
- Fully functional action
- Integration tests
- ADR document if new patterns emerge

### Phase 3: Optimization & Polish (Estimate: X days)

**Objectives**
- Performance optimization
- Error handling
- Documentation & examples

**Deliverables**
- Optimized implementation
- Comprehensive tests
- Usage documentation

---

## Testing Strategy

### Unit Tests
- Location: `tests/unit/test_xxxxx.py`
- Coverage target: >85%
- Key test cases:
  - Happy path
  - Edge cases
  - Error conditions

### Integration Tests
- Location: `tests/integration/test_xxxxx.py`
- Validate end-to-end workflow
- Verify database operations

### Spike Tests (if applicable)
- Location: `tests/spikes/NNN_xxxxx/`
- Experimental validation
- Proof of concepts

---

## Success Criteria

- [ ] All unit tests pass with >85% coverage
- [ ] Integration tests pass with real database
- [ ] Feature branch passes CI/CD pipeline
- [ ] Code review approved
- [ ] Documentation complete
- [ ] ADR created (if architectural decision required)
- [ ] CHANGELOG.md updated
- [ ] Version bumped in `__init__.py` and README.md

---

## Dependencies & Blockers

### Internal Dependencies
- Requires X component to be completed first
- Depends on database migration Y

### External Dependencies
- Requires library Z version ≥ 1.0
- Depends on external service availability

### Known Blockers
- Issue #123: Need to resolve before proceeding
- Missing design decision on ABC

---

## References

- **ADRs**: Link to relevant Architectural Decision Records
- **Spikes**: Link to validation spikes (e.g., `tests/spikes/014_xxxxx/`)
- **Related Issues**: Link to GitHub issues
- **Documentation**: Link to existing docs

---

## Timeline & Milestones

| Milestone | Target Date | Status |
|-----------|------------|--------|
| Phase 1 complete | YYYY-MM-DD | Not Started |
| Phase 2 complete | YYYY-MM-DD | Not Started |
| Phase 3 complete | YYYY-MM-DD | Not Started |
| Feature review | YYYY-MM-DD | Not Started |
| Merge to main | YYYY-MM-DD | Not Started |

---

## Notes & Open Questions

- Question 1: How should we handle X scenario?
- Question 2: Should we optimize for Y or Z?
- Note: Keep eye on performance metric for Z

---

**Last Updated**: YYYY-MM-DD  
**Next Review**: YYYY-MM-DD
