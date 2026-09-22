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

---

## 3. $0 eval (no API keys, `--skip-sandbox`)

Bill-safe smokes use **`file`** / **`stub` only**.

### Self-smoke + extract human patch

```bash
python3 scripts/score_against_human.py \
  --instance django/django#22 --self-smoke --passed-tests true \
  --agent-patch /tmp/django22_human.patch
```

Expect ACE ≈ **1.0**, drift **0**, churn_ratio **1.0**.

### Human-replay

```bash
python3 scripts/run_agent_eval.py \
  --instance django/django#22 \
  --model human-replay \
  --agent file \
  --agent-patch /tmp/django22_human.patch \
  --passed-tests true \
  --skip-sandbox \
  --db "$ACE_DB_PATH" \
  --eval-db ~/ace-bench-data/eval_runs.sqlite
```

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

### Stub bloated (ACE ≪ 1)

```bash
python3 scripts/run_agent_eval.py \
  --instance django/django#22 \
  --model stub-bloated \
  --agent stub \
  --stub-bloated \
  --passed-tests true \
  --skip-sandbox \
  --db "$ACE_DB_PATH"
```

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

`AGENT_PR.md` is a **local** title / `model_name` / ACE summary — not a real GitHub PR. Use `--no-pr-artifact` to skip.

---

## 6. Paid agents (optional)

`--agent openai` / `--agent anthropic` need `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` and incur API cost. Prefer the $0 path above unless you intend to spend. Details: [EVAL.md](EVAL.md).
