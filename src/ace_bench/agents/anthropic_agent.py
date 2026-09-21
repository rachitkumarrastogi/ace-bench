"""Optional Anthropic agent — issue text only (no full repo in v0)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from ace_bench.agents.base import (
    AgentContext,
    AgentError,
    AgentResult,
    BaseAgent,
    issue_prompt,
)


class AnthropicAgent(BaseAgent):
    """Call Anthropic Messages API if ``ANTHROPIC_API_KEY`` is set."""

    name = "anthropic"

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name.strip()
        if not self.model_name:
            raise AgentError(
                "anthropic agent requires --model (e.g. claude-sonnet-4)"
            )

    def run(self, ctx: AgentContext) -> AgentResult:
        key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if not key:
            raise AgentError(
                "ANTHROPIC_API_KEY not set; use --agent file|stub offline, "
                "or export ANTHROPIC_API_KEY for --agent anthropic"
            )
        prompt = issue_prompt(ctx)
        body = {
            "model": self.model_name,
            "max_tokens": 8192,
            "messages": [{"role": "user", "content": prompt}],
            "system": (
                "You output only a unified diff that applies with git apply. "
                "No markdown fences, no explanation."
            ),
        }
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise AgentError(f"Anthropic HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise AgentError(f"Anthropic request failed: {exc.reason}") from exc

        try:
            blocks = payload["content"]
            text = "".join(
                b.get("text", "") for b in blocks if b.get("type") == "text"
            )
        except (KeyError, TypeError) as exc:
            raise AgentError("unexpected Anthropic response shape") from exc
        patch = _strip_fences(text or "")
        return AgentResult(
            patch_text=patch,
            notes=f"anthropic model={self.model_name}",
            meta={"provider": "anthropic"},
        )


def _strip_fences(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        lines = t.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        t = "\n".join(lines).strip()
    return t
