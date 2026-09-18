# Eval v0 — Django ACE score MVP (usable now)

Step-3 lite: pick high-quality Django instances from the pattern DB and score an
agent unified diff against the human baseline. **Docker agent sandbox stays stubbed**;
pass/fail is a CLI flag until sandbox lands.

| Piece | Path |
|-------|------|
| Export instances | `scripts/export_eval_instances.py` → `benchmarks/django_eval_v0.jsonl` |
| Score CLI | `scripts/score_against_human.py` |
| Helpers | `src/ace_bench/eval_v0.py` |
| Formula | `src/ace_bench/scoring.py` (`compute_ace_score`) |

## DB

| Source | Path |
|--------|------|
| Env | `ACE_DB_PATH` |
| Frozen (DGX) | `$HOME/ace-bench/data/frozen/ace_patterns_django_pre2021_6125.sqlite` |
| Live | `$HOME/ace-bench/data/ace_patterns.sqlite` filtered `repo=django/django` |

Prefer the **frozen** twin for eval so ongoing corpus harvest does not move the goalposts.

## AST proxy (important)

`compute_ace_score` wants AST node counts. Tree-sitter is not wired yet, so v0 uses:

```text
ast_nodes_proxy = max(added_lines, 1)
```

(`PatchMetrics.added_lines` = count of `+` lines in the unified diff.)

This is a **size** proxy, not syntactic complexity. When tree-sitter lands, swap
`ast_nodes_proxy()` in `eval_v0.py` without changing the ACE formula.

## Export (~50 metadata-only instances)

```bash
cd ~/ace-bench   # or local clone
export ACE_DB_PATH=$HOME/ace-bench/data/frozen/ace_patterns_django_pre2021_6125.sqlite

python3 scripts/export_eval_instances.py --limit 50
# → benchmarks/django_eval_v0.jsonl
```

Filters: `file_count` 1–8, non-empty title+body, non-empty `patch_text`, `additions>0`,
`merged_at < 2021-01-01`, prefer paths that look like tests.

JSONL is **metadata only** (no `patch_text`) so it can live in git. Patches remain in
SQLite. Optional local smoke dumps:

```bash
python3 scripts/export_eval_instances.py \
  --limit 50 \
  --write-patches-dir data/eval/patches
# data/eval/patches is gitignored
```

## Score an agent patch

```bash
# Self-smoke (human vs itself) — GitHub patches are headerless; this uses files_json
python3 scripts/score_against_human.py \
  --instance django/django#22 \
  --self-smoke \
  --passed-tests true

# Real agent emitting a normal `git diff`
python3 scripts/score_against_human.py \
  --repo django/django --pr 22 \
  --agent-patch /path/to/agent.diff \
  --passed-tests false

# Headerless agent patch: supply file list explicitly
python3 scripts/score_against_human.py \
  --instance django/django#22 \
  --agent-patch /tmp/hunks.patch \
  --agent-files tests/regressiontests/admin_views/tests.py \
  --passed-tests true
```

Printed signals:

- **ACE score** — formula with AST proxy + file ratio + pass/fail gate
- **File boundary drift** — `|F_A Δ F_H|` (symmetric set difference size)
- **Churn ratio** — agent/human `(additions+deletions)`
- **Surgical / sprawl** — vs Django baseline p50 files=2 (surgical ≤2; sprawl ≥9 ≈ past p90)

Self-smoke expectation: ACE ≈ **1.0**, drift **0**, churn_ratio **1.0**.

## What “done” looks like for plugging a real agent tomorrow

1. Load a line from `benchmarks/django_eval_v0.jsonl` (`title`, `body_snippet`, `base_sha`, `files`).
2. Checkout `base_sha` in a sandbox (Docker stub later).
3. Give the agent **issue text only** (title + body); capture unified diff → `agent.diff`.
4. Run tests → `--passed-tests true|false`.
5. `score_against_human.py --instance … --agent-patch agent.diff --passed-tests …`
6. Log ACE + drift + churn; do not treat pass/fail alone as the score.

See also [EVAL_LOOP.md](EVAL_LOOP.md) for the long-term dual-execution loop.
