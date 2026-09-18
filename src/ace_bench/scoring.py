"""ACE Index scoring.

ACE Score = (AST_nodes(P_H) / AST_nodes(P_A)) * (|F_H| / |F_A|) * pass_fail_multiplier

Score = 0 when the agent patch fails the unit tests.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AceScoreInputs:
    """Inputs for a single evaluation instance."""

    human_ast_nodes: int
    agent_ast_nodes: int
    human_file_count: int
    agent_file_count: int
    passed_tests: bool


def compute_ace_score(inputs: AceScoreInputs) -> float:
    """Return the ACE Index for one human/agent patch pair.

    Raises:
        ValueError: If any count is non-positive when tests passed.
    """
    if not inputs.passed_tests:
        return 0.0

    if inputs.human_ast_nodes <= 0 or inputs.agent_ast_nodes <= 0:
        raise ValueError("AST node counts must be positive when tests pass")
    if inputs.human_file_count <= 0 or inputs.agent_file_count <= 0:
        raise ValueError("File counts must be positive when tests pass")

    ast_ratio = inputs.human_ast_nodes / inputs.agent_ast_nodes
    file_ratio = inputs.human_file_count / inputs.agent_file_count
    return ast_ratio * file_ratio
