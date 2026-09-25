"""Unit tests for batch eval instance selection helpers."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ace_bench.db import HumanPattern, PatternStore  # noqa: E402
from run_batch_eval import (  # noqa: E402
    load_jsonl_instances,
    pad_from_db,
    select_instances,
)


def _pat(pr: int, files: list[str] | None = None) -> HumanPattern:
    files = files or [f"tests/t{pr}.py"]
    return HumanPattern(
        repo="django/django",
        pr_number=pr,
        merged_at=f"2015-01-{pr:02d}T00:00:00Z",
        base_sha="a" * 40,
        merge_commit_sha="b" * 40,
        title=f"PR {pr}",
        body=f"body {pr}",
        author_login="dev",
        html_url=f"https://github.com/django/django/pull/{pr}",
        files=files,
        file_count=len(files),
        additions=3,
        deletions=1,
        directories_touched=1,
        patch_text=f"@@ -1 +1,2 @@\n+fix_{pr}\n",
        metrics={"added_lines": 1, "deleted_lines": 0},
    )


class BatchSelectTests(unittest.TestCase):
    def test_load_jsonl_and_pad(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db_path = root / "t.sqlite"
            jsonl = root / "eval.jsonl"
            with PatternStore(db_path) as store:
                run_id = store.start_run(["django/django"], "2021-01-01")
                for pr in range(1, 8):
                    store.upsert_pattern(_pat(pr), run_id)

            rows = [
                {
                    "instance_id": "django/django#1",
                    "repo": "django/django",
                    "pr_number": 1,
                    "html_url": "https://github.com/django/django/pull/1",
                    "title": "PR 1",
                    "patch_in_db": True,
                },
                {
                    "instance_id": "django/django#2",
                    "repo": "django/django",
                    "pr_number": 2,
                    "html_url": "https://github.com/django/django/pull/2",
                    "title": "PR 2",
                    "patch_in_db": True,
                },
            ]
            jsonl.write_text(
                "\n".join(json.dumps(r) for r in rows) + "\n",
                encoding="utf-8",
            )
            loaded = load_jsonl_instances(jsonl)
            self.assertEqual(len(loaded), 2)
            self.assertEqual(loaded[0].source, "jsonl")

            with PatternStore(db_path) as store:
                selected = select_instances(
                    jsonl_path=jsonl,
                    store=store,
                    limit=5,
                )
            self.assertEqual(len(selected), 5)
            self.assertEqual(selected[0].instance_id, "django/django#1")
            self.assertEqual(selected[1].instance_id, "django/django#2")
            sources = {s.instance_id: s.source for s in selected}
            self.assertEqual(sources["django/django#1"], "jsonl")
            # padded ids should be db
            for iid, src in sources.items():
                if iid not in ("django/django#1", "django/django#2"):
                    self.assertEqual(src, "db")

    def test_pad_skips_already(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "t.sqlite"
            with PatternStore(db_path) as store:
                run_id = store.start_run(["django/django"], "2021-01-01")
                for pr in range(1, 5):
                    store.upsert_pattern(_pat(pr), run_id)
                pad = pad_from_db(
                    store,
                    already={"django/django#1", "django/django#2"},
                    need=2,
                )
            ids = [p.instance_id for p in pad]
            self.assertEqual(len(ids), 2)
            self.assertNotIn("django/django#1", ids)
            self.assertNotIn("django/django#2", ids)


if __name__ == "__main__":
    unittest.main()
