# Skill: Assurance Acceptance Criteria

> Four criteria derived from cross-log gap analysis. Apply before merging any
> new feature, measurement tool, or architectural change.

---

## The Four Checks

### 1. Spec convergence — no shims
Does every artifact (spec, code, tests) agree on names, paths, and behaviour?

- [ ] No translation dicts, aliases, or path remaps hiding a disagreement
- [ ] Spec updated alongside the code, not after or never
- [ ] `make progress` shows no new UNPROVEN or path-not-found warnings

> *Shims freeze contradictions. A divergence between spec and code is a defect,
> not a mapping problem.*

---

### 2. Quality gate passes for everyone
Does `make quality` pass on the branch before merge?

- [ ] `make quality` green (lint + format + typecheck + tests + security)
- [ ] No "I'll fix it after merge" exceptions for agent-authored PRs
- [ ] If quality dropped, understand why before re-running

> *Quality is a confidence multiplier on every requirement's assurance score.
> One failing check degrades the whole system, not just the file that failed.*

---

### 3. Complexity acknowledged, not suppressed
If static analysis flagged a complexity spike, is it resolved or documented?

- [ ] If inherent (breadth-driven, irreducible): ADR filed, `ADDRESSED_BY` wired
- [ ] If incidental (tangled logic): refactored or tracked as a debt issue
- [ ] No raw suppressions (`# noqa`, `# nosec`) without a comment explaining why

> *The goal is "flagged, evaluated, accepted" in the traceability graph —
> not "flagged and ignored."*

---

### 4. New metrics calibrated before trusted
If this PR introduces or changes a measurement dimension, was it tested for failure?

- [ ] Constructed a known-bad input and verified the metric degraded correctly
- [ ] Added a test that asserts the score fails when it should (not just passes)
- [ ] Score changes in CHANGELOG or assurance log entry

> *Adding a metric is not the same as having a reliable metric. Trust it only
> after it has been shown to fail correctly.*

---

## Usage

Run this checklist mentally (or literally) at PR review time. A PR that passes
all four is ready to merge. A PR that fails one needs either a fix or an explicit
recorded exception in the assurance log.

For automated coverage: `make quality` handles #2. The others require judgment.

**Related:** `docs/assurance_log.md` — Captured Insights (2026-02-27)
