#!/usr/bin/env bash
# tmux-friendly pilot harvest wrapper (capped). For thousands of PRs use
# scripts/dgx_full_harvest.sh (monthly Search API windows — avoids the 1000-hit cap).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# shellcheck source=scripts/_load_github_token.sh
source "$ROOT/scripts/_load_github_token.sh"

export ACE_DB_PATH="${ACE_DB_PATH:-$ROOT/data/ace_patterns.sqlite}"
MAX_PRS="${MAX_PRS:-200}"
REPOS="${REPOS:-django/django}"
MERGED_BEFORE="${MERGED_BEFORE:-2021-01-01}"
PYTHON="${PYTHON:-python3}"
TOKEN_FILE="${TOKEN_FILE:-$HOME/.config/ace-bench/github_token}"

mkdir -p "$(dirname "$ACE_DB_PATH")"

echo "== ACE-Bench harvest (pilot cap) =="
echo "db:            $ACE_DB_PATH"
echo "repos:         $REPOS"
echo "merged_before: $MERGED_BEFORE"
echo "max_prs:       $MAX_PRS"
echo "note:          for full baseline see ./scripts/dgx_full_harvest.sh"
echo "started:       $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo

ace_load_github_token

# Pass repos as separate argv words (no eval / shell=True).
# shellcheck disable=SC2206
REPO_ARR=($REPOS)
"$PYTHON" scripts/run_harvest.py \
  --repos "${REPO_ARR[@]}" \
  --merged-before "$MERGED_BEFORE" \
  --max-prs "$MAX_PRS" \
  --db "$ACE_DB_PATH"

echo
echo "== DB summary =="
"$PYTHON" scripts/run_harvest.py --db "$ACE_DB_PATH" --summary-only
"$PYTHON" scripts/check_db_size.py --db "$ACE_DB_PATH" --ok-missing || true
echo
echo "finished: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
