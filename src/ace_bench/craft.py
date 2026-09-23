"""Craft v0 — offline patch-shape similarity vs the same-PR human baseline.

Used only in ``thorough`` eval mode. Compares agent unified diff to that
instance's human patch (not other PRs). No paid APIs; no full-repo checkout.

Formula
-------
``craft_score`` = mean of available components in ``[0, 1]``:

* ``path_jaccard`` — Jaccard of file path sets
* ``line_overlap`` — fraction of human changed lines (normalized ``+``/``-``
  bodies) that appear in the agent changed-line multiset
* ``symbol_overlap`` — Jaccard of identifier tokens extracted from ``+`` lines
* ``structural_sim`` (optional) — Python AST node-type multiset Jaccard on
  concatenated added snippets; omitted when parse fails / non-Python

Human-replay (identical patches) → craft ≈ 1.0. Unrelated stubs → low.
"""

from __future__ import annotations

import ast
import re
from dataclasses import asdict, dataclass
from typing import Any

# Unified-diff body lines (exclude +++ / --- headers).
_ADDED_BODY_RE = re.compile(r"^\+(?!\+\+)(.*)$", re.MULTILINE)
_REMOVED_BODY_RE = re.compile(r"^-(?!--)(.*)$", re.MULTILINE)
# Identifiers: Python-ish / C-ish tokens (skip pure digits).
_IDENT_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")
_NOISE_IDENTS = frozenset(
    {
        "a",
        "b",
        "c",
        "i",
        "j",
        "k",
        "n",
        "x",
        "y",
        "z",
        "if",
        "else",
        "elif",
        "for",
        "while",
        "def",
        "class",
        "return",
        "import",
        "from",
        "as",
        "pass",
        "None",
        "True",
        "False",
        "self",
        "cls",
        "and",
        "or",
        "not",
        "in",
        "is",
        "with",
        "try",
        "except",
        "finally",
        "raise",
        "yield",
        "async",
        "await",
        "lambda",
        "assert",
        "break",
        "continue",
        "global",
        "nonlocal",
        "del",
        "print",
    }
)


def jaccard(a: set[str], b: set[str]) -> float:
    """Set Jaccard; empty∩empty → 1.0 (identical void)."""
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def normalize_line(text: str) -> str:
    """Strip trailing newline + collapse internal whitespace for overlap."""
    return " ".join(text.strip().split())


def changed_line_bodies(patch_text: str | None, *, side: str = "both") -> list[str]:
    """Return normalized bodies of ``+`` / ``-`` hunk lines (no headers)."""
    text = patch_text or ""
    out: list[str] = []
    if side in ("added", "both"):
        for m in _ADDED_BODY_RE.finditer(text):
            out.append(normalize_line(m.group(1)))
    if side in ("removed", "both"):
        for m in _REMOVED_BODY_RE.finditer(text):
            out.append(normalize_line(m.group(1)))
    return [ln for ln in out if ln]


def path_jaccard(human_files: list[str], agent_files: list[str]) -> float:
    return jaccard(set(human_files), set(agent_files))


def line_overlap(human_patch: str | None, agent_patch: str | None) -> float:
    """Fraction of human changed lines that appear in the agent patch.

    Uses a multiset-aware count: each distinct normalized human line can match
    up to ``min(human_count, agent_count)`` times.
    """
    human_lines = changed_line_bodies(human_patch, side="both")
    agent_lines = changed_line_bodies(agent_patch, side="both")
    if not human_lines and not agent_lines:
        return 1.0
    if not human_lines or not agent_lines:
        return 0.0

    agent_counts: dict[str, int] = {}
    for ln in agent_lines:
        agent_counts[ln] = agent_counts.get(ln, 0) + 1

    matched = 0
    for ln in human_lines:
        left = agent_counts.get(ln, 0)
        if left > 0:
            matched += 1
            agent_counts[ln] = left - 1
    return matched / len(human_lines)


def extract_identifiers(patch_text: str | None, *, added_only: bool = True) -> set[str]:
    """Regex identifiers from ``+`` (and optionally ``-``) hunk bodies."""
    side = "added" if added_only else "both"
    lines = changed_line_bodies(patch_text, side=side)
    idents: set[str] = set()
    for ln in lines:
        for tok in _IDENT_RE.findall(ln):
            if tok in _NOISE_IDENTS:
                continue
            if tok.isdigit():
                continue
            idents.add(tok)
    return idents


def symbol_overlap(human_patch: str | None, agent_patch: str | None) -> float:
    return jaccard(
        extract_identifiers(human_patch, added_only=True),
        extract_identifiers(agent_patch, added_only=True),
    )


def _added_snippet_text(patch_text: str | None) -> str:
    bodies = changed_line_bodies(patch_text, side="added")
    return "\n".join(bodies)


def _ast_node_type_multiset(source: str) -> dict[str, int] | None:
    """Parse concatenated added lines as a Python module; count node types."""
    if not source.strip():
        return {}
    # Indent so bare statements / expr fragments can parse as a module body.
    indented = "\n".join(
        ("    " + ln) if ln.strip() else ln for ln in source.splitlines()
    )
    wrapped = f"def __ace_craft_snippet__():\n{indented}\n"
    try:
        tree = ast.parse(wrapped)
    except SyntaxError:
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return None
    counts: dict[str, int] = {}
    for node in ast.walk(tree):
        name = type(node).__name__
        counts[name] = counts.get(name, 0) + 1
    return counts


def _multiset_jaccard(a: dict[str, int], b: dict[str, int]) -> float:
    if not a and not b:
        return 1.0
    keys = set(a) | set(b)
    if not keys:
        return 1.0
    inter = sum(min(a.get(k, 0), b.get(k, 0)) for k in keys)
    union = sum(max(a.get(k, 0), b.get(k, 0)) for k in keys)
    if union <= 0:
        return 1.0
    return inter / union


def structural_similarity(
    human_patch: str | None, agent_patch: str | None
) -> float | None:
    """Optional Python AST structural Jaccard; ``None`` when unavailable."""
    h = _ast_node_type_multiset(_added_snippet_text(human_patch))
    a = _ast_node_type_multiset(_added_snippet_text(agent_patch))
    if h is None or a is None:
        return None
    return _multiset_jaccard(h, a)


@dataclass(frozen=True, slots=True)
class CraftReport:
    """Craft v0 breakdown for one human/agent patch pair."""

    craft_score: float
    path_jaccard: float
    line_overlap: float
    symbol_overlap: float
    structural_sim: float | None
    components_used: list[str]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def compute_craft(
    *,
    human_files: list[str],
    agent_files: list[str],
    human_patch: str | None,
    agent_patch: str | None,
) -> CraftReport:
    """Aggregate craft components into ``craft_score`` ∈ [0, 1]."""
    path = path_jaccard(human_files, agent_files)
    lines = line_overlap(human_patch, agent_patch)
    symbols = symbol_overlap(human_patch, agent_patch)
    structural = structural_similarity(human_patch, agent_patch)

    parts: list[tuple[str, float]] = [
        ("path_jaccard", path),
        ("line_overlap", lines),
        ("symbol_overlap", symbols),
    ]
    if structural is not None:
        parts.append(("structural_sim", structural))

    score = sum(v for _, v in parts) / len(parts)
    # Clamp numerical noise into [0, 1].
    score = max(0.0, min(1.0, score))
    return CraftReport(
        craft_score=score,
        path_jaccard=path,
        line_overlap=lines,
        symbol_overlap=symbols,
        structural_sim=structural,
        components_used=[name for name, _ in parts],
    )
