"""Eval v0 helpers: instance selection proxies + score report vs human baseline.

AST proxy (no tree-sitter yet)
------------------------------
``compute_ace_score`` expects ``human_ast_nodes`` / ``agent_ast_nodes``. Until a
real AST pass lands, we use:

    ast_nodes_proxy = max(added_lines, 1)

i.e. the count of ``+`` lines in the unified diff (same as ``PatchMetrics.added_lines``).
This is a **size** proxy, not syntactic complexity. Documented so agent plugs stay
honest: when tree-sitter lands, swap this helper without changing the ACE formula.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from ace_bench.ast_metrics import (
    AST_PROXY_ADDED_LINES,
    ast_nodes_from_patch,
    ast_nodes_report_note,
)
from ace_bench.craft import CraftReport, compute_craft
from ace_bench.metrics import PatchMetrics, metrics_from_patch
from ace_bench.scoring import AceScoreInputs, compute_ace_score

# Django human baseline (docs/CORPUS.md)
DJANGO_P50_FILES = 2
DJANGO_SURGICAL_MAX_FILES = 2  # ≤ p50 → surgical
DJANGO_SPRAWL_MIN_FILES = 9  # > human p90 (8) → sprawl flag

EVAL_MODE_IMMEDIATE = "immediate"
EVAL_MODE_THOROUGH = "thorough"
EVAL_MODES = frozenset({EVAL_MODE_IMMEDIATE, EVAL_MODE_THOROUGH})


def normalize_eval_mode(value: str | None) -> str:
    """Return ``immediate`` (default) or ``thorough``; raise on unknown."""
    mode = (value or EVAL_MODE_IMMEDIATE).strip().lower()
    if mode not in EVAL_MODES:
        raise ValueError(
            f"eval mode must be one of {sorted(EVAL_MODES)} (got {value!r})"
        )
    return mode

_DIFF_GIT_RE = re.compile(r"^diff --git a/(.+?) b/(.+)$", re.MULTILINE)
_PLUS_PLUS_RE = re.compile(r"^\+\+\+ [ab]/(.+)$", re.MULTILINE)
# Canonical: owner/repo#123 — owner/repo@123 accepted as legacy alias.
_INSTANCE_ID_RE = re.compile(
    r"^([A-Za-z0-9._-]+/[A-Za-z0-9._-]+)[#@](\d+)$"
)
_REPO_SLUG_RE = re.compile(r"^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$")
_BODY_SNIPPET_CHARS = 400


class InstanceIdError(ValueError):
    """Invalid eval instance id or missing human baseline row."""


def parse_instance_id(value: str) -> tuple[str, int]:
    """Parse ``owner/repo#123`` (or legacy ``owner/repo@123``). Fail closed."""
    text = (value or "").strip()
    m = _INSTANCE_ID_RE.match(text)
    if not m:
        raise InstanceIdError(
            "instance must look like owner/repo#123 "
            f"(got {value!r})"
        )
    return m.group(1), int(m.group(2))


def validate_repo_slug(repo: str) -> str:
    repo = (repo or "").strip()
    if not _REPO_SLUG_RE.match(repo):
        raise InstanceIdError(
            f"invalid repo slug {repo!r}; expected owner/name"
        )
    return repo


def files_from_patch(patch_text: str | None) -> list[str]:
    """Extract unique destination paths from a unified diff.

    Supports ``diff --git`` and ``+++ b/path`` headers. GitHub ``files[].patch``
    blobs are often *headerless* hunks only — callers must supply ``files_json``
    (or ``--agent-files``) in that case.
    """
    if not patch_text:
        return []
    seen: list[str] = []

    def _add(path: str) -> None:
        path = path.strip()
        if path in ("/dev/null", ""):
            return
        if path not in seen:
            seen.append(path)

    for _a, b in _DIFF_GIT_RE.findall(patch_text):
        _add(b)
    if not seen:
        for path in _PLUS_PLUS_RE.findall(patch_text):
            _add(path)
    return seen


def ast_nodes_proxy(metrics: PatchMetrics) -> int:
    """Map patch size → positive AST-node stand-in for ACE v0.

    Delegates to ``ace_bench.ast_metrics`` (added-lines proxy until tree-sitter).
    """
    nodes, _name = ast_nodes_from_patch(None, metrics=metrics)
    return nodes


def touches_tests(files: list[str]) -> bool:
    """Heuristic: path looks like a test module or lives under a tests/ tree."""
    for f in files:
        lower = f.lower().replace("\\", "/")
        name = Path(lower).name
        if "/tests/" in f"/{lower}" or "/test/" in f"/{lower}":
            return True
        if name.startswith("test_") or name.endswith("_test.py") or name == "tests.py":
            return True
    return False


def body_snippet(body: str | None, limit: int = _BODY_SNIPPET_CHARS) -> str:
    text = (body or "").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def file_boundary_drift(human_files: list[str], agent_files: list[str]) -> dict[str, Any]:
    h = set(human_files)
    a = set(agent_files)
    only_agent = sorted(a - h)
    only_human = sorted(h - a)
    return {
        "human_file_count": len(h),
        "agent_file_count": len(a),
        "symmetric_diff_size": len(h.symmetric_difference(a)),
        "only_in_agent": only_agent,
        "only_in_human": only_human,
        "intersection_size": len(h & a),
    }


def surgical_sprawl_flags(
    file_count: int,
    *,
    surgical_max: int = DJANGO_SURGICAL_MAX_FILES,
    sprawl_min: int = DJANGO_SPRAWL_MIN_FILES,
) -> dict[str, bool]:
    return {
        "surgical": file_count <= surgical_max,
        "sprawl": file_count >= sprawl_min,
    }


@dataclass(frozen=True, slots=True)
class ScoreReport:
    instance_id: str
    repo: str
    pr_number: int
    passed_tests: bool
    ace_score: float
    ast_proxy: str
    human_ast_nodes: int
    agent_ast_nodes: int
    human_file_count: int
    agent_file_count: int
    human_added_lines: int
    agent_added_lines: int
    churn_ratio: float | None
    boundary: dict[str, Any]
    agent_flags: dict[str, bool]
    human_flags: dict[str, bool]
    notes: list[str]
    eval_mode: str = EVAL_MODE_IMMEDIATE
    craft_score: float | None = None
    craft: dict[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def score_agent_vs_human(
    *,
    repo: str,
    pr_number: int,
    human_files: list[str],
    human_patch: str | None,
    agent_patch: str,
    passed_tests: bool,
    human_metrics: dict[str, Any] | None = None,
    agent_files: list[str] | None = None,
    mode: str = EVAL_MODE_IMMEDIATE,
) -> ScoreReport:
    """Score an agent unified diff against a human pattern row.

    ``mode=immediate`` (default): ACE + file_drift + churn only.
    ``mode=thorough``: same, plus craft signals vs this PR's human patch.
    """
    eval_mode = normalize_eval_mode(mode)
    notes: list[str] = [
        ast_nodes_report_note(),
        f"Django baseline p50 files={DJANGO_P50_FILES}; "
        f"surgical≤{DJANGO_SURGICAL_MAX_FILES}; sprawl≥{DJANGO_SPRAWL_MIN_FILES}",
        f"eval_mode={eval_mode}",
    ]

    parsed_agent_files = files_from_patch(agent_patch)
    if parsed_agent_files:
        resolved_agent_files = parsed_agent_files
    elif agent_files:
        resolved_agent_files = list(agent_files)
        notes.append(
            "agent patch has no file headers (GitHub-style hunks); using provided agent_files"
        )
    else:
        resolved_agent_files = []
        notes.append(
            "warning: no files parsed from agent patch and no agent_files provided — "
            "pass --agent-files or use --self-smoke"
        )

    if human_patch:
        human_pm = metrics_from_patch(human_patch, human_files)
    elif human_metrics:
        h_added = int(human_metrics.get("added_lines") or 0)
        h_removed = int(human_metrics.get("removed_lines") or 0)
        human_pm = PatchMetrics(
            added_lines=h_added,
            removed_lines=h_removed,
            net_lines=h_added - h_removed,
            decision_points_added=int(human_metrics.get("decision_points_added") or 0),
            loops_added=int(human_metrics.get("loops_added") or 0),
            functions_added=int(human_metrics.get("functions_added") or 0),
            file_count=len(human_files) or int(human_metrics.get("file_count") or 0),
            directories_touched=int(human_metrics.get("directories_touched") or 0),
            extensions=dict(human_metrics.get("extensions") or {}),
        )
    else:
        human_pm = metrics_from_patch(None, human_files)

    agent_pm = metrics_from_patch(agent_patch, resolved_agent_files)

    h_ast, h_proxy = ast_nodes_from_patch(human_patch, human_files, metrics=human_pm)
    a_ast, a_proxy = ast_nodes_from_patch(
        agent_patch, resolved_agent_files, metrics=agent_pm
    )
    proxy_label = h_proxy if h_proxy == a_proxy else f"{h_proxy}|{a_proxy}"
    h_files_n = max(len(human_files), human_pm.file_count, 1)
    a_files_n = max(len(resolved_agent_files), agent_pm.file_count, 1)
    if not resolved_agent_files:
        # Keep ACE file ratio defined, but boundary will show full mismatch.
        a_files_n = max(agent_pm.file_count, 1)
        notes.append("warning: agent_file_count fell back to metrics/1 for ACE file ratio")

    if passed_tests:
        ace = compute_ace_score(
            AceScoreInputs(
                human_ast_nodes=h_ast,
                agent_ast_nodes=a_ast,
                human_file_count=h_files_n,
                agent_file_count=a_files_n,
                passed_tests=True,
            )
        )
    else:
        ace = 0.0

    human_churn = human_pm.added_lines + human_pm.removed_lines
    agent_churn = agent_pm.added_lines + agent_pm.removed_lines
    churn_ratio: float | None
    if human_churn > 0:
        churn_ratio = agent_churn / human_churn
    else:
        churn_ratio = None
        notes.append("warning: human churn is 0; churn_ratio undefined")

    boundary = file_boundary_drift(human_files, resolved_agent_files)

    craft_score: float | None = None
    craft_payload: dict[str, Any] | None = None
    if eval_mode == EVAL_MODE_THOROUGH:
        craft_report: CraftReport = compute_craft(
            human_files=list(human_files),
            agent_files=list(resolved_agent_files),
            human_patch=human_patch,
            agent_patch=agent_patch,
        )
        craft_score = craft_report.craft_score
        craft_payload = craft_report.as_dict()
        notes.append(
            "craft_score = mean("
            + ", ".join(craft_report.components_used)
            + f") = {craft_score:.4f}"
        )

    return ScoreReport(
        instance_id=f"{repo}#{pr_number}",
        repo=repo,
        pr_number=pr_number,
        passed_tests=passed_tests,
        ace_score=ace,
        ast_proxy=proxy_label or AST_PROXY_ADDED_LINES,
        human_ast_nodes=h_ast,
        agent_ast_nodes=a_ast,
        human_file_count=h_files_n,
        agent_file_count=a_files_n,
        human_added_lines=human_pm.added_lines,
        agent_added_lines=agent_pm.added_lines,
        churn_ratio=churn_ratio,
        boundary=boundary,
        agent_flags=surgical_sprawl_flags(a_files_n),
        human_flags=surgical_sprawl_flags(h_files_n),
        notes=notes,
        eval_mode=eval_mode,
        craft_score=craft_score,
        craft=craft_payload,
    )


def instance_record_from_row(row: dict[str, Any]) -> dict[str, Any]:
    """Metadata-only eval instance (no patch_text) for git-friendly JSONL."""
    files = row.get("files") or []
    if isinstance(files, str):
        files = json.loads(files)
    metrics = row.get("metrics") or {}
    if isinstance(metrics, str):
        metrics = json.loads(metrics)
    return {
        "instance_id": f"{row['repo']}#{row['pr_number']}",
        "repo": row["repo"],
        "pr_number": row["pr_number"],
        "merged_at": row.get("merged_at"),
        "base_sha": row.get("base_sha"),
        "merge_commit_sha": row.get("merge_commit_sha"),
        "title": row.get("title") or "",
        "body_snippet": body_snippet(row.get("body")),
        "html_url": row.get("html_url"),
        "files": files,
        "file_count": row.get("file_count"),
        "additions": row.get("additions"),
        "deletions": row.get("deletions"),
        "directories_touched": row.get("directories_touched"),
        "metrics": metrics,
        "touches_tests": touches_tests(list(files)),
        "human_flags": surgical_sprawl_flags(int(row.get("file_count") or len(files))),
        "db_id": row.get("id"),
        "patch_in_db": True,
    }
