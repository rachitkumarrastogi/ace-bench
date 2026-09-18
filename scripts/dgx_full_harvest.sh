#!/usr/bin/env bash
# Overnight full pre-AI django/django harvest (monthly Search API windows).
# Safe to re-run: SQLite upserts on (repo, pr_number) skip/refresh dupes.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export ACE_DB_PATH="${ACE_DB_PATH:-$ROOT/data/ace_patterns.sqlite}"
export REPOS="${REPOS:-django/django}"
export MERGED_AFTER="${MERGED_AFTER:-2012-01-01}"
export MERGED_BEFORE="${MERGED_BEFORE:-2021-01-01}"
export WINDOW="${WINDOW:-months}"
export WINDOW_SIZE="${WINDOW_SIZE:-1}"
export MAX_PRS="${MAX_PRS:-1000}"
export SLEEP="${SLEEP:-0.25}"
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

# Prefer env token; else load from mode-600 file; else gh auth token.
if [[ -z "${GITHUB_TOKEN:-}" && -z "${GH_TOKEN:-}" ]]; then
  if [[ -f "$TOKEN_FILE" ]]; then
    # shellcheck disable=SC1090
    export GITHUB_TOKEN="$(tr -d '[:space:]' <"$TOKEN_FILE")"
    echo "using token from: $TOKEN_FILE"
  elif command -v gh >/dev/null 2>&1; then
    if TOK="$(gh auth token 2>/dev/null)"; then
      export GH_TOKEN="$TOK"
      echo "using token from: gh auth token"
    fi
  fi
fi

if [[ -z "${GITHUB_TOKEN:-}" && -z "${GH_TOKEN:-}" ]]; then
  echo "warning: no token — set GITHUB_TOKEN or write $TOKEN_FILE (mode 600)" >&2
fi

"$PYTHON" scripts/run_full_django_harvest.py

echo
echo "== DB summary =="
"$PYTHON" scripts/run_harvest.py --db "$ACE_DB_PATH" --summary-only
echo
echo "finished: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
