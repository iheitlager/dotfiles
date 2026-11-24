Audit the Claude Code permission surface for secret-exfiltration risk and propose hardening.

## Usage

```
/harden           Audit exfiltration surface + inventory local secrets (read-only)
/harden --fix      Audit, then propose concrete deny/allow edits and show a diff
```

The core also scans for credential files that actually exist on disk
(`harden_audit.py --no-secrets` skips this). A real secret sitting on a SILENT
path is flagged CRITICAL and forces a FAIL — exposure × presence, not just theory.

`/harden` never edits settings on its own. Even with `--fix` it shows a diff and
waits for approval before writing.

## What this checks

The threat model is **prompt injection**, not a malicious operator: a poisoned
file, PR, web page, or MCP result tricks the agent into reading a secret and
sending it outbound. The gate that stops this is the permission config — so the
audit inspects that config, not the model's intentions.

## Process

1. **Run the deterministic core** — this is the source of truth for verdicts, not
   model reasoning:

   ```
   local/bin/harden_audit.py
   ```

   It parses every settings layer (`~/.claude/settings.json`,
   `~/.claude/settings.local.json`, `./.claude/settings.json`,
   `./.claude/settings.local.json`), merges them (`deny` wins over `allow`;
   `allow` is the union), reads the posture switches (`defaultMode`,
   `skipAutoPermissionPrompt`, `bypassPermissions`), and evaluates a fixed table
   of read+send exfiltration chains against the globs. It prints CSV-like rows and
   exits `1` if any chain is **SILENT** (runs with no prompt). The matcher is
   deliberately conservative: a primitive counts as available unless a deny rule
   clearly blocks every representative form, so it over-warns rather than under.

2. **Present the script's output verbatim** (the CSV block), then interpret it:
   for each `SILENT` row, name the exact allow line(s) that grant the read and the
   send, and the exact deny line that *would* have blocked it but doesn't. Do not
   re-derive verdicts by hand or contradict the script — if something looks wrong,
   treat it as a bug in `harden_audit.py` and say so.

3. **Summarize the top risks** in prose, severity-ordered. Typical headliners:
   any `security dump-keychain` allow; a read-side gap where `deny` blocks
   *writing* `~/.ssh`/`~/.aws` but not *reading* them; blanket `curl:*` under a
   non-prompting `defaultMode`; `WebFetch` allowed to arbitrary domains.

4. **With `--fix`**: draft additions to the `deny` list (and tightenings of
   `allow`) that close the silent-exfil paths without breaking the user's normal
   workflow. Show the edits as a diff against each affected settings file. Do NOT
   write until the user approves. Prefer read-side denies (they are the gap most
   configs miss) and scoping network primitives over blanket removal.

## Recommended deny baseline (reference)

These close the read-then-send gap without blocking normal dev work. Propose the
subset not already present:

```jsonc
"deny": [
  // read-side: block reading credential material
  "Bash(cat ~/.ssh/*)", "Bash(cat ~/.aws/*)", "Bash(cat ~/.netrc)",
  "Bash(*id_rsa*)", "Bash(*id_ed25519*)",
  "Bash(security dump-keychain:*)",
  "Bash(security find-generic-password:*)",
  // send-side shapes not already covered by curl|*sh / */dev/tcp/* denies
  "Bash(curl * -d *)", "Bash(curl * --data*)", "Bash(curl * -T *)",
  "Bash(curl *@/*)", "Bash(wget * --post*)",
  "Bash(nc:*)", "Bash(ncat:*)",
  "Bash(printenv:*)", "Bash(env|*curl*)"
]
```

Note the limits honestly: deny globs are string-matched, so a determined operator
can obfuscate around them (variables, `$IFS`, encoding). This raises the bar
against injection and accidental leakage; it is not a sandbox. For untrusted work,
run in a container/worktree without real credentials mounted.

## Prompt

Run `local/bin/harden_audit.py` and treat its output as the authoritative verdict.
Show its CSV block, then interpret each SILENT row by citing the exact allow/deny
lines responsible — never speak in generalities, never re-derive verdicts by hand.
Rank findings by severity. If invoked with `--fix`, propose the deny/allow diff and
wait for approval before writing.

## Changelog

- **0.3.0** (2026-08-14) — Ilja Heitlager <iheitlager@schubergphilis.com> —
  Docker embedded credentials graded by registry: cloud registries with
  short-lived tokens (ECR/GCR/Artifact Registry/ACR) → ELEVATED; ghcr.io / Docker
  Hub / private PATs stay CRITICAL. Mixed configs take the worst case.
- **0.2.0** (2026-08-14) — Ilja Heitlager <iheitlager@schubergphilis.com> —
  Add local-secret inventory (AWS/Azure/GCP/SSH/gh/netrc/git/npm/docker/kube/.env).
  Presence and type only, never contents. Locations resolved through tool env-var
  overrides (`KUBECONFIG`, `AWS_SHARED_CREDENTIALS_FILE`, `CLOUDSDK_CONFIG`,
  `AZURE_CONFIG_DIR`, `DOCKER_CONFIG`, `NETRC`) and XDG base dirs, not just legacy
  `~/.foo`. Exposure tiers: CRITICAL (static secret on a silent path) vs ELEVATED
  (short-lived), from a declarative credential-lifetime taxonomy
  (`harden_audit.py --list-assets`); lifetime is read from file *contents* where a
  path is ambiguous (AWS STS session token vs static key). New `--no-secrets` /
  `--list-assets`; FAIL on any silent path or CRITICAL.
- **0.1.0** (2026-08-14) — Ilja Heitlager <iheitlager@schubergphilis.com> —
  Initial release. Deterministic core (`local/bin/harden_audit.py`) drives
  verdicts; command layer interprets and proposes `--fix` diffs. Review (default)
  and fix (`--fix`) modes.
