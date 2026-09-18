"""Lightweight structural metrics from unified diffs (first-pass, no full AST).

These are cheap proxies so DGX harvest can run continuously. tree-sitter AST
metrics can replace / augment them in a later pass without changing the DB shape
(metrics stay in metrics_json).
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path

_IF_RE = re.compile(r"^\+\s*(?:if|elif|else\s+if|case)\b", re.MULTILINE)
_LOOP_RE = re.compile(r"^\+\s*(?:for|while|do)\b", re.MULTILINE)
_CATCH_RE = re.compile(r"^\+\s*(?:catch|except|rescue)\b", re.MULTILINE)
_FUNC_RE = re.compile(
    r"^\+\s*(?:def|function|fn|func|public|private|protected|async\s+def)\b",
    re.MULTILINE,
)
_ADDED_LINE_RE = re.compile(r"^\+(?!\+\+)", re.MULTILINE)
_REMOVED_LINE_RE = re.compile(r"^-(?!--)", re.MULTILINE)


@dataclass(frozen=True, slots=True)
class PatchMetrics:
    """First-pass metrics derived from a unified diff."""

    added_lines: int
    removed_lines: int
    net_lines: int
    decision_points_added: int  # crude cyclomatic proxy on added lines
    loops_added: int
    functions_added: int
    file_count: int
    directories_touched: int
    extensions: dict[str, int]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def directories_from_files(files: list[str]) -> int:
    dirs = {str(Path(f).parent) for f in files if f}
    return len(dirs)


def extension_hist(files: list[str]) -> dict[str, int]:
    hist: dict[str, int] = {}
    for f in files:
        ext = Path(f).suffix.lower() or "<none>"
        hist[ext] = hist.get(ext, 0) + 1
    return hist


def metrics_from_patch(patch_text: str | None, files: list[str]) -> PatchMetrics:
    text = patch_text or ""
    added = len(_ADDED_LINE_RE.findall(text))
    removed = len(_REMOVED_LINE_RE.findall(text))
    decisions = len(_IF_RE.findall(text)) + len(_CATCH_RE.findall(text))
    loops = len(_LOOP_RE.findall(text))
    functions = len(_FUNC_RE.findall(text))
    return PatchMetrics(
        added_lines=added,
        removed_lines=removed,
        net_lines=added - removed,
        decision_points_added=decisions,
        loops_added=loops,
        functions_added=functions,
        file_count=len(files),
        directories_touched=directories_from_files(files),
        extensions=extension_hist(files),
    )
