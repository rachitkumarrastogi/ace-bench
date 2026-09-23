"""PR-shaped local artifact after an agent eval (no real ``gh pr``).

Writes ``AGENT_PR.md`` summarizing title, ``model_name``, ACE score, and
file drift. This is a metaphor for "raise a PR" — operators inspect the
markdown + patch in the worktree; opening a GitHub PR is out of scope.
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence


def write_agent_pr_md(
    dest_dir: Path,
    *,
    title: str,
    model_name: str,
    instance_id: str,
    ace_score: float,
    file_drift: int,
    human_files: Sequence[str],
    agent_files: Sequence[str],
    agent_name: str | None = None,
    churn_ratio: float | None = None,
    patch_path: str | Path | None = None,
    base_sha: str | None = None,
    eval_mode: str | None = None,
    craft_score: float | None = None,
) -> Path:
    """Write ``AGENT_PR.md`` under ``dest_dir`` and return its path."""
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    path = dest_dir / "AGENT_PR.md"

    h_files = list(human_files)
    a_files = list(agent_files)
    only_agent = sorted(set(a_files) - set(h_files))
    only_human = sorted(set(h_files) - set(a_files))
    shared = sorted(set(h_files) & set(a_files))

    churn = "n/a" if churn_ratio is None else f"{churn_ratio:.4f}"
    lines = [
        f"# {title or 'Agent patch'}",
        "",
        "_PR-shaped artifact (local only — not opened on GitHub)._",
        "",
        f"- **instance:** `{instance_id}`",
        f"- **model_name:** `{model_name}`",
    ]
    if agent_name:
        lines.append(f"- **agent:** `{agent_name}`")
    if base_sha:
        lines.append(f"- **base_sha:** `{base_sha}`")
    if eval_mode:
        lines.append(f"- **eval_mode:** `{eval_mode}`")
    lines.extend(
        [
            f"- **ACE score:** {ace_score:.6f}",
            f"- **file_drift:** {file_drift}  (|F_A Δ F_H|)",
            f"- **churn_ratio:** {churn}",
        ]
    )
    if craft_score is not None:
        lines.append(f"- **craft_score:** {craft_score:.6f}")
    if patch_path:
        lines.append(f"- **patch:** `{patch_path}`")
    lines.extend(
        [
            "",
            "## File drift",
            "",
            f"- shared ({len(shared)}): "
            + (", ".join(f"`{f}`" for f in shared) or "_none_"),
            f"- only agent ({len(only_agent)}): "
            + (", ".join(f"`{f}`" for f in only_agent) or "_none_"),
            f"- only human ({len(only_human)}): "
            + (", ".join(f"`{f}`" for f in only_human) or "_none_"),
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
