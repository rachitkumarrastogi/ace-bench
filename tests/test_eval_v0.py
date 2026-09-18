"""Offline unit tests for eval v0 scoring helpers."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ace_bench.eval_v0 import (
    files_from_patch,
    score_agent_vs_human,
    touches_tests,
)

SAMPLE = """\
diff --git a/django/foo.py b/django/foo.py
--- a/django/foo.py
+++ b/django/foo.py
@@ -1,3 +1,4 @@
 def f():
-    return 1
+    return 2
+    # note
diff --git a/tests/test_foo.py b/tests/test_foo.py
--- a/tests/test_foo.py
+++ b/tests/test_foo.py
@@ -1,2 +1,3 @@
 def test_f():
+    assert True
     pass
"""


class EvalV0Tests(unittest.TestCase):
    def test_files_from_patch(self) -> None:
        self.assertEqual(
            files_from_patch(SAMPLE),
            ["django/foo.py", "tests/test_foo.py"],
        )

    def test_touches_tests(self) -> None:
        self.assertTrue(touches_tests(["tests/test_foo.py"]))
        self.assertTrue(touches_tests(["django/tests/queries/tests.py"]))
        self.assertFalse(touches_tests(["django/db/models.py"]))

    def test_self_score_is_one(self) -> None:
        files = files_from_patch(SAMPLE)
        report = score_agent_vs_human(
            repo="django/django",
            pr_number=1,
            human_files=files,
            human_patch=SAMPLE,
            agent_patch=SAMPLE,
            passed_tests=True,
        )
        self.assertAlmostEqual(report.ace_score, 1.0, places=6)
        self.assertEqual(report.boundary["symmetric_diff_size"], 0)
        self.assertEqual(report.churn_ratio, 1.0)

    def test_headerless_needs_agent_files(self) -> None:
        hunks = "@@ -1,1 +1,2 @@\n foo\n+bar\n"
        files = ["pkg/mod.py"]
        report = score_agent_vs_human(
            repo="django/django",
            pr_number=2,
            human_files=files,
            human_patch=hunks,
            agent_patch=hunks,
            passed_tests=True,
            agent_files=files,
        )
        self.assertAlmostEqual(report.ace_score, 1.0, places=6)
        self.assertEqual(report.boundary["symmetric_diff_size"], 0)


if __name__ == "__main__":
    unittest.main()
