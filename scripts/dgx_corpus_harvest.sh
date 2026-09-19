#!/usr/bin/env bash
# Full curated corpus harvest (Tier A → B → C → D) into the same ACE_DB_PATH.
# Sequential only: one repo at a time. Continues on per-repo failure.
#
# Reads owner/name list from data/corpus_repos.json (prefer) unless REPOS= is set.
# Skips status done_frozen / in_harvest / done / done_harvested, plus SKIP_REPOS
# (defaults to the five already-ingested kickoff repos). Also skips entries with
# harvest_status in {done, done_harvested, done_frozen, skipped}.
#
# Queue order: tier_a → tier_b → tier_c → tier_d (master list ~1000; first wave
# was A–C ~110). A live run that baked in the old ~105 list is left alone —
# relaunch this script after it finishes to pick up Tier D backlog.
#
# Optional env:
#   CORPUS_LIMIT=N     — stop after N queued repos (useful for staged waves)
#   CORPUS_TIERS=a,b,c — limit which tiers to include (default: a,b,c,d)
#   QUEUE_FILE_IN=path — use a prebuilt list (e.g. data/corpus_tier_d_queue.txt)
#   REFRESH_STATUS=1   — refresh docs/CORPUS_STATUS.md after each repo (DB-only)
#
# Rate limits (authenticated): Search ≈30/min (harvest floors page gaps at 2.0s);
# core REST ≈5k/hr (default SLEEP 1.0s between PR fetches).
#
# Cron status: ./scripts/dgx_refresh_status.sh
# Expect days–weeks of wall time for the full master list — intentional.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# shellcheck source=scripts/_load_github_token.sh
source "$ROOT/scripts/_load_github_token.sh"

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
# DB-only CORPUS_STATUS refresh after each repo (0=off, 1=on).
REFRESH_STATUS="${REFRESH_STATUS:-0}"
# Optional: max repos from the built queue (empty = no limit).
CORPUS_LIMIT="${CORPUS_LIMIT:-}"
# Comma-separated tier letters: a,b,c,d (default all).
CORPUS_TIERS="${CORPUS_TIERS:-a,b,c,d}"
# Optional prebuilt queue file (one owner/name per line).
QUEUE_FILE_IN="${QUEUE_FILE_IN:-}"

mkdir -p "$(dirname "$ACE_DB_PATH")" "$(dirname "$LOG")"

export SLEEP="${SLEEP:-$DEFAULT_SLEEP}"

build_queue() {
  if [[ -n "${REPOS:-}" ]]; then
    # shellcheck disable=SC2086
    printf '%s\n' $REPOS
    return 0
  fi
  if [[ -n "$QUEUE_FILE_IN" ]]; then
    if [[ ! -f "$QUEUE_FILE_IN" ]]; then
      echo "error: QUEUE_FILE_IN not found: $QUEUE_FILE_IN" >&2
      return 1
    fi
    # Strip comments/blank lines; apply SKIP_REPOS only.
    SKIP_REPOS="$SKIP_REPOS" QUEUE_FILE_IN="$QUEUE_FILE_IN" CORPUS_LIMIT="$CORPUS_LIMIT" "$PYTHON" - <<'PY'
import os
from pathlib import Path
skip = {r for r in os.environ.get("SKIP_REPOS", "").split() if r}
limit = os.environ.get("CORPUS_LIMIT") or ""
limit_n = int(limit) if limit.strip().isdigit() else None
n = 0
for line in Path(os.environ["QUEUE_FILE_IN"]).read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    if line in skip:
        continue
    print(line)
    n += 1
    if limit_n is not None and n >= limit_n:
        break
PY
    return 0
  fi
  if [[ ! -f "$CORPUS_JSON" ]]; then
    echo "error: corpus JSON not found: $CORPUS_JSON" >&2
    return 1
  fi
  SKIP_REPOS="$SKIP_REPOS" CORPUS_JSON="$CORPUS_JSON" CORPUS_LIMIT="$CORPUS_LIMIT" CORPUS_TIERS="$CORPUS_TIERS" "$PYTHON" - <<'PY'
import json, os
from pathlib import Path

path = Path(os.environ["CORPUS_JSON"])
skip = {r for r in os.environ.get("SKIP_REPOS", "").split() if r}
data = json.loads(path.read_text())
done_statuses = {"done_frozen", "in_harvest", "done", "done_harvested", "skipped"}
status_skip = {
    e["repo"]
    for e in data.get("status", [])
    if e.get("status") in done_statuses
}
skip |= status_skip
tier_map = {
    "a": "tier_a",
    "b": "tier_b",
    "c": "tier_c",
    "d": "tier_d",
}
wanted = []
for part in os.environ.get("CORPUS_TIERS", "a,b,c,d").split(","):
    part = part.strip().lower()
    if part in tier_map:
        wanted.append(tier_map[part])
limit = os.environ.get("CORPUS_LIMIT") or ""
limit_n = int(limit) if limit.strip().isdigit() else None
queued = []
for tier in wanted:
    for entry in data.get(tier, []):
        repo = entry.get("repo")
        if not repo or repo in skip:
            continue
        hs = str(entry.get("harvest_status") or entry.get("status") or "").lower()
        if hs in done_statuses:
            continue
        queued.append(repo)
        if limit_n is not None and len(queued) >= limit_n:
            break
    if limit_n is not None and len(queued) >= limit_n:
        break
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
echo "queue_file_in: ${QUEUE_FILE_IN:-—}"
echo "tiers:         $CORPUS_TIERS"
echo "corpus_limit:  ${CORPUS_LIMIT:-none}"
echo "queued:        $QUEUE_COUNT"
echo "skip:          $SKIP_REPOS"
echo "merged_after:  $MERGED_AFTER"
echo "merged_before: $MERGED_BEFORE"
echo "window:        $WINDOW x $WINDOW_SIZE"
echo "max_prs/window:$MAX_PRS"
echo "sleep:         $SLEEP (Search pages ≥2.0s; sequential repos)"
echo "refresh_status:$REFRESH_STATUS (DB-only CORPUS_STATUS after each repo)"
echo "log:           $LOG"
echo "started:       $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "first_repos:"
head -n 8 "$QUEUE_FILE" | sed 's/^/  - /'
echo

ace_load_github_token

{
  echo "==== corpus harvest start $(date -u +%Y-%m-%dT%H:%M:%SZ) ===="
  echo "queued: $QUEUE_COUNT"
  echo "tiers: $CORPUS_TIERS"
  echo "corpus_limit: ${CORPUS_LIMIT:-none}"
  echo "queue_file_in: ${QUEUE_FILE_IN:-—}"
  echo "skip: $SKIP_REPOS"
  echo "sleep: ${SLEEP:-$DEFAULT_SLEEP}"
  echo "db: $ACE_DB_PATH"
  echo "refresh_status: $REFRESH_STATUS"
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
  "$PYTHON" scripts/check_db_size.py --db "$ACE_DB_PATH" --ok-missing 2>&1 | tee -a "$LOG" || true
  if [[ "$REFRESH_STATUS" == "1" || "$REFRESH_STATUS" == "true" ]]; then
    echo "refresh_status: $(date -u +%Y-%m-%dT%H:%M:%SZ) (DB-only)" | tee -a "$LOG"
    "$PYTHON" scripts/refresh_corpus_status.py --db "$ACE_DB_PATH" 2>&1 | tee -a "$LOG" || true
  fi
done <"$QUEUE_FILE"

echo
echo "== Final DB summary =="
"$PYTHON" scripts/run_harvest.py --db "$ACE_DB_PATH" --summary-only 2>&1 | tee -a "$LOG" || true
"$PYTHON" scripts/check_db_size.py --db "$ACE_DB_PATH" --ok-missing 2>&1 | tee -a "$LOG" || true
if [[ "$REFRESH_STATUS" == "1" || "$REFRESH_STATUS" == "true" ]]; then
  "$PYTHON" scripts/refresh_corpus_status.py --db "$ACE_DB_PATH" 2>&1 | tee -a "$LOG" || true
fi
echo
echo "corpus_done: $(date -u +%Y-%m-%dT%H:%M:%SZ) ok=$OK fail=$FAIL queued=$QUEUE_COUNT" | tee -a "$LOG"
# Non-zero only if every repo failed.
if [[ "$OK" -eq 0 && "$FAIL" -gt 0 ]]; then
  exit 1
fi
exit 0
