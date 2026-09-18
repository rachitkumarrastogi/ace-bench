"""Harvest merged GitHub PRs as human baseline patterns."""

from __future__ import annotations

import json
import os
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Iterator

import certifi

from ace_bench.db import HumanPattern, PatternStore
from ace_bench.metrics import directories_from_files, metrics_from_patch


GITHUB_API = "https://api.github.com"
_TRANSIENT_HTTP = {408, 429, 500, 502, 503, 504}
_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


@dataclass(frozen=True, slots=True)
class HarvestConfig:
    repos: list[str]
    merged_before: str  # ISO date YYYY-MM-DD — exclusive upper bound (pre-AI era)
    merged_after: str | None = None
    max_prs_per_repo: int = 100
    sleep_seconds: float = 0.25
    token: str | None = None
    max_retries: int = 5


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
        """Yield merged PRs newest-first via search API (supports date filters)."""
        # Search is the reliable way to filter merged:<date>
        # Example: repo:django/django is:pr is:merged merged:<2021-01-01
        parts = [f"repo:{repo}", "is:pr", "is:merged", f"merged:<{merged_before}"]
        if merged_after:
            parts.append(f"merged:>={merged_after}")
        query = " ".join(parts)
        page = 1
        yielded = 0
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
            items = payload.get("items") or []
            if not items:
                break
            for item in items:
                yield item
                yielded += 1
                if yielded >= max_prs:
                    break
            page += 1
            time.sleep(sleep_seconds)

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


def harvest(store: PatternStore, config: HarvestConfig) -> dict[str, Any]:
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
        "summary": store.summary(),
    }
