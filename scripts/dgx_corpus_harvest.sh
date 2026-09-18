#!/usr/bin/env bash
# Full curated corpus harvest (Tier A → B → C) into the same ACE_DB_PATH.
# Sequential only: one repo at a time. Continues on per-repo failure.
#
# Reads owner/name list from data/corpus_repos.json (prefer) unless REPOS= is set.
# Skips status done_frozen / in_harvest / done, plus SKIP_REPOS (defaults to the
# five already-ingested kickoff repos).
#
# Rate limits (authenticated): Search ≈30/min (harvest floors page gaps at 2.0s);
# core REST ≈5k/hr (default SLEEP 1.0s between PR fetches).
#
# Expect days of wall time for ~100 repos / large Tier C volumes — intentional.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export ACE_DB_PATH="${ACE_DB_PATH:-$HOME/ace-bench/data/ace_patterns.sqlite}"
export MERGED_AFTER="${MERGED_AFTER:-2012-01-01}"
export MERGED_BEFORE="${MERGED_BEFORE:-2021-01-01}"
export WINDOW="${WINDOW:-months}"
export WINDOW_SIZE="${WINDOW_SIZE:-1}"
export MAX_PRS="${MAX_PRS:-1000}"
DEFAULT_SLEEP="${DEFAULT_SLEEP:-1.0}"
PYTHON="${PYTHON:-python3}"
TOKEN_FILE="${TOKEN_FILE:-$HOME/.config/ace-bench/github_token}"
CORPUS_JSON="${CORPUS_JSON:-$ROOT/data/corpus_repos.json}"
LOG="${CORPUS_HARVEST_LOG:-$HOME/ace-bench/data/corpus_harvest.log}"
# Space-separated; always skipped even if still listed under a tier.
DEFAULT_SKIP="django/django pallets/flask expressjs/express spf13/cobra clap-rs/clap"
SKIP_REPOS="${SKIP_REPOS:-$DEFAULT_SKIP}"

mkdir -p "$(dirname "$ACE_DB_PATH")" "$(dirname "$LOG")"

export SLEEP="${SLEEP:-$DEFAULT_SLEEP}"

build_queue() {
  if [[ -n "${REPOS:-}" ]]; then
    # shellcheck disable=SC2086
    printf '%s\n' $REPOS
    return 0
  fi
  if [[ ! -f "$CORPUS_JSON" ]]; then
    echo "error: corpus JSON not found: $CORPUS_JSON" >&2
    return 1
  fi
  SKIP_REPOS="$SKIP_REPOS" CORPUS_JSON="$CORPUS_JSON" "$PYTHON" - <<'PY'
import json, os
from pathlib import Path

path = Path(os.environ["CORPUS_JSON"])
skip = {r for r in os.environ.get("SKIP_REPOS", "").split() if r}
data = json.loads(path.read_text())
status_skip = {
    e["repo"]
    for e in data.get("status", [])
    if e.get("status") in {"done_frozen", "in_harvest", "done", "done_harvested"}
}
skip |= status_skip
queued = []
for tier in ("tier_a", "tier_b", "tier_c"):
    for entry in data.get(tier, []):
        repo = entry.get("repo")
        if not repo or repo in skip:
            continue
        queued.append(repo)
for repo in queued:
    print(repo)
PY
}

QUEUE_FILE="$(mktemp "${TMPDIR:-/tmp}/ace-corpus-queue.XXXXXX")"
trap 'rm -f "$QUEUE_FILE"' EXIT

if ! build_queue >"$QUEUE_FILE"; then
  exit 1
fi

QUEUE_COUNT="$(grep -c . "$QUEUE_FILE" || true)"
if [[ "$QUEUE_COUNT" -eq 0 ]]; then
  echo "error: empty harvest queue (nothing left after skips)" >&2
  exit 1
fi

echo "== ACE-Bench CORPUS windowed harvest =="
echo "db:            $ACE_DB_PATH"
echo "corpus:        $CORPUS_JSON"
echo "queued:        $QUEUE_COUNT"
echo "skip:          $SKIP_REPOS"
echo "merged_after:  $MERGED_AFTER"
echo "merged_before: $MERGED_BEFORE"
echo "window:        $WINDOW x $WINDOW_SIZE"
echo "max_prs/window:$MAX_PRS"
echo "sleep:         $SLEEP (Search pages ≥2.0s; sequential repos)"
echo "log:           $LOG"
echo "started:       $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "first_repos:"
head -n 8 "$QUEUE_FILE" | sed 's/^/  - /'
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
  echo "==== corpus harvest start $(date -u +%Y-%m-%dT%H:%M:%SZ) ===="
  echo "queued: $QUEUE_COUNT"
  echo "skip: $SKIP_REPOS"
  echo "sleep: ${SLEEP:-$DEFAULT_SLEEP}"
  echo "db: $ACE_DB_PATH"
  echo "first:"
  head -n 8 "$QUEUE_FILE" | sed 's/^/  /'
} >>"$LOG"

OK=0
FAIL=0
IDX=0

while IFS= read -r repo; do
  [[ -z "$repo" ]] && continue
  IDX=$((IDX + 1))
  export SLEEP="${SLEEP:-$DEFAULT_SLEEP}"
  echo
  echo "-------- [$IDX/$QUEUE_COUNT] repo: $repo --------"
  echo "started_repo: $(date -u +%Y-%m-%dT%H:%M:%SZ) $repo sleep=$SLEEP idx=$IDX/$QUEUE_COUNT" | tee -a "$LOG"
  export REPOS="$repo"
  "$PYTHON" scripts/run_full_django_harvest.py 2>&1 | tee -a "$LOG"
  rc=${PIPESTATUS[0]}
  if [[ "$rc" -eq 0 ]]; then
    OK=$((OK + 1))
    echo "finished_repo: $(date -u +%Y-%m-%dT%H:%M:%SZ) $repo rc=0" | tee -a "$LOG"
  else
    FAIL=$((FAIL + 1))
    echo "FAILED_repo: $(date -u +%Y-%m-%dT%H:%M:%SZ) $repo rc=$rc (continuing)" | tee -a "$LOG"
  fi
  "$PYTHON" scripts/run_harvest.py --db "$ACE_DB_PATH" --summary-only 2>&1 | tee -a "$LOG" || true
done <"$QUEUE_FILE"

echo
echo "== Final DB summary =="
"$PYTHON" scripts/run_harvest.py --db "$ACE_DB_PATH" --summary-only 2>&1 | tee -a "$LOG" || true
echo
echo "corpus_done: $(date -u +%Y-%m-%dT%H:%M:%SZ) ok=$OK fail=$FAIL queued=$QUEUE_COUNT" | tee -a "$LOG"
# Non-zero only if every repo failed.
if [[ "$OK" -eq 0 && "$FAIL" -gt 0 ]]; then
  exit 1
fi
exit 0
