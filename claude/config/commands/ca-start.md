Coordinate an architectural analysis session. Bootstraps the `.openspec/` traceability structure per ADR-0019 and ADR-0020 from code-analyzer.

## Reference ADRs

The OpenSpec convention and traceability metamodel are defined in:
- `~/wc/code-analyzer/.openspec/adr/0019-traceability_metamodel.md` — formal semantics of spec-code linkage (entity taxonomy, edge semantics, proof obligations, convergence invariants)
- `~/wc/code-analyzer/.openspec/adr/0020-openspec_convention.md` — directory layout, spec format, RFC 2119 usage, change workflow

Read these ADRs if you need to understand the full metamodel. The key points are inlined below.

## Steps

1. **Verify `code-analyzer` MCP is connected.** If not, stop and tell the user to run `/ca-init` and restart.

2. **Get project path** (cwd unless user specified). Note any analysis focus from the user's arguments.

3. **Parse the project** using `parse_directory` and `get_summary` to understand the codebase structure.

4. **Create GitHub issues in the fork** to track the reverse-engineering work. Use `gh issue create` against the `origin` remote (the user's fork):

   **Issue 1: Reverse-engineer OpenSpec specifications**
   ```
   Title: Reverse-engineer .openspec specs from codebase analysis
   Labels: openspec, documentation
   Body:
   ## Goal
   Reverse-engineer behavioral specifications from the existing codebase using code-analyzer.

   ## Tasks
   - [ ] Parse codebase with code-analyzer
   - [ ] Identify major subsystems and module boundaries
   - [ ] Generate one spec per subsystem in `.openspec/specs/NNN-name/spec.md`
   - [ ] Write requirements with RFC 2119 keywords (MUST/SHOULD/MAY)
   - [ ] Add `**Implementation**: <path>` references to actual source files
   - [ ] Write GIVEN-WHEN-THEN scenarios for each requirement
   - [ ] Review and refine generated specs for accuracy

   ## Reference
   - Format: ~/wc/code-analyzer/.openspec/adr/0020-openspec_convention.md
   - Metamodel: ~/wc/code-analyzer/.openspec/adr/0019-traceability_metamodel.md
   ```

   **Issue 2: Reverse-engineer Architectural Decision Records**
   ```
   Title: Reverse-engineer ADRs from codebase architectural patterns
   Labels: openspec, documentation
   Body:
   ## Goal
   Identify and document significant architectural decisions found in the codebase as ADRs.

   ## Tasks
   - [ ] Analyze codebase architecture with code-analyzer (hotspots, graph metrics, module dependencies)
   - [ ] Identify key architectural patterns and design decisions
   - [ ] Generate ADRs in `.openspec/adr/NNNN-title.md` for each significant decision
   - [ ] Link ADRs from spec requirements via `ADR-XXXX` references
   - [ ] Review and refine generated ADRs for accuracy

   ## Reference
   - Format: ~/wc/code-analyzer/.openspec/adr/0020-openspec_convention.md
   - Metamodel: ~/wc/code-analyzer/.openspec/adr/0019-traceability_metamodel.md
   ```

   Note the issue numbers — reference them in commit messages as work progresses.

5. **Bootstrap `.openspec/` structure** if it doesn't exist yet:

   ```
   .openspec/
   ├── specs/          # Behavioral specs (current implemented state)
   ├── adr/            # Architectural Decision Records
   ├── changes/        # Delta specs (proposed changes)
   └── README.md
   ```

   Create the directories. Write a `README.md` following the pattern from code-analyzer's `.openspec/README.md`, adapted to the current project.

   Add `.openspec/` to version control (do NOT gitignore it — specs are part of the project).

6. **Generate initial specs and ADRs** based on the parsed codebase:

   ### Spec format (per ADR-0020):
   ```markdown
   ---
   domain: <subsystem name>
   version: <project version or 0.1.0>
   status: draft
   date: YYYY-MM-DD
   ---

   # <Title>

   ## Overview
   <High-level description of this subsystem>

   ## Philosophy
   <Core design principles>

   ## Requirements

   ### Requirement N: <Title>
   <RFC 2119 statement: The system MUST/SHOULD/MAY ...>

   **Implementation**: src/path/to/file.py (or ADR-XXXX)

   #### Scenario: <name>
   - GIVEN ...
   - WHEN ...
   - THEN ...
   ```

   ### ADR format:
   ```markdown
   # ADR-NNNN: <Title>

   **Status**: Proposed | Accepted | Deprecated | Superseded

   **Date**: YYYY-MM-DD

   **Decision ID**: NNNN-slug

   ---

   ## Context
   <Why this decision was needed>

   ## Decision
   <What was decided>

   ## Consequences
   ### Positive
   ### Negative
   ### Neutral
   ```

   ### What to generate:
   - **One spec per major subsystem/module** discovered in the parsed graph. Use `get_summary` and `list_entities` to identify subsystem boundaries (top-level packages, major modules with high fan-in).
   - **Requirements** based on the public API surface: classes, interfaces, and exported functions. Use RFC 2119 keywords (MUST for core behavior, SHOULD for recommended patterns, MAY for optional features).
   - **Implementation references**: Every requirement MUST include an `**Implementation**: <path>` line pointing to the actual source file(s).
   - **Scenarios**: At least one GIVEN-WHEN-THEN scenario per requirement, derived from how the code is actually used (look at tests, call sites, examples).
   - **ADRs**: Generate ADRs for any significant architectural patterns discovered (e.g., dependency injection approach, module structure, key design patterns). Reference these from requirements via `ADR-XXXX` in the Implementation line.

7. **Report to the user**:
   - What `.openspec/` structure was created
   - GitHub issue numbers created for specs and ADRs reverse-engineering
   - How many specs and ADRs were generated
   - Identified gaps and next steps for refinement

## Traceability Edges (from ADR-0019)

The specs you generate establish these cross-domain edges in the traceability graph:
- **IMPLEMENTED_BY** (Requirement → code entity): via `**Implementation**: src/path` lines
- **ADDRESSED_BY** (Requirement → ADR): via `ADR-XXXX` references in Implementation lines
- **TESTED_BY** (Scenario → TestFunction): inferred later via structural analysis (Phase 2) or declared via `**Tests**: tests/path` lines on scenarios

The goal is to bootstrap the project to ADR-0019 Step 1 (baseline assessment): all specs, requirements, and scenarios exist with implementation references, ready for convergence analysis.
