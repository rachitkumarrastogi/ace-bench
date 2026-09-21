"""Stub agent for plumbing tests (no model call)."""

from __future__ import annotations

from ace_bench.agents.base import AgentContext, AgentResult, BaseAgent

# Minimal no-op unified diff — tiny vs real human → ACE ≫ 1 (over-surgical).
STUB_PATCH = """\
diff --git a/.ace_stub b/.ace_stub
new file mode 100644
--- /dev/null
+++ b/.ace_stub
@@ -0,0 +1 @@
+# ace-bench stub agent
"""


def build_bloated_stub_patch(*, n_files: int = 4, lines_per: int = 20) -> str:
    """Multi-file sprawl patch so ACE ≪ 1 vs a surgical human baseline."""
    parts: list[str] = []
    # Cap so smoke stays cheap and patch stays under MAX_AGENT_PATCH_BYTES.
    n_files = max(1, min(n_files, 16))
    lines_per = max(1, min(lines_per, 80))
    body_lines = "\n".join(f"+    x{i} = {i}" for i in range(1, lines_per + 1))
    for i in range(n_files):
        path = f"bloated/extra_{i}.py"
        parts.append(
            f"diff --git a/{path} b/{path}\n"
            f"new file mode 100644\n"
            f"--- /dev/null\n"
            f"+++ b/{path}\n"
            f"@@ -0,0 +1,{lines_per + 1} @@\n"
            f"+def f():\n"
            f"{body_lines}\n"
        )
    return "".join(parts)


class StubAgent(BaseAgent):
    """Writes a synthetic patch for harness smoke tests (no API)."""

    name = "stub"

    def __init__(self, *, empty: bool = False, bloated: bool = False) -> None:
        self.empty = empty
        self.bloated = bloated

    def run(self, ctx: AgentContext) -> AgentResult:
        del ctx
        if self.empty:
            return AgentResult(patch_text="", notes="stub empty patch")
        if self.bloated:
            return AgentResult(
                patch_text=build_bloated_stub_patch(),
                notes="stub bloated multi-file patch",
            )
        return AgentResult(patch_text=STUB_PATCH, notes="stub minimal no-op patch")
