#!/usr/bin/env python3
"""Full pre-AI django/django harvest via monthly Search API windows (2012→2021).

GitHub Search returns at most 1000 results per query. A single
`merged:<2021-01-01` search cannot enumerate the whole baseline, so this
script drives `ace_bench.harvest` with `--window months` from 2012-01-01
through 2021-01-01 (exclusive). Upserts are idempotent on (repo, pr_number).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ace_bench.cli import main

# Inclusive lower / exclusive upper bound for the pre-AI human baseline.
DEFAULT_AFTER = "2012-01-01"
DEFAULT_BEFORE = "2021-01-01"


def build_argv() -> list[str]:
    """Compose CLI args; env vars override defaults for DGX wrappers."""
    after = os.environ.get("MERGED_AFTER", DEFAULT_AFTER)
    before = os.environ.get("MERGED_BEFORE", DEFAULT_BEFORE)
    repos = os.environ.get("REPOS", "django/django").split()
    db = os.environ.get("ACE_DB_PATH", "./data/ace_patterns.sqlite")
    sleep = os.environ.get("SLEEP", "0.75")
    window = os.environ.get("WINDOW", "months")
    window_size = os.environ.get("WINDOW_SIZE", "1")
    # Per-window cap = Search API max unless caller overrides.
    max_prs = os.environ.get("MAX_PRS", "1000")

    argv = [
        "--repos",
        *repos,
        "--merged-after",
        after,
        "--merged-before",
        before,
        "--window",
        window,
        "--window-size",
        window_size,
        "--max-prs",
        max_prs,
        "--sleep",
        sleep,
        "--db",
        db,
    ]
    return argv


if __name__ == "__main__":
    raise SystemExit(main(build_argv()))
