"""Security-focused offline unit tests (paths, SSRF, tokens, SQL, scoring)."""

from __future__ import annotations

import sqlite3
import stat
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ace_bench.db import HumanPattern, PatternStore
from ace_bench.eval_v0 import InstanceIdError, parse_instance_id, score_agent_vs_human
from ace_bench.github_url import UnsafeGitHubUrlError, assert_github_api_url, redact_secrets
from ace_bench.metrics import metrics_from_patch
from ace_bench.paths import PathEscapeError, read_text_capped, resolve_allowed_path
from ace_bench.scoring import AceScoreInputs, compute_ace_score
from ace_bench.tokens import load_token_from_file, token_file_mode_ok


class PathSafetyTests(unittest.TestCase):
    def test_resolve_under_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            target = root / "data" / "x.sqlite"
            target.parent.mkdir(parents=True)
            target.write_text("x", encoding="utf-8")
            resolved = resolve_allowed_path(
                target, allowed_roots=[root], purpose="db"
            )
            self.assertEqual(resolved, target.resolve())

    def test_reject_escape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            outside = root.parent / "outside.txt"
            with self.assertRaises(PathEscapeError):
                resolve_allowed_path(outside, allowed_roots=[root], purpose="db")

    def test_read_text_capped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "big.patch"
            p.write_bytes(b"a" * 100)
            with self.assertRaises(ValueError):
                read_text_capped(p, max_bytes=50)


class GithubUrlTests(unittest.TestCase):
    def test_allow_api_github(self) -> None:
        assert_github_api_url("https://api.github.com/search/issues?q=x")

    def test_reject_other_hosts(self) -> None:
        with self.assertRaises(UnsafeGitHubUrlError):
            assert_github_api_url("https://evil.example/x")
        with self.assertRaises(UnsafeGitHubUrlError):
            assert_github_api_url("http://api.github.com/x")

    def test_redact_authorization(self) -> None:
        text = "Authorization: Bearer ghp_secretvalue123"
        self.assertIn("[REDACTED]", redact_secrets(text))
        self.assertNotIn("ghp_secretvalue123", redact_secrets(text))


class TokenFileTests(unittest.TestCase):
    def test_loose_mode_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "github_token"
            p.write_text("fake-token\n", encoding="utf-8")
            p.chmod(0o644)
            self.assertFalse(token_file_mode_ok(p))
            # load still works; does not return via print
            self.assertEqual(load_token_from_file(p), "fake-token")

    def test_strict_mode_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "github_token"
            p.write_text("tok\n", encoding="utf-8")
            p.chmod(0o600)
            self.assertTrue(token_file_mode_ok(p))
            self.assertEqual(stat.S_IMODE(p.stat().st_mode), 0o600)


class SqlParameterizationTests(unittest.TestCase):
    def test_get_pattern_uses_binds(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "t.sqlite"
            with PatternStore(db) as store:
                run_id = store.start_run(["django/django"], "2021-01-01")
                patch = "+x\n"
                store.upsert_pattern(
                    HumanPattern(
                        repo="django/django",
                        pr_number=7,
                        merged_at="2020-01-01T00:00:00Z",
                        base_sha="a",
                        merge_commit_sha="b",
                        title="t",
                        body="b",
                        author_login="u",
                        html_url="https://github.com/django/django/pull/7",
                        files=["a.py"],
                        file_count=1,
                        additions=1,
                        deletions=0,
                        directories_touched=1,
                        patch_text=patch,
                        metrics=metrics_from_patch(patch, ["a.py"]).as_dict(),
                    ),
                    run_id,
                )
                # Malicious-looking slug must not match via injection; parameterized.
                evil = store.get_pattern("django/django' OR '1'='1", 7)
                self.assertIsNone(evil)
                row = store.get_pattern("django/django", 7)
                self.assertIsNotNone(row)
                # Ensure connection still healthy with explicit bind query.
                n = store._conn.execute(
                    "SELECT COUNT(*) AS n FROM human_patterns WHERE repo = ?",
                    ("django/django",),
                ).fetchone()["n"]
                self.assertEqual(n, 1)


class InstanceIdTests(unittest.TestCase):
    def test_parse_ok(self) -> None:
        self.assertEqual(parse_instance_id("django/django#22"), ("django/django", 22))
        self.assertEqual(parse_instance_id("django/django@22"), ("django/django", 22))

    def test_parse_reject(self) -> None:
        with self.assertRaises(InstanceIdError):
            parse_instance_id("../etc/passwd#1")
        with self.assertRaises(InstanceIdError):
            parse_instance_id("django/django")
        with self.assertRaises(InstanceIdError):
            parse_instance_id("django/django#-1")


class ScoringTests(unittest.TestCase):
    def test_fail_closed_on_tests(self) -> None:
        self.assertEqual(
            compute_ace_score(
                AceScoreInputs(10, 10, 2, 2, passed_tests=False)
            ),
            0.0,
        )

    def test_self_consistency(self) -> None:
        sample = (
            "diff --git a/a.py b/a.py\n"
            "--- a/a.py\n+++ b/a.py\n"
            "@@ -1 +1,2 @@\n x\n+y\n"
        )
        files = ["a.py"]
        report = score_agent_vs_human(
            repo="django/django",
            pr_number=1,
            human_files=files,
            human_patch=sample,
            agent_patch=sample,
            passed_tests=True,
        )
        self.assertAlmostEqual(report.ace_score, 1.0, places=6)


class SqliteSchemaSmoke(unittest.TestCase):
    def test_schema_script_is_static(self) -> None:
        # SCHEMA is a constant string — no user interpolation.
        from ace_bench.db import SCHEMA

        self.assertIn("CREATE TABLE", SCHEMA)
        conn = sqlite3.connect(":memory:")
        conn.executescript(SCHEMA)
        conn.close()


if __name__ == "__main__":
    unittest.main()
