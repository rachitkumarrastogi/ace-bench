#!/usr/bin/env bash
# Build ACE pattern prior DB on DGX (read-only vs harvest).
#
# Prefer frozen shard_001; optionally include live DB via mode=ro (or a
# sqlite .backup snapshot). Does NOT stop ace-harvest / ace-shard-watch.
#
# Usage (DGX, tmux-friendly):
#   ./scripts/dgx_build_patterns.sh
#   INCLUDE_LIVE=0 ./scripts/dgx_build_patterns.sh   # shard_001 only
#   COPY_TO_MAC=1 ./scripts/dgx_build_patterns.sh    # scp to Mac after build
#
# Env:
#   ACE_DB_PATH / SHARD_001 / PATTERN_OUT / CORPUS_JSON / PYTHON
#   INCLUDE_LIVE=1 (default) — also read live ace_patterns.sqlite (ro)
#   LIVE_VIA_BACKUP=1 — sqlite3 .backup live → /tmp then analyze (safer under write load)
#   COPY_TO_MAC=0 — if 1, scp pattern DB to MAC_HOST:MAC_PATTERNS_DIR
#   MAC_HOST=...  MAC_PATTERNS_DIR=~/ace-bench-data/patterns
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-python3}"
ACE_DB_PATH="${ACE_DB_PATH:-$HOME/ace-bench/data/ace_patterns.sqlite}"
SHARD_001="${SHARD_001:-$HOME/ace-bench/data/shards/ace_patterns_shard_001.sqlite}"
PATTERN_OUT="${PATTERN_OUT:-$HOME/ace-bench/data/patterns/ace_patterns_prior.sqlite}"
CORPUS_JSON="${CORPUS_JSON:-$ROOT/data/corpus_repos.json}"
INCLUDE_LIVE="${INCLUDE_LIVE:-1}"
# Prefer consistent snapshot of live DB while harvest may be writing.
LIVE_VIA_BACKUP="${LIVE_VIA_BACKUP:-1}"
COPY_TO_MAC="${COPY_TO_MAC:-0}"
MAC_HOST="${MAC_HOST:-}"
MAC_PATTERNS_DIR="${MAC_PATTERNS_DIR:-~/ace-bench-data/patterns}"
LOG="${PATTERN_BUILD_LOG:-$HOME/ace-bench/data/pattern_build.log}"
LIVE_BACKUP="${LIVE_BACKUP:-/tmp/ace_patterns_live_ro_backup.sqlite}"

mkdir -p "$(dirname "$PATTERN_OUT")" "$(dirname "$LOG")"

log() {
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" | tee -a "$LOG"
}

log "== ACE pattern DB build =="
log "shard_001: $SHARD_001"
log "live:      $ACE_DB_PATH (include=$INCLUDE_LIVE via_backup=$LIVE_VIA_BACKUP)"
log "out:       $PATTERN_OUT"
log "corpus:    $CORPUS_JSON"

if [[ ! -f "$SHARD_001" ]]; then
  log "error: shard_001 not found: $SHARD_001"
  exit 1
fi

ARGS=(--harvest-db "$SHARD_001" --out "$PATTERN_OUT" --corpus-json "$CORPUS_JSON")
ARGS+=(--notes "dgx_build_patterns shard_001+optional_live $(date -u +%Y-%m-%dT%H:%M:%SZ)")

if [[ "$INCLUDE_LIVE" == "1" || "$INCLUDE_LIVE" == "true" ]]; then
  if [[ -f "$ACE_DB_PATH" ]]; then
    if [[ "$LIVE_VIA_BACKUP" == "1" || "$LIVE_VIA_BACKUP" == "true" ]]; then
      log "live via sqlite .backup → $LIVE_BACKUP"
      rm -f "$LIVE_BACKUP"
      if sqlite3 "$ACE_DB_PATH" ".backup '$LIVE_BACKUP'"; then
        ARGS+=(--harvest-db "$LIVE_BACKUP")
      else
        log "warning: .backup failed; falling back to mode=ro on live"
        ARGS+=(--harvest-db "$ACE_DB_PATH")
      fi
    else
      log "live via mode=ro (no lock/stop of harvest)"
      ARGS+=(--harvest-db "$ACE_DB_PATH")
    fi
  else
    log "warning: live DB missing; shard_001 only"
  fi
fi

log "harvest sessions (untouched):"
tmux ls 2>/dev/null | tee -a "$LOG" || true

set +e
"$PYTHON" "$ROOT/scripts/build_pattern_db.py" "${ARGS[@]}" 2>&1 | tee -a "$LOG"
rc=${PIPESTATUS[0]}
set -e

if [[ "$rc" -ne 0 ]]; then
  log "error: build_pattern_db.py rc=$rc"
  exit "$rc"
fi

if [[ -f "$PATTERN_OUT" ]]; then
  log "pattern_db size: $(du -h "$PATTERN_OUT" | awk '{print $1}') ($(stat -c%s "$PATTERN_OUT" 2>/dev/null || stat -f%z "$PATTERN_OUT") bytes)"
fi

# Confirm harvest still running / untouched intent
log "post-build tmux (harvest should still be up):"
tmux ls 2>/dev/null | tee -a "$LOG" || true

if [[ "$COPY_TO_MAC" == "1" || "$COPY_TO_MAC" == "true" ]]; then
  if [[ -z "$MAC_HOST" ]]; then
    log "error: COPY_TO_MAC=1 but MAC_HOST unset"
    exit 1
  fi
  log "scp → ${MAC_HOST}:${MAC_PATTERNS_DIR}/"
  # Expand ~ on remote via ssh shell.
  ssh "$MAC_HOST" "mkdir -p ${MAC_PATTERNS_DIR}"
  scp "$PATTERN_OUT" "${MAC_HOST}:${MAC_PATTERNS_DIR}/ace_patterns_prior.sqlite"
  log "copied pattern DB to Mac"
fi

log "done rc=0"
exit 0
