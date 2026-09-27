# ACE-Bench SQLite shards / snapshots (Mac backup)

Local backup of DGX harvest shards. **Gitignored** except this README — do **not** commit `*.sqlite` (multi-GB).

| Kind | Naming | Source |
|------|--------|--------|
| Live snapshot | `ace_patterns_live_snapshot_YYYYMMDD.sqlite` | Consistent `sqlite3`/Python `.backup` from DGX, then `scp`/`rsync` |
| Completed shards | `ace_patterns_shard_NNN.sqlite` | Copied from DGX `$HOME/ace-bench/data/shards/` after rotate |
| Frozen Django | `ace_patterns_django_pre2021_6125.sqlite` | Eval smoke copy (canonical freeze also under `data/frozen/`) |
| Manifest | `shards_manifest.json` | DGX `$HOME/ace-bench/data/shards_manifest.json` |

Canonical ops: [docs/OPS.md](../../docs/OPS.md) (sharding at 1 GiB, never commit `*.sqlite`).

## Pull from DGX (laptop)

```bash
# from ace-bench repo root
mkdir -p data/shards
rsync -avz --progress \
  LocalModelRunner:~/ace-bench/data/shards/ \
  data/shards/

# live snapshot while harvest runs (preferred over raw scp of live file):
# on DGX:
#   sqlite3 "$ACE_DB_PATH" ".backup '/tmp/ace_patterns_backup.sqlite'"
# on Mac:
scp LocalModelRunner:/tmp/ace_patterns_backup.sqlite \
  data/shards/ace_patterns_live_snapshot_YYYYMMDD.sqlite
```

DGX live DB: `$HOME/ace-bench/data/ace_patterns.sqlite`  
DGX shards: `$HOME/ace-bench/data/shards/`  
DGX manifest: `$HOME/ace-bench/data/shards_manifest.json`

## Path history

Previously mirrored at `~/ace-bench-data/shards/` (outside the checkout). Prefer this in-repo `data/shards/` path; scripts fall back to the old location if present.

Pattern prior (separate): `~/ace-bench-data/patterns/` or DGX `$HOME/ace-bench/data/patterns/`.
