# Corpus — curated repos, freeze, human baseline

Machine-readable master list: [`data/corpus_repos.json`](../data/corpus_repos.json) (**~1000** repos: 5 kickoff + Tier A/B/C + Tier D backlog).  
Living coverage: [CORPUS_STATUS.md](CORPUS_STATUS.md) (`python3 scripts/refresh_corpus_status.py [--fetch-github]`).

Default cutoff for all harvests: `merged:<2021-01-01` (windowed monthly/quarterly as needed).

---

## Master list vs harvest waves

| Layer | Count | Role |
|-------|------:|------|
| Kickoff / status | 5 | Frozen Django + four mid-size libs (**done**) |
| Tier A | 15 | Mid-size, high signal |
| Tier B | 40 | Larger / more languages |
| Tier C | 50 | Heavyweights; stricter filters later |
| **Tier D** | **~890** | Ongoing backlog — `harvest_status: queued`; **do not** interrupt the live A–C run |

Harvest remains **one repo at a time**. First wave was A–C (~110). Relaunch `./scripts/dgx_corpus_harvest.sh` after the current job finishes to continue into Tier D (script reads all non-done tiers **A→B→C→D**). Optional: `CORPUS_LIMIT=N`, `CORPUS_TIERS=d`, or `QUEUE_FILE_IN=data/corpus_tier_d_queue.txt`.

---

## Kickoff (do not re-queue)

| Repo | Status | Lang | Harvested |
|------|--------|------|-----------|
| `django/django` | **DONE / frozen** | Python | **6125** |
| `pallets/flask` | DONE | Python | 1054 |
| `expressjs/express` | DONE | JavaScript | 196 |
| `spf13/cobra` | DONE | Go | 343 |
| `clap-rs/clap` | DONE | Rust | 967 |

Remaining Tier A → B → C → D: `./scripts/dgx_corpus_harvest.sh` on DGX (one repo at a time; see [OPS.md](OPS.md)).

---

## Curation principles

- Clear GitHub PR history before 2021; issue-linked merges; eventual testability.
- Diversify languages (Python, JS/TS, Go, Rust, Java, C/C++, Ruby, Kotlin, Swift, C#, PHP, Scala, Elixir, …).
- Prefer foundations / mid-tier libraries with real PR culture (CNCF-ish, Apache, Mozilla, Google/Microsoft OSS, HashiCorp, Elastic mid-tier, …).
- Skip mailing-list-primary workflows as **primary** targets (kernel, many GNU projects), mirrors, `awesome-*`, content farms.
- Heavyweights (React, VS Code, …) stay in **Tier C** with stricter filters later; Tier D adds more mid-size.
- **Never** parallelize repos — shared Search + REST rate budget.

### Harvest order

1. Kickoff batch — **done**.
2. Tier A → B → C via `scripts/dgx_corpus_harvest.sh` (continue-on-failure) — **first wave / in progress**.
3. Tier D backlog — after A–C finishes (or `CORPUS_TIERS=d` / queue file on next launch).
4. Tier C filters: full windowed harvest first is intentional; apply bot/issue/size filters later.

### Exclusions (primary harvest)

`torvalds/linux`, GNU / savannah mirrors, `awesome-*`, docs-only / joke / malware repos, post-2021-only projects, unfiltered mega-mirrors (`chromium`), generated/vendored dumps. Thin early targets: `sqlalchemy/sqlalchemy` (~53 pre-2021 merges), verify `tiangolo/fastapi` before enqueue. Full exclusion notes live in `data/corpus_repos.json` → `exclusions`.

### Tier C filter checklist (before enqueue)

- Exclude bot authors (`dependabot`, `renovate`, `github-actions`, …)
- Prefer issue-linked merges when Search allows
- Cap changed files / net lines for dual-exec tractability
- Skip pure docs/changelog/CI-only paths for “code pattern” sets

---

## Frozen Django snapshot

Immutable first human-pattern harvest.

| Field | Value |
|-------|--------|
| Repo | `django/django` |
| Cutoff | `merged:<2021-01-01` (windows `2012-01-01` → `2021-01-01`, monthly) |
| Rows | **6125** |
| Freeze date | 2026-09-18 (UTC) |
| Method | `VACUUM INTO` (+ `.bak`) |
| Path | `$HOME/ace-bench/data/frozen/ace_patterns_django_pre2021_6125.sqlite` |

- **Frozen** = do not write. Prefer for eval ([EVAL.md](EVAL.md)).
- **Live** = `ace_patterns.sqlite` / `$ACE_DB_PATH` — multi-repo upserts on `UNIQUE(repo, pr_number)`. Django rows remain in live DB alongside new repos.
- **Shards** — when live DB ≥ **1 GiB**, harvest rotates between repos into `data/shards/ace_patterns_shard_NNN.sqlite` (manifest: `data/shards_manifest.json`). Mac mirror: `~/ace-bench-data/shards/` (outside git; see [OPS.md](OPS.md)). **Never commit** `*.sqlite`.

### Recreate freeze

```bash
LIVE=~/ace-bench/data/ace_patterns.sqlite
OUT=~/ace-bench/data/frozen/ace_patterns_django_pre2021_6125.sqlite
mkdir -p "$(dirname "$OUT")"
sqlite3 "$LIVE" "VACUUM INTO '$OUT'"
cp -a "$OUT" "${OUT}.bak"
python3 scripts/run_harvest.py --db "$OUT" --summary-only
# expect total: 6125, single django/django under by_repo
```

`*.sqlite` under `data/` is gitignored; only this doc + `corpus_repos.json` are the public freeze record. Live shards and Mac copies stay on disk only (DGX `data/shards/`, Mac `~/ace-bench-data/shards/`).

---

## Human pattern baseline (Django headlines)

Statistical prior from **6125** pre-2021 Django PRs — not a live leaderboard. Agent compare is next ([EVAL.md](EVAL.md)).

Human Django PRs are **small and surgical**:

| Signal | Value |
|--------|--------|
| Median files | **2** (p90 = 8; p99 ≈ 64) |
| Median churn (add+del) | **20** lines (p90 = 136) |
| ≤2 files | **57%** of PRs |
| ≤5 files | **84%** |
| >20 files | **3.3%** (often mechanical) |
| Median decision-points / loops / funcs added | **0** |

Scoring idea: agents that routinely land 8–15 files for bugfixes are already past human p90. Prefer **p50/p90**, not means (means are mega-PR skewed). Eval v0 flags surgical ≤2 files and sprawl ≥9.

Compact live harvest coverage stays in [CORPUS_STATUS.md](CORPUS_STATUS.md); do not duplicate huge repo tables here — use the JSON.
