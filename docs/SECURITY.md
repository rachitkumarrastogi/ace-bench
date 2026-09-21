# Security — ACE-Bench hardening notes

Local CLI + harvest tooling (not a multi-tenant web app). This pass hardens secrets
hygiene, path handling, SQL parameterization, SSRF on GitHub fetches, and rate-limit
floors. **Not** a SOC2 / formal penetration-test certification.

## Threat model

| Actor / surface | Risk |
|-----------------|------|
| Operator laptop / DGX | Token file or env leak; accidental commit of SQLite / patches |
| CLI args (`--db`, `--agent-patch`, `--out`) | Path escape / oversized patch read |
| Harvest scripts | Token echoed in logs; shell word-splitting on `REPOS` |
| GitHub HTTP client | SSRF if a URL were ever user-controlled; Authorization in error text |
| Shared host | World-readable `~/.config/ace-bench/github_token` |

Out of scope (deferred): Docker test-runner isolation (`--network none`), public HTTP API, multi-user authz.
Host-git sandbox checkout is allowlisted to `https://github.com/owner/name.git` only.

## Findings

| ID | Severity | Finding | Status |
|----|----------|---------|--------|
| S1 | P1 | Token loaders did not warn on loose file modes; scripts duplicated load logic | **Fixed** — `ace_bench.tokens` + `scripts/_load_github_token.sh` (0600 warn); never print token values |
| S2 | P1 | `--db` / `--agent-patch` / export paths unconstrained | **Fixed** — `ace_bench.paths.resolve_allowed_path` (cwd, `$HOME/ace-bench`, `/tmp`, repo root, `ACE_ALLOWED_ROOTS`); agent patch size cap 10 MiB |
| S3 | P1 | GitHub client accepted any URL string into `urlopen` | **Fixed** — allowlist `https://api.github.com` only (`ace_bench.github_url`) |
| S4 | P2 | Error strings included full request URLs / raw bodies | **Fixed** — URL query stripped; `Authorization` redacted in bodies |
| S5 | P2 | `--max-prs` / Search pacing undocumented as safety knobs | **Fixed** — hard cap 1000; Search page sleep floor ≥2.0 s documented |
| S6 | P2 | Instance ids loosely parsed; missing human row already failed but format weak | **Fixed** — `owner/repo#123` validation; fail-closed on missing baseline |
| S7 | P0 | Secrets committed in tree | **Not found** in current tree; `.gitignore` hardened further |
| S8 | P2 | SQLite growth unbounded on long harvests | **Mitigated** — `scripts/check_db_size.py` soft ~1 GiB warn (no auto-shard) |
| S9 | P2 | SQL injection via string-built queries | **OK** — `PatternStore` uses parameterized `?` binds (smoke-tested) |
| S10 | P2 | `shell=True` / subprocess with user input | **OK** — no `shell=True`; wrappers pass argv lists |

## Residual risks

- Path allowlist is a local-operator guard, not a sandbox; extend via `ACE_ALLOWED_ROOTS`.
- Token still lives in process env after load — avoid `set -x` / debug dumps of the environment.
- Harvest rate limits are polite floors, not a DoS shield against a malicious local caller.
- Checkout sandboxes do not execute agent code; do not apply/run untrusted patches outside a future Docker `--network none` test boundary.
- Formal SOC2 / WCAG / full red-team: **not claimed**.

## Operator checklist

1. `chmod 600 ~/.config/ace-bench/github_token` — never commit it.
2. Keep `ACE_DB_PATH` under `$HOME/ace-bench` or the repo `data/` tree (gitignored).
3. Prefer `REFRESH_STATUS=1` / `scripts/dgx_refresh_status.sh` for status docs (DB-only by default).
4. Run `scripts/check_db_size.py` in cron if harvests run for days.

See also: [OPS.md](OPS.md), [EVAL.md](EVAL.md).
