# Frozen corpus: django/django (pre-AI)

Immutable snapshot of the first ACE-Bench human-pattern harvest.

| Field | Value |
|-------|--------|
| **Repo** | `django/django` |
| **Cutoff** | `merged:<2021-01-01` (windowed harvest `2012-01-01` → `2021-01-01`, monthly) |
| **Row count** | **6125** |
| **Freeze date** | 2026-09-18 (UTC) |
| **Method** | `VACUUM INTO` compact copy (+ `.bak`) |
| **DGX path** | `/home/arnavrastogi/ace-bench/data/frozen/ace_patterns_django_pre2021_6125.sqlite` |
| **Backup** | same dir, `ace_patterns_django_pre2021_6125.sqlite.bak` |

## Live vs frozen

- **Frozen** = immutable snapshot. Do not write to it.
- **Live** DB remains at `~/ace-bench/data/ace_patterns.sqlite` (or `$ACE_DB_PATH`).
  Multi-repo harvests upsert into the live DB on `UNIQUE(repo, pr_number)`.
  Django rows stay in the live DB; new repos (Flask, Express, Cobra, Clap, …)
  are added alongside.

## Recreate freeze (DGX)

```bash
LIVE=~/ace-bench/data/ace_patterns.sqlite
OUT=~/ace-bench/data/frozen/ace_patterns_django_pre2021_6125.sqlite
mkdir -p "$(dirname "$OUT")"
sqlite3 "$LIVE" "VACUUM INTO '$OUT'"
cp -a "$OUT" "${OUT}.bak"
sqlite3 "$OUT" "SELECT repo, COUNT(*) FROM human_patterns GROUP BY repo;"
```

## Verify

```bash
python3 scripts/run_harvest.py --db ~/ace-bench/data/frozen/ace_patterns_django_pre2021_6125.sqlite --summary-only
```

Expect `total: 6125` and a single `django/django` entry under `by_repo`.
