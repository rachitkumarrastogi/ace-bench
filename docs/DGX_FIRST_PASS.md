# DGX First Pass — Django harvest

Goal: collect **pre-AI era** merged PRs from `django/django` into a local SQLite DB so you can eyeball human structural patterns before building the agent compare loop. Prefer a **full human baseline** (thousands of PRs) over the small pilot cap.

Linux kernel harvest is **deferred**. Default repo is `django/django`.

## GitHub Search 1000-result limit

The GitHub **Search API returns at most 1000 results per query**. A single
`repo:django/django is:pr is:merged merged:<2021-01-01` search **cannot**
enumerate the full pre-AI baseline.

**Windowed harvest** slices `[merged_after, merged_before)` into monthly (or
daily) queries so each window stays under ~1000 hits, then upserts into the
same SQLite DB (idempotent on `(repo, pr_number)`).

Each window uses the range qualifier `merged:YYYY-MM-DD..YYYY-MM-DD` (inclusive).
Do **not** combine `merged:>=` with `merged:<` — GitHub Search often ignores the
lower bound and reports a bogus inflated `total_count`.

| Mode | Script | Scope |
|------|--------|-------|
| Pilot (capped) | `scripts/dgx_harvest.sh` | `--max-prs 200` (no windows) |
| Full baseline | `scripts/dgx_full_harvest.sh` | monthly windows `2012-01-01` → `2021-01-01` (default: django) |
| Multi-repo batch | `scripts/dgx_multi_harvest.sh` | same windows; loops Flask / Express / Cobra / Clap into live DB |

CLI equivalent for full mode:

```bash
python3 scripts/run_harvest.py \
  --repos django/django \
  --merged-after 2012-01-01 \
  --merged-before 2021-01-01 \
  --window months \
  --window-size 1 \
  --max-prs 1000 \
  --db "$ACE_DB_PATH"
# or: python3 scripts/run_full_django_harvest.py
```

If a window still reports `total_count > 1000`, shrink `--window-size` (or use
`--window days`) and re-run; upserts skip duplicates.

## Prerequisites

- Python 3.11+
- GitHub token with public-repo read (`GITHUB_TOKEN` or `GH_TOKEN`)
- Optional: `tmux` for overnight runs

## Clone on DGX

```bash
git clone git@github-rachit:rachitkumarrastogi/ace-bench.git
cd ace-bench
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Or without install (scripts add `src/` to `sys.path`):

```bash
python3 scripts/run_harvest.py --help
```

## Token

```bash
export GITHUB_TOKEN=ghp_...   # or GH_TOKEN
# never commit .env / tokens
```

`scripts/dgx_harvest.sh` will also try `gh auth token` if neither env var is set.

## Where the DB lives

| Setting | Default |
|---------|---------|
| Env | `ACE_DB_PATH` |
| Fallback | `./data/ace_patterns.sqlite` |

On DGX, point at local disk (not NFS if possible):

```bash
export ACE_DB_PATH=/raid/ace/ace_patterns.sqlite
mkdir -p "$(dirname "$ACE_DB_PATH")"
```

`data/*.sqlite` is gitignored; `data/.gitkeep` keeps the folder in the repo.

## Smoke (laptop)

```bash
python3 scripts/run_harvest.py --max-prs 3 --db /tmp/ace_smoke.sqlite
python3 scripts/run_harvest.py --db /tmp/ace_smoke.sqlite --summary-only
```

Expect ~3 rows for `django/django` with `merged_at` before `2021-01-01`.

## Token on DGX (file, mode 600)

```bash
mkdir -p ~/.config/ace-bench
# write token once (never commit); chmod 600
chmod 600 ~/.config/ace-bench/github_token
# wrappers load it without printing:
#   export GITHUB_TOKEN="$(tr -d '[:space:]' <~/.config/ace-bench/github_token)"
```

## Overnight / tmux on DGX — full windowed harvest

```bash
export ACE_DB_PATH=/home/arnavrastogi/ace-bench/data/ace_patterns.sqlite
# token from ~/.config/ace-bench/github_token (mode 600) or GITHUB_TOKEN

tmux new -s ace-harvest
./scripts/dgx_full_harvest.sh
# detach: Ctrl-b d
```

Re-attach: `tmux attach -t ace-harvest`.

Pilot (capped) still available: `./scripts/dgx_harvest.sh` with `MAX_PRS=200`.

Harvest is **idempotent** on `(repo, pr_number)` — safe to re-run; existing rows are refreshed. Full harvest upserts over any prior pilot rows.

## What success looks like

- Full run: pattern count climbs into the **thousands** for `django/django` (monthly windows 2012–2020).
- Pilot: **~50–200** patterns after a capped run.
- Spot-check a few rows: title, file_count, additions/deletions, `metrics_json` (decision-point proxies).
- No secrets in the DB or git history.

```bash
python3 scripts/run_harvest.py --db "$ACE_DB_PATH" --summary-only
sqlite3 "$ACE_DB_PATH" "SELECT pr_number, file_count, additions, deletions, title FROM human_patterns LIMIT 10;"
```

## Defaults

| Knob | Pilot | Full windowed |
|------|-------|---------------|
| Repo | `django/django` | same |
| Range | `merged_before=2021-01-01` | `2012-01-01` → `2021-01-01` |
| Windows | none | `--window months --window-size 1` (~108 months) |
| Max PRs | `100` CLI / `200` dgx script | `1000` per window (Search API max) |
| Sleep | `0.25s` | same (Search paced ≥0.35s) |

Optional second repo later: `--repos django/django someorg/smallrepo`.

## Django freeze + multi-repo (same live DB)

Django baseline is frozen at **6125** rows — see [CORPUS_DJANGO.md](CORPUS_DJANGO.md)
and [data/FROZEN.md](../data/FROZEN.md). Keep using the live
`ace_patterns.sqlite` for further upserts (`UNIQUE(repo, pr_number)`).

Curated multi-language batch (pre-AI Search totals verified ≥50; no swaps):

| Repo | Language |
|------|----------|
| `pallets/flask` | Python |
| `expressjs/express` | JavaScript |
| `spf13/cobra` | Go |
| `clap-rs/clap` | Rust |

```bash
export ACE_DB_PATH=/home/arnavrastogi/ace-bench/data/ace_patterns.sqlite
# kill idle ace-harvest shell only; do not touch pn-web
tmux kill-session -t ace-harvest 2>/dev/null || true
tmux new -s ace-harvest
./scripts/dgx_multi_harvest.sh
# detach: Ctrl-b d
```

Override repos: `REPOS="psf/requests axios/axios" ./scripts/dgx_multi_harvest.sh`.
Default sleep is `0.4s` (rate-limit friendly). Log: `data/multi_harvest.log`.

## Next (not this pass)

Agent sandbox + ACE compare is stubbed in [EVAL_LOOP.md](EVAL_LOOP.md). Do not expect agent execution from these scripts yet.
