# <project> — agent instructions

<one-line purpose>

## Project

<!-- TODO: architecture boundaries, invariants, what must never happen (e.g. "render never allocates"). Link ADRs. -->

## Commands

Use the Makefile; it is what CI runs.

| Task | Command |
|---|---|
| All CI gates | `make check` |
| Tests | `make test` (`cargo nextest run` if installed, else `cargo test`) |
| Lint | `make lint` (clippy `-D warnings` + `cargo fmt --check`) |
| Format | `make fmt` |
| Dependency audit | `make deny` (cargo-deny) |

Run `make check` before declaring work done.

## Code

- Stable toolchain pinned in `rust-toolchain.toml`; edition from `Cargo.toml`.
- No `mod.rs`: use `foo.rs` + `foo/`.
- Errors: `thiserror` in libraries, `anyhow` only in binaries and tests. No `unwrap()`/`expect()` in library code outside tests unless the invariant is commented.
- No `unsafe` without a `// SAFETY:` comment; prefer none.
- Clippy warnings are errors. Don't `#[allow]` without a reason in a comment.
- Public items get a doc comment. Doc examples must compile.

## Tests

- Unit tests in the module (`#[cfg(test)] mod tests`), integration tests in `tests/`.
- Property tests (`proptest`) for parsers, encoders and anything with an inverse.
- A bug fix starts with a failing test.

## Specs and decisions

- ADRs in `.openspec/adr/NNNN-title.md`; check them before an architectural change, add one when you make one.
- Specs in `.openspec/specs/NNN-name/spec.md`, requirements as `### Requirement N: Title [MUST|SHOULD|MAY]` with `**Implementation:**` and `**Tests:**` links.

## Makefile

The `## ...` after a target is what `make help` prints: 3-6 words, no asides. Detail goes in a `#` comment above the target.

## Releases

- A version bump is **one commit**: `Cargo.toml` version, `VERSION` const (if any), `CHANGELOG.md` entry, and `Cargo.lock` (`cargo update -w`). Then tag *that* commit.
- After any bump tool, run `git status` and grep the old version string repo-wide before committing.
- `feat/` → minor, `fix/` → patch, others no bump.
- Don't write markdown docs nobody asked for; update existing ones when behavior changes.
