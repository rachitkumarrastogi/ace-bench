"""Agent backend registry."""

from __future__ import annotations

from ace_bench.agents.anthropic_agent import AnthropicAgent
from ace_bench.agents.base import AgentError, BaseAgent
from ace_bench.agents.file_agent import FileAgent
from ace_bench.agents.openai_agent import OpenAIAgent
from ace_bench.agents.stub import StubAgent, build_bloated_stub_patch

AGENT_NAMES = ("file", "stub", "openai", "anthropic")


def build_agent(
    name: str,
    *,
    model_name: str,
    agent_patch: str | None = None,
    stub_bloated: bool = False,
) -> BaseAgent:
    key = (name or "").strip().lower()
    if key == "file":
        if not agent_patch:
            raise AgentError("--agent file requires --agent-patch PATH")
        return FileAgent(agent_patch)
    if key == "stub":
        return StubAgent(bloated=stub_bloated)
    if key == "openai":
        return OpenAIAgent(model_name)
    if key == "anthropic":
        return AnthropicAgent(model_name)
    raise AgentError(
        f"unknown agent {name!r}; expected one of: {', '.join(AGENT_NAMES)}"
    )


__all__ = [
    "AGENT_NAMES",
    "AgentError",
    "AnthropicAgent",
    "BaseAgent",
    "FileAgent",
    "OpenAIAgent",
    "StubAgent",
    "build_agent",
    "build_bloated_stub_patch",
]
