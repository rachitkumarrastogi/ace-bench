"""Offline unit tests for metrics + PatternStore upsert (no network)."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ace_bench.db import HumanPattern, PatternStore
from ace_bench.metrics import metrics_from_patch

SAMPLE_PATCH = """\
diff --git a/foo/bar.py b/foo/bar.py
--- a/foo/bar.py
+++ b/foo/bar.py
@@ -1,5 +1,12 @@
 def old():
-    return 1
+    return 2
+
+def new_helper():
+    if True:
+        for x in range(3):
+            pass
+    try:
+        pass
+    except Exception:
+        pass
"""


class MetricsTests(unittest.TestCase):
    def test_metrics_from_patch(self) -> None:
        files = ["foo/bar.py", "foo/baz.py"]
        m = metrics_from_patch(SAMPLE_PATCH, files)
        self.assertGreater(m.added_lines, 0)
        self.assertGreater(m.removed_lines, 0)
        self.assertEqual(m.file_count, 2)
        self.assertEqual(m.directories_touched, 1)
        self.assertGreaterEqual(m.decision_points_added, 1)
        self.assertGreaterEqual(m.loops_added, 1)
        self.assertGreaterEqual(m.functions_added, 1)
        self.assertIn(".py", m.extensions)
        d = m.as_dict()
        self.assertEqual(d["file_count"], 2)


class DbUpsertTests(unittest.TestCase):
    def test_upsert_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "t.sqlite"
            with PatternStore(db) as store:
                run_id = store.start_run(["django/django"], "2021-01-01")
                pattern = HumanPattern(
                    repo="django/django",
                    pr_number=42,
                    merged_at="2020-06-01T00:00:00Z",
                    base_sha="abc",
                    merge_commit_sha="def",
                    title="fix thing",
                    body="details",
                    author_login="someone",
                    html_url="https://github.com/django/django/pull/42",
                    files=["foo/bar.py"],
                    file_count=1,
                    additions=10,
                    deletions=2,
                    directories_touched=1,
                    patch_text=SAMPLE_PATCH,
                    metrics=metrics_from_patch(SAMPLE_PATCH, ["foo/bar.py"]).as_dict(),
                )
                self.assertTrue(store.upsert_pattern(pattern, run_id))
                self.assertEqual(store.count_patterns(), 1)

                updated = replace(
                    pattern,
                    title="fix thing (revised)",
                    additions=11,
                )
                self.assertFalse(store.upsert_pattern(updated, run_id))
                self.assertEqual(store.count_patterns(), 1)

                row = store._conn.execute(
                    "SELECT title, additions, metrics_json FROM human_patterns WHERE pr_number = 42"
                ).fetchone()
                self.assertEqual(row["title"], "fix thing (revised)")
                self.assertEqual(row["additions"], 11)
                metrics = json.loads(row["metrics_json"])
                self.assertIn("decision_points_added", metrics)

                store.finish_run(run_id, "completed")
                summary = store.summary()
                self.assertEqual(summary["total"], 1)
                self.assertEqual(summary["by_repo"][0]["repo"], "django/django")


if __name__ == "__main__":
    unittest.main()
