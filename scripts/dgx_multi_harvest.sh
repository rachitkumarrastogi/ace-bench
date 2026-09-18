#!/usr/bin/env bash
# Multi-repo pre-AI windowed harvest into the same ACE_DB_PATH.
# Loops repos one-at-a-time so progress / per-repo counts stay readable.
# Safe to re-run: SQLite upserts on (repo, pr_number).
#
# Default batch (curated, not blind top-100) — all have substantial
# merged:<2021-01-01 GitHub PRs (verified ≥50 before kickoff):
#   pallets/flask (Python), expressjs/express (JS),
#   spf13/cobra (Go), clap-rs/clap (Rust)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export ACE_DB_PATH="${ACE_DB_PATH:-$ROOT/data/ace_patterns.sqlite}"
export MERGED_AFTER="${MERGED_AFTER:-2012-01-01}"
export MERGED_BEFORE="${MERGED_BEFORE:-2021-01-01}"
export WINDOW="${WINDOW:-months}"
export WINDOW_SIZE="${WINDOW_SIZE:-1}"
export MAX_PRS="${MAX_PRS:-1000}"
# Slightly slower default for multi-repo overnight runs (Search ~30 req/min).
export SLEEP="${SLEEP:-0.4}"
PYTHON="${PYTHON:-python3}"
TOKEN_FILE="${TOKEN_FILE:-$HOME/.config/ace-bench/github_token}"
LOG="${MULTI_HARVEST_LOG:-$ROOT/data/multi_harvest.log}"

# Space-separated owner/name list (override with REPOS=...).
DEFAULT_REPOS="pallets/flask expressjs/express spf13/cobra clap-rs/clap"
REPOS_LIST="${REPOS:-$DEFAULT_REPOS}"

mkdir -p "$(dirname "$ACE_DB_PATH")" "$(dirname "$LOG")"

echo "== ACE-Bench MULTI-REPO windowed harvest =="
echo "db:            $ACE_DB_PATH"
echo "repos:         $REPOS_LIST"
echo "merged_after:  $MERGED_AFTER"
echo "merged_before: $MERGED_BEFORE"
echo "window:        $WINDOW x $WINDOW_SIZE"
echo "max_prs/window:$MAX_PRS"
echo "sleep:         $SLEEP"
echo "log:           $LOG"
echo "started:       $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo

if [[ -z "${GITHUB_TOKEN:-}" && -z "${GH_TOKEN:-}" ]]; then
  if [[ -f "$TOKEN_FILE" ]]; then
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

{
  echo "==== multi harvest start $(date -u +%Y-%m-%dT%H:%M:%SZ) ===="
  echo "repos: $REPOS_LIST"
} >>"$LOG"

# shellcheck disable=SC2086
for repo in $REPOS_LIST; do
  echo
  echo "-------- repo: $repo --------"
  echo "started_repo: $(date -u +%Y-%m-%dT%H:%M:%SZ) $repo" | tee -a "$LOG"
  export REPOS="$repo"
  "$PYTHON" scripts/run_full_django_harvest.py 2>&1 | tee -a "$LOG"
  echo "finished_repo: $(date -u +%Y-%m-%dT%H:%M:%SZ) $repo" | tee -a "$LOG"
  "$PYTHON" scripts/run_harvest.py --db "$ACE_DB_PATH" --summary-only | tee -a "$LOG"
done

echo
echo "== Final DB summary =="
"$PYTHON" scripts/run_harvest.py --db "$ACE_DB_PATH" --summary-only | tee -a "$LOG"
echo
echo "finished: $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$LOG"
