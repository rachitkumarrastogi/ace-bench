"""Bring-your-own agent patch from a local file."""

from __future__ import annotations

from pathlib import Path

from ace_bench.agents.base import AgentContext, AgentError, AgentResult, BaseAgent
from ace_bench.paths import MAX_AGENT_PATCH_BYTES, PathEscapeError, read_text_capped, resolve_allowed_path


class FileAgent(BaseAgent):
    """Load a precomputed unified diff from disk (offline)."""

    name = "file"

    def __init__(self, patch_path: str | Path) -> None:
        self.patch_path = Path(patch_path)

    def run(self, ctx: AgentContext) -> AgentResult:
        del ctx  # unused; path is operator-supplied
        try:
            path = resolve_allowed_path(
                self.patch_path, purpose="agent-patch", must_exist=False
            )
        except PathEscapeError as exc:
            raise AgentError(str(exc)) from exc
        if not path.is_file():
            raise AgentError(f"agent patch not found: {path}")
        try:
            text = read_text_capped(path, max_bytes=MAX_AGENT_PATCH_BYTES)
        except ValueError as exc:
            raise AgentError(str(exc)) from exc
        return AgentResult(patch_text=text, notes=f"loaded from {path}")
