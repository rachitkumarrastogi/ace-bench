# Test — copy-paste guide

Short path to verify the install and $0 offline eval. Deeper agent/sandbox flags and design notes: [EVAL.md](EVAL.md).

Homebrew Python enforces PEP 668 — use a **venv** (do not `pip install --break-system-packages`).

---

## 1. Setup

```bash
cd /path/to/ace-bench

# Skip create if .venv already exists
python3 -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"

export ACE_DB_PATH=data/frozen/ace_patterns_django_pre2021_6125.sqlite
```

Frozen DB must be present under `data/frozen/` (see [CORPUS.md](CORPUS.md)).  
Live harvest DBs and eval SQLite are gitignored; default results path is under `~/ace-bench-data/`.

---

## 2. Unit tests

```bash
pytest -q
```

Includes craft helpers (`tests/test_craft.py`) and existing eval/sandbox suites.

---

## 3. $0 eval (no API keys, `--skip-sandbox`)

Bill-safe smokes use **`file`** / **`stub` only**.

**Modes:** `--mode immediate` (default) = ACE + drift + churn vs same-PR human.
`--mode thorough` = same **plus** `craft_score` (path/line/symbol overlap). See [EVAL.md](EVAL.md).

### Self-smoke + extract human patch

```bash
python3 scripts/score_against_human.py \
  --instance django/django#22 --self-smoke --passed-tests true \
  --agent-patch /tmp/django22_human.patch
```

Expect ACE ≈ **1.0**, drift **0**, churn_ratio **1.0**.

Thorough self-smoke (craft ≈ **1.0**):

```bash
python3 scripts/score_against_human.py \
  --instance django/django#22 --self-smoke --passed-tests true \
  --mode thorough --json
```

### Human-replay (immediate + thorough)

```bash
python3 scripts/run_agent_eval.py \
  --instance django/django#22 \
  --model human-replay \
  --agent file \
  --agent-patch /tmp/django22_human.patch \
  --passed-tests true \
  --skip-sandbox \
  --mode immediate \
  --db "$ACE_DB_PATH" \
  --eval-db ~/ace-bench-data/eval_runs.sqlite

python3 scripts/run_agent_eval.py \
  --instance django/django#22 \
  --model human-replay \
  --agent file \
  --agent-patch /tmp/django22_human.patch \
  --passed-tests true \
  --skip-sandbox \
  --mode thorough \
  --db "$ACE_DB_PATH" \
  --eval-db ~/ace-bench-data/eval_runs.sqlite
```

Thorough human-replay: ACE ≈ **1.0**, craft ≈ **1.0**. Immediate: craft `n/a`.

### Stub (tiny patch — ACE ≫ 1)

```bash
python3 scripts/run_agent_eval.py \
  --instance django/django#22 \
  --model stub-default \
  --agent stub \
  --passed-tests true \
  --skip-sandbox \
  --db "$ACE_DB_PATH"
```

### Stub bloated (ACE ≪ 1; thorough craft low)

```bash
python3 scripts/run_agent_eval.py \
  --instance django/django#22 \
  --model stub-bloated \
  --agent stub \
  --stub-bloated \
  --passed-tests true \
  --skip-sandbox \
  --mode thorough \
  --db "$ACE_DB_PATH"
```

Expect bloated thorough `craft_score` **lower** than human-replay thorough (and typically lower than stub-default thorough).

---

## 4. Optional: real sandbox checkout

Needs network (git clone). Still $0 if you keep `--agent stub`:

```bash
python3 scripts/run_agent_eval.py \
  --instance django/django#22 \
  --model stub-default \
  --agent stub \
  --passed-tests true \
  --work-root ~/ace-bench-data/sandboxes \
  --db "$ACE_DB_PATH"
```

Checkout only:

```bash
python3 scripts/run_sandbox_checkout.py \
  --repo django/django \
  --base-sha 02a5b41db4ff8544f93a5d9854b346a9aae4f556 \
  --work-root ~/ace-bench-data/sandboxes \
  --title "…" --body "…" --json
```

---

## 5. Where results live

| Artifact | Location |
|----------|----------|
| Eval runs DB | `~/ace-bench-data/eval_runs.sqlite` (override with `--eval-db`) |
| PR-shaped summary | `AGENT_PR.md` next to the saved patch / in the sandbox worktree |
| Patches | under `--work-root` or repo `data/eval/` (gitignored) |

`AGENT_PR.md` is a **local** title / `model_name` / ACE summary — not a real GitHub PR. Use `--no-pr-artifact` to skip. Thorough runs also record `craft_score` / `craft_json` on the eval row.

### Batch ~100 (stub vs human-replay)

For a reusable offline sweep (~100 Django instances × human-replay / stub-default / stub-bloated), see **[EVAL_BATCH_100.md](EVAL_BATCH_100.md)** — summary tables, PR links, where stubs tank vs human ACE=1, and bloat. Re-run with `$0` stubs only:

```bash
python3 scripts/run_batch_eval.py \
  --limit 100 --mode thorough --skip-sandbox \
  --write-report docs/EVAL_BATCH_100.md \
  --eval-db ~/ace-bench-data/eval_runs.sqlite
```

Paid OpenAI/Anthropic are off by default; `--allow-paid` caps at 5 instances.

---

## 6. Paid agents (optional)

`--agent openai` / `--agent anthropic` need `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` and incur API cost. Prefer the $0 path above unless you intend to spend. Details: [EVAL.md](EVAL.md).
