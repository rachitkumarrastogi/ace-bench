#!/usr/bin/env bash
# Overnight full pre-AI django/django harvest (monthly Search API windows).
# Safe to re-run: SQLite upserts on (repo, pr_number) skip/refresh dupes.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# shellcheck source=scripts/_load_github_token.sh
source "$ROOT/scripts/_load_github_token.sh"

export ACE_DB_PATH="${ACE_DB_PATH:-$ROOT/data/ace_patterns.sqlite}"
export REPOS="${REPOS:-django/django}"
export MERGED_AFTER="${MERGED_AFTER:-2012-01-01}"
export MERGED_BEFORE="${MERGED_BEFORE:-2021-01-01}"
export WINDOW="${WINDOW:-months}"
export WINDOW_SIZE="${WINDOW_SIZE:-1}"
export MAX_PRS="${MAX_PRS:-1000}"
# REST pacing (~5k/hr). Search pages are floored at 2.0s in harvest.py (~30/min).
export SLEEP="${SLEEP:-0.75}"
PYTHON="${PYTHON:-python3}"
TOKEN_FILE="${TOKEN_FILE:-$HOME/.config/ace-bench/github_token}"

mkdir -p "$(dirname "$ACE_DB_PATH")"

echo "== ACE-Bench FULL windowed harvest =="
echo "db:            $ACE_DB_PATH"
echo "repos:         $REPOS"
echo "merged_after:  $MERGED_AFTER"
echo "merged_before: $MERGED_BEFORE"
echo "window:        $WINDOW x $WINDOW_SIZE"
echo "max_prs/window:$MAX_PRS"
echo "started:       $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo

ace_load_github_token

"$PYTHON" scripts/run_full_django_harvest.py

echo
echo "== DB summary =="
"$PYTHON" scripts/run_harvest.py --db "$ACE_DB_PATH" --summary-only
"$PYTHON" scripts/check_db_size.py --db "$ACE_DB_PATH" --ok-missing || true
echo
echo "finished: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
