# DGX First Pass — Django harvest

Pilot goal: collect **pre-AI era** merged PRs from `django/django` into a local SQLite DB so you can eyeball human structural patterns before building the agent compare loop.

Linux kernel harvest is **deferred**. Default repo is `django/django`.

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

## Overnight / tmux on DGX

```bash
export GITHUB_TOKEN=...
export ACE_DB_PATH=/raid/ace/ace_patterns.sqlite
export MAX_PRS=200          # raise later
export REPOS="django/django"
export MERGED_BEFORE=2021-01-01

tmux new -s ace-harvest
./scripts/dgx_harvest.sh
# detach: Ctrl-b d
```

Re-attach: `tmux attach -t ace-harvest`.

Manual equivalent:

```bash
python3 scripts/run_harvest.py \
  --repos django/django \
  --merged-before 2021-01-01 \
  --max-prs 200 \
  --db "$ACE_DB_PATH"
```

Harvest is **idempotent** on `(repo, pr_number)` — safe to re-run; existing rows are refreshed.

## What success looks like

- DB summary shows **~50–200** patterns for `django/django` after a real run.
- Spot-check a few rows: title, file_count, additions/deletions, `metrics_json` (decision-point proxies).
- No secrets in the DB or git history.

```bash
python3 scripts/run_harvest.py --db "$ACE_DB_PATH" --summary-only
sqlite3 "$ACE_DB_PATH" "SELECT pr_number, file_count, additions, deletions, title FROM human_patterns LIMIT 10;"
```

## Defaults (v1 pilot)

| Knob | Default |
|------|---------|
| Repo | `django/django` |
| Cutoff | `merged_before=2021-01-01` |
| Max PRs | `100` (CLI) / `200` (dgx script via `MAX_PRS`) |
| Sleep | `0.25s` between API calls |

Optional second repo later: `--repos django/django someorg/smallrepo`.

## Next (not this pass)

Agent sandbox + ACE compare is stubbed in [EVAL_LOOP.md](EVAL_LOOP.md). Do not expect agent execution from these scripts yet.
