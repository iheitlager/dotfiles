# Grounded C4 Architecture JSON Schemas

**Version:** 1.0.0
**Date:** 2026-02-11

This directory contains JSON Schema definitions for validating Grounded C4 architecture models.

---

## Schemas

### 1. `interface.schema.json`

Defines an interface for interacting with a resource.

**Required fields:**
- `id` - Unique identifier (pattern: `^[a-z0-9-]+$`)
- `protocol` - Communication protocol (e.g., https, kafka, websocket)
- `direction` - One of: `publish`, `subscribe`, `request-response`, `bidirectional`, `read`, `write`

**Optional fields:**
- `description` - Human-readable description
- `topic` - Topic name for pub-sub protocols
- `metadata` - Extensible key-value pairs for protocol-specific details

**Example:**
```yaml
id: cache-api
protocol: redis
direction: bidirectional
description: Redis cache read/write operations
metadata:
  latency_p99: 5ms
  instance: cache.r7g.large
```

---

### 2. `resource.schema.json`

Defines a concrete or abstract resource in the architecture model.

**Required fields:**
- `id` - Unique identifier within parent scope (pattern: `^[a-z0-9-]+$`)
- `name` - Human-readable name
- `type` - Concrete type identifier (e.g., `bash-script`, `rds-postgresql`, `go-service`)

**Optional fields:**
- `abstract` - Boolean flag for logical groupings (default: `false`)
- `technology` - Specific version/configuration (e.g., "Go 1.22", "Redis 7.2")
- `description` - Detailed description
- `repository` - Repository URL or file path
- `instance` - Cloud instance type (e.g., "cache.r7g.large")
- `tags` - Array of strings for categorization
- `metadata` - Extensible key-value pairs
- `interfaces` - Array of Interface objects
- `children` - Array of nested Resource objects (recursive)
- `implementation` - Array of CodeRef objects linking to code

**Nested types:**
- **Interface** - See `interface.schema.json`
- **CodeRef** - Code reference for traceability
  - Required: `path` (file path)
  - Optional: `lines` (e.g., "53-73"), `function` (name), `description`

**Example:**
```yaml
id: bootstrap
name: Bootstrap Script
type: bash-script
technology: Bash 5.2
repository: ~/.dotfiles/script/bootstrap
interfaces:
  - id: cli
    protocol: bash
    direction: request-response
implementation:
  - path: script/bootstrap
    lines: 53-73
    function: setup_xdg_dirs()
```

---

### 3. `relationship.schema.json`

Defines a relationship connecting two interfaces or resources.

**Required fields:**
- `from` - Source InterfaceRef or ResourceRef (pattern: `^[a-z0-9.-]+$`)
- `to` - Target InterfaceRef or ResourceRef

**Optional fields:**
- `via` - Intermediate ResourceRef (e.g., API gateway, load balancer)
- `description` - What this connection does
- `tags` - Array of strings for categorization
- `metadata` - Extensible key-value pairs (latency, bandwidth, etc.)

**Path notation:**
- ResourceRef: `system.domain.service` (dotted path to resource)
- InterfaceRef: `system.domain.service.interface-id` (resource path + interface id)

**Example:**
```yaml
from: dotfiles.bootstrap.xdg-setup
to: dotfiles.xdg-dirs.config-dir
description: Creates XDG_CONFIG_HOME directory
metadata:
  operation: mkdir
```

---

## Validation Rules

### JSON Schema Level (Structural)

Enforced by these schemas:
- ✅ Required fields present
- ✅ Types correct (string, boolean, array, object)
- ✅ Enums match allowed values (e.g., `direction`)
- ✅ Patterns match (IDs: `^[a-z0-9-]+$`, paths: `^[a-z0-9.-]+$`)
- ✅ Line ranges match pattern (e.g., "42" or "53-73")

### Business Logic Level (Python Validator)

Not enforced by schemas (requires model-wide validation):
- ⚠️  Abstract resources have at least one child
- ⚠️  Referential integrity (from/to resolve to actual resources/interfaces)
- ⚠️  Unique IDs within scope (no sibling duplicates)
- ⚠️  State machine anchors to concrete (non-abstract) resource
- ⚠️  Orphan interface detection (interfaces used in no relationships)

---

## Usage

### Python (with jsonschema)

```python
import json
import yaml
from jsonschema import validate

# Load schema
with open('local/share/arch/schemas/resource.schema.json') as f:
    schema = json.load(f)

# Load and validate YAML model
with open('.openspec/architecture/resources/core.yaml') as f:
    model = yaml.safe_load(f)

# Validate
validate(instance=model, schema=schema)
```

### Command Line (with Python jsonschema)

```bash
# Install jsonschema CLI
pip install jsonschema

# Validate a YAML file
jsonschema -i architecture.yaml local/share/arch/schemas/resource.schema.json
```

### With the `arch` Tool

```bash
# Validate all architecture models
arch validate

# The tool will:
# 1. Load all YAML files from .openspec/architecture/
# 2. Validate against JSON schemas
# 3. Perform business logic validation
# 4. Report errors and warnings
```

---

## Design Decisions

### 1. Concrete Types Over Abstractions

Resources use specific types (`rds-postgresql`, `elasticache-redis`) instead of abstract classifications (`Database`, `Cache`). This makes models:
- More accurate and queryable
- Easier to map to cost/operations
- Less prone to taxonomy debates

### 2. Extensible Metadata

Both `metadata` fields and protocol-specific top-level fields (e.g., `topic`) allow flexibility without breaking schema compatibility.

### 3. Self-Referential Resources

The Resource schema uses `$ref: "#"` to allow recursive nesting of children, supporting arbitrary hierarchy depth.

### 4. Path Patterns

- **IDs**: Lowercase kebab-case (`^[a-z0-9-]+$`)
- **Paths**: Dotted notation with hyphens (`^[a-z0-9.-]+$`)

This ensures consistency and parsability.

### 5. Direction Enum

Strict validation with exactly 6 allowed values prevents typos and ensures consistency across models.

### 6. No Schema Versioning (Yet)

Versioning will be added when backward compatibility becomes necessary. For now, schemas are considered v1.0.0.

---

## Future Schemas (Phase 2)

- `sequence.schema.json` - Runtime interaction flows
- `state-machine.schema.json` - Operational state transitions

---

## References

- **JSON Schema**: https://json-schema.org/
- **Draft 07 Spec**: https://json-schema.org/draft-07/schema
- **Grounded C4 Design Doc**: `docs/grounded-c4.md`
- **OpenSpec Specification**: `.openspec/specs/008-grounded-c4-architecture/spec.md`

---

**License:** Apache-2.0
**Copyright:** 2026 Ilja Heitlager
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
