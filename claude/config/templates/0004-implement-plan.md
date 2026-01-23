# Implementation Plan Template

**Branch**: `feat/xxxxx` or `refactor/xxxxx`  
**Date**: YYYY-MM-DD  
**Status**: Planning | In Progress | Complete | On Hold  
**Owner**: @username  
**Related ADRs**: [ADR-NNNN](../adr/NNNN-title.md), [ADR-MMMM](../adr/MMMM-title.md)  

---

## Overview

Provide a concise summary of the implementation:
- **What**: What feature/component is being implemented?
- **Why**: What problem does this solve or capability does it enable?
- **When**: What's the timeline/scope?
- **How**: High-level approach to implementation

Include any relevant business context or strategic importance.

---

## Objectives

Clear, measurable goals for this implementation:

- [ ] Objective 1: Specific, testable outcome
- [ ] Objective 2: Specific, testable outcome
- [ ] Objective 3: Specific, testable outcome

Include success criteria and acceptance tests.

---

## Key Design Decisions

Document critical architectural and technical decisions:

1. **Decision 1**: Description and rationale
   - Trade-offs considered
   - Why this choice was made
   - Impact on system

2. **Decision 2**: Description and rationale
   - Trade-offs considered
   - Why this choice was made
   - Impact on system

3. **Decision 3**: Description and rationale
   - Trade-offs considered
   - Why this choice was made
   - Impact on system

**Reference**: Link to relevant ADRs that informed these decisions.

---

## Architecture

### System Context

Brief description of how this fits into the overall system:
- What layer does it operate on (Layer 1-4)?
- What existing components does it interact with?
- What new components are being added?

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    System Name                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐     ┌──────────────────┐             │
│  │  Component A     │────▶│  Component B     │             │
│  │                  │     │                  │             │
│  └────────┬─────────┘     └────────┬─────────┘             │
│           │                        │                       │
│           ▼                        ▼                       │
│  ┌────────────────────────────────────────┐               │
│  │  Shared Data/State                     │               │
│  │  • Database                            │               │
│  │  • Graph                               │               │
│  │  • Configuration                       │               │
│  └────────────────────────────────────────┘               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

Describe how data flows through the system:
1. Input → Processing → Output
2. Integration points with existing systems
3. External dependencies

---

## Implementation Components

### 1. Data Models & Schema

**Location**: `src/code_analyzer/core/xxxxx_models.py`

**Pydantic Models**:
```python
from pydantic import BaseModel, Field
from dataclasses import dataclass
from typing import Optional, Dict, List, Any
from datetime import datetime

@dataclass
class MyModel:
    """Description of model purpose."""
    
    # Core identity fields
    id: Optional[int] = None
    fqn: str = ""
    
    # Data fields
    field1: str = ""
    field2: int = 0
    field3: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        ...
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MyModel":
        """Create from dictionary."""
        ...
```

**Database Schema** (if applicable):
```sql
-- Primary table for main entities
CREATE TABLE xxxxx (
    id SERIAL PRIMARY KEY,
    
    -- Identity & linking
    fqn TEXT NOT NULL,
    name TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    
    -- Content
    field1 TEXT,
    field2 INTEGER,
    
    -- Flexible metadata
    metadata JSONB DEFAULT '{}',
    
    -- Temporal
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(project_id, fqn),
    CONSTRAINT valid_type CHECK (entity_type IN (...))
);

-- Indexes for common queries
CREATE INDEX idx_xxxxx_type ON xxxxx(entity_type);
CREATE INDEX idx_xxxxx_fqn ON xxxxx(fqn);
CREATE INDEX idx_xxxxx_metadata ON xxxxx USING GIN(metadata);
```

---

### 2. Core Logic/Action Class

**Location**: `src/code_analyzer/actions/xxxxx_action.py`

```python
from code_analyzer.actions.base import ActionBase
from typing import Optional, List, Dict, Any

class MyAction(ActionBase):
    """Implementation of xxxxx feature.
    
    Responsibility:
    - Describe what this action does
    - How it integrates with the pipeline
    - What state it produces
    """
    
    def execute_step1(self) -> None:
        """First step of processing.
        
        Reads: self.state["source_data"]
        Writes: self.state["intermediate_data"]
        """
        source = self._get_or_init_state("source_data", default=[])
        
        # Process
        result = self._process(source)
        
        # Store result
        self._set_state("intermediate_data", result)
    
    def execute_step2(self) -> None:
        """Second step of processing.
        
        Reads: self.state["intermediate_data"]
        Writes: self.state["final_result"]
        """
        data = self._get_or_init_state("intermediate_data", default=[])
        
        # Further processing
        result = self._transform(data)
        
        # Store final result
        self._set_state("final_result", result)
    
    def _process(self, data: List) -> List:
        """Internal helper for processing."""
        ...
    
    def _transform(self, data: List) -> Dict:
        """Internal helper for transformation."""
        ...
```

**Fluent Pipeline Integration**:
```python
# Usage in fluent pipeline
result = (Definition()
    .my_action()
    .execute_step1()
    .execute_step2()
    .do()
)
```

---

### 3. Database/Persistence Layer

**Location**: `src/code_analyzer/db/xxxxx_manager.py`

```python
from typing import List, Dict, Optional, Any
import psycopg

class XXXXXManager:
    """Database operations for xxxxx feature."""
    
    def __init__(self, connection_string: str):
        self.conn = psycopg.connect(connection_string)
    
    def persist_entity(self, entity: MyModel, project_id: int) -> int:
        """Insert or update entity."""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO xxxxx (fqn, name, field1, metadata, project_id)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (project_id, fqn) DO UPDATE SET
                    field1 = EXCLUDED.field1,
                    metadata = EXCLUDED.metadata,
                    updated_at = NOW()
                RETURNING id
            """, (
                entity.fqn,
                entity.name,
                entity.field1,
                json.dumps(entity.metadata),
                project_id
            ))
            return cur.fetchone()[0]
    
    def get_entity(self, fqn: str, project_id: int) -> Optional[MyModel]:
        """Retrieve entity by FQN."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM xxxxx
                WHERE fqn = %s AND project_id = %s
            """, (fqn, project_id))
            row = cur.fetchone()
            if row:
                return self._row_to_model(row)
            return None
    
    def _row_to_model(self, row: Dict) -> MyModel:
        """Convert database row to model."""
        return MyModel(
            id=row['id'],
            fqn=row['fqn'],
            field1=row['field1'],
            metadata=row['metadata'],
        )
```

---

### 4. Configuration & Constants

**Location**: `src/code_analyzer/config/xxxxx_config.py`

```python
from typing import Dict, List
from enum import Enum

class XXXXXType(Enum):
    """Types of xxxxx entities."""
    TYPE_A = "type_a"
    TYPE_B = "type_b"
    TYPE_C = "type_c"

# Configuration constants
DEFAULT_XXXXX_CONFIG = {
    "max_retries": 3,
    "timeout_seconds": 30,
    "batch_size": 100,
    "enable_caching": True,
}

# Validation rules
VALID_XXXXX_FIELDS = {"field1", "field2", "field3"}
REQUIRED_XXXXX_FIELDS = {"field1", "name"}
```

---

## Testing Strategy

### Unit Tests

**Location**: `tests/unit/actions/test_xxxxx_action.py`

```python
import pytest
from code_analyzer.actions.xxxxx_action import MyAction

class TestMyAction:
    def test_execute_step1_produces_correct_output(self):
        """Test that step 1 produces expected intermediate data."""
        ...
    
    def test_execute_step2_transforms_data_correctly(self):
        """Test that step 2 applies correct transformations."""
        ...
    
    def test_edge_case_empty_input(self):
        """Test behavior with empty input."""
        ...
```

### Integration Tests

**Location**: `tests/integration/test_xxxxx_pipeline.py`

```python
def test_full_pipeline_end_to_end(code_graph, database):
    """Test complete pipeline from input to persistence."""
    result = (Definition()
        .my_action()
        .execute_step1()
        .execute_step2()
        .persist_to_db()
        .do()
    )
    
    # Verify database contains expected results
    assert result["success"] is True
    assert len(result["persisted"]) > 0
```

### Test Coverage

Target: >80% code coverage for new components

- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] Coverage > 80%
- [ ] Edge cases documented

---

## Performance Considerations

### Scalability

- Expected performance characteristics
- Constraints and limits (e.g., max entities, throughput)
- How does it scale with codebase size?

### Optimization Strategies

- Caching patterns
- Batch operations
- Database index utilization
- Lazy evaluation where appropriate

---

## Rollout Plan

### Phases

**Phase 1: Development & Testing** (Target: Week N)
- [ ] Design review and approval
- [ ] Component implementation
- [ ] Unit test coverage >80%
- [ ] Internal review

**Phase 2: Integration** (Target: Week N+1)
- [ ] Integration testing
- [ ] Documentation
- [ ] Code review
- [ ] Performance validation

**Phase 3: Deployment** (Target: Week N+2)
- [ ] Merge to main
- [ ] Release notes
- [ ] User documentation
- [ ] Monitoring setup

### Rollback Plan

Describe how to rollback if issues occur:
- Database migration rollback steps
- Feature flag disable procedures
- Data cleanup if needed

---

## Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Risk 1 | Medium | High | Mitigation strategy |
| Risk 2 | Low | Medium | Mitigation strategy |
| Risk 3 | High | Low | Mitigation strategy |

---

## Documentation

### Code Documentation

- [ ] Docstrings for all public methods
- [ ] Type hints throughout
- [ ] Complex logic explained with comments
- [ ] Examples in docstrings

### User Documentation

- [ ] Usage guide
- [ ] API documentation
- [ ] Configuration guide
- [ ] Troubleshooting guide

### ADR Updates

- [ ] New ADRs written if architectural decisions made
- [ ] Existing ADRs updated if relevant
- [ ] Decision rationale documented

---

## Dependencies & Prerequisites

### External Dependencies

- List any new package dependencies
- Version constraints
- License compatibility

### Internal Dependencies

- Required components that must exist first
- APIs or modules that need to be available
- Database schema prerequisites

---

## Success Metrics

How will we know this implementation is successful?

- [ ] Metric 1: Specific, measurable target
- [ ] Metric 2: Specific, measurable target
- [ ] Metric 3: Specific, measurable target

---

## Timeline & Effort Estimate

| Task | Effort | Duration | Dependencies |
|------|--------|----------|--------------|
| Design & review | 2 days | Week 1 | None |
| Implementation | 5 days | Weeks 1-2 | Design approved |
| Testing | 3 days | Week 2 | Implementation done |
| Documentation | 2 days | Week 2-3 | Implementation done |
| Review & QA | 2 days | Week 3 | All above done |
| **Total** | **14 days** | **3 weeks** | |

---

## References & Resources

### Related Documentation

- [ADR-0001: Four-Layer Architecture](../adr/0001-four_layer_architecture.md)
- [Action Base Class](../../src/code_analyzer/actions/base.py)
- [Database Manager Template](../../src/code_analyzer/db/manager.py)

### External References

- Relevant papers, blog posts, or standards
- Third-party library documentation
- Protocol specifications

---

## Questions & Open Items

Unresolved questions or decisions needed:

- [ ] Question 1: What's the decision? Who decides?
- [ ] Question 2: What's the decision? Who decides?
- [ ] Question 3: What's the decision? Who decides?

---

## Sign-Off

- **Design Review**: 
- **Technical Lead**: 
- **Product Owner**: 

---

**Last Updated**: YYYY-MM-DD  
**Status**: Ready for implementation | In progress | Complete
