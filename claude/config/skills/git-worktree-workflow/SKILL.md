# Git Worktree Workflow - Code Analyzer

## Overview

This project uses **Git worktrees** to enable efficient parallel development. Multiple worktrees allow you to work on different branches simultaneously without repeatedly switching branches or stashing changes.

## Why Git Worktrees?

- **Parallel Development**: Work on multiple branches at once
- **No Stashing**: Keep changes on one branch while switching to another
- **Isolated Dependencies**: Each worktree can have its own virtual environment
- **Faster Context Switching**: No need to rebuild on every branch switch
- **CI/CD Testing**: Test multiple branches before committing

## Worktree Structure

```
code-analyzer/                                 (main worktree)
├── .git
├── src/
├── tests/
└── pyproject.toml

code-analyzer-worktree/                        (worktree parent directory)
├── agent-1/                                   (branch: feat/query)
│   ├── .git → ../../../.git/worktrees/agent-1/
│   ├── src/
│   └── .venv/
├── feat-cli/                                  (branch: feat/cli)
│   ├── .git → ../../../.git/worktrees/feat-cli/
│   ├── src/
│   └── .venv/
```

**Convention**: Worktrees are created in `../code-analyzer-worktree/` directory (sibling to main repo)

## Worktree Aliases (Makefile-Like)

The project provides convenient shell aliases:

```bash
gw <branch>      # Create worktree for branch
gwc <branch>    # Create worktree + setup environment
wm <name>       # Move to worktree directory
lw              # List all worktrees
bw              # Go back to main worktree
rw <name>       # Remove worktree
pw              # Print current worktree info
cw              # Cleanup pruned worktrees
```

## Quick Workflow Examples

### Example 1: Feature Development on New Worktree

```bash
# Start in main worktree
cd ~/wc/code-analyzer

# Create and setup new worktree for feature
gwc feat/new-query-engine
# Creates: ../code-analyzer-worktree/feat-new-query-engine/
# Auto-runs: make env (creates venv + installs deps)

# Switch to new worktree
wm feat-new-query-engine

# Develop your feature
code src/code_analyzer/graph_query/optimizer.py
make test

# Commit changes
git add -A
git commit -m "feat: Implement query optimizer for graph queries"

# Back to main
bw

# Still on main worktree, original state unchanged
```

### Example 2: Bug Fix in Parallel

```bash
# While working on feature in worktree
pwd
# /Users/iheitlager/wc/code-analyzer-worktree/feat-new-query-engine

# In another terminal, create bug-fix worktree
gwc fix/database-connection

# Switch to bug-fix worktree
wm fix-database-connection

# Fix bug
make test  # Runs in isolated environment

# Commit and merge
git add -A
git commit -m "fix: Handle database reconnection timeout"

# Back to feature work
wm feat-new-query-engine
```

### Example 3: Testing Multiple Branches

```bash
# Create worktrees for testing
gw main
gw develop
gw staging

# List all worktrees
lw
# Output:
#   /Users/iheitlager/wc/code-analyzer [main]
# 👉 /Users/iheitlager/wc/code-analyzer-worktree/develop [develop]
#   /Users/iheitlager/wc/code-analyzer-worktree/staging [staging]

# Test main branch
wm main
make test

# Test develop without switching
wm develop
make test

# Test staging without switching
wm staging
make test
```

## Detailed Alias Reference

### `gw <branch>` - Create Worktree

Creates a new worktree for the specified branch.

```bash
gw feat/parser-optimization
# Creates: ../code-analyzer-worktree/feat-parser-optimization/
# Checks out branch: feat/parser-optimization
# No automatic setup (unlike gwc)
```

**Usage**:
- When you just want a quick worktree for an existing branch
- When you'll setup manually

**Shell Implementation**:
```bash
alias gw='git worktree add ../code-analyzer-worktree/$(basename $1) -b $1'
```

### `gwc <branch>` - Create + Setup

Creates worktree AND automatically sets up the development environment.

```bash
gwc feat/embedding-v2
# 1. Creates worktree
# 2. Switches to worktree
# 3. Runs: make env (creates venv + installs dependencies)
# 4. Ready to develop
```

**Usage**:
- For new features requiring full development setup
- When you want venv ready immediately

**Implementation**:
```bash
alias gwc='function() {
    branch=$1
    gw "$branch"
    cd ../code-analyzer-worktree/$(basename "$branch")
    make env
}; function'
```

### `wm <name>` - Move to Worktree

Changes current directory to specified worktree.

```bash
wm feat-parser-optimization
# cd /Users/iheitlager/wc/code-analyzer-worktree/feat-parser-optimization

wm agent-1
# cd /Users/iheitlager/wc/code-analyzer-worktree/agent-1
```

**Usage**: Switching between worktrees

**Shell Implementation**:
```bash
alias wm='cd ../code-analyzer-worktree/$1 && pwd && git branch'
```

### `lw` - List Worktrees

Lists all worktrees with branch information and current location marker.

```bash
lw
# Output:
#   /Users/iheitlager/wc/code-analyzer [main]
# 👉 /Users/iheitlager/wc/code-analyzer-worktree/agent-1 [feat/query]
#   /Users/iheitlager/wc/code-analyzer-worktree/feat-cli [feat/cli]
```

**Shell Implementation**:
```bash
alias lw='git worktree list --porcelain | awk "{print \$1, \$2}" | column -t'
```

### `bw` - Back to Main

Returns to the main worktree.

```bash
pwd
# /Users/iheitlager/wc/code-analyzer-worktree/feat-cli

bw
# cd /Users/iheitlager/wc/code-analyzer
```

**Usage**: Quick navigation back to main

**Shell Implementation**:
```bash
alias bw='cd /path/to/code-analyzer && pwd && git branch'
```

### `rw <name>` - Remove Worktree

Deletes a worktree after cleaning up its branch.

```bash
rw feat-cli
# Removes: /Users/iheitlager/wc/code-analyzer-worktree/feat-cli/
# Cleans up: .git/worktrees/feat-cli/
```

**Usage**: Cleaning up finished features

**Shell Implementation**:
```bash
alias rw='git worktree remove ../code-analyzer-worktree/$1'
```

### `pw` - Print Worktree Info

Shows information about current worktree.

```bash
pw
# Output:
# Worktree: /Users/iheitlager/wc/code-analyzer-worktree/feat-query
# Branch: feat/query
# Commit: abc1234 (feat: Add query DSL support)
```

**Implementation**:
```bash
alias pw='echo "Worktree: $(pwd)" && echo "Branch: $(git branch --show-current)" && echo "Commit: $(git log -1 --oneline)"'
```

### `cw` - Cleanup Pruned Worktrees

Removes orphaned worktree references.

```bash
cw
# Cleans up: .git/worktrees/ for deleted directories
```

**Usage**: After manually deleting worktree directories

**Shell Implementation**:
```bash
alias cw='git worktree prune'
```

## Worktree Lifecycle

### 1. Create Worktree

```bash
gwc feat/new-feature
# Creates worktree with branch and environment
```

### 2. Develop

```bash
# Make changes, commit
make test
git add -A
git commit -m "feat: Add new feature"
```

### 3. Create PR

```bash
# Push branch
git push origin feat/new-feature

# Create PR from GitHub/GitLab
```

### 4. Code Review

```bash
# Changes requested during review
# Make fixes in the worktree
git add -A
git commit -m "refactor: Address review feedback"
git push origin feat/new-feature
```

### 5. Merge

```bash
# After PR approval and merge to main
# Go back to main
bw

# Pull latest
git pull origin main
```

### 6. Cleanup

```bash
# Remove merged feature worktree
rw feat-new-feature

# List remaining worktrees
lw
```

## Worktree Isolation

Each worktree is **fully isolated**:

### Virtual Environments

```bash
# Main worktree venv
/Users/iheitlager/wc/code-analyzer/.venv

# Feature worktree venv (separate)
/Users/iheitlager/wc/code-analyzer-worktree/feat-cli/.venv

# Changes to one don't affect the other
```

### Dependency Versions

```bash
# Main has dependencies at specific version
# Feature worktree might have different versions during development
```

### Build Artifacts

```bash
# Main: build/ folder at /code-analyzer/build/
# Feature: build/ folder at code-analyzer-worktree/feat-cli/build/

# No interference between builds
```

## Best Practices

### 1. **Use `gwc` for New Development**

```bash
# Good: Setup everything in one command
gwc feat/my-feature

# Less convenient: Manual setup required
gw feat/my-feature
cd ../code-analyzer-worktree/feat-my-feature
make env
```

### 2. **Keep Worktrees Named Meaningfully**

```bash
# Good: Clear purpose
gwc fix/database-timeout
gwc feat/graph-optimization

# Bad: Unclear branch names
gwc work
gwc temp
```

### 3. **List Before Removing**

```bash
# Always check what you're removing
lw
rw feat-cli  # Confirm name matches
```

### 4. **Use `bw` to Return to Main**

```bash
# After finishing in worktree
bw

# Back to main, state unchanged
```

### 5. **Cleanup Regularly**

```bash
# Remove finished features
rw feat-old-feature

# Cleanup orphaned references
cw
```

### 6. **Don't Delete Manually**

```bash
# Bad: Direct filesystem deletion
rm -rf ../code-analyzer-worktree/feat-cli

# Good: Use git worktree command
rw feat-cli  # Cleans up properly
```

## Troubleshooting

### Issue: Worktree Not Found

```bash
lw  # List all worktrees to find correct name

# Then:
wm correct-name
```

### Issue: Branch Already Checked Out

```bash
# Error: Branch already exists in another worktree
gwc feat/existing-branch

# Solution: Use different branch name or remove old worktree
rw old-name
gwc feat/existing-branch
```

### Issue: Orphaned Worktree References

```bash
# After unexpected deletion
cw  # Cleanup pruned references
```

### Issue: Virtual Environment Issues

```bash
# Corrupt venv in worktree
rm -rf .venv
make env  # Recreate venv
```

## Advanced: Manual Worktree Operations

### Create Worktree Without Alias

```bash
git worktree add ../code-analyzer-worktree/my-branch -b my-branch
cd ../code-analyzer-worktree/my-branch
make env
```

### List Worktree Details

```bash
git worktree list --verbose
# Shows full paths and commit info
```

### Lock Worktree (Prevent Removal)

```bash
git worktree lock ../code-analyzer-worktree/critical-feature
git worktree unlock ../code-analyzer-worktree/critical-feature
```

## Integration with CI/CD

### Multiple Branch Testing

```bash
# Create worktrees for branches to test
gwc main
gwc develop
gwc staging

# Test all in parallel
for wd in main develop staging; do
    wm $wd
    make test
done
```

### Parallel Builds

```bash
# Build multiple versions without rebuilding everything
gwc v0.16.0
gwc v0.17.0-dev

wm v0.16.0
python -m build

wm v0.17.0-dev
python -m build
```

## Key Takeaway

Git worktrees transform development workflow:

| Without Worktrees | With Worktrees |
|-------------------|----------------|
| Stash/switch constantly | Multiple branches open |
| Rebuild after switch | Built environments persist |
| Sequential testing | Parallel testing |
| Context switching overhead | Zero-cost switching |

Use `gwc`, `wm`, `lw`, `bw`, `rw` for 90% of worktree operations.
