# ACE-Bench rotated SQLite shards (Mac backup)

Local mirror of completed DGX harvest shards. **Gitignored** except this README — do **not** commit `*.sqlite` (multi-GB).

## What belongs here

| Keep | Naming | Notes |
|------|--------|-------|
| Completed shards | `ace_patterns_shard_NNN.sqlite` | Copied from DGX `$HOME/ace-bench/data/shards/` after rotate |
| Manifest | `shards_manifest.json` | From DGX `$HOME/ace-bench/data/shards_manifest.json` |
| This file | `README.md` | Tracked in git |

Do **not** keep in this directory:

- `ace_patterns_live_snapshot_*.sqlite` — point-in-time live backups; redundant once shards exist (store elsewhere if needed)
- Frozen Django eval DB — canonical path is `data/frozen/ace_patterns_django_pre2021_6125.sqlite`

Canonical ops: [docs/OPS.md](../../docs/OPS.md) (sharding at 1 GiB, never commit `*.sqlite`).

## Pull from DGX (laptop)

```bash
# from ace-bench repo root
mkdir -p data/shards
rsync -avz --progress \
  LocalModelRunner:~/ace-bench/data/shards/ \
  data/shards/
```

Optional live snapshot (while harvest runs; prefer not leaving it in `data/shards/` long-term):

```bash
# on DGX:
#   sqlite3 "$ACE_DB_PATH" ".backup '/tmp/ace_patterns_backup.sqlite'"
# on Mac (temp location, not as a permanent shards/ resident):
scp LocalModelRunner:/tmp/ace_patterns_backup.sqlite \
  /tmp/ace_patterns_live_snapshot_YYYYMMDD.sqlite
```

DGX live DB: `$HOME/ace-bench/data/ace_patterns.sqlite`  
DGX shards: `$HOME/ace-bench/data/shards/`  
DGX manifest: `$HOME/ace-bench/data/shards_manifest.json`

## Path history

Previously mirrored at `~/ace-bench-data/shards/` (outside the checkout). Prefer this in-repo `data/shards/` path; scripts fall back to the old location if present.

Pattern prior (separate): `~/ace-bench-data/patterns/` or DGX `$HOME/ace-bench/data/patterns/`.
