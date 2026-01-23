# Spike Hypothesis Template

Use this template to document experimental spikes in `tests/spikes/NNN_descriptive_name/README.md`. Spikes are hypothesis-driven explorations that answer specific architectural or technical questions before committing to implementation.

---

## Spike NNN: [Title]

**Branch**: `spike/branch-name`  
**Date**: YYYY-MM-DD  
**Author**: Your Name  
**Status**: In Progress | Complete | Integrated | Rejected | Deferred

---

## 1. Problem Statement

[What decision are we making? What gap in knowledge exists?]

Be specific and concrete. Avoid vague statements. Focus on the decision at hand, not just general curiosity.

**Example**:
"We need to determine whether PostgreSQL full-text search can support sub-100ms query latency across 1M+ papers while maintaining acceptable index sizes (<2GB)."

---

## 2. Hypothesis

### Primary Hypothesis (H1)

[Testable prediction about what WILL happen]

**Format**: "[Technology/Approach X] will achieve [quantifiable outcome Y] under [specific constraints Z]"

**Example**:
"PostgreSQL with full-text search indices will achieve <100ms query latency on 1M+ documents with typical keyword queries."

### Null Hypothesis (H0)

[Prediction of what will NOT happen]

**Example**:
"PostgreSQL will NOT achieve <100ms query latency, or query latency will exceed 100ms on production-scale datasets."

### Alternative Hypotheses

[Other possible outcomes worth exploring]

**Examples**:
- "Query latency will be acceptable (<100ms) but index size will exceed 2GB"
- "Performance will be acceptable only with specific PostgreSQL configurations not available in production"

---

## 3. Research Design

### Success Criteria

Define measurable, binary criteria for evaluating the hypothesis.

| Metric | Target | Rationale | Priority |
|--------|--------|-----------|----------|
| Metric 1 | Target Value | Why this matters | High/Medium/Low |
| Metric 2 | Target Value | Why this matters | High/Medium/Low |
| Metric 3 | Target Value | Why this matters | High/Medium/Low |

**Example**:

| Metric | Target | Rationale | Priority |
|--------|--------|-----------|----------|
| Query Latency (simple) | <100ms | User-facing UI responsiveness | High |
| Query Latency (complex) | <200ms | Complex queries still usable | Medium |
| Index Size | <2GB | Storage/infrastructure cost | High |
| Index Build Time | <5 min | Re-indexing overhead | Low |
| Memory Usage | <512MB | Resource constraints | Medium |

### Experimental Design

- **Unit Under Test**: [What are you testing? (e.g., PostgreSQL full-text search)]
- **Test Environment**: [Docker | Local | Cloud | Other, with OS/software versions]
- **Dataset**: [Type of test data, size, distribution]
- **Duration**: [Expected time for complete experiment]
- **Sample Size**: [Number of iterations/replicates]
- **Control Variables**: [What conditions are held constant?]

**Example**:
- **Unit Under Test**: PostgreSQL full-text search with GIN indices
- **Test Environment**: Docker container (PostgreSQL 15.1, Ubuntu 22.04)
- **Dataset**: JSONL format papers (titles, abstracts, keywords) - 100K, 500K, 1M sizes
- **Duration**: 2-3 days for full experiment
- **Sample Size**: 3 replicates per test condition, 10 queries per replicate
- **Control Variables**: Query complexity, index type, hardware configuration

### Test Strategy

Outline the sequence of tests you'll run to prove/disprove hypothesis.

1. **Baseline Test**: [Establish current state or simple case]
2. **Configuration Tests**: [Try different configurations or parameters]
3. **Load Tests**: [Stress test with increasing load]
4. **Edge Case Tests**: [Boundary conditions and failure modes]
5. **Regression Tests**: [Ensure changes don't break existing functionality]

**Example**:
1. **Baseline**: Single query on 10K document index (establish methodology)
2. **Scale-up**: Repeat same query on 100K, 500K, 1M indices (measure degradation)
3. **Query Complexity**: Simple vs. phrase vs. boolean queries (identify performance cliffs)
4. **Concurrent Load**: Multiple queries in parallel (real-world simulation)
5. **Index Types**: GIN vs. GIST vs. full-text default (compare approaches)

---

## 4. Experiment Execution

### Setup Instructions

```bash
# Step-by-step reproduction
# Include exact commands to set up environment, data, and run tests
```

**Example**:
```bash
# Start PostgreSQL
docker-compose up -d postgres

# Create database and schema
psql -U postgres -c "CREATE DATABASE spike_test;"
psql -U postgres spike_test < schema.sql

# Load test data
uv run python -m tests.spikes.NNN_postgres_performance.generate_data --size 1000000

# Run tests
uv run pytest tests/spikes/NNN_postgres_performance/test_NNN_main.py -v --benchmark-only
```

### Results

Document findings AS THEY ARE DISCOVERED (not after all tests complete).

#### Test 1: [Test Name]
- **Condition**: [What parameters/configuration?]
- **Expected**: [What we predicted]
- **Actual**: [What actually happened]
- **Result**: ✅ PASS | ⚠️ PARTIAL | ❌ FAIL
- **Notes**: [Observations, surprises, investigation notes]

**Example**:
#### Test 1: Baseline Query on 10K Documents
- **Condition**: Single keyword query, GIN index, 10K papers
- **Expected**: <50ms latency
- **Actual**: 12ms average, 8-18ms range
- **Result**: ✅ PASS
- **Notes**: Excellent performance on small dataset. Provides baseline for scaling analysis.

#### Test 2: Complex Query Scalability
- **Condition**: Multi-keyword phrase query, GIN index, increasing dataset size
- **Expected**: <100ms latency up to 1M documents
- **Actual**: 10K=45ms, 100K=120ms, 500K=380ms, 1M=1200ms
- **Result**: ❌ FAIL at scale
- **Notes**: Performance degrades exponentially. Index size grows proportionally. May require partitioning or alternative approach.

---

## 5. Analysis

### Hypothesis Evaluation

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Simple Query Latency | <100ms | 45ms | ✅ PASS |
| Complex Query Latency | <200ms | 1200ms | ❌ FAIL |
| Index Size (1M docs) | <2GB | 1.8GB | ✅ PASS |

### Key Findings

**Finding 1: [What did we discover?]**
- **Evidence**: [Supporting data/metrics]
- **Interpretation**: [What does this mean for our decision?]

**Finding 2: [Next finding]**
- **Evidence**: [Supporting data/metrics]
- **Interpretation**: [What does this mean?]

**Example**:

**Finding 1: Simple queries scale well, complex queries do not**
- **Evidence**: Simple queries maintained <50ms across all scales. Complex phrase queries exceeded target at 500K docs (380ms) and failed at 1M docs (1200ms)
- **Interpretation**: Full-text search is viable for keyword-based UI search but insufficient for advanced boolean/phrase queries at production scale

**Finding 2: Index size is manageable but grows with query complexity**
- **Evidence**: 1M document index = 1.8GB with GIN. GIST index = 2.3GB (too large). Full-text default = 1.2GB but slower queries
- **Interpretation**: GIN with tuning is acceptable; requires regular maintenance but fits infrastructure budget

### Limitations

[What wasn't tested? What assumptions did we make? What edge cases remain?]

**Example**:
- Tested READ-ONLY queries; concurrent writes not evaluated
- Used standard PostgreSQL configuration; didn't explore custom tuning (shared_buffers, work_mem, etc.)
- Dataset is synthetic (normalized text); real-world PDFs with special characters not tested
- Did not evaluate full-text ranking algorithms (ts_rank, BM25)
- Hardware: tested on Docker container; physical hardware performance unknown

---

## 6. Conclusion

### Hypothesis Verdict

**Result**: ✅ ACCEPTED | ⚠️ PARTIALLY ACCEPTED | ❌ REJECTED

**Summary**: [1-2 sentences on whether hypothesis was supported and what this means]

**Example**:
"Primary hypothesis is PARTIALLY ACCEPTED. PostgreSQL full-text search achieves target latency (<100ms) for simple keyword queries but fails for complex boolean/phrase queries at production scale. Acceptable for basic UI search; insufficient for advanced use cases without further optimization."

### Decision Pathway

Based on findings, choose one:

#### Pathway A: Hypothesis Confirmed → Feature Branch
**Action**: Proceed to production implementation
1. Create ADR referencing spike findings
2. Create feature branch: `feat/feature-name`
3. Rewrite spike code with production quality standards
4. Add comprehensive test coverage
5. Code review before merge

#### Pathway B: Partially Confirmed → Refinement
**Action**: Iterate on approach and re-test
1. Identify what failed (e.g., query complexity handling)
2. Try alternative configuration or optimization
3. Create follow-up spike or feature branch
4. Re-run experiment with improvements

#### Pathway C: Rejected → Document and Archive
**Action**: Document findings, suggest alternative
1. Document clearly why hypothesis failed
2. Note in CHANGELOG under "Investigated but Rejected"
3. Keep test for historical reference
4. Recommend alternative approach

#### Pathway D: Deferred → Future Consideration
**Action**: Good idea but wrong timing
1. Document feasibility clearly (hypothesis was confirmed)
2. Note why we're deferring (timing, resources, priority)
3. Add to roadmap for v2.0 or future milestone
4. Periodically review for changed circumstances

---

## 7. Recommendations

### Immediate Action

1. [Specific next step based on findings]
2. [Specific next step]
3. [If applicable: timeline estimate]

**Example**:
1. Implement PostgreSQL full-text search for simple keyword queries
2. Defer advanced boolean/phrase query support to v2.0
3. Create database index optimization ADR
4. Estimated effort: 3-5 days for feature implementation

### If Proceeding
- Create ADR: `ADR-NNN: [Decision Title]`
- Create feature branch: `feat/feature-name`
- Effort estimate: [T-shirt size: XS/S/M/L/XL]
- Owner: [Who leads implementation?]

### If Rejected
- Root cause: [Why hypothesis failed]
- Alternative: [Suggested approach instead]
- Document: [What to add to CHANGELOG?]

---

## 8. References

- [Link to related spike]
- [Link to documentation]
- [Link to issue or discussion]
- [Link to supporting article/benchmark]
- [Link to ADR if created]

---

## Appendix: Test Results Summary

**Last Run**: YYYY-MM-DD HH:MM UTC  
**Environment**: Python X.X, PostgreSQL X, Docker, [other relevant versions]  
**Status**: ✅ All tests pass | ⚠️ Some failures | ❌ Major issues  

### Metrics Summary
- Total tests run: N
- Passed: N
- Failed: N
- Skipped: N
- Total execution time: Xh Ym

---

## Decisions

- Store all spike hypothesis documentation in spike `README.md` files
- Use this template as starting point for all new spikes
- Update spike status in `tests/spikes/README.md` index after completion
- Archive all spikes (never delete) as historical record
- Link spikes from ADRs when spike findings inform architectural decisions
