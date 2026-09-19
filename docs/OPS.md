# Ops — harvest on DGX (tokens, tmux, rate limits)

Goal: collect **pre-AI** merged PRs into local SQLite before (or alongside) the agent compare loop. Prefer a **full** human baseline over a tiny pilot cap. Linux kernel harvest is **deferred**.

Eval / scoring: [EVAL.md](EVAL.md). Corpus list + freeze: [CORPUS.md](CORPUS.md).

---

## GitHub Search 1000-result limit

Search returns **at most 1000 results per query**. Windowed harvest slices `[merged_after, merged_before)` into monthly (or daily) queries, then upserts into one SQLite DB (idempotent on `(repo, pr_number)`).

Use range qualifier `merged:YYYY-MM-DD..YYYY-MM-DD` (inclusive). Do **not** combine `merged:>=` with `merged:<` — GitHub often ignores the lower bound and inflates `total_count`.

| Mode | Script | Scope |
|------|--------|-------|
| Pilot (capped) | `scripts/dgx_harvest.sh` | `--max-prs 200` (no windows) |
| Full baseline | `scripts/dgx_full_harvest.sh` | monthly `2012-01-01` → `2021-01-01` (default: django) |
| Multi-repo kickoff | `scripts/dgx_multi_harvest.sh` | Flask / Express / Cobra / Clap |
| Full curated corpus | `scripts/dgx_corpus_harvest.sh` | Tier A→D from `data/corpus_repos.json` (~1000 master; first wave A–C) |

```bash
python3 scripts/run_harvest.py \
  --repos django/django \
  --merged-after 2012-01-01 \
  --merged-before 2021-01-01 \
  --window months \
  --window-size 1 \
  --max-prs 1000 \
  --db "$ACE_DB_PATH"
```

If a window still reports `total_count > 1000`, shrink `--window-size` (or `--window days`) and re-run.

---

## Prerequisites

- Python 3.11+
- GitHub token with public-repo read (`GITHUB_TOKEN` or `GH_TOKEN`)
- Optional: `tmux` for overnight runs

```bash
git clone git@github-rachit:rachitkumarrastogi/ace-bench.git
cd ace-bench
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

Scripts also work without install (they add `src/` to `sys.path`).

### Token (never commit)

```bash
export GITHUB_TOKEN=...   # or GH_TOKEN
# wrappers may fall back to: gh auth token
```

On DGX, prefer a mode-600 file (wrappers warn if group/other bits are set):

```bash
mkdir -p ~/.config/ace-bench
# write token once; never commit; never `cat` into logs
chmod 600 ~/.config/ace-bench/github_token
# loaders: scripts/_load_github_token.sh / ace_bench.tokens
```

Security notes: [SECURITY.md](SECURITY.md).

### DB location

| Setting | Default |
|---------|---------|
| Env | `ACE_DB_PATH` |
| Fallback | `./data/ace_patterns.sqlite` |

Prefer local disk on DGX (not NFS if possible). `data/*.sqlite` is gitignored.

Soft size guardrail (~1 GiB):

```bash
python3 scripts/check_db_size.py --db "$ACE_DB_PATH"
```

When over threshold: freeze a snapshot under `data/frozen/`, point a new `ACE_DB_PATH` at a fresh file — no automatic sharding yet.

---

## Smoke (laptop)

```bash
python3 scripts/run_harvest.py --max-prs 3 --db /tmp/ace_smoke.sqlite
python3 scripts/run_harvest.py --db /tmp/ace_smoke.sqlite --summary-only
```

---

## Overnight / tmux

```bash
export ACE_DB_PATH="$HOME/ace-bench/data/ace_patterns.sqlite"

tmux new -s ace-harvest
./scripts/dgx_full_harvest.sh          # or dgx_multi_harvest / dgx_corpus_harvest
# detach: Ctrl-b d
```

Re-attach: `tmux attach -t ace-harvest`. Harvest is **idempotent** on `(repo, pr_number)`.

### Multi-repo / corpus

```bash
# kickoff four libs (sequential)
./scripts/dgx_multi_harvest.sh
# log: data/multi_harvest.log

# Tier A→B→C→D from master list (skips done_frozen / done / in_harvest + kickoff five).
# Live ace-harvest jobs that baked in the old ~105 list are left alone — relaunch
# after they finish to pick up Tier D (~890 backlog).
./scripts/dgx_corpus_harvest.sh
# optional: refresh docs/CORPUS_STATUS.md after each repo (DB-only, no Search)
REFRESH_STATUS=1 ./scripts/dgx_corpus_harvest.sh
# staged waves / Tier D only:
CORPUS_LIMIT=50 ./scripts/dgx_corpus_harvest.sh
CORPUS_TIERS=d ./scripts/dgx_corpus_harvest.sh
QUEUE_FILE_IN=data/corpus_tier_d_queue.txt ./scripts/dgx_corpus_harvest.sh
# log: $HOME/ace-bench/data/corpus_harvest.log (override CORPUS_HARVEST_LOG)

# cron-friendly status refresh (DB-only; FETCH_GITHUB=1 to hit Search)
./scripts/dgx_refresh_status.sh
# partial Search fills for the ~1000 list:
python3 scripts/refresh_corpus_status.py --fetch-github --fetch-limit 50
```

Override repos: `REPOS="psf/requests encode/httpx" ./scripts/dgx_corpus_harvest.sh`.  
Do **not** parallelize repos. Kill only idle `ace-harvest` sessions — do not touch unrelated tmux sessions. **Do not stop** a running corpus harvest to load Tier D; wait for finish or start a follow-on with `QUEUE_FILE_IN` / `CORPUS_TIERS=d`.

### Defaults / rate limits

| Knob | Pilot | Full windowed |
|------|-------|---------------|
| Sleep (REST) | ~0.75–1.0s | same (core ≈5k req/hr) |
| Search pages | ≥2.0s floor | Search ≈30 req/min |
| Max PRs / window | — | 1000 (API max; CLI hard-caps here) |

### Success check

```bash
python3 scripts/run_harvest.py --db "$ACE_DB_PATH" --summary-only
python3 scripts/check_db_size.py --db "$ACE_DB_PATH"
sqlite3 "$ACE_DB_PATH" "SELECT pr_number, file_count, additions, deletions, title FROM human_patterns LIMIT 10;"
```

Refresh the living status table:

```bash
python3 scripts/refresh_corpus_status.py              # DB + cached JSON only
python3 scripts/refresh_corpus_status.py --fetch-github
./scripts/dgx_refresh_status.sh
```

Django freeze + recreate: [CORPUS.md](CORPUS.md). Agent sandbox is not part of these harvest scripts — see [EVAL.md](EVAL.md).
