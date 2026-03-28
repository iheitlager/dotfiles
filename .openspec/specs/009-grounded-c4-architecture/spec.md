# Grounded C4 Architecture Modeling System Specification

**Domain:** Software Architecture Documentation
**Version:** 1.0.0
**Status:** Proposed
**Date:** 2026-02-11
**Owner:** Ilja Heitlager

## Overview

A specification-driven architecture modeling system that integrates with OpenSpec to provide structural and behavioral documentation of software systems. Grounded C4 combines C4's progressive zoom with concrete resource modeling (Ilograph-inspired), sequence diagrams, and state machines, creating a unified model where architecture, behavior, and code are traceable.

### Philosophy

- **Concrete-First Modeling**: Model real resources with actual types (PostgreSQL, Redis, Kafka) rather than abstract classifications (Container, Component)
- **Progressive Zoom**: Support multiple zoom levels (landscape → domain → service → interface) that emerge from the model's natural nesting, not prescribed taxonomy
- **Interface-Based Relationships**: Connect specific interfaces with protocols and directionality, not vague "uses" arrows
- **Behavior Alongside Structure**: Sequences and state machines are first-class model elements, maintained alongside resources
- **Fragments Compose**: Each concern contributes YAML fragments; tooling merges and validates referential integrity
- **Traceability**: Specs reference architecture, architecture references code, creating bidirectional traceability

### Key Capabilities

- **Resource Modeling**: Define concrete resources with types, technologies, interfaces, and nesting
- **Relationship Modeling**: Connect interfaces with protocols, directionality, and intermediaries
- **Sequence Modeling**: Document runtime interactions with ordered steps referencing resources
- **State Machine Modeling**: Capture operational states and transitions for resources
- **Validation**: Schema validation and referential integrity checks across all model elements
- **Diagram Generation**: Generate Mermaid C4 diagrams, sequence diagrams, and state diagrams from models
- **Reverse Engineering**: Extract architecture from existing codebases (scripts, configs, manifests)
- **OpenSpec Integration**: Architecture models live alongside specs in `.openspec/architecture/`
- **Coverage Tracking**: Compare documented architecture against actual codebase

---

## RFC 2119 Keywords

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

---

## Requirements

### Requirement: Concrete Resource Modeling

The system MUST support modeling concrete resources with specific technology types rather than abstract classifications.

#### Scenario: Define Resource with Concrete Type

- GIVEN an architect modeling a system
- WHEN they define a resource in YAML
- THEN they SHALL specify a concrete type (e.g., `rds-postgresql`, `elasticache-redis`, `sagemaker-endpoint`)
- AND the type SHALL be technology-specific, not abstract (NOT "Database" or "Container")
- AND the resource MAY include technology metadata (version, instance type, configuration)

#### Scenario: Abstract Groupings Flagged

- GIVEN an architect creating a domain grouping
- WHEN they want to group multiple concrete resources
- THEN they SHALL mark the grouping as `abstract: true`
- AND the abstract resource MUST contain at least one concrete child
- AND validation SHALL fail if abstract resources lack children

#### Scenario: Resource Nesting

- GIVEN a resource with internal components
- WHEN modeling the structure
- THEN the resource MAY contain nested children
- AND nesting depth MAY be arbitrary (no prescribed levels)
- AND each child SHALL have a unique ID within its parent scope

### Requirement: Progressive Zoom Levels

The system MUST support multiple zoom levels that emerge from the model's nesting structure, not prescribed taxonomy.

#### Scenario: Landscape View

- GIVEN a complete architecture model
- WHEN generating a landscape view
- THEN the system SHALL show top-level resources and external systems
- AND SHALL omit internal details (interfaces, nested children)
- AND SHALL render in C4 Context diagram style

#### Scenario: Domain View

- GIVEN a resource marked as abstract (domain grouping)
- WHEN generating a domain view
- THEN the system SHALL show the abstract grouping and its direct children
- AND SHALL display concrete resource types for children
- AND SHALL render in C4 Container diagram style

#### Scenario: Service View

- GIVEN a concrete resource with interfaces
- WHEN generating a service view
- THEN the system SHALL show the resource, its interfaces, and relationships
- AND SHALL include protocol and directionality metadata
- AND SHALL render in C4 Component diagram style

#### Scenario: Custom Zoom Levels

- GIVEN a project with specific concerns
- WHEN defining zoom levels
- THEN architects MAY define custom levels appropriate to their system
- AND SHALL NOT be constrained to Context/Container/Component/Code

### Requirement: Interface-Based Relationships

The system MUST connect relationships via specific interfaces with protocols and directionality, not resource-to-resource arrows.

#### Scenario: Define Relationship

- GIVEN two resources with interfaces
- WHEN defining a relationship
- THEN the relationship SHALL specify `from` and `to` as interface references
- AND SHALL include protocol (e.g., `https`, `websocket`, `kafka`, `redis`)
- AND SHALL include direction (`publish`, `subscribe`, `request-response`, `bidirectional`, `read`, `write`)
- AND MAY include metadata (latency, rate limits, topics)

#### Scenario: Intermediate Infrastructure

- GIVEN a relationship that routes through infrastructure
- WHEN the connection uses an intermediary (API gateway, event bus, load balancer)
- THEN the relationship SHALL specify `via: <resource-ref>`
- AND diagrams SHALL show the intermediary when zoomed in
- AND diagrams SHALL elide the intermediary when zoomed out

#### Scenario: Orphan Interface Detection

- GIVEN an interface defined on a resource
- WHEN no relationship references the interface
- THEN validation SHALL emit a warning (not error)
- AND SHALL suggest the interface may be unused

### Requirement: Sequence Modeling

The system MUST support modeling runtime interactions as ordered steps that reference structural model elements.

#### Scenario: Define Sequence

- GIVEN a runtime flow to document
- WHEN defining a sequence
- THEN the sequence SHALL have an id, name, and description
- AND SHALL contain ordered steps with `from`, `to`, and `action`
- AND steps MAY include conditions (guards) and notes
- AND `from`/`to` SHALL reference resources or interfaces from the structural model

#### Scenario: Parallel Steps

- GIVEN concurrent operations in a flow
- WHEN modeling parallel execution
- THEN a step MAY contain a `parallel` array of sub-steps
- AND sequence diagrams SHALL render these as concurrent flows (fork/join)

#### Scenario: Alternative Flows

- GIVEN conditional branching in a flow
- WHEN modeling alternatives
- THEN a step MAY contain an `alt` array of alternative blocks
- AND each block SHALL have a condition and sub-steps
- AND sequence diagrams SHALL render these as alternative branches

#### Scenario: Link Sequence to Spec Scenario

- GIVEN a spec with a Given-When-Then scenario
- WHEN the scenario describes a runtime flow
- THEN the spec MAY reference a sequence by ID
- AND readers SHALL be able to follow the reference to detailed flow documentation

### Requirement: State Machine Modeling

The system MUST support modeling operational states and transitions for resources.

#### Scenario: Define State Machine

- GIVEN a resource with meaningful operational states
- WHEN defining a state machine
- THEN the state machine SHALL anchor to a specific resource via `resource` field
- AND SHALL define states with id, name, and description
- AND SHALL define transitions with `from`, `to`, `trigger`, and optional `guard`, `action`
- AND SHALL specify an initial state

#### Scenario: Link Transition to Sequence

- GIVEN a state transition that triggers a complex flow
- WHEN defining the transition
- THEN the transition MAY reference a sequence via `sequence` field
- AND readers SHALL be able to follow the reference to detailed flow documentation

#### Scenario: Generate State Diagram

- GIVEN a state machine definition
- WHEN generating diagrams
- THEN the system SHALL produce a Mermaid state diagram
- AND SHALL highlight the initial state
- AND SHALL show all states and transitions with triggers

### Requirement: Referential Integrity Validation

The system MUST validate that all references resolve to existing model elements.

#### Scenario: Validate Relationship References

- GIVEN a relationship definition
- WHEN validating the model
- THEN the system SHALL verify `from` resolves to a resource or interface
- AND SHALL verify `to` resolves to a resource or interface
- AND SHALL report errors with file, line, and path context if resolution fails

#### Scenario: Validate Sequence References

- GIVEN a sequence with steps
- WHEN validating the model
- THEN the system SHALL verify all `from`/`to` references resolve
- AND SHALL report errors if any step references non-existent resources

#### Scenario: Validate State Machine Anchoring

- GIVEN a state machine definition
- WHEN validating the model
- THEN the system SHALL verify the `resource` field points to a concrete (non-abstract) resource
- AND SHALL report an error if the resource is abstract or does not exist

#### Scenario: Unique ID Validation

- GIVEN resources in a model
- WHEN validating the model
- THEN the system SHALL verify no two siblings share an ID
- AND SHALL verify full paths are globally unique
- AND SHALL report errors for duplicate IDs

### Requirement: YAML-Based Model Format

The system MUST use YAML for human-readable, version-control-friendly architecture definitions.

#### Scenario: Single File Model

- GIVEN a small system
- WHEN defining architecture
- THEN the architect MAY define all resources in a single YAML file
- AND the file SHALL validate against the resource schema

#### Scenario: Multi-File Model (Fragments)

- GIVEN a large system with multiple concerns
- WHEN defining architecture
- THEN the architect MAY split resources across multiple YAML files
- AND SHALL organize by concern (e.g., `resources/core.yaml`, `resources/infra.yaml`)
- AND the system SHALL merge fragments on load
- AND SHALL validate cross-file references

#### Scenario: JSON Schema Validation

- GIVEN a YAML model file
- WHEN validating the model
- THEN the system SHALL validate against JSON schemas
- AND SHALL report schema violations with clear error messages
- AND schemas SHALL be versioned and extensible

### Requirement: Diagram Generation

The system MUST generate visual diagrams from architecture models.

#### Scenario: Generate Mermaid C4 Diagram

- GIVEN a valid architecture model
- WHEN generating a diagram with `--format=mermaid`
- THEN the system SHALL produce Mermaid C4 diagram syntax
- AND SHALL support multiple zoom levels (landscape, domain, service)
- AND SHALL output to stdout or file

#### Scenario: Generate Sequence Diagram

- GIVEN a sequence definition
- WHEN generating a sequence diagram
- THEN the system SHALL produce Mermaid sequence diagram syntax
- AND SHALL render parallel and alternative flows
- AND SHALL output to stdout or file

#### Scenario: Generate State Diagram

- GIVEN a state machine definition
- WHEN generating a state diagram
- THEN the system SHALL produce Mermaid state diagram syntax
- AND SHALL highlight the initial state
- AND SHALL output to stdout or file

#### Scenario: Preview Diagram in Terminal

- GIVEN a generated diagram
- WHEN previewing with `--preview`
- THEN the system SHALL use glow or bat for markdown rendering
- AND SHALL fall back to stdout if tools unavailable

### Requirement: OpenSpec Integration

The system MUST integrate with OpenSpec, enabling specs and architecture to coexist and reference each other.

#### Scenario: Architecture Directory Structure

- GIVEN an OpenSpec project
- WHEN adding architecture modeling
- THEN architecture MUST reside in `.openspec/architecture/`
- AND SHALL contain subdirectories: `resources/`, `sequences/`, `state-machines/`, `decisions/`
- AND the structure SHALL mirror `.openspec/specs/` organization

#### Scenario: Specs Reference Architecture

- GIVEN a spec with a requirement
- WHEN the requirement has architectural implications
- THEN the spec MAY include an "Architecture:" section
- AND MAY reference resource IDs, interface IDs, or sequence IDs
- AND readers SHALL be able to follow references to architecture definitions

#### Scenario: Architecture References Code

- GIVEN a resource definition
- WHEN the resource is implemented in code
- THEN the resource MAY include an `implementation` section
- AND SHALL list file paths and line numbers
- AND MAY reference specific functions or classes

#### Scenario: Delta Architecture in Changes

- GIVEN a proposed feature in `.openspec/changes/[change]/`
- WHEN the feature requires architectural changes
- THEN the change MAY include `architecture/` subdirectory
- AND SHALL contain delta resources (new, modified, removed)
- AND SHALL validate against the baseline architecture

### Requirement: Reverse Engineering

The system SHOULD support extracting architecture from existing codebases to bootstrap documentation.

#### Scenario: Extract from Bash Scripts

- GIVEN bash scripts in a directory
- WHEN running reverse engineering
- THEN the system SHALL detect scripts as resources
- AND SHALL extract functions as nested components
- AND SHALL detect interfaces (environment variables, file operations, external commands)
- AND SHALL generate initial YAML model

#### Scenario: Extract from Docker Compose

- GIVEN a docker-compose.yml file
- WHEN running reverse engineering
- THEN the system SHALL extract services as resources
- AND SHALL detect volumes, networks, and ports as interfaces
- AND SHALL generate relationships based on service dependencies
- AND SHALL generate initial YAML model

#### Scenario: Extract from Kubernetes Manifests

- GIVEN Kubernetes YAML manifests
- WHEN running reverse engineering
- THEN the system SHALL extract Pods, Services, Deployments as resources
- AND SHALL detect ports, volumes, config maps as interfaces
- AND SHALL generate relationships based on label selectors
- AND SHALL generate initial YAML model

#### Scenario: Interactive Confirmation

- GIVEN reverse engineering results
- WHEN writing to architecture directory
- THEN the system SHALL prompt for confirmation
- AND SHALL show preview of changes
- AND MAY allow editing before writing

### Requirement: Coverage Tracking

The system SHOULD track which resources are documented vs. exist in code.

#### Scenario: Scan Codebase for Resources

- GIVEN a codebase directory
- WHEN running coverage analysis
- THEN the system SHALL scan for scripts, services, configs
- AND SHALL build a list of actual resources

#### Scenario: Compare Against Model

- GIVEN actual resources and architecture model
- WHEN calculating coverage
- THEN the system SHALL report documented resources (in model)
- AND SHALL report undocumented resources (exist but not in model)
- AND SHALL report orphaned resources (in model but don't exist)

#### Scenario: Coverage Report

- GIVEN coverage analysis results
- WHEN displaying the report
- THEN the system SHALL show summary statistics
- AND SHALL use color coding (green=documented, red=undocumented, yellow=orphaned)
- AND SHALL support table and JSON output formats

### Requirement: Interactive Architecture Browser

The system SHOULD provide an interactive fzf-based browser for exploring architecture (similar to `spec` for specs).

#### Scenario: Browse Resources

- GIVEN a valid architecture model
- WHEN running `arch` (interactive mode)
- THEN the system SHALL display an fzf browser
- AND SHALL show resources in tree structure
- AND SHALL preview resource details in fzf pane

#### Scenario: Navigate Relationships

- GIVEN a resource with relationships
- WHEN viewing in the browser
- THEN the system SHALL show incoming and outgoing relationships
- AND SHALL allow jumping to related resources

#### Scenario: View Interfaces

- GIVEN a resource with interfaces
- WHEN viewing in the browser
- THEN the system SHALL list all interfaces with protocols
- AND SHALL show which relationships use each interface

---

## Current Implementation

**Status:** Not yet implemented (Proposed)

This specification describes the intended behavior of the Grounded C4 architecture modeling system. Implementation will follow the phased approach outlined in the proposal and tasks documents.

---

## Testing Requirements

### Unit Tests

- Schema validation (valid and invalid YAML)
- Resource loading and parsing
- Referential integrity validation
- Diagram generation
- Reverse engineering extractors

### Integration Tests

- Multi-file model loading
- Cross-file referential integrity
- End-to-end diagram generation
- Reverse engineering workflows
- Coverage analysis

### Manual Testing

1. Model the dotfiles system architecture
2. Link architecture to existing specs
3. Generate diagrams for README
4. Reverse engineer from script/ directory
5. Validate coverage against actual code

---

## Dependencies

### Required

- Python 3.12+
- PyYAML (YAML parsing)
- jsonschema (schema validation)

### Optional

- fzf (interactive browser)
- glow or bat (markdown rendering)
- Mermaid CLI (diagram rendering)

---

## Non-Functional Requirements

### Performance

- Model loading SHOULD complete in <1 second for typical projects (<100 resources)
- Validation SHOULD complete in <2 seconds for typical projects
- Diagram generation SHOULD complete in <3 seconds for typical views

### Usability

- Error messages MUST include file, line, and context
- CLI output SHOULD use color for readability
- Interactive browser SHOULD feel responsive (no lag)

### Compatibility

- YAML format MUST be git-friendly (diffable, mergeable)
- Schema versions MUST be backward compatible
- Diagram format SHOULD be tool-agnostic (Mermaid, PlantUML, etc.)

---

## Security

- The system MUST NOT execute untrusted code from YAML files
- Reverse engineering MUST NOT modify source code (read-only)
- Coverage tracking MUST NOT expose sensitive paths in public reports

---

## References

- **RFC 2119**: https://datatracker.ietf.org/doc/html/rfc2119
- **C4 Model**: https://c4model.com/
- **Ilograph**: https://www.ilograph.com/
- **Mermaid**: https://mermaid.js.org/
- **OpenSpec**: https://github.com/Fission-AI/OpenSpec

## Internal Documentation

- **Proposal**: `.openspec/changes/grounded-c4-architecture/proposal.md`
- **Tasks**: `.openspec/changes/grounded-c4-architecture/tasks.md`
- **Design Doc**: `docs/grounded-c4.md` (to be created)

---

**License:** Apache-2.0
**Copyright:** 2026 Ilja Heitlager
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
