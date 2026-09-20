#!/usr/bin/env bash
# Lightweight watcher: when live ACE DB ≥ 1 GiB, wait for a repo boundary
# (finished_repo / FAILED_repo in the harvest log + no run_full_django child),
# then rotate via scripts/rotate_shard_if_needed.py.
#
# Intended for tmux while an older dgx_corpus_harvest.sh (without the rotate
# hook) is still running. Safe to run alongside a harvest that already calls
# rotate — the rotate script is a no-op under the limit / after rotation.
#
# Usage (DGX):
#   tmux new -s ace-shard-watch './scripts/dgx_shard_watch.sh'
#   # or: nohup ./scripts/dgx_shard_watch.sh >> data/shard_watch.log 2>&1 &
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export ACE_DB_PATH="${ACE_DB_PATH:-$HOME/ace-bench/data/ace_patterns.sqlite}"
LOG="${CORPUS_HARVEST_LOG:-$HOME/ace-bench/data/corpus_harvest.log}"
WATCH_LOG="${SHARD_WATCH_LOG:-$HOME/ace-bench/data/shard_watch.log}"
POLL_SECONDS="${POLL_SECONDS:-300}"
LIMIT_BYTES="${LIMIT_BYTES:-1073741824}"
PYTHON="${PYTHON:-python3}"
SIGNAL_FILE="${SHARD_ROTATE_SIGNAL:-$HOME/ace-bench/data/shard_rotate_needed}"

mkdir -p "$(dirname "$ACE_DB_PATH")" "$(dirname "$WATCH_LOG")"

log() {
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" | tee -a "$WATCH_LOG"
}

harvest_python_running() {
  pgrep -f "scripts/run_full_django_harvest.py" >/dev/null 2>&1
}

last_repo_boundary_line() {
  if [[ ! -f "$LOG" ]]; then
    echo ""
    return 0
  fi
  # Prefer the newest finished/failed marker.
  grep -E '^(finished_repo|FAILED_repo):' "$LOG" | tail -n 1 || true
}

log "shard_watch_start db=$ACE_DB_PATH poll=${POLL_SECONDS}s limit=$LIMIT_BYTES"

LAST_HANDLED_BOUNDARY=""

while true; do
  if [[ ! -f "$ACE_DB_PATH" ]]; then
    log "db_missing path=$ACE_DB_PATH"
    sleep "$POLL_SECONDS"
    continue
  fi

  size="$(stat -c %s "$ACE_DB_PATH" 2>/dev/null || stat -f %z "$ACE_DB_PATH" 2>/dev/null || echo 0)"
  if [[ "$size" -lt "$LIMIT_BYTES" ]]; then
    rm -f "$SIGNAL_FILE" 2>/dev/null || true
    sleep "$POLL_SECONDS"
    continue
  fi

  touch "$SIGNAL_FILE" 2>/dev/null || true
  log "over_limit size=$size — waiting for repo boundary + idle harvest python"

  boundary="$(last_repo_boundary_line)"
  if [[ -z "$boundary" ]]; then
    log "no_boundary_yet in $LOG"
    sleep "$POLL_SECONDS"
    continue
  fi

  if [[ "$boundary" == "$LAST_HANDLED_BOUNDARY" ]]; then
    # Already rotated (or attempted) for this boundary; wait for next finished_repo.
    sleep "$POLL_SECONDS"
    continue
  fi

  if harvest_python_running; then
    log "harvest_python_still_running; defer rotate (boundary=$boundary)"
    sleep 30
    continue
  fi

  # Brief settle so the bash parent can finish summary-only / check_db_size.
  sleep 5
  if harvest_python_running; then
    log "harvest_python_restarted; defer"
    sleep 30
    continue
  fi

  log "rotating after boundary: $boundary"
  if "$PYTHON" scripts/rotate_shard_if_needed.py --db "$ACE_DB_PATH" --limit-bytes "$LIMIT_BYTES" >>"$WATCH_LOG" 2>&1; then
    LAST_HANDLED_BOUNDARY="$boundary"
    rm -f "$SIGNAL_FILE" 2>/dev/null || true
    log "rotate_ok; harvest parent should keep writing to fresh live DB"
    # Note for operators if the running bash never got the in-loop hook:
    log "note: if harvest bash predates rotate hook, it already points at ACE_DB_PATH (same path); fresh file is fine"
  else
    rc=$?
    log "rotate_failed rc=$rc — will retry after next poll / new boundary"
  fi

  sleep "$POLL_SECONDS"
done
