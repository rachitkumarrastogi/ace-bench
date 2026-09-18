#!/usr/bin/env python3
"""Refresh docs/CORPUS_STATUS.md from live DB + optional GitHub Search counts.

Reads harvested counts from SQLite (ACE_DB_PATH), corpus membership/tiers from
data/corpus_repos.json, and optionally fills missing pre_2021_merged_prs via
GitHub Search (total_count) with a gentle rate limit. Caches fetched counts
back into the JSON so re-runs skip Search for known values.

Usage (DGX or local):

  export ACE_DB_PATH=$HOME/ace-bench/data/ace_patterns.sqlite
  export GITHUB_TOKEN=...   # or ~/.config/ace-bench/github_token
  python3 scripts/refresh_corpus_status.py --fetch-github

  # cached JSON counts only (no Search):
  python3 scripts/refresh_corpus_status.py
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import certifi

    _SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:  # pragma: no cover
    _SSL_CONTEXT = ssl.create_default_context()

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ace_bench.github_url import assert_github_api_url, redact_secrets, redact_url
from ace_bench.harvest import SEARCH_PAGE_SLEEP_SECONDS, validate_repo_slug
from ace_bench.paths import PathEscapeError, resolve_allowed_path
from ace_bench.tokens import DEFAULT_TOKEN_FILE, resolve_github_token

DEFAULT_DB = Path(os.environ.get("ACE_DB_PATH") or (ROOT / "data" / "ace_patterns.sqlite"))
DEFAULT_CORPUS = ROOT / "data" / "corpus_repos.json"
DEFAULT_OUT = ROOT / "docs" / "CORPUS_STATUS.md"
DEFAULT_LOG = Path(
    os.environ.get("CORPUS_HARVEST_LOG")
    or (Path.home() / "ace-bench" / "data" / "corpus_harvest.log")
)
CUTOFF_QUERY = "merged:<2021-01-01"
SEARCH_SLEEP_SECONDS = SEARCH_PAGE_SLEEP_SECONDS
COVERAGE_DONE_THRESHOLD = 0.95
ABS_SLACK = 5
GITHUB_API = "https://api.github.com"
_TRANSIENT_HTTP = {408, 429, 500, 502, 503, 504}


@dataclass(frozen=True, slots=True)
class RepoRow:
    repo: str
    tier: str
    github_pre2021: int | None
    harvested: int
    status: str
    coverage_pct: float | None
    notes: str
    why: str
    lang: str
    risk: str


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def resolve_token(explicit: str | None, token_file: Path) -> str | None:
    return resolve_github_token(explicit=explicit, token_file=token_file)


def load_harvested_counts(db_path: Path) -> dict[str, int]:
    if not db_path.is_file():
        print(f"warning: DB not found at {db_path}; harvested counts = 0", file=sys.stderr)
        return {}
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        rows = conn.execute(
            "SELECT repo, COUNT(*) FROM human_patterns GROUP BY repo"
        ).fetchall()
    finally:
        conn.close()
    return {str(repo): int(n) for repo, n in rows}


def parse_harvest_log(log_path: Path) -> tuple[set[str], set[str], str | None]:
    """Return (finished_ok, failed, currently_harvesting)."""
    finished_ok: set[str] = set()
    failed: set[str] = set()
    started: list[str] = []
    if not log_path.is_file():
        return finished_ok, failed, None

    started_re = re.compile(r"started_repo:\s+\S+\s+(\S+)")
    finished_re = re.compile(r"finished_repo:\s+\S+\s+(\S+)\s+rc=0")
    failed_re = re.compile(r"FAILED_repo:\s+\S+\s+(\S+)")

    text = log_path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        m = started_re.search(line)
        if m:
            started.append(m.group(1))
            continue
        m = finished_re.search(line)
        if m:
            finished_ok.add(m.group(1))
            continue
        m = failed_re.search(line)
        if m:
            failed.add(m.group(1))

    harvesting: str | None = None
    if started:
        last = started[-1]
        if last not in finished_ok and last not in failed:
            harvesting = last
    return finished_ok, failed, harvesting


def iter_corpus_repos(data: dict[str, Any]) -> list[tuple[str, str, dict[str, Any]]]:
    """Yield (repo, tier_label, entry) for status + tier_a/b/c (deduped)."""
    seen: set[str] = set()
    out: list[tuple[str, str, dict[str, Any]]] = []

    for entry in data.get("status", []):
        repo = entry.get("repo")
        if not repo or repo in seen:
            continue
        seen.add(repo)
        out.append((repo, "kickoff", entry))

    for tier_key, label in (
        ("tier_a", "A"),
        ("tier_b", "B"),
        ("tier_c", "C"),
    ):
        for entry in data.get(tier_key, []):
            repo = entry.get("repo")
            if not repo or repo in seen:
                continue
            seen.add(repo)
            out.append((repo, label, entry))

    return out


def github_search_total(repo: str, token: str | None, max_retries: int = 5) -> int:
    repo = validate_repo_slug(repo)
    query = f"repo:{repo} is:pr is:merged {CUTOFF_QUERY}"
    params = urllib.parse.urlencode({"q": query, "per_page": 1})
    url = f"{GITHUB_API}/search/issues?{params}"
    assert_github_api_url(url)
    safe_url = redact_url(url)
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "ace-bench-corpus-status/0.1",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    last_err: Exception | None = None
    for attempt in range(max_retries):
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=60, context=_SSL_CONTEXT) as resp:
                remaining = resp.headers.get("X-RateLimit-Remaining")
                if remaining is not None and int(remaining) < 3:
                    reset = int(resp.headers.get("X-RateLimit-Reset", "0"))
                    wait = max(0, reset - int(time.time()) + 5)
                    if wait > 0:
                        print(f"  rate-limit pause {wait}s…", file=sys.stderr)
                        time.sleep(wait)
                payload = json.loads(resp.read().decode("utf-8"))
                return int(payload.get("total_count") or 0)
        except urllib.error.HTTPError as exc:
            body = redact_secrets(exc.read().decode("utf-8", errors="replace"))
            last_err = RuntimeError(f"GitHub API {exc.code} for {safe_url}: {body[:300]}")
            if exc.code not in _TRANSIENT_HTTP or attempt + 1 >= max_retries:
                raise last_err from exc
            retry_after = exc.headers.get("Retry-After")
            if retry_after and retry_after.isdigit():
                wait = int(retry_after) + 1
            else:
                wait = min(60, (2**attempt) + 1)
            time.sleep(wait)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_err = exc
            if attempt + 1 >= max_retries:
                raise RuntimeError(
                    f"GitHub request failed for {safe_url}: {exc}"
                ) from exc
            time.sleep(min(60, (2**attempt) + 1))
    raise RuntimeError(f"GitHub request failed for {safe_url}: {last_err}")


def cache_count_into_corpus(
    data: dict[str, Any],
    repo: str,
    count: int,
) -> bool:
    """Set pre_2021_merged_prs + prs_verified on the matching entry. Return True if changed."""
    changed = False
    for key in ("status", "tier_a", "tier_b", "tier_c"):
        for entry in data.get(key, []):
            if entry.get("repo") != repo:
                continue
            if entry.get("pre_2021_merged_prs") != count or not entry.get("prs_verified"):
                entry["pre_2021_merged_prs"] = count
                entry["prs_verified"] = True
                changed = True
            return changed
    return changed


def decide_status(
    *,
    repo: str,
    harvested: int,
    github: int | None,
    finished_ok: set[str],
    harvesting: str | None,
    entry: dict[str, Any],
) -> tuple[str, str]:
    """Return (status, notes_extra)."""
    json_status = str(entry.get("status") or "")
    notes_bits: list[str] = []

    coverage_ok = False
    if github is not None and github > 0 and harvested > 0:
        if harvested / github >= COVERAGE_DONE_THRESHOLD:
            coverage_ok = True
        elif abs(harvested - github) <= ABS_SLACK:
            coverage_ok = True

    if harvesting == repo:
        return "harvesting", "active in corpus_harvest.log"

    if repo in finished_ok:
        return "done", "finished_repo in harvest log"

    if harvested > 0 and coverage_ok:
        return "done", f"coverage ≥{int(COVERAGE_DONE_THRESHOLD * 100)}% of GitHub Search"

    if json_status in {"done_frozen", "done_harvested", "done"} and harvested > 0:
        return "done", json_status.replace("_", " ")

    if harvested > 0 and github is None:
        notes_bits.append("partial / github count TBD")
        return "queued", "; ".join(notes_bits)

    if harvested > 0 and github is not None and not coverage_ok:
        return "queued", "partial harvest vs GitHub count (resume)"

    if json_status in {"skipped", "excluded"}:
        return "skipped", json_status

    return "queued", ""


def coverage_pct(harvested: int, github: int | None) -> float | None:
    if github is None or github <= 0:
        return None
    return 100.0 * harvested / github


def build_rows(
    data: dict[str, Any],
    harvested: dict[str, int],
    finished_ok: set[str],
    harvesting: str | None,
) -> list[RepoRow]:
    rows: list[RepoRow] = []
    for repo, tier, entry in iter_corpus_repos(data):
        gh_raw = entry.get("pre_2021_merged_prs")
        github = int(gh_raw) if isinstance(gh_raw, int) else None
        n = int(harvested.get(repo, 0))
        status, extra = decide_status(
            repo=repo,
            harvested=n,
            github=github,
            finished_ok=finished_ok,
            harvesting=harvesting,
            entry=entry,
        )
        base_notes = str(entry.get("notes") or "").strip()
        why = str(entry.get("why") or "").strip()
        note_parts = [p for p in (base_notes, extra) if p]
        rows.append(
            RepoRow(
                repo=repo,
                tier=tier,
                github_pre2021=github,
                harvested=n,
                status=status,
                coverage_pct=coverage_pct(n, github),
                notes="; ".join(note_parts),
                why=why,
                lang=str(entry.get("lang") or ""),
                risk=str(entry.get("risk") or ""),
            )
        )
    return rows


def fmt_github(n: int | None) -> str:
    return "TBD" if n is None else str(n)


def fmt_coverage(pct: float | None) -> str:
    if pct is None:
        return "—"
    return f"{pct:.1f}%"


def render_markdown(
    rows: list[RepoRow],
    *,
    generated_at: str,
    db_path: Path,
    corpus_path: Path,
    log_path: Path,
    fetched: int,
    harvest_active: str | None,
) -> str:
    total_harvested = sum(r.harvested for r in rows)
    repos_with_data = sum(1 for r in rows if r.harvested > 0)
    n_done = sum(1 for r in rows if r.status == "done")
    n_harvesting = sum(1 for r in rows if r.status == "harvesting")
    n_queued = sum(1 for r in rows if r.status == "queued")
    n_skipped = sum(1 for r in rows if r.status == "skipped")
    github_known = sum(1 for r in rows if r.github_pre2021 is not None)
    github_sum = sum(r.github_pre2021 or 0 for r in rows if r.github_pre2021 is not None)

    lines: list[str] = [
        "# ACE-Bench corpus status",
        "",
        f"_Generated: **{generated_at}** (UTC)_",
        "",
        "Per-repo GitHub Search `total_count` for "
        f"`is:pr is:merged {CUTOFF_QUERY}` vs rows in `human_patterns`.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total harvested rows | **{total_harvested}** |",
        f"| Repos with data | **{repos_with_data}** / {len(rows)} |",
        f"| Status: done | {n_done} |",
        f"| Status: harvesting | {n_harvesting} |",
        f"| Status: queued / pending | {n_queued} |",
        f"| Status: skipped | {n_skipped} |",
        f"| GitHub counts known | {github_known} / {len(rows)} "
        f"(sum of known = {github_sum}) |",
        f"| Active harvest (log) | `{harvest_active or '—'}` |",
        f"| DB | `{db_path}` |",
        f"| Corpus JSON | `{corpus_path}` |",
        f"| Harvest log | `{log_path}` |",
        f"| GitHub Search fetches this run | {fetched} |",
        "",
        "**Done** when harvested &gt; 0 and harvest finished for the repo in logs, "
        f"or coverage ≥ {int(COVERAGE_DONE_THRESHOLD * 100)}% of the GitHub count "
        f"(or within ±{ABS_SLACK} PRs).",
        "",
        "Refresh:",
        "",
        "```bash",
        "export ACE_DB_PATH=$HOME/ace-bench/data/ace_patterns.sqlite",
        "python3 scripts/refresh_corpus_status.py --fetch-github",
        "```",
        "",
        "## Per-repo table",
        "",
        "| repo | tier | status | github_pre2021 | harvested | coverage % | notes |",
        "|------|------|--------|----------------|-----------|------------|-------|",
    ]

    for r in rows:
        notes = r.notes.replace("|", "\\|") if r.notes else ""
        lines.append(
            f"| `{r.repo}` | {r.tier} | {r.status} | {fmt_github(r.github_pre2021)} | "
            f"{r.harvested} | {fmt_coverage(r.coverage_pct)} | {notes} |"
        )

    lines.extend(
        [
            "",
            "## Exclusions (not harvested as primary)",
            "",
        ]
    )
    # exclusions rendered from caller via optional second pass — keep stub if empty
    return "\n".join(lines) + "\n"


def append_exclusions(md: str, data: dict[str, Any]) -> str:
    excl = data.get("exclusions") or []
    if not excl:
        return md.rstrip() + "\n\n_(none listed)_\n"
    lines = [
        md.rstrip(),
        "",
        "| repo_or_class | reason |",
        "|---------------|--------|",
    ]
    for e in excl:
        name = str(e.get("repo_or_class") or "").replace("|", "\\|")
        reason = str(e.get("reason") or "").replace("|", "\\|")
        lines.append(f"| {name} | {reason} |")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--db", type=Path, default=DEFAULT_DB, help="SQLite path (ACE_DB_PATH)")
    p.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS, help="corpus_repos.json")
    p.add_argument("--out", type=Path, default=DEFAULT_OUT, help="CORPUS_STATUS.md path")
    p.add_argument("--harvest-log", type=Path, default=DEFAULT_LOG)
    p.add_argument(
        "--fetch-github",
        action="store_true",
        help="Fetch missing pre_2021_merged_prs via Search API and cache into JSON",
    )
    p.add_argument(
        "--refetch-github",
        action="store_true",
        help="Re-fetch Search total_count even when JSON already has a value",
    )
    p.add_argument("--sleep", type=float, default=SEARCH_SLEEP_SECONDS)
    p.add_argument("--token-file", type=Path, default=DEFAULT_TOKEN_FILE)
    p.add_argument("--dry-run", action="store_true", help="Print markdown; do not write files")
    args = p.parse_args(argv)

    try:
        db_path = resolve_allowed_path(args.db, purpose="--db")
        corpus_path = resolve_allowed_path(args.corpus, purpose="--corpus")
        out_path = resolve_allowed_path(args.out, purpose="--out")
        # Harvest logs may live under $HOME/ace-bench — allow missing file.
        try:
            log_path = resolve_allowed_path(args.harvest_log, purpose="--harvest-log")
        except PathEscapeError:
            log_path = Path(args.harvest_log).expanduser()
    except PathEscapeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.sleep < SEARCH_SLEEP_SECONDS:
        print(
            f"warning: --sleep {args.sleep} < Search floor {SEARCH_SLEEP_SECONDS}s; "
            f"using {SEARCH_SLEEP_SECONDS}",
            file=sys.stderr,
        )
        args.sleep = SEARCH_SLEEP_SECONDS

    token = resolve_token(None, args.token_file)
    data = json.loads(corpus_path.read_text(encoding="utf-8"))
    harvested = load_harvested_counts(db_path)
    finished_ok, _failed, harvesting = parse_harvest_log(log_path)

    fetched = 0
    corpus_changed = False
    if args.fetch_github or args.refetch_github:
        if not token:
            print(
                "warning: no GITHUB_TOKEN / GH_TOKEN / token file — "
                "cannot fetch Search counts",
                file=sys.stderr,
            )
        else:
            targets = iter_corpus_repos(data)
            for i, (repo, _tier, entry) in enumerate(targets, start=1):
                existing = entry.get("pre_2021_merged_prs")
                if (
                    not args.refetch_github
                    and isinstance(existing, int)
                    and entry.get("prs_verified")
                ):
                    continue
                print(f"[{i}/{len(targets)}] Search total_count {repo}…", file=sys.stderr)
                try:
                    count = github_search_total(repo, token)
                except Exception as exc:
                    msg = redact_secrets(str(exc))
                    short = msg.split(":", 1)[0][:80]
                    print(f"  FAILED {repo}: {msg}", file=sys.stderr)
                    # Leave count as TBD; stash a short note for STATUS.md.
                    for key in ("status", "tier_a", "tier_b", "tier_c"):
                        for entry in data.get(key, []):
                            if entry.get("repo") == repo:
                                note = str(entry.get("notes") or "").strip()
                                tag = f"Search unavailable ({short})"
                                if tag not in note:
                                    entry["notes"] = f"{note}; {tag}".strip("; ").strip()
                                    corpus_changed = True
                                break
                    time.sleep(args.sleep)
                    continue
                print(f"  → {count}", file=sys.stderr)
                if cache_count_into_corpus(data, repo, count):
                    corpus_changed = True
                fetched += 1
                time.sleep(args.sleep)

    rows = build_rows(data, harvested, finished_ok, harvesting)
    generated_at = _utc_now()
    md = render_markdown(
        rows,
        generated_at=generated_at,
        db_path=db_path,
        corpus_path=corpus_path,
        log_path=log_path,
        fetched=fetched,
        harvest_active=harvesting,
    )
    md = append_exclusions(md, data)

    if args.dry_run:
        sys.stdout.write(md)
    else:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")
        print(f"wrote {out_path}", file=sys.stderr)
        if corpus_changed:
            corpus_path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            print(f"updated cache in {corpus_path}", file=sys.stderr)

    total = sum(r.harvested for r in rows)
    with_data = sum(1 for r in rows if r.harvested > 0)
    queued = sum(1 for r in rows if r.status == "queued")
    print(
        f"summary: harvested={total} repos_with_data={with_data} "
        f"queued={queued} harvesting={harvesting or '-'} fetched={fetched}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
