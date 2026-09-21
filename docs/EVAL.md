# Eval — score vs human (v0) + future loop

Human harvest is live. **Eval v0** (export + score CLI) is usable now; **Docker agent sandbox** stays stubbed. Full dual-execution is future work.

## Long-term loop

```
┌─────────────────────┐
│ 1. Harvest humans   │  merged PRs (pre-AI cutoff) → harvest SQLite
│    PatternStore     │  files, patch, metrics_json
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│ 2. Pattern prior DB │  cross-repo p50/p90 / % surgical (separate SQLite)
│    pattern_db.py    │  read-only vs shards; feeds ACE compare
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│ 3. Task + sandbox   │  issue/title/body + base_sha; agent → P_A, F_A
│    (sandbox stub)   │
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│ 4. ACE compare      │  vs human row + repo/global prior; pass-fail gate
│    (scoring.py v0)  │
└─────────────────────┘
```

| Phase | Status |
|-------|--------|
| Human PR harvest → SQLite | **Live** |
| Diff metrics in `metrics_json` | **Live** (AST/GNN later) |
| Pattern prior DB (step 2) | **Live** — `ace_patterns_prior.sqlite` ([CORPUS.md](CORPUS.md)) |
| Export + score-vs-human CLI | **Live** (below; per-PR human row) |
| Agent sandbox / dual execution | Stub — **blocks step 3 agent loop** |
| tree-sitter metrics | Stub in `ast_metrics.py` — v0 AST proxy = `max(added_lines, 1)` |
| Public leaderboard | Deferred |

Pattern prior path (DGX): `$HOME/ace-bench/data/patterns/ace_patterns_prior.sqlite`. Mac: `~/ace-bench-data/patterns/`. Build: `./scripts/dgx_build_patterns.sh` (does not stop harvest).

Do not treat pass/fail alone as the score — efficiency vs human structure is the point.

---

## Eval v0 — Django ACE score MVP

| Piece | Path |
|-------|------|
| Export instances | `scripts/export_eval_instances.py` → `benchmarks/django_eval_v0.jsonl` |
| Score CLI | `scripts/score_against_human.py` |
| Helpers | `src/ace_bench/eval_v0.py` |
| AST interface | `src/ace_bench/ast_metrics.py` (tree-sitter TODO; v0 fallback) |
| Formula | `src/ace_bench/scoring.py` (`compute_ace_score`) |

Instance ids must look like **`owner/repo#123`**. Missing human baseline rows fail closed (exit 2). Agent patches are size-capped (10 MiB) and path-checked — see [SECURITY.md](SECURITY.md).

### DB

| Source | Path |
|--------|------|
| Env | `ACE_DB_PATH` |
| Frozen (prefer) | `$HOME/ace-bench/data/frozen/ace_patterns_django_pre2021_6125.sqlite` |
| Live | `$HOME/ace-bench/data/ace_patterns.sqlite` filtered `repo=django/django` |

Prefer the **frozen** twin so ongoing corpus harvest does not move the goalposts. See [CORPUS.md](CORPUS.md).

### AST proxy

`compute_ace_score` wants AST node counts. `ace_bench.ast_metrics.ast_nodes_from_patch` is the swap point. Until tree-sitter + a language grammar land:

```text
ast_nodes_proxy = max(added_lines, 1)
```

(`PatchMetrics.added_lines` = count of `+` lines in the unified diff.) Size proxy only — complete the TODO in `ast_metrics.py` later without changing the ACE formula.

### Export (~50 metadata-only instances)

```bash
cd ~/ace-bench
export ACE_DB_PATH=$HOME/ace-bench/data/frozen/ace_patterns_django_pre2021_6125.sqlite

python3 scripts/export_eval_instances.py --limit 50
# → benchmarks/django_eval_v0.jsonl
```

Filters: `file_count` 1–8, non-empty title+body, non-empty `patch_text`, `additions>0`, `merged_at < 2021-01-01`, prefer test-like paths.

JSONL is **metadata only** (no `patch_text`) so it can live in git. Optional local smoke:

```bash
python3 scripts/export_eval_instances.py --limit 50 --write-patches-dir data/eval/patches
# data/eval/patches is gitignored
```

### Score an agent patch

```bash
# Self-smoke (human vs itself)
python3 scripts/score_against_human.py \
  --instance django/django#22 \
  --self-smoke \
  --passed-tests true

# Real agent unified diff
python3 scripts/score_against_human.py \
  --repo django/django --pr 22 \
  --agent-patch /path/to/agent.diff \
  --passed-tests false

# Headerless agent patch: supply file list
python3 scripts/score_against_human.py \
  --instance django/django#22 \
  --agent-patch /tmp/hunks.patch \
  --agent-files tests/regressiontests/admin_views/tests.py \
  --passed-tests true
```

Printed signals: **ACE score**, **file boundary drift** (`|F_A Δ F_H|`), **churn ratio**, **surgical / sprawl** (vs Django p50 files=2; sprawl ≥9 ≈ past p90).

Self-smoke expectation: ACE ≈ **1.0**, drift **0**, churn_ratio **1.0**.

### Plugging a real agent tomorrow

1. Load a line from `benchmarks/django_eval_v0.jsonl`.
2. Checkout `base_sha` in a sandbox (Docker later).
3. Give the agent **issue text only**; capture unified diff.
4. Run tests → `--passed-tests true|false`.
5. `score_against_human.py --instance … --agent-patch … --passed-tests …`
6. Log ACE + drift + churn — not pass/fail alone.

### Compare inputs (when sandbox exists)

From each `human_patterns` row: task (`title`/`body`), baseline (`files_json`, `patch_text`, `metrics_json`, `base_sha`), agent patch + files + test gate → `ace_bench.scoring.compute_ace_score`.
