#!/usr/bin/env bash
# tmux-friendly overnight harvest wrapper for DGX / long-running hosts.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export ACE_DB_PATH="${ACE_DB_PATH:-$ROOT/data/ace_patterns.sqlite}"
MAX_PRS="${MAX_PRS:-200}"
REPOS="${REPOS:-django/django}"
MERGED_BEFORE="${MERGED_BEFORE:-2021-01-01}"
PYTHON="${PYTHON:-python3}"

mkdir -p "$(dirname "$ACE_DB_PATH")"

echo "== ACE-Bench harvest =="
echo "db:            $ACE_DB_PATH"
echo "repos:         $REPOS"
echo "merged_before: $MERGED_BEFORE"
echo "max_prs:       $MAX_PRS"
echo "started:       $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo

# Prefer GITHUB_TOKEN / GH_TOKEN already in the environment.
if [[ -z "${GITHUB_TOKEN:-}" && -z "${GH_TOKEN:-}" ]]; then
  if command -v gh >/dev/null 2>&1; then
    if TOK="$(gh auth token 2>/dev/null)"; then
      export GH_TOKEN="$TOK"
      echo "using token from: gh auth token"
    fi
  fi
fi

if [[ -z "${GITHUB_TOKEN:-}" && -z "${GH_TOKEN:-}" ]]; then
  echo "warning: no token — set GITHUB_TOKEN or GH_TOKEN before overnight runs" >&2
fi

# shellcheck disable=SC2086
"$PYTHON" scripts/run_harvest.py \
  --repos $REPOS \
  --merged-before "$MERGED_BEFORE" \
  --max-prs "$MAX_PRS" \
  --db "$ACE_DB_PATH"

echo
echo "== DB summary =="
"$PYTHON" scripts/run_harvest.py --db "$ACE_DB_PATH" --summary-only
echo
echo "finished: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
