---
name: bootstrap
description: Create or update the project's AGENTS.md from a language template (rust default, python) and a forge template (github default, gitlab). Use when the user runs /bootstrap, or asks to set up project instructions, AGENTS.md or CLAUDE.md for a repo.
argument-hint: "[rust|python] [github|gitlab]"
---

# /bootstrap [rust|python] [github|gitlab]

Write the project's agent instructions to `./AGENTS.md`, so Claude Code, opencode and other agents read the same file. Arguments come in any order.

## /bootstrap help

If the argument is `help`, print the text below (as-is, no file changes) and stop.

```
/bootstrap [rust|python] [github|gitlab]     write ./AGENTS.md for this repo
/bootstrap help                              this text

  language  rust (default) | python   — detected from Cargo.toml / pyproject.toml
  forge     github (default) | gitlab — detected from the origin remote / .gitlab-ci.yml
  existing  AGENTS.md is merged; CLAUDE.md is moved into AGENTS.md and
            replaced by "@AGENTS.md" (Claude Code skips AGENTS.md if CLAUDE.md exists)

Workflow commands, from ticket to merge:

  /issue                 list open issues, suggest what to pick up
  /issue <text>          create an issue from a description
                         (GOAL:/CONSTRAINTS:/FORMAT:/FAILURE CONDITIONS: → prompt contract)
  /issue #N              show one issue

  /take #N               pre-flight (clean tree, rebase on main), branch, plan, implement
                         epic label → one branch, one commit per sub-ticket, one PR
  /take                  suggest issues to take

  /review [#N] [aspect]  review the branch/PR with specialist agents
                         aspects: code security tests docs types simplify all
                         posts findings to the PR, or keeps them for /pr

  /pr [draft|<base>]     create the PR/MR with summary, test plan, Closes #N,
                         and the review findings in the body
  /pr list | #N          list or show PRs

  /fix                   address the review findings, plan first
  /fix "<error>"         analyse a specific error

  /merge [#N]            check findings fixed and CI green, merge, clean up the branch
  /merge --dry-run       show what would happen

  Loop: /issue → /take #N → /review → /pr → /fix → /merge
  GitHub and GitLab: /pr, /merge.   GitHub only (gh): /issue, /take, /review, /fix.
```

## Steps

1. **Pick the language.** Use the argument if given. Otherwise: `Cargo.toml` at the root → rust; `pyproject.toml` (and no `Cargo.toml`) → python; neither → rust (the default).
2. **Pick the forge.** Use the argument if given. Otherwise: `git remote get-url origin` contains `gitlab` (incl. self-hosted GitLab hosts) or the repo has `.gitlab-ci.yml` → gitlab; else github (the default).
3. **Read the templates** next to this file: `templates/<lang>.md`, then append `templates/<forge>.md` as its own section. They are a starting point, not gospel.
4. **Fill them from the repo**, don't guess:
   - Project name and a one-line purpose from `Cargo.toml` / `pyproject.toml` / `README.md`.
   - The real `make` targets (`grep -E '^[a-z-]+:.*##' Makefile`). Replace template commands that don't exist; drop lines for tools the repo doesn't use (`deny.toml`, `clippy.toml`, `rust-toolchain.toml`, `.openspec/`, `changes/`).
   - Where ADRs and specs actually live, if anywhere. Whether the repo is public (`gh repo view --json visibility` / `glab repo view`).
   - Leave a short `## Project` section with TODOs for what only the user knows (architecture boundaries, invariants).
5. **Existing files.** Claude Code reads `AGENTS.md` only when there is no `CLAUDE.md`.
   - `AGENTS.md` exists → merge: keep its project-specific content, add missing template sections, don't duplicate.
   - `CLAUDE.md` exists → move its content into `AGENTS.md` (merged with the template), then replace `CLAUDE.md` with the single line `@AGENTS.md`, so Claude Code keeps loading it.
   - Show the user the diff before overwriting anything they wrote.
6. **Keep it lean.** The file loads on every request. Target under 120 lines; link to docs instead of copying them. Don't repeat what `~/.claude/CLAUDE.md` already says (plan first, bugs, git, branches, PR/MR rules).
7. Tell the user in two lines what was written (language, forge) and which TODOs are left. Don't commit unless asked.
