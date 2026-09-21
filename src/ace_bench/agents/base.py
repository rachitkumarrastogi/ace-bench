"""Pluggable agent backends that emit a unified diff for ACE scoring."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class AgentContext:
    """Inputs available to an agent for one eval instance."""

    instance_id: str
    repo: str
    pr_number: int
    title: str
    body: str
    model_name: str
    worktree: Path | None
    human_files: list[str]
    base_sha: str | None


@dataclass(frozen=True, slots=True)
class AgentResult:
    """Agent output: unified diff text (+ optional notes)."""

    patch_text: str
    notes: str = ""
    meta: dict[str, Any] | None = None


class AgentError(RuntimeError):
    """Agent could not produce a patch (missing key, bad input, API error)."""


class BaseAgent(ABC):
    """Agent that produces a unified diff for scoring."""

    name: str = "base"

    @abstractmethod
    def run(self, ctx: AgentContext) -> AgentResult:
        """Return a unified diff (may be empty for stub)."""


def issue_prompt(ctx: AgentContext) -> str:
    """Build a short issue-only prompt (no full repo contents)."""
    hints = ""
    if ctx.human_files:
        # Optional narrow hints — not the full human patch.
        listed = "\n".join(f"- {f}" for f in ctx.human_files[:20])
        hints = (
            "\n\nOptional file-path hints (may be incomplete; do not assume "
            "these are required):\n"
            f"{listed}\n"
        )
    return (
        "You are fixing a GitHub issue. Produce a unified diff (git apply style) "
        "that solves the issue. Output ONLY the diff — no prose.\n\n"
        f"Repository: {ctx.repo}\n"
        f"Instance: {ctx.instance_id}\n"
        f"Title: {ctx.title}\n\n"
        f"Body:\n{ctx.body or '(empty)'}\n"
        f"{hints}"
    )
