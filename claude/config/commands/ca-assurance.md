Compute ADR-0019 convergence assurance using the code-analyzer MCP server and Cypher queries.

Equivalent to `sp_progress` but graph-native: traverses the parsed code graph rather than scanning
markdown on disk. Reports implementation score, scenario test coverage, and assurance state per
requirement across all OpenSpec specs in the project.

## Prerequisites

1. The `code-analyzer` MCP server must be running and connected (`/ca-init` to configure).
2. The project must have been parsed: call `parse_directory` with the project root path if not already done.

## Steps

### 1. Parse the project

```
parse_directory(<project_root>)
get_summary()
```

Verify that the output includes `requirement`, `scenario`, and `tested_by` entity/relationship counts.
If any are zero, the project has no OpenSpec specs — stop here and tell the user.

### 2. Enumerate specs and requirement counts

```cypher
MATCH (spec:Spec)-[:HAS_REQUIREMENT]->(r:Requirement)
RETURN spec.name, spec.fqn, count(r) as requirement_count
ORDER BY spec.fqn
```

### 3. Scenario test coverage — per requirement

This is the most reliable metric currently available from the graph. Each `TESTED_BY` edge
represents a test reference declared in a scenario's `**Tests**:` line.

```cypher
MATCH (spec:Spec)-[:HAS_REQUIREMENT]->(r:Requirement)-[:CONTAINS]->(s:Scenario)-[:TESTED_BY]->(t)
RETURN spec.name, r.name, count(t) as test_refs
ORDER BY spec.fqn, r.name
```

To find requirements whose scenarios have **no** test references (untested requirements):

```cypher
MATCH (spec:Spec)-[:HAS_REQUIREMENT]->(r:Requirement)-[:CONTAINS]->(s:Scenario)
WHERE NOT (s)-[:TESTED_BY]->()
RETURN spec.name, r.name, s.name
ORDER BY spec.fqn, r.name
```

### 4. Summary metrics

```cypher
MATCH (r:Requirement)-[:CONTAINS]->(s:Scenario)
RETURN count(s) as total_scenarios

MATCH (s:Scenario)-[:TESTED_BY]->(t)
RETURN count(s) as scenario_test_links

MATCH (a:Adr)
RETURN count(a) as adr_count
```

### 5. Compute and report

From the query results, compute the **partial assurance score** (scenario coverage dimension only):

```
scenario_coverage = scenario_test_links / total_scenarios
```

Note: this is a **lower bound** on the full ADR-0019 assurance score. The full formula is:

```
structural = 0.4 × has_impl + 0.4 × scenario_coverage + 0.2 × has_rationale
confidence  = FULLY_PROVEN=1.0 | PARTIALLY_PROVEN=0.7 | UNTETHERED=0.3 | UNPROVEN=0.0
assurance   = Σ(priority_weight × structural × confidence) / Σ(priority_weight)
```

where `priority_weight` = MUST:3.0, SHOULD:1.0, MAY:0.5.

### 6. Report known gaps

**Implementation existence — use node label to filter ghost references:**

`IMPLEMENTED_BY` edges resolve to `:Module` when the file exists on disk, and to `:External_Reference`
when the file is declared in the spec but absent from the filesystem. Always filter by label:

```cypher
-- Correct: only real implementations
MATCH (r:Requirement)-[:IMPLEMENTED_BY]->(m:Module)

-- Wrong: includes spec-declared but non-existent files
MATCH (r:Requirement)-[:IMPLEMENTED_BY]->(m)
```

**Remaining gaps vs sp_progress equivalence:**

| Gap | Status | Filed Issue |
|-----|--------|-------------|
| Implementation tracing | Fixed (#335) — use `:Module` label filter | code-analyzer#335 |
| ADR rationale links | Fixed (#324, #345) | code-analyzer#324 |
| TESTED_BY edge parsing | Fixed (#343) | code-analyzer#343 |
| FQN serialization crash | Fixed (#323) | code-analyzer#323 |
| rfc_level SHOULD/MAY detection | **Open** — parser defaults all to MUST | code-analyzer#349 |

### 7. Present the report

Format the output as a dashboard matching sp_progress output:

```
Assurance (MCP/Cypher)          Project: <project_name>
────────────────────────────────────────────────────────
Specs parsed:       N
Requirements:       N
Total scenarios:    N
Tested scenarios:   N  (scenario_test_links / total_scenarios — note: test-link count, not unique scenarios)

Scenario coverage:  XX.X%  (partial assurance, awaiting IMPLEMENTED_BY + rfc_level fixes)

Requirements with no test links:
  [list from query 3]

Note: Full ADR-0019 assurance score requires code-analyzer#335, #336, #324, #323 to be resolved.
```

## When the gaps are fixed

Once `rfc_level` SHOULD/MAY detection is fixed (#349), run the full convergence assurance query.
Note: always use `:Module` label on `IMPLEMENTED_BY` targets to exclude ghost references.

```cypher
-- MUST requirements with full traceability (FULLY_PROVEN candidates)
MATCH (r:Requirement)
WHERE r.rfc_level = 'MUST'
  AND (r)-[:IMPLEMENTED_BY]->(:Module)
  AND (r)-[:ADDRESSED_BY]->(:Adr)
  AND (r)-[:CONTAINS]->(:Scenario)-[:TESTED_BY]->()
RETURN count(r) as fully_proven_must_candidates

-- MUST requirements missing real implementation (file exists)
MATCH (r:Requirement)
WHERE r.rfc_level = 'MUST'
  AND NOT (r)-[:IMPLEMENTED_BY]->(:Module)
RETURN r.fqn, r.name, 'missing_impl' as gap

-- MUST requirements missing ADR rationale
MATCH (r:Requirement)
WHERE r.rfc_level = 'MUST'
  AND NOT (r)-[:ADDRESSED_BY]->(:Adr)
RETURN r.fqn, r.name, 'missing_rationale' as gap
```
