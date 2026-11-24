# Brew Package Management Specification

**Domain:** Personal Development Environment / Package Management
**Version:** 1.0.0
**Status:** Implemented
**Date:** 2026-03-28
**Owner:** Ilja Heitlager

## Overview

A hybrid imperative/declarative package management system built on Homebrew. Each topic declares its own dependencies in `brew_packages` scripts (imperative), which are executed during bootstrap. After execution, the full system state is exported to a `Brewfile` (declarative) for fast, idempotent subsequent runs.

### Philosophy

- **Topic Ownership**: Each topic owns its dependencies — no central package list to maintain
- **Imperative Bootstrap, Declarative Steady-State**: First run discovers and installs; subsequent runs converge via `brew bundle`
- **Automatic Discovery**: `dot` finds all `brew_packages` files by convention, no registration needed
- **Orphan Detection**: Packages installed but not declared in any topic are surfaced for cleanup

### Key Capabilities

- **Two-Phase Install**: Imperative topic scripts for first run, `brew bundle` for subsequent runs
- **Brewfile Export**: Snapshot of installed state for reproducibility
- **Orphan Audit**: `dot orphans` identifies untracked packages
- **Status Dashboard**: `dot status` shows installed counts, outdated packages, and cache state

---

## RFC 2119 Keywords

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

---

## Requirements

### Requirement 1: Topic-Level Declaration [MUST]

Each topic MUST declare its Homebrew dependencies in a `brew_packages` file at the topic root.

**Implementation:** `<topic>/brew_packages`

#### Scenario: Topic declares formula and cask dependencies

- GIVEN a topic directory `latex/`
- WHEN `latex/brew_packages` exists
- THEN it is discovered and executed by `dot --new`

#### Scenario: brew_packages script format

- GIVEN a `brew_packages` file
- WHEN it contains `brew install <pkg> || brew upgrade <pkg>` lines
- THEN each package is installed if missing or upgraded if outdated

---

### Requirement 2: Two-Phase Package Installation [MUST]

The system MUST support two distinct installation modes: imperative (first run) and declarative (subsequent runs).

**Implementation:** `local/bin/dot`

#### Scenario: First run or forced regeneration

- GIVEN no Brewfile exists or `--new` flag is passed
- WHEN `dot` or `dot --new` is executed
- THEN all `brew_packages` scripts are sourced in discovery order
- AND the resulting system state is exported to `$XDG_DATA_HOME/Brewfile`

#### Scenario: Subsequent run with existing Brewfile

- GIVEN a Brewfile exists at `$XDG_DATA_HOME/Brewfile`
- WHEN `dot` is executed without `--new`
- THEN `brew bundle --file=$BREWFILE` is run for fast idempotent convergence

---

### Requirement 3: Brewfile Export [MUST]

The system MUST be able to export the current Homebrew state to a Brewfile.

**Implementation:** `local/bin/dot` (`--export` flag)

#### Scenario: Export current state

- GIVEN packages are installed via Homebrew
- WHEN `dot -x` is executed
- THEN `brew bundle dump` writes current state to `$XDG_DATA_HOME/Brewfile`

---

### Requirement 4: Orphan Detection [SHOULD]

The system SHOULD detect packages installed via Homebrew but not declared in any topic's `brew_packages`.

**Implementation:** `local/bin/dot` (`orphans` subcommand)

#### Scenario: Identify untracked formulae

- GIVEN `bat` is installed but not in any `brew_packages` file
- WHEN `dot orphans` is executed
- THEN `bat` is listed as an orphaned formula
- AND the user is advised to either uninstall or add to a topic

#### Scenario: Identify untracked casks

- GIVEN `mactex` is installed but only `mactex-no-gui` is declared
- WHEN `dot orphans` is executed
- THEN `mactex` is listed as an orphaned cask

---

### Requirement 5: Bootstrap Integration [MUST]

The `script/bootstrap` MUST invoke brew package installation as part of the full system setup.

**Implementation:** `script/bootstrap` → `install_brew_packages()`

#### Scenario: Fresh machine bootstrap

- GIVEN a clean macOS installation
- WHEN `script/bootstrap` is run
- THEN `dot --new` is called to install all topic dependencies
- AND topic `install.sh` scripts are run afterward for post-brew setup

---

### Requirement 6: Stale Upgrade Cleanup [SHOULD]

The system SHOULD detect and clean up stale Homebrew upgrade directories before installing.

**Implementation:** `local/bin/dot` (stale dir cleanup)

#### Scenario: Stale cask upgrade directory

- GIVEN `/opt/homebrew/Caskroom/<pkg>/<version>.upgrading` exists from a failed upgrade
- WHEN `dot --new` is executed
- THEN the stale directory is removed before proceeding

---

## Data Flow

```
                        ┌─────────────────────────────┐
                        │    script/bootstrap          │
                        │    (first run)               │
                        └──────────┬──────────────────┘
                                   │
                                   ▼
                        ┌─────────────────────────────┐
                        │    dot --new                 │
                        │    (imperative phase)        │
                        │                             │
                        │  for each topic:            │
                        │    source brew_packages     │
                        │      → brew install || upgrade│
                        └──────────┬──────────────────┘
                                   │
                                   ▼
                        ┌─────────────────────────────┐
                        │    brew bundle dump          │
                        │    → $XDG_DATA_HOME/Brewfile │
                        │    (export snapshot)         │
                        └──────────┬──────────────────┘
                                   │
                    subsequent runs │
                                   ▼
                        ┌─────────────────────────────┐
                        │    dot                       │
                        │    (declarative phase)       │
                        │                             │
                        │    brew bundle --file=...    │
                        │    (fast, idempotent)        │
                        └─────────────────────────────┘
```

## Maintenance Commands

| Command | Purpose |
|---------|---------|
| `dot` | Install from existing Brewfile (declarative) |
| `dot --new` | Regenerate from topic scripts (imperative) |
| `dot -x` | Export current state to Brewfile |
| `dot status` | Show installed packages, outdated, cache state |
| `dot orphans` | List installed packages not tracked in dotfiles |
| `dot invalidate` | Clear shell caches |

---

## Related Specifications

- [001-dotfiles-core](../001-dotfiles-core/spec.md) - Topic organization and bootstrap
- [002-dotfiles-caching](../002-dotfiles-caching/spec.md) - Shell caching system
