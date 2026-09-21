"""Stub agent for plumbing tests (no model call)."""

from __future__ import annotations

from ace_bench.agents.base import AgentContext, AgentResult, BaseAgent

# Minimal no-op unified diff — scores poorly vs a real human patch unless
# the human patch is also empty.
STUB_PATCH = """\
diff --git a/.ace_stub b/.ace_stub
new file mode 100644
--- /dev/null
+++ b/.ace_stub
@@ -0,0 +1 @@
+# ace-bench stub agent
"""


class StubAgent(BaseAgent):
    """Writes a tiny no-op patch for harness smoke tests."""

    name = "stub"

    def __init__(self, *, empty: bool = False) -> None:
        self.empty = empty

    def run(self, ctx: AgentContext) -> AgentResult:
        del ctx
        if self.empty:
            return AgentResult(patch_text="", notes="stub empty patch")
        return AgentResult(patch_text=STUB_PATCH, notes="stub minimal no-op patch")
