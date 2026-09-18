#!/usr/bin/env python3
"""Smoke-check the ACE Index formula with a few hand examples."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ace_bench.scoring import AceScoreInputs, compute_ace_score


def main() -> None:
    matched = compute_ace_score(
        AceScoreInputs(
            human_ast_nodes=100,
            agent_ast_nodes=100,
            human_file_count=1,
            agent_file_count=1,
            passed_tests=True,
        )
    )
    bloated = compute_ace_score(
        AceScoreInputs(
            human_ast_nodes=50,
            agent_ast_nodes=200,
            human_file_count=1,
            agent_file_count=4,
            passed_tests=True,
        )
    )
    failed = compute_ace_score(
        AceScoreInputs(
            human_ast_nodes=50,
            agent_ast_nodes=40,
            human_file_count=1,
            agent_file_count=1,
            passed_tests=False,
        )
    )
    print(f"matched≈1.0 → {matched:.4f}")
    print(f"bloated≪1.0 → {bloated:.4f}")
    print(f"failed=0.0  → {failed:.4f}")


if __name__ == "__main__":
    main()
