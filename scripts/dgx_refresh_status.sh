#!/usr/bin/env bash
# Cron-friendly CORPUS_STATUS refresh (DB-only by default — no GitHub Search).
# For Search fills: FETCH_GITHUB=1 ./scripts/dgx_refresh_status.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# shellcheck source=scripts/_load_github_token.sh
source "$ROOT/scripts/_load_github_token.sh"

export ACE_DB_PATH="${ACE_DB_PATH:-$HOME/ace-bench/data/ace_patterns.sqlite}"
PYTHON="${PYTHON:-python3}"
FETCH_GITHUB="${FETCH_GITHUB:-0}"

ace_load_github_token

echo "== ACE-Bench CORPUS_STATUS refresh =="
echo "db:     $ACE_DB_PATH"
echo "fetch:  $FETCH_GITHUB"
echo "started:$(date -u +%Y-%m-%dT%H:%M:%SZ)"

ARGS=(scripts/refresh_corpus_status.py --db "$ACE_DB_PATH")
if [[ "$FETCH_GITHUB" == "1" || "$FETCH_GITHUB" == "true" ]]; then
  ARGS+=(--fetch-github)
fi

"$PYTHON" "${ARGS[@]}"
"$PYTHON" scripts/check_db_size.py --db "$ACE_DB_PATH" --ok-missing || true

echo "finished: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
