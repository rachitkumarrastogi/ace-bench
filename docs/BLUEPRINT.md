# ACE-Bench — Executive Blueprint

Canonical narrative lives in the root [README](../README.md). This file tracks
design decisions as the harness takes shape.

## Design principles

1. **Human baseline is ground truth for efficiency**, not for correctness alone.
2. **Pass/fail is a gate**, not the score — failing tests → ACE = 0.
3. **Prefer AST metrics over line diffs** — formatting noise should not dominate.
4. **Agent-agnostic harness** — any agent that emits a patch against a checkout.

## Planned packages

| Module | Role |
|--------|------|
| `ace_bench.ingest` | PR harvest → instance JSON (issue, \(P_H\), \(F_H\), base SHA) |
| `ace_bench.sandbox` | Docker/microVM runner; collect \(P_A\), \(F_A\), traces |
| `ace_bench.analyze` | tree-sitter AST overhead, scope creep, redundancy, complexity Δ |
| `ace_bench.scoring` | ACE Index (implemented v0) |
| `ace_bench.report` | Leaderboard + per-instance reports |

## Instance schema (draft)

```json
{
  "id": "repo__pr_123",
  "repo": "owner/name",
  "base_sha": "...",
  "issue": { "title": "...", "body": "..." },
  "human": {
    "patch_path": "baselines/repo__pr_123.patch",
    "files": ["src/foo.py"]
  },
  "tests": { "command": "pytest -q", "timeout_sec": 600 }
}
```

## Open questions

- SWE-bench instance reuse vs. fresh PR harvest?
- How to weight redundancy / complexity vs. the core ACE formula?
- Multi-language AST parity (Python / TS / Rust first)?
