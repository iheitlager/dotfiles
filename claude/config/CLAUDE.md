# Claude Code Instructions

Global workflow rules for every repo. Language and project conventions live in the project's own `AGENTS.md` (or `CLAUDE.md`); create one with `/bootstrap [rust|python] [github|gitlab]`.

## Working style

- **Plan before implementing.** For any non-trivial change (>1 file or >20 lines), give a 3-5 line plan first: which files change, the approach, what could go wrong. Wait for approval. Trivial changes (one-liner, typo, config): just do it.
- **Simplicity first.** Minimum code for today's problem. No speculative abstractions, no Strategy pattern for one implementation, no config for one value. Refactor when the second use case arrives.
- **Surgical changes.** Touch only what the task needs. Don't reformat adjacent code or restyle untouched functions. The diff should trace entirely to the request.
- Read files before modifying them. Track multi-step work with a todo list.

## Token economy

Every request resends the whole context, so size is the cost.

- **Read narrow.** `grep` first, then read with `offset`/`limit`. Don't re-read a file you just edited.
- **Keep bulk output out of the main context.** Big searches or sweeps go to a subagent; noisy commands get `head`/`tail`/`grep`.
- **Answer first, briefly.** No restating the request, no recap of a diff the user can see.
- **Say when to clear.** At a task boundary, or past 200k context (statusline 100%), suggest `/clear` or `/compact`.

## Bugs and test failures: own them

- Fix bugs you find, whatever their origin. You may note once, factually, that it was already on main; then fix it anyway.
- If a fix is out of scope or risky, say so and propose the fix; don't just move on.
- Test failures block the PR, whoever introduced them.

## Bash and git

- Use Bash and git freely (tests, builds, installs, commits, branches, rebases, pushes). No need to ask.
- No force pushes or hard resets unless explicitly asked.
- **Commit signing failure = I'm away.** Signing goes through 1Password and needs my fingerprint. If a signed commit or tag fails, don't retry and don't bypass signing (no `--no-gpg-sign`, no config changes). Stop and say you're waiting until I'm back.

## Branches and worktrees

| Type | Format | Version impact |
|---|---|---|
| Feature | `feat/xxx` | minor |
| Bug fix | `fix/xxx` | patch |
| Refactor | `refactor/xxx` | none |
| Spike | `spike/NNN_xxx` | none |
| Docs | `docs/xxx` | none |
| Chore | `chore/xxx` | none |

`agent-XX` branches (e.g. `agent-1`) are **worktree base branches**, not feature branches: never push them, never open a PR from them. In a worktree: `git fetch && git rebase origin/main`, then `git checkout -b feat/...`, push that and open the PR from it.

## GitHub / GitLab

Same rules for PRs (GitHub) and MRs (GitLab); the project's `AGENTS.md` names the forge and its CLI.

- Comments posted with `gh issue comment` / `gh pr comment` / `glab issue note` / `glab mr note create` end with:

  ```
  ---
  🤖 *Analysis by Claude*
  ```

- **Finish the issue in the PR.** Close every open acceptance criterion on the same branch (missing tests, unmeasured perf claims, uncovered paths), then write `Closes #N`. Don't use `Related to #N` to dodge leftovers.
- Open a follow-up issue (with `gh issue create` / `glab issue create`, without asking, and link it) only when a criterion truly can't be done in this repo; still write `Closes #N`.
- `Related to #N` only for planned partial work (phase 1 of 3, one step of an epic).
- Never put close/fix/resolve before `#N` in a negated sentence; GitHub ignores the negation.
- In code repos, after an investigation, propose issues for the findings before implementing.
