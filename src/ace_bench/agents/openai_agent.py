"""Optional OpenAI agent — issue text only (no full repo in v0)."""

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


class OpenAIAgent(BaseAgent):
    """Call OpenAI Chat Completions if ``OPENAI_API_KEY`` is set."""

    name = "openai"

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name.strip()
        if not self.model_name:
            raise AgentError("openai agent requires --model (e.g. gpt-4o)")

    def run(self, ctx: AgentContext) -> AgentResult:
        key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not key:
            raise AgentError(
                "OPENAI_API_KEY not set; use --agent file|stub offline, "
                "or export OPENAI_API_KEY for --agent openai"
            )
        prompt = issue_prompt(ctx)
        body = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You output only a unified diff that applies with git apply. "
                        "No markdown fences, no explanation."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0,
        }
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise AgentError(f"OpenAI HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise AgentError(f"OpenAI request failed: {exc.reason}") from exc

        try:
            text = payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise AgentError("unexpected OpenAI response shape") from exc
        patch = _strip_fences(text or "")
        return AgentResult(
            patch_text=patch,
            notes=f"openai model={self.model_name}",
            meta={"provider": "openai"},
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
