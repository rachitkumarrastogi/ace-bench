"""Harvest merged GitHub PRs as human baseline patterns."""

from __future__ import annotations

import calendar
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, replace
from datetime import date, datetime, timedelta
from typing import Any, Iterator, Literal

import certifi

from ace_bench.db import HumanPattern, PatternStore
from ace_bench.metrics import directories_from_files, metrics_from_patch


GITHUB_API = "https://api.github.com"
# GitHub Search API hard-caps at 1000 results per query — window harvests stay under this.
SEARCH_RESULT_CAP = 1000
_TRANSIENT_HTTP = {408, 429, 500, 502, 503, 504}
_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())

WindowUnit = Literal["days", "months"]


@dataclass(frozen=True, slots=True)
class HarvestConfig:
    repos: list[str]
    merged_before: str  # ISO date YYYY-MM-DD — exclusive upper bound (pre-AI era)
    merged_after: str | None = None
    max_prs_per_repo: int = 100
    sleep_seconds: float = 0.25
    token: str | None = None
    max_retries: int = 5
    # When set, harvest() slices [merged_after, merged_before) into windows and runs each.
    window_unit: WindowUnit | None = None
    window_size: int = 1


def parse_iso_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def format_iso_date(value: date) -> str:
    return value.isoformat()


def add_months(value: date, months: int) -> date:
    """Advance calendar months without clamping mid-month (day preserved when possible)."""
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def iter_date_windows(
    merged_after: str,
    merged_before: str,
    unit: WindowUnit,
    size: int = 1,
) -> Iterator[tuple[str, str]]:
    """Yield (after_inclusive, before_exclusive) ISO date pairs covering [after, before).

    GitHub Search returns at most 1000 hits per query; callers should choose window
    sizes so each slice stays under that cap (monthly is usually safe for django/django).
    """
    if size < 1:
        raise ValueError(f"window size must be >= 1, got {size}")
    start = parse_iso_date(merged_after)
    end = parse_iso_date(merged_before)
    if start >= end:
        raise ValueError(f"merged_after ({merged_after}) must be < merged_before ({merged_before})")

    cursor = start
    while cursor < end:
        if unit == "days":
            nxt = cursor + timedelta(days=size)
        elif unit == "months":
            nxt = add_months(cursor, size)
        else:
            raise ValueError(f"unsupported window unit: {unit!r}")
        if nxt > end:
            nxt = end
        yield format_iso_date(cursor), format_iso_date(nxt)
        cursor = nxt


def build_merged_search_query(
    repo: str,
    merged_before: str,
    merged_after: str | None,
) -> str:
    """Build a GitHub Search query for merged PRs in a date range.

    Prefer ``merged:YYYY-MM-DD..YYYY-MM-DD`` when both bounds are set.
    Combining ``merged:>=`` with ``merged:<`` is unreliable (GitHub may ignore
    the lower bound and inflate total_count). Windows are [after, before).
    """
    parts = [f"repo:{repo}", "is:pr", "is:merged"]
    if merged_after:
        # Inclusive range covering [after, before): end date is the day before before.
        end_inclusive = parse_iso_date(merged_before) - timedelta(days=1)
        start = parse_iso_date(merged_after)
        if end_inclusive < start:
            raise ValueError(
                f"empty merged window: after={merged_after} before={merged_before}"
            )
        parts.append(f"merged:{format_iso_date(start)}..{format_iso_date(end_inclusive)}")
    else:
        parts.append(f"merged:<{merged_before}")
    return " ".join(parts)


class GitHubClient:
    def __init__(self, token: str | None = None, max_retries: int = 5) -> None:
        self.token = token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        self.max_retries = max_retries

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "ace-bench-harvest/0.1",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def get_json(self, url: str) -> Any:
        last_err: Exception | None = None
        for attempt in range(self.max_retries):
            req = urllib.request.Request(url, headers=self._headers())
            try:
                with urllib.request.urlopen(req, timeout=60, context=_SSL_CONTEXT) as resp:
                    remaining = resp.headers.get("X-RateLimit-Remaining")
                    if remaining is not None and int(remaining) < 5:
                        reset = int(resp.headers.get("X-RateLimit-Reset", "0"))
                        wait = max(0, reset - int(time.time()) + 5)
                        if wait > 0:
                            time.sleep(wait)
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace")
                last_err = RuntimeError(f"GitHub API {exc.code} for {url}: {body[:500]}")
                if exc.code not in _TRANSIENT_HTTP or attempt + 1 >= self.max_retries:
                    raise last_err from exc
                # Respect Retry-After when present (esp. secondary rate limits).
                retry_after = exc.headers.get("Retry-After")
                if retry_after and retry_after.isdigit():
                    wait = int(retry_after) + 1
                else:
                    wait = min(60, (2**attempt) + 1)
                time.sleep(wait)
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                last_err = exc
                if attempt + 1 >= self.max_retries:
                    raise RuntimeError(f"GitHub request failed for {url}: {exc}") from exc
                time.sleep(min(60, (2**attempt) + 1))
        raise RuntimeError(f"GitHub request failed for {url}: {last_err}")

    def iter_merged_pulls(
        self,
        repo: str,
        merged_before: str,
        merged_after: str | None,
        max_prs: int,
        sleep_seconds: float,
    ) -> Iterator[dict[str, Any]]:
        """Yield merged PRs newest-first via search API (supports date filters).

        GitHub Search returns at most SEARCH_RESULT_CAP (1000) hits per query.
        Use date windows so each query stays under that cap.
        """
        query = build_merged_search_query(repo, merged_before, merged_after)
        page = 1
        yielded = 0
        warned_cap = False
        while yielded < max_prs:
            params = urllib.parse.urlencode(
                {
                    "q": query,
                    "sort": "updated",
                    "order": "desc",
                    "per_page": min(50, max_prs - yielded),
                    "page": page,
                }
            )
            url = f"{GITHUB_API}/search/issues?{params}"
            payload = self.get_json(url)
            total_count = int(payload.get("total_count") or 0)
            if not warned_cap and total_count > SEARCH_RESULT_CAP:
                print(
                    f"warning: search for {repo} "
                    f"[{merged_after or '...'}, {merged_before}) reports "
                    f"total_count={total_count} (> {SEARCH_RESULT_CAP}); "
                    "results beyond the Search API cap are invisible — use smaller windows",
                    file=sys.stderr,
                )
                warned_cap = True
            items = payload.get("items") or []
            if not items:
                break
            for item in items:
                yield item
                yielded += 1
                if yielded >= max_prs:
                    break
            page += 1
            # Search API allows ~30 req/min authenticated; keep polite pacing.
            time.sleep(max(sleep_seconds, 0.35))
            # Hard stop: Search pagination cannot go past result #1000.
            if page * 50 > SEARCH_RESULT_CAP:
                break

    def get_pull(self, repo: str, number: int) -> dict[str, Any]:
        return self.get_json(f"{GITHUB_API}/repos/{repo}/pulls/{number}")

    def get_pull_files(self, repo: str, number: int) -> list[dict[str, Any]]:
        files: list[dict[str, Any]] = []
        page = 1
        while True:
            url = f"{GITHUB_API}/repos/{repo}/pulls/{number}/files?per_page=100&page={page}"
            batch = self.get_json(url)
            if not batch:
                break
            files.extend(batch)
            if len(batch) < 100:
                break
            page += 1
        return files


def build_pattern(
    repo: str,
    search_item: dict[str, Any],
    pull: dict[str, Any],
    files_payload: list[dict[str, Any]],
) -> HumanPattern:
    files = [f.get("filename") or "" for f in files_payload if f.get("filename")]
    patch_chunks = [f.get("patch") or "" for f in files_payload if f.get("patch")]
    patch_text = "\n".join(patch_chunks) if patch_chunks else None
    metrics = metrics_from_patch(patch_text, files)
    additions = int(pull.get("additions") or sum(int(f.get("additions") or 0) for f in files_payload))
    deletions = int(pull.get("deletions") or sum(int(f.get("deletions") or 0) for f in files_payload))
    user = pull.get("user") or {}
    base = pull.get("base") or {}
    return HumanPattern(
        repo=repo,
        pr_number=int(pull.get("number") or search_item.get("number")),
        merged_at=pull.get("merged_at"),
        base_sha=base.get("sha"),
        merge_commit_sha=pull.get("merge_commit_sha"),
        title=pull.get("title") or search_item.get("title"),
        body=pull.get("body") or search_item.get("body"),
        author_login=user.get("login"),
        html_url=pull.get("html_url") or search_item.get("html_url"),
        files=files,
        file_count=len(files),
        additions=additions,
        deletions=deletions,
        directories_touched=directories_from_files(files),
        patch_text=patch_text,
        metrics=metrics.as_dict(),
    )


def _harvest_single_window(store: PatternStore, config: HarvestConfig) -> dict[str, Any]:
    """Harvest one [merged_after, merged_before) slice into the store."""
    client = GitHubClient(token=config.token, max_retries=config.max_retries)
    run_id = store.start_run(config.repos, config.merged_before)
    inserted = 0
    updated = 0
    skipped = 0
    errors: list[str] = []

    try:
        for repo in config.repos:
            for item in client.iter_merged_pulls(
                repo=repo,
                merged_before=config.merged_before,
                merged_after=config.merged_after,
                max_prs=config.max_prs_per_repo,
                sleep_seconds=config.sleep_seconds,
            ):
                number = int(item["number"])
                try:
                    pull = client.get_pull(repo, number)
                    if not pull.get("merged_at"):
                        skipped += 1
                        continue
                    files_payload = client.get_pull_files(repo, number)
                    pattern = build_pattern(repo, item, pull, files_payload)
                    if store.upsert_pattern(pattern, run_id):
                        inserted += 1
                    else:
                        updated += 1
                except Exception as exc:  # noqa: BLE001 — keep harvest looping on DGX
                    errors.append(f"{repo}#{number}: {exc}")
                time.sleep(config.sleep_seconds)
        status = "completed" if not errors else "completed_with_errors"
        store.finish_run(run_id, status=status, notes=f"errors={len(errors)}")
    except Exception as exc:  # noqa: BLE001
        store.finish_run(run_id, status="failed", notes=str(exc))
        raise

    return {
        "run_id": run_id,
        "inserted": inserted,
        "updated": updated,
        "skipped": skipped,
        "errors": errors[:20],
        "error_count": len(errors),
        "merged_after": config.merged_after,
        "merged_before": config.merged_before,
        "summary": store.summary(),
    }


def harvest(store: PatternStore, config: HarvestConfig) -> dict[str, Any]:
    """Harvest patterns; when window_unit is set, slice the date range and upsert each window."""
    if config.window_unit is None:
        return _harvest_single_window(store, config)

    after = config.merged_after
    if not after:
        raise ValueError("--merged-after is required when using --window")

    windows = list(
        iter_date_windows(
            merged_after=after,
            merged_before=config.merged_before,
            unit=config.window_unit,
            size=config.window_size,
        )
    )
    print(
        f"windowed harvest: {len(windows)} {config.window_unit} window(s) "
        f"of size {config.window_size} over [{after}, {config.merged_before})",
        file=sys.stderr,
    )

    inserted = 0
    updated = 0
    skipped = 0
    error_count = 0
    window_errors: list[str] = []
    sample_errors: list[str] = []
    run_ids: list[int] = []

    for idx, (win_after, win_before) in enumerate(windows, start=1):
        print(
            f"[{idx}/{len(windows)}] window [{win_after}, {win_before}) …",
            file=sys.stderr,
        )
        win_config = replace(
            config,
            merged_after=win_after,
            merged_before=win_before,
            window_unit=None,  # recurse into single-window path
        )
        try:
            result = _harvest_single_window(store, win_config)
        except Exception as exc:  # noqa: BLE001 — continue remaining windows
            msg = f"window [{win_after}, {win_before}): {exc}"
            window_errors.append(msg)
            error_count += 1
            print(f"error: {msg}", file=sys.stderr)
            continue

        inserted += int(result["inserted"])
        updated += int(result["updated"])
        skipped += int(result["skipped"])
        error_count += int(result["error_count"])
        run_ids.append(int(result["run_id"]))
        for err in result.get("errors") or []:
            if len(sample_errors) < 20:
                sample_errors.append(err)
        print(
            f"  → inserted={result['inserted']} updated={result['updated']} "
            f"errors={result['error_count']} "
            f"db_total={result['summary'].get('pattern_count')}",
            file=sys.stderr,
        )

    return {
        "run_ids": run_ids,
        "windows": len(windows),
        "window_unit": config.window_unit,
        "window_size": config.window_size,
        "inserted": inserted,
        "updated": updated,
        "skipped": skipped,
        "errors": sample_errors,
        "window_errors": window_errors[:20],
        "error_count": error_count,
        "summary": store.summary(),
    }
