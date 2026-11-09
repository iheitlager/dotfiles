# ADR-001: Home root folder policy — what stays at `~` and why

- **Status:** Accepted
- **Date:** 2026-11-09
- **Deciders:** iheitlager

## Context

The home root had accumulated ~30 dotdirs over the years. This repo follows the
XDG Base Directory spec (`~/.config`, `~/.local/share`, `~/.local/state`,
`~/.cache`), redirecting tools via env vars in each topic's `bash_env`. That made
several root dirs stale leftovers, while other tools have no XDG support at all
and must keep their root path.

## Decision

Everything lives under XDG dirs **unless** a tool hardcodes its root path or the
dir is an OS/app convention. The rule:

1. Tool supports an env var → set it in the topic's `bash_env`
   (`CARGO_HOME`, `RUSTUP_HOME`, `AWS_CONFIG_FILE`, `NPM_CONFIG_USERCONFIG`,
   `ANSIBLE_HOME`, `LIMA_HOME`, `COLIMA_HOME`, `BUN_INSTALL`, `OLLAMA_MODELS`,
   `DOCKER_CONFIG`, `GNUPGHOME`, `VIBE_HOME`, `BUNDLE_USER_*`, `HISTFILE`, ...).
   Rule: if an env var exists, there is **no root symlink** — the root entry disappears.
2. Tool has no env support → keep the root path as a **symlink** to the XDG
   location (`~/.duckdb` → `~/.local/share/duckdb`, `~/.cdk` → `~/.cache/cdk`,
   `~/.cups` → `~/.config/cups`, `~/.sigstore` → `~/.config/sigstore`,
   `~/.duckdb_history` → `~/.local/state/duckdb/history`). Wired in
   `osx/install.sh`. Tools that can be configured themselves (e.g. column-rs)
   get no symlink — their own config points at the XDG path directly.
3. App home that must exist at root and holds versionable config → symlink the
   whole dir into the repo (`~/.vibe` → `~/.dotfiles/ai/vibe/config`; runtime
   files inside are gitignored). Same triple-layer pattern as
   `claude/` (`~/.claude` keeps runtime, config symlinked from `~/.config/claude`).

### Kept at root (no XDG support / OS convention)

| Path | Why it stays |
|---|---|
| `~/.ssh` | OpenSSH hardcodes it; no env override |
| `~/.Trash` | macOS Finder system path |
| `~/.cisco`, `~/.vpn` | Cisco AnyConnect system install |
| `~/.bash_sessions` | macOS `/etc/bashrc` session persistence |
| `~/.vscode` | VS Code extensions dir, no XDG support |
| `~/.claude` | Claude Code app home; versioned config is layered out to `~/.config/claude` via symlinks (triple-layer), runtime state (`jobs/`, `projects/`) stays |
| `~/.ollama` | Only models move (`OLLAMA_MODELS`); keypair + cache stay |
| `~/.espup`, `~/.paper-scanner` | tiny app dirs, hardcoded paths |
| `~/Applications`, `~/Desktop`, ... | standard macOS/user dirs |

### Removed or relocated (2026-11-09 cleanup)

| Root item | Action | Live location |
|---|---|---|
| `~/.aws` | removed (stale) | `~/.config/aws` via `AWS_CONFIG_FILE` / `AWS_SHARED_CREDENTIALS_FILE` |
| `~/.ansible` | removed (stale) | `~/.config/ansible` via `ANSIBLE_HOME` |
| `~/.npm`, `~/.npmrc` | settings merged, removed | `~/.config/npm/npmrc`, `~/.cache/npm` |
| `~/.cargo`, `~/.rustup` | removed (stale; root-owned remnants need `sudo rm -rf`) | `~/.local/share/cargo`, `~/.local/share/rustup` |
| `~/.bun` | moved | `~/.local/share/bun` via `BUN_INSTALL` (node topic) |
| `~/.lima` | moved | `~/.local/share/lima` via `LIMA_HOME` |
| `~/.duckdb`, `~/.cdk`, `~/.duckdb_history` | symlinked | `~/.local/share/duckdb`, `~/.cache/cdk`, `~/.local/state/duckdb/history` |
| `~/.bundle` | no root entry — env vars only | `~/.cache/bundle` etc. via `BUNDLE_USER_*` (ruby topic) |
| `~/.vibe` | no root entry — env var only | `$XDG_CONFIG_HOME/vibe` via `VIBE_HOME` (→ repo `ai/vibe/config`); a root symlink exists only transiently while a session that started before the switch is running |
| `~/.column-rs_history` | root stub removed; column-rs itself is configured to use XDG state | `~/.local/state/column-rs/history` |
| `~/.wasi-sdk` | removed (empty dir) | — |
| `~/.cups` | symlinked | `~/.config/cups` |
| `~/.sigstore` | symlinked (key material moved manually, never by automation) | `~/.config/sigstore`, mode 0700 |
| `~/.gnupg` | moved via `GNUPGHOME` (guarded export in `osx/bash_env` until keyring is moved manually) | `~/.config/gnupg`, mode 0700 |
| `~/.config/colima` (21G orphaned VM disks), `~/.cache/colima` | purged | colima home is now `~/.local/share/colima` via `COLIMA_HOME` |
| `~/.DS_Store`, `~/.claude.json*` | removed (junk; `.claude.json` is recreated by Claude Code, see anthropics/claude-code#22260 — `dot clean` removes it) | — |

## Consequences

- Positive: home root is down to OS conventions, user dirs, and the keep-list;
  all tool state is under XDG dirs or versioned in this repo.
- Negative / risks: GUI apps and non-login contexts don't see the `bash_env`
  env vars, so they fall back to the hardcoded root paths — for tools in rule 1
  the root dir may reappear (recreated empty); that's expected and harmless.
  Root-owned stale dirs (`~/.cargo`, `~/.rustup` from sudo installs) need a
  manual `sudo rm -rf`.
- The `dot` env cache must be invalidated when `bash_env` files change
  (`dot invalidate`); `bash_profile.symlink` now also checks per-file mtimes
  so edits regenerate the cache automatically.
