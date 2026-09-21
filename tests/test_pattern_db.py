"""Unit tests for pattern prior DB (offline; no harvest network)."""

from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ace_bench.db import HumanPattern, PatternStore
from ace_bench.metrics import metrics_from_patch
from ace_bench.pattern_db import build_pattern_db, percentile

SAMPLE_PATCH = """\
diff --git a/foo.py b/foo.py
--- a/foo.py
+++ b/foo.py
@@ -1,1 +1,3 @@
-x = 1
+x = 2
+if True:
+    pass
"""


class PercentileTests(unittest.TestCase):
    def test_p50(self) -> None:
        self.assertEqual(percentile([1, 2, 3, 4, 5], 50), 3.0)


class PatternDbBuildTests(unittest.TestCase):
    def test_build_from_harvest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            harvest = tmp_path / "harvest.sqlite"
            out = tmp_path / "patterns.sqlite"
            corpus = tmp_path / "corpus.json"
            corpus.write_text(
                json.dumps(
                    {
                        "tier_a": [
                            {"repo": "acme/lib", "lang": "Python"},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            with PatternStore(harvest) as store:
                run_id = store.start_run(["acme/lib"], "2021-01-01")
                file_sets = (["a1.py"], ["a2.py", "b2.py"])
                for i, files in enumerate(file_sets, start=1):
                    m = metrics_from_patch(SAMPLE_PATCH, files)
                    store.upsert_pattern(
                        HumanPattern(
                            repo="acme/lib",
                            pr_number=i,
                            merged_at="2020-01-01T00:00:00Z",
                            base_sha="abc",
                            merge_commit_sha="def",
                            title=f"pr {i}",
                            body="body",
                            author_login="u",
                            html_url=f"https://example.com/{i}",
                            files=list(files),
                            file_count=len(files),
                            additions=3,
                            deletions=1,
                            directories_touched=1,
                            patch_text=SAMPLE_PATCH,
                            metrics=m.as_dict(),
                        ),
                        run_id,
                    )

            result = build_pattern_db([harvest], out, corpus_json=corpus)
            self.assertEqual(result["n_repos"], 1)
            self.assertEqual(result["n_prs"], 2)
            self.assertTrue(out.is_file())

            conn = sqlite3.connect(out)
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM repo_baselines WHERE repo = ?", ("acme/lib",)
            ).fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row["language"], "Python")
            self.assertEqual(row["n"], 2)
            global_row = conn.execute(
                "SELECT * FROM global_baselines WHERE scope = 'all'"
            ).fetchone()
            self.assertEqual(global_row["n_prs"], 2)
            conn.close()


if __name__ == "__main__":
    unittest.main()
