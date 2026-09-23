"""Unit tests for craft v0 helpers."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ace_bench.agents.stub import STUB_PATCH, build_bloated_stub_patch
from ace_bench.craft import (
    compute_craft,
    jaccard,
    line_overlap,
    path_jaccard,
    symbol_overlap,
)
from ace_bench.eval_v0 import (
    EVAL_MODE_IMMEDIATE,
    EVAL_MODE_THOROUGH,
    files_from_patch,
    score_agent_vs_human,
)

SAMPLE = """\
diff --git a/django/foo.py b/django/foo.py
--- a/django/foo.py
+++ b/django/foo.py
@@ -1,3 +1,4 @@
 def f():
-    return 1
+    return compute_answer()
+    # note
diff --git a/tests/test_foo.py b/tests/test_foo.py
--- a/tests/test_foo.py
+++ b/tests/test_foo.py
@@ -1,2 +1,3 @@
 def test_f():
+    assert compute_answer() == 2
     pass
"""

NEAR_MISS = """\
diff --git a/django/foo.py b/django/foo.py
--- a/django/foo.py
+++ b/django/foo.py
@@ -1,3 +1,3 @@
 def f():
-    return 1
+    return compute_answer()
"""


class CraftHelperTests(unittest.TestCase):
    def test_jaccard_empty_and_partial(self) -> None:
        self.assertEqual(jaccard(set(), set()), 1.0)
        self.assertEqual(jaccard({"a"}, set()), 0.0)
        self.assertAlmostEqual(jaccard({"a", "b"}, {"b", "c"}), 1 / 3)

    def test_path_jaccard(self) -> None:
        self.assertEqual(path_jaccard(["a.py"], ["a.py"]), 1.0)
        self.assertEqual(path_jaccard(["a.py"], ["b.py"]), 0.0)

    def test_identical_craft_is_one(self) -> None:
        files = files_from_patch(SAMPLE)
        report = compute_craft(
            human_files=files,
            agent_files=files,
            human_patch=SAMPLE,
            agent_patch=SAMPLE,
        )
        self.assertAlmostEqual(report.craft_score, 1.0, places=6)
        self.assertEqual(report.path_jaccard, 1.0)
        self.assertEqual(report.line_overlap, 1.0)
        self.assertEqual(report.symbol_overlap, 1.0)
        self.assertIn("path_jaccard", report.components_used)
        self.assertIn("line_overlap", report.components_used)
        self.assertIn("symbol_overlap", report.components_used)

    def test_unrelated_stub_low_craft(self) -> None:
        files = files_from_patch(SAMPLE)
        stub_files = files_from_patch(STUB_PATCH)
        report = compute_craft(
            human_files=files,
            agent_files=stub_files,
            human_patch=SAMPLE,
            agent_patch=STUB_PATCH,
        )
        self.assertLess(report.craft_score, 0.35)
        self.assertEqual(report.path_jaccard, 0.0)

    def test_bloated_lower_than_near_miss(self) -> None:
        files = files_from_patch(SAMPLE)
        near = compute_craft(
            human_files=files,
            agent_files=files_from_patch(NEAR_MISS),
            human_patch=SAMPLE,
            agent_patch=NEAR_MISS,
        )
        bloated_patch = build_bloated_stub_patch()
        bloated = compute_craft(
            human_files=files,
            agent_files=files_from_patch(bloated_patch),
            human_patch=SAMPLE,
            agent_patch=bloated_patch,
        )
        self.assertGreater(near.craft_score, bloated.craft_score)
        self.assertLess(bloated.craft_score, 0.25)

    def test_line_and_symbol_helpers(self) -> None:
        self.assertEqual(line_overlap(SAMPLE, SAMPLE), 1.0)
        self.assertGreater(symbol_overlap(SAMPLE, NEAR_MISS), 0.0)


class EvalModeCraftTests(unittest.TestCase):
    def test_immediate_omits_craft(self) -> None:
        files = files_from_patch(SAMPLE)
        report = score_agent_vs_human(
            repo="django/django",
            pr_number=1,
            human_files=files,
            human_patch=SAMPLE,
            agent_patch=SAMPLE,
            passed_tests=True,
            mode=EVAL_MODE_IMMEDIATE,
        )
        self.assertEqual(report.eval_mode, EVAL_MODE_IMMEDIATE)
        self.assertIsNone(report.craft_score)
        self.assertIsNone(report.craft)

    def test_thorough_self_score_craft_one(self) -> None:
        files = files_from_patch(SAMPLE)
        report = score_agent_vs_human(
            repo="django/django",
            pr_number=1,
            human_files=files,
            human_patch=SAMPLE,
            agent_patch=SAMPLE,
            passed_tests=True,
            mode=EVAL_MODE_THOROUGH,
        )
        self.assertEqual(report.eval_mode, EVAL_MODE_THOROUGH)
        assert report.craft_score is not None
        self.assertAlmostEqual(report.craft_score, 1.0, places=6)
        self.assertIsNotNone(report.craft)


if __name__ == "__main__":
    unittest.main()
