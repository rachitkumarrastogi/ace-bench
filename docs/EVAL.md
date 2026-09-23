# Eval — score vs human + agent sandbox (step 3/4 MVP)

Copy-paste setup + $0 smokes: **[TEST.md](TEST.md)**. This page is the deeper reference.

Human harvest + pattern prior are live. **Step 3 MVP** runs a named model/agent
in a checkout at ``base_sha``, scores vs the human row, and stores ``model_name``.

## Eval modes

| Mode | Default | What it computes | Craft |
|------|---------|------------------|-------|
| **immediate** | yes | ACE (size×files) vs **same PR** human patch + `file_drift` + `churn_ratio` | omitted / `NULL` |
| **thorough** | no | Everything in immediate **plus** craft signals vs that PR's human patch | `craft_score` ∈ [0,1] |

Both modes still compare the agent to **this instance's** human fix (geometric /
overlap compare to that PR). Immediate is the fast path; thorough is slower only
because it walks diff lines for craft — still offline, no paid APIs, no extra
checkout.

CLI: `--mode immediate|thorough` on `run_agent_eval.py` and `score_against_human.py`.

### Craft v0 formula

```text
craft_score = mean(available components)

components (always attempted):
  path_jaccard   = |F_H ∩ F_A| / |F_H ∪ F_A|
  line_overlap   = fraction of human changed lines (normalized +/- bodies)
                   that appear in the agent changed-line multiset
  symbol_overlap = Jaccard of identifier tokens extracted from + hunks

optional:
  structural_sim = Python AST node-type multiset Jaccard on added snippets
                   (stdlib ast; skipped when parse fails)
```

Human-replay (identical patch) → craft ≈ **1.0**. Unrelated stub / bloated
sprawl → low. Craft is a **shape similarity** hint, not correctness and not a
substitute for ACE.

**Limits (honest):** whitespace-normalized line match is brittle to rewrites;
regex symbols miss renames; AST is Python-snippet-only and best-effort; no
embedding / LLM judge; does not search other PRs for a baseline.

---

## Loop

```
┌─────────────────────┐
│ 1. Harvest humans   │  merged PRs → harvest SQLite
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│ 2. Pattern prior DB │  p50/p90 / % surgical (optional --prior)
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│ 3. Sandbox + agent  │  ISSUE.md @ base_sha → agent.patch (named model)
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│ 4. ACE compare      │  vs human (+ craft if --mode thorough) → eval_runs
│    + AGENT_PR.md    │  PR-shaped local artifact (no real gh pr)
└─────────────────────┘
```

| Phase | Status |
|-------|--------|
| Human PR harvest | **Live** |
| Pattern prior DB | **Live** |
| Export + score-vs-human CLI | **Live** |
| Sandbox checkout @ ``base_sha`` | **MVP** — host git (Docker optional later) |
| Pluggable agents + ``model_name`` | **MVP** — `file` / `stub` / `openai` / `anthropic` |
| Eval modes + craft v0 | **MVP** — `immediate` / `thorough` |
| PR-shaped artifact (`AGENT_PR.md`) | **MVP** — local summary only (not `gh pr`) |
| Docker test runner (`--network none`) | Stub |
| Full-repo LLM context | Deferred (issue text only in v0) |
| Multi-model leaderboard UI | Deferred |

---

## Step 3 — one instance end-to-end ($0 offline)

Bill-safe quickstart uses **`file`** / **`stub` only** (no OpenAI/Anthropic keys).

```bash
cd ~/path/to/ace-bench
export ACE_DB_PATH=data/frozen/ace_patterns_django_pre2021_6125.sqlite

# Extract human patch once (for file / human-replay smoke)
python3 scripts/score_against_human.py \
  --instance django/django#22 --self-smoke --passed-tests true \
  --agent-patch /tmp/django22_human.patch

# Human-replay offline (ACE ≈ 1.0, model_name=human-replay) — immediate
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

# Same human-replay with craft (≈ 1.0)
python3 scripts/run_agent_eval.py \
  --instance django/django#22 \
  --model human-replay \
  --agent file \
  --agent-patch /tmp/django22_human.patch \
  --passed-tests true \
  --skip-sandbox \
  --mode thorough \
  --db "$ACE_DB_PATH"

# Stub tiny patch (ACE ≫ 1 — over-surgical vs human)
python3 scripts/run_agent_eval.py \
  --instance django/django#22 \
  --model stub-default \
  --agent stub \
  --passed-tests true \
  --skip-sandbox \
  --db "$ACE_DB_PATH"

# Stub bloated sprawl (ACE ≪ 1; thorough craft low)
python3 scripts/run_agent_eval.py \
  --instance django/django#22 \
  --model stub-bloated \
  --agent stub \
  --stub-bloated \
  --passed-tests true \
  --skip-sandbox \
  --mode thorough \
  --db "$ACE_DB_PATH"

# Real checkout (network) then stub agent
python3 scripts/run_agent_eval.py \
  --instance django/django#22 \
  --model stub-default \
  --agent stub \
  --passed-tests true \
  --work-root ~/ace-bench-data/sandboxes \
  --db "$ACE_DB_PATH"
```

After each run, look for **`AGENT_PR.md`** next to the saved patch (or in the
sandbox worktree). It is a **PR-shaped artifact**: title, `model_name`, ACE
score, file drift — not a real GitHub PR. Use `--no-pr-artifact` to skip.
Optional `gh pr` to a fork is **not** required and is out of scope for MVP.

Checkout only:

```bash
python3 scripts/run_sandbox_checkout.py \
  --repo django/django \
  --base-sha 02a5b41db4ff8544f93a5d9854b346a9aae4f556 \
  --work-root ~/ace-bench-data/sandboxes \
  --title "…" --body "…" --json
```

### Flags

| Flag | Notes |
|------|--------|
| `--model` | **Required** — stored as `model_name` (even for `file` / `stub`) |
| `--agent` | `file` \| `stub` \| `openai` \| `anthropic` |
| `--agent-patch` | Required for `--agent file` |
| `--mode` | `immediate` (default) \| `thorough` (adds craft) |
| `--stub-bloated` | With `--agent stub`: multi-file sprawl (ACE ≪ 1) |
| `--no-pr-artifact` | Skip writing `AGENT_PR.md` |
| `--db` | Harvest / frozen SQLite |
| `--eval-db` | Results store (default `~/ace-bench-data/eval_runs.sqlite`) |
| `--prior` | Optional pattern prior SQLite (notes only in MVP) |
| `--passed-tests` | `true` \| `false` \| `unknown` |
| `--skip-sandbox` | Offline scoring (no git clone) |
| `--work-root` | Default `~/ace-bench-data/sandboxes` or `/tmp/ace-sandbox` |

### Env (API agents)

| Var | Used by |
|-----|---------|
| `OPENAI_API_KEY` | `--agent openai` (e.g. `--model gpt-4o`) |
| `ANTHROPIC_API_KEY` | `--agent anthropic` (e.g. `--model claude-sonnet-4`) |
| `ACE_DB_PATH` | Default harvest DB |
| `ACE_SANDBOX_DOCKER` | Prefer Docker when set (checkout still host-git in MVP) |
| `ACE_ALLOWED_ROOTS` | Extend path allowlist |

API agents receive **issue title/body only** (+ optional human file-path hints). They do **not** get the full repo in v0. Missing keys → clear error; use `file` / `stub` offline.

### Results store

`src/ace_bench/eval_runs.py` → SQLite (gitignored). Schema in code: `id`, `instance_id`, `model_name`, `agent_name`, timestamps, `passed_tests`, `ace_score`, `file_drift`, `churn_ratio`, `eval_mode`, `craft_score`, `craft_json`, file lists (JSON), notes/error, `patch_path` / `patch_hash`. Craft columns are `NULL` on immediate runs. Multiple runs per `(instance, model)` allowed.

### Security

- Clone URLs: **github.com** HTTPS only for `owner/name`
- Work roots under path allowlist (`paths.py`)
- No untrusted agent code execution in this MVP
- Agent patches size-capped (10 MiB) — see [SECURITY.md](SECURITY.md)

---

## Eval v0 — score CLI (no agent)

| Piece | Path |
|-------|------|
| Export instances | `scripts/export_eval_instances.py` → `benchmarks/django_eval_v0.jsonl` |
| Score CLI | `scripts/score_against_human.py` |
| Orchestrator | `scripts/run_agent_eval.py` |
| Sandbox | `src/ace_bench/sandbox.py` + `scripts/run_sandbox_checkout.py` |
| Eval runs | `src/ace_bench/eval_runs.py` |
| Craft | `src/ace_bench/craft.py` |
| PR artifact | `src/ace_bench/pr_artifact.py` → `AGENT_PR.md` |
| Formula | `src/ace_bench/scoring.py` |

Instance ids: **`owner/repo#123`**. Prefer **frozen** Django DB so harvest does not move goalposts.

### AST proxy

```text
ast_nodes_proxy = max(added_lines, 1)
```

### Self-smoke (score CLI)

```bash
# immediate (default)
python3 scripts/score_against_human.py \
  --instance django/django#22 --self-smoke --passed-tests true

# thorough (+ craft ≈ 1.0)
python3 scripts/score_against_human.py \
  --instance django/django#22 --self-smoke --passed-tests true --mode thorough
```

Expect ACE ≈ **1.0**, drift **0**, churn_ratio **1.0**; thorough also craft ≈ **1.0**.

### Still missing

1. Real Docker test runner (`docker run --network none` + pytest gate)
2. Full-repo / file-content context for LLM agents
3. Multi-model leaderboard over `eval_runs`
4. Optional real `gh pr` to a personal fork (explicitly not MVP)
5. Richer craft (embeddings / rename-aware symbols) beyond v0
