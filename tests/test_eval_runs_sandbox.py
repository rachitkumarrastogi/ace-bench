"""Unit tests for eval_runs store + sandbox path validation (offline)."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ace_bench.agents.base import AgentContext
from ace_bench.agents.stub import StubAgent, build_bloated_stub_patch
from ace_bench.eval_runs import EvalRunStore, patch_sha256
from ace_bench.pr_artifact import write_agent_pr_md
from ace_bench.sandbox import (
    SandboxError,
    assert_sandbox_path_safe,
    github_clone_url,
    validate_base_sha,
    validate_work_root,
    write_issue_md,
)


class EvalRunStoreTests(unittest.TestCase):
    def test_start_finish_and_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "eval_runs.sqlite"
            with EvalRunStore(db) as store:
                run_id = store.start_run(
                    instance_id="django/django#22",
                    model_name="human-replay",
                    agent_name="file",
                )
                self.assertGreater(run_id, 0)
                store.finish_run(
                    run_id,
                    passed_tests=True,
                    ace_score=1.0,
                    file_drift=0,
                    churn_ratio=1.0,
                    human_files=["a.py"],
                    agent_files=["a.py"],
                    notes="smoke",
                    patch_hash=patch_sha256("+x\n"),
                    patch_path="/tmp/x.patch",
                )
                # Second run same instance+model allowed.
                run_id2 = store.start_run(
                    instance_id="django/django#22",
                    model_name="human-replay",
                    agent_name="file",
                )
                store.finish_run(run_id2, ace_score=0.5, passed_tests=False)

                row = store.get_run(run_id)
                assert row is not None
                self.assertEqual(row.model_name, "human-replay")
                self.assertEqual(row.ace_score, 1.0)
                self.assertTrue(row.passed_tests)
                self.assertEqual(row.human_files, ["a.py"])
                self.assertEqual(store.count_runs(), 2)
                listed = store.list_runs(instance_id="django/django#22")
                self.assertEqual(len(listed), 2)

    def test_model_name_required(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "eval_runs.sqlite"
            with EvalRunStore(db) as store:
                with self.assertRaises(ValueError):
                    store.start_run(instance_id="a/b#1", model_name="  ")


class SandboxPathTests(unittest.TestCase):
    def test_github_clone_url_allowlist(self) -> None:
        self.assertEqual(
            github_clone_url("django/django"),
            "https://github.com/django/django.git",
        )

    def test_validate_base_sha(self) -> None:
        self.assertEqual(validate_base_sha("abc1234"), "abc1234")
        with self.assertRaises(SandboxError):
            validate_base_sha("../etc/passwd")
        with self.assertRaises(SandboxError):
            validate_base_sha("zzzz")

    def test_work_root_under_tmp(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
            root = validate_work_root(tmp)
            # macOS resolves /tmp → /private/tmp
            self.assertTrue(
                str(root).startswith("/tmp") or str(root).startswith("/private/tmp")
            )
            nested = root / "django__django__abc"
            nested.mkdir()
            safe = assert_sandbox_path_safe(nested, work_root=root)
            self.assertEqual(safe, nested.resolve())

    def test_reject_escape_from_work_root(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
            root = Path(tmp).resolve()
            outside = root.parent / "outside"
            with self.assertRaises(SandboxError):
                assert_sandbox_path_safe(outside, work_root=root)

    def test_write_issue_md(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            wt = Path(tmp)
            path = write_issue_md(
                wt,
                title="T",
                body="Body text",
                instance_id="django/django#22",
            )
            text = path.read_text(encoding="utf-8")
            self.assertIn("# T", text)
            self.assertIn("Body text", text)
            self.assertIn("django/django#22", text)

    def test_agent_pr_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            wt = Path(tmp)
            path = write_agent_pr_md(
                wt,
                title="Fix admin views",
                model_name="human-replay",
                instance_id="django/django#22",
                ace_score=1.0,
                file_drift=0,
                human_files=["a.py"],
                agent_files=["a.py"],
                agent_name="file",
                churn_ratio=1.0,
                patch_path="/tmp/x.patch",
                base_sha="02a5b41db4ff8544f93a5d9854b346a9aae4f556",
            )
            self.assertEqual(path.name, "AGENT_PR.md")
            text = path.read_text(encoding="utf-8")
            self.assertIn("model_name", text)
            self.assertIn("human-replay", text)
            self.assertIn("ACE score", text)
            self.assertIn("PR-shaped artifact", text)

    def test_bloated_stub_patch(self) -> None:
        patch = build_bloated_stub_patch(n_files=4, lines_per=20)
        self.assertIn("bloated/extra_0.py", patch)
        self.assertGreater(patch.count("diff --git"), 3)
        result = StubAgent(bloated=True).run(
            AgentContext(
                instance_id="x/y#1",
                repo="x/y",
                pr_number=1,
                title="",
                body="",
                model_name="stub-bloated",
                worktree=None,
                human_files=[],
                base_sha=None,
            )
        )
        self.assertIn("bloated/", result.patch_text)

    def test_checkout_mocked_git(self) -> None:
        """Checkout path wiring without touching the network."""
        from ace_bench.sandbox import checkout_at_base_sha

        with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
            root = Path(tmp)

            def fake_clone(url: str, workdir: Path, sha: str) -> None:
                workdir.mkdir(parents=True)
                (workdir / ".git").mkdir()
                (workdir / "README").write_text("ok", encoding="utf-8")

            with patch("ace_bench.sandbox._clone_partial", side_effect=fake_clone):
                result = checkout_at_base_sha(
                    repo="django/django",
                    base_sha="02a5b41db4ff8544f93a5d9854b346a9aae4f556",
                    work_root=root,
                    title="t",
                    body="b",
                    instance_id="django/django#22",
                )
            self.assertTrue(result.worktree.is_dir())
            self.assertTrue((result.worktree / "ISSUE.md").is_file())
            self.assertFalse(result.used_docker)


if __name__ == "__main__":
    unittest.main()
