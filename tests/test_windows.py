"""Unit tests for date-window slicing (GitHub Search 1000-hit cap)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ace_bench.harvest import (
    add_months,
    build_merged_search_query,
    iter_date_windows,
    parse_iso_date,
)


class WindowTests(unittest.TestCase):
    def test_monthly_windows_cover_range(self) -> None:
        windows = list(iter_date_windows("2012-01-01", "2012-04-01", "months", 1))
        self.assertEqual(
            windows,
            [
                ("2012-01-01", "2012-02-01"),
                ("2012-02-01", "2012-03-01"),
                ("2012-03-01", "2012-04-01"),
            ],
        )

    def test_full_django_span_is_108_months(self) -> None:
        windows = list(iter_date_windows("2012-01-01", "2021-01-01", "months", 1))
        self.assertEqual(len(windows), 108)
        self.assertEqual(windows[0], ("2012-01-01", "2012-02-01"))
        self.assertEqual(windows[-1], ("2020-12-01", "2021-01-01"))

    def test_daily_windows(self) -> None:
        windows = list(iter_date_windows("2020-01-01", "2020-01-04", "days", 1))
        self.assertEqual(len(windows), 3)
        self.assertEqual(windows[0], ("2020-01-01", "2020-01-02"))

    def test_add_months_end_of_month(self) -> None:
        self.assertEqual(add_months(parse_iso_date("2012-01-31"), 1).isoformat(), "2012-02-29")

    def test_bad_range(self) -> None:
        with self.assertRaises(ValueError):
            list(iter_date_windows("2021-01-01", "2012-01-01", "months", 1))

    def test_search_query_uses_range_syntax(self) -> None:
        q = build_merged_search_query("django/django", "2012-02-01", "2012-01-01")
        self.assertIn("merged:2012-01-01..2012-01-31", q)
        self.assertNotIn("merged:>=", q)
        self.assertNotIn("merged:<2012-02-01", q)

    def test_search_query_before_only(self) -> None:
        q = build_merged_search_query("django/django", "2021-01-01", None)
        self.assertIn("merged:<2021-01-01", q)


if __name__ == "__main__":
    unittest.main()
