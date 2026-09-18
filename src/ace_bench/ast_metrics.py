"""AST node counts for ACE Index (tree-sitter optional; v0 fallback).

TODO (real AST)
---------------
When ``tree-sitter`` + a language grammar (e.g. ``tree-sitter-python``) are
wired:

1. Parse each *added* region from the unified diff (or full post-image files).
2. Count AST nodes (or a documented subset: statements / expressions).
3. Return that count as ``ast_nodes`` for ``compute_ace_score``.

Until then, ``ast_nodes_from_patch`` falls back to the v0 size proxy
``max(added_lines, 1)`` — same as historical ``eval_v0.ast_nodes_proxy``.
See docs/EVAL.md.
"""

from __future__ import annotations

from typing import Any

from ace_bench.metrics import PatchMetrics, metrics_from_patch

# Documented proxy name for score reports / JSON.
AST_PROXY_ADDED_LINES = "max(added_lines, 1)"
AST_PROXY_TREE_SITTER = "tree-sitter"  # reserved when real parsing lands


def ast_nodes_proxy_from_metrics(metrics: PatchMetrics) -> int:
    """V0 stand-in: positive count from added ``+`` lines in the diff."""
    return max(int(metrics.added_lines), 1)


def try_tree_sitter_python_nodes(patch_text: str | None) -> int | None:
    """Optional tree-sitter path for Python-only diffs.

    Returns ``None`` when grammars are unavailable or parsing is not yet
    implemented — callers must fall back to the added-lines proxy.

    Dependency note: ``pyproject.toml`` lists ``tree-sitter`` but not a
    language pack; installing ``tree-sitter-python`` alone is not enough until
    this function is completed.
    """
    if not patch_text:
        return None
    try:
        import tree_sitter
    except ImportError:
        return None
    # TODO: parse added Python hunks with tree_sitter_python and count nodes.
    # Intentionally unused until grammar + hunk extraction land.
    _ = tree_sitter
    return None


def ast_nodes_from_patch(
    patch_text: str | None,
    files: list[str] | None = None,
    *,
    metrics: PatchMetrics | None = None,
) -> tuple[int, str]:
    """Return ``(ast_nodes, proxy_name)`` for ACE scoring.

    Prefer tree-sitter when implemented and successful; otherwise added-lines.
    """
    ts = try_tree_sitter_python_nodes(patch_text)
    if ts is not None and ts > 0:
        return ts, AST_PROXY_TREE_SITTER

    pm = metrics if metrics is not None else metrics_from_patch(patch_text, list(files or []))
    return ast_nodes_proxy_from_metrics(pm), AST_PROXY_ADDED_LINES


def ast_nodes_report_note() -> str:
    return (
        f"AST proxy = {AST_PROXY_ADDED_LINES} via ace_bench.ast_metrics; "
        "replace with tree-sitter when available"
    )


def describe_backend() -> dict[str, Any]:
    """Small introspection helper for docs / tests."""
    try:
        import tree_sitter  # noqa: F401

        ts_present = True
    except ImportError:
        ts_present = False
    return {
        "tree_sitter_importable": ts_present,
        "active_proxy": AST_PROXY_ADDED_LINES,
        "tree_sitter_implemented": False,
    }
