# Grounded C4: Architecture Modeling Integration with OpenSpec

**Status:** Proposed
**Date:** 2026-02-11
**Author:** Ilja Heitlager

---

## Intent

Extend the OpenSpec system to include architectural modeling alongside behavioral specifications. The goal is to create a **spec-driven development system** where architecture documentation lives next to requirements, providing traceability from specs → architecture → implementation.

### Problem Statement

Currently, OpenSpec provides excellent behavioral specification through requirements and scenarios, but lacks:

1. **Structural views**: No way to model resources, components, and their relationships
2. **Behavioral flows**: No sequence diagrams or state machines linked to specs
3. **Traceability**: Missing connections between specs, architecture, and code
4. **Reverse engineering**: No tools to extract architecture from existing codebases
5. **Visualization**: Requirements are textual; architecture needs diagrams

### Solution: Grounded C4

Combine:
- **C4's progressive zoom** (Context → Container → Component → Code)
- **Ilograph's concrete modeling** (model actual resources, not abstractions)
- **Sequence diagrams** (runtime interactions)
- **State machines** (operational states)
- **OpenSpec integration** (specs reference architecture, architecture references code)

---

## Scope

### In Scope

**Phase 1: Core Modeling (MVP)**
- YAML-based resource model (resources, relationships, interfaces)
- Validation tooling (schema validation, referential integrity)
- Basic visualization (generate Mermaid diagrams)
- Integration with OpenSpec (architecture/ directory, delta architecture)

**Phase 2: Behavioral Modeling**
- Sequence definitions (runtime flows)
- State machine definitions (operational states)
- Link sequences to spec scenarios
- Generate UML sequence diagrams

**Phase 3: Reverse Engineering**
- Extract resources from config files (docker-compose, k8s manifests)
- Detect interfaces from code (API routes, event topics)
- Generate initial architecture models
- Coverage tracking (which resources are documented vs. exist)

**Phase 4: Advanced Tooling**
- Interactive architecture browser (fzf-based, like `spec`)
- Dependency visualization
- Impact analysis (what depends on this resource?)
- Integration with ADRs (link decisions to resources)

### Out of Scope

- Automatic diagram rendering (use external tools: Mermaid CLI, PlantUML)
- Real-time collaboration features
- Cloud-hosted architecture repository
- Executable architecture (code generation from models)

---

## Approach

### Directory Structure

```
.openspec/
├── architecture/                  # Main architecture (current state)
│   ├── landscape.yaml            # Top-level system context
│   ├── resources/                # Resource definitions
│   │   ├── core.yaml
│   │   ├── tools.yaml
│   │   └── shell.yaml
│   ├── sequences/                # Runtime interaction flows
│   │   ├── bootstrap-flow.yaml
│   │   └── package-install.yaml
│   ├── state-machines/           # Operational states
│   │   └── bootstrap-lifecycle.yaml
│   └── decisions/                # ADRs linked to architecture
│       ├── 001-bash-vs-zsh.md
│       └── 002-homebrew-packages.md
│
├── changes/                       # Delta architecture (proposals)
│   └── add-feature/
│       ├── proposal.md
│       ├── specs/                # Delta specs
│       ├── tasks.md
│       └── architecture/         # Delta architecture
│           ├── resources/        # New/modified resources
│           └── sequences/        # New flows
│
└── specs/                        # Behavioral specifications
    └── 001-dotfiles-core/
        └── spec.md               # Links to architecture resources
```

### Model Format (YAML)

```yaml
# resources/core.yaml
resources:
  - id: dotfiles
    name: Dotfiles System
    type: system
    description: Personal development environment management
    abstract: true
    children:
      - id: bootstrap
        name: Bootstrap Script
        type: bash-script
        technology: Bash 5.2
        repository: ~/.dotfiles/script/bootstrap
        interfaces:
          - id: cli
            protocol: bash
            direction: request-response
            description: Command-line invocation
          - id: xdg-setup
            protocol: filesystem
            direction: write
            description: Creates XDG directories

      - id: brew-manager
        name: Homebrew Package Manager
        type: bash-script
        technology: Bash 5.2
        repository: ~/.dotfiles/homebrew/brew_install.sh
        interfaces:
          - id: brew-api
            protocol: bash
            direction: request-response
            description: Invokes brew commands

relationships:
  - from: dotfiles.bootstrap.xdg-setup
    to: dotfiles.xdg-config
    description: Creates XDG_CONFIG_HOME directory

  - from: dotfiles.bootstrap.brew-install
    to: dotfiles.brew-manager.brew-api
    description: Installs Homebrew packages from all topics
```

### Tooling: `arch` Command

```bash
# Browse architecture interactively
arch

# List all resources
arch list

# Show system landscape
arch landscape

# Validate architecture model
arch validate

# Generate diagrams
arch diagram --format=mermaid --output=docs/architecture.md

# Reverse engineer from codebase
arch reverse-engineer --source=script/

# Check coverage (documented vs. actual)
arch coverage
```

### Integration with OpenSpec

**Specs reference architecture:**

```markdown
## Requirements

### Requirement: XDG Base Directory Compliance

The system MUST follow XDG Base Directory Specification.

**Architecture:**
- Resources: `dotfiles.bootstrap.xdg-setup`, `dotfiles.xdg-config`
- Interfaces: `dotfiles.bootstrap.xdg-setup` (filesystem write)
- Sequences: `bootstrap-flow.yaml`

#### Scenario: Bootstrap Creates XDG Directories
- GIVEN a fresh Mac installation
- WHEN script/bootstrap runs
- THEN it SHALL create ~/.config (XDG_CONFIG_HOME)
```

**Architecture references code:**

```yaml
# resources/core.yaml
resources:
  - id: bootstrap
    name: Bootstrap Script
    type: bash-script
    repository: ~/.dotfiles/script/bootstrap
    implementation:
      - path: script/bootstrap
        lines: 53-73
        function: setup_xdg_dirs()
      - path: script/bootstrap
        lines: 23-26
        function: XDG environment variables
```

---

## Alternatives Considered

### Alternative 1: Use Existing C4 Tools (Structurizr, PlantUML)

**Pros:**
- Mature tooling ecosystem
- Wide adoption

**Cons:**
- Separate from OpenSpec (drift risk)
- Abstract taxonomy (Container/Component debate)
- No behavior modeling (sequences, state machines)
- No reverse engineering

**Decision:** Rejected. We want tight integration with OpenSpec and concrete modeling.

### Alternative 2: Use Ilograph Directly

**Pros:**
- Excellent concrete modeling
- Visual interface

**Cons:**
- Proprietary, cloud-hosted
- No OpenSpec integration
- No local-first workflow
- Limited extensibility

**Decision:** Rejected. We want local-first, git-friendly, extensible.

### Alternative 3: ADR-Only Approach

**Pros:**
- Simple (just markdown)
- Already using ADRs

**Cons:**
- No structured model (can't query, validate, visualize)
- No progressive zoom
- No traceability to code

**Decision:** Rejected. ADRs complement architecture models but don't replace them.

---

## Impact

### Breaking Changes

None. This is a pure addition to OpenSpec.

### Dependencies

**New tools required:**
- Python 3.12+ (already required by openspec)
- PyYAML (for YAML parsing)
- jsonschema (for validation)
- Optional: Mermaid CLI (for diagram generation)

**Existing dependencies:**
- fzf (already used by `spec`)
- bat/glow (already used by `spec`)

### Migration Path

Existing OpenSpec users can adopt incrementally:
1. Start with resource definitions (no sequences/state machines)
2. Add sequences when modeling flows
3. Add reverse engineering for existing codebases
4. Link specs to architecture over time

---

## Testing Strategy

### Unit Tests

- YAML schema validation
- Referential integrity checks
- Interface resolution
- Resource path parsing

### Integration Tests

- Load multi-file architecture models
- Validate cross-file references
- Generate diagrams from models
- Reverse engineer test fixtures

### Manual Testing

1. Model the dotfiles system architecture
2. Link existing specs to architecture
3. Generate diagrams for README
4. Reverse engineer from script/ directory
5. Validate coverage against actual code

---

## Implementation Phases

### Phase 1: Core Modeling (2-3 weeks)

**Goals:**
- Define YAML schemas for resources and relationships
- Implement `arch` CLI tool with basic commands
- Validate models (schema + referential integrity)
- Generate basic Mermaid diagrams

**Deliverables:**
- OpenSpec specification (008-grounded-c4-architecture)
- Design document (docs/grounded-c4.md)
- `arch` tool implementation (local/bin/arch)
- Schema definitions (share/arch/schemas/)
- Sample architecture (dotfiles system)

### Phase 2: Behavioral Modeling (1-2 weeks)

**Goals:**
- Add sequence and state machine definitions
- Link sequences to spec scenarios
- Generate UML sequence diagrams

**Deliverables:**
- Sequence schema
- State machine schema
- Diagram generation (sequences)
- Sample sequences (bootstrap flow)

### Phase 3: Reverse Engineering (2 weeks)

**Goals:**
- Extract resources from config files
- Detect interfaces from code
- Coverage tracking

**Deliverables:**
- Reverse engineering tool
- Coverage command
- Integration with existing tools

### Phase 4: Advanced Tooling (1-2 weeks)

**Goals:**
- Interactive browser
- Dependency visualization
- Impact analysis

**Deliverables:**
- `arch` fzf browser
- Dependency queries
- ADR integration

---

## Success Criteria

1. **Spec-Architecture Traceability**: Every spec requirement can link to architecture resources
2. **Code Traceability**: Every architecture resource can link to implementation code
3. **Validation**: Architecture models are validated for consistency and completeness
4. **Visualization**: Can generate C4-style diagrams at multiple zoom levels
5. **Reverse Engineering**: Can extract architecture from existing codebases
6. **Adoption**: Successfully model dotfiles system architecture and link to existing specs

---

## Next Steps

1. **Write OpenSpec specification** (008-grounded-c4-architecture/spec.md)
2. **Create detailed design doc** (docs/grounded-c4.md)
3. **Create GitHub epic** with phased tasks
4. **Implement Phase 1**:
   - Schema definitions
   - `arch` CLI tool skeleton
   - Validation logic
   - Basic diagram generation
5. **Model dotfiles architecture** as proof-of-concept
6. **Iterate based on feedback**

---

**License:** Apache-2.0
**Copyright:** 2026 Ilja Heitlager
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
