# OpenSpec Templates

This directory contains templates for creating OpenSpec specification files.

## Available Templates

### `template.md` - Main Spec Template

**Use for**: Creating **main specs** that document current system behavior.

**Location**: `.openspec/specs/NNN-name/spec.md`

**Sections**:
- `## ADDED Requirements` - Current active requirements in the system
- `## Current Implementation` - How it's implemented
- `## Testing Requirements` - How to verify
- `## Dependencies` - What it needs
- `## Non-Functional Requirements` - Performance, reliability, etc.

**When to use**:
- Documenting existing systems
- Creating specs for new features that are being implemented directly
- Specifying systems with Status: Implemented or In Progress

**Example**:
```bash
cp ~/.dotfiles/local/share/spec/template.md .openspec/specs/005-my-feature/spec.md
```

---

### `template-delta.md` - Delta Spec Template

**Use for**: Creating **delta specs** that propose changes to existing specs.

**Location**: `.openspec/changes/NNN-proposal/specs/XXX-name/spec.md`

**Lifecycle Sections**:
- `## ADDED Requirements` - Brand new requirements
- `## MODIFIED Requirements` - Changes to existing requirements
- `## REMOVED Requirements` - Deprecated features
- `## RENAMED Requirements` - Requirement name changes

**Additional Sections**:
- `## Impact Analysis` - Breaking changes, dependencies
- `## Rollout Plan` - Implementation phases

**When to use**:
- Proposing changes to existing specs
- Planning new features that need approval
- Documenting breaking changes
- Removing deprecated features

**Example**:
```bash
mkdir -p .openspec/changes/006-my-change/specs/005-my-feature
cp ~/.dotfiles/local/share/spec/template-delta.md \
   .openspec/changes/006-my-change/specs/005-my-feature/spec.md
```

---

## Workflow

### 1. Main Spec Creation (New Feature)

```bash
# Create directory
mkdir -p .openspec/specs/005-my-feature

# Copy template
cp ~/.dotfiles/local/share/spec/template.md .openspec/specs/005-my-feature/spec.md

# Edit the spec
$EDITOR .openspec/specs/005-my-feature/spec.md

# Validate
openspec validate
```

### 2. Delta Spec Creation (Propose Change)

```bash
# Create change directory structure
mkdir -p .openspec/changes/001-my-proposal/specs/005-my-feature

# Copy proposal template (create manually or use)
cat > .openspec/changes/001-my-proposal/proposal.md << 'EOF'
# Proposal: My Change
**Intent**: [Why]
**Scope**: [What]
**Approach**: [How]
EOF

# Copy delta spec template
cp ~/.dotfiles/local/share/spec/template-delta.md \
   .openspec/changes/001-my-proposal/specs/005-my-feature/spec.md

# Edit delta spec
$EDITOR .openspec/changes/001-my-proposal/specs/005-my-feature/spec.md

# Create tasks checklist
cat > .openspec/changes/001-my-proposal/tasks.md << 'EOF'
# Implementation Tasks
- [ ] Phase 1: Implementation
- [ ] Phase 2: Testing
- [ ] Phase 3: Documentation
EOF

# Validate (includes delta specs)
openspec validate
```

### 3. Merge Delta to Main (Manual)

After implementing and reviewing a change:

```bash
# 1. Copy ADDED requirements from delta to main spec
# 2. Update MODIFIED requirements in main spec
# 3. Remove REMOVED requirements from main spec
# 4. Rename RENAMED requirements in main spec
# 5. Update main spec version number
# 6. Archive the change

# Move to archive
mv .openspec/changes/001-my-proposal .openspec/changes/archive/

# Validate main spec
openspec validate
```

---

## Lifecycle Marker Reference

| Marker | Purpose | In Delta Spec | In Main Spec |
|--------|---------|---------------|--------------|
| `ADDED` | New requirements | "Proposing to add" | "Currently implemented" |
| `MODIFIED` | Changed requirements | "Proposing to change" | N/A (update in place) |
| `REMOVED` | Deprecated features | "Proposing to remove" | N/A (delete from spec) |
| `RENAMED` | Name changes | "Proposing to rename" | N/A (rename in place) |

**Key Insight**: In **main specs**, `## ADDED Requirements` means "these are the current active requirements". In **delta specs**, it means "these are brand new requirements being proposed".

---

## Validation

Both templates are validated by `openspec`:

```bash
# Validate all (main + delta)
openspec validate

# Check specific spec
openspec validate my-feature

# JSON output
openspec validate --json

# Strict mode
openspec validate --strict
```

Delta specs MUST have at least one lifecycle marker section (ADDED, MODIFIED, REMOVED, or RENAMED).

---

## More Information

- **OpenSpec Documentation**: `.openspec/README.md`
- **Spec Skill**: `~/.claude/skills/spec/SKILL.md`
- **OpenSpec Specification**: `.openspec/specs/004-openspec-specification/spec.md`

---

**License:** Apache-2.0
**Copyright:** 2026 Ilja Heitlager
