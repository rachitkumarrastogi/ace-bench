#!/usr/bin/env python3
"""CLI: harvest pre-AI merged PRs into SQLite human-pattern store."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ace_bench.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
