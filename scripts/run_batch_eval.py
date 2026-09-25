#!/usr/bin/env python3
"""Batch offline eval: stub vs human-replay across ~100 Django instances.

Bill-safe by default: only ``--agent stub`` and ``--agent file`` (human-replay).
Paid OpenAI/Anthropic agents require ``--allow-paid`` and are capped at 5 instances.

Example ($0, thorough on all selected):

  export ACE_DB_PATH=data/frozen/ace_patterns_django_pre2021_6125.sqlite
  python3 scripts/run_batch_eval.py \\
    --limit 100 \\
    --mode thorough \\
    --skip-sandbox \\
    --write-report docs/EVAL_BATCH_100.md \\
    --eval-db ~/ace-bench-data/eval_runs.sqlite
"""

from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(_REPO_ROOT / "src"))
sys.path.insert(0, str(_SCRIPTS))

from ace_bench.db import PatternStore
from ace_bench.eval_runs import default_eval_runs_db_path
from ace_bench.eval_v0 import EVAL_MODES, touches_tests
from ace_bench.paths import PathEscapeError, resolve_allowed_path

import run_agent_eval as _single  # noqa: E402

FROZEN_NAME = "ace_patterns_django_pre2021_6125.sqlite"
DEFAULT_JSONL = Path("benchmarks/django_eval_v0.jsonl")
DEFAULT_REPORT = Path("docs/EVAL_BATCH_100.md")
PAID_INSTANCE_CAP = 5
BILL_SAFE_AGENTS = frozenset({"stub", "file"})
PAID_AGENTS = frozenset({"openai", "anthropic"})

@dataclass(frozen=True, slots=True)
class BatchInstance:
    """One eval target with optional metadata from JSONL."""

    instance_id: str
    repo: str
    pr_number: int
    html_url: str | None
    title: str | None
    source: str  # "jsonl" | "db"
    patch_in_db: bool


@dataclass(frozen=True, slots=True)
class VariantSpec:
    """One (model, agent, flags) combination to run per instance."""

    model_name: str
    agent: str
    stub_bloated: bool = False
    needs_human_patch: bool = False


DEFAULT_VARIANTS: tuple[VariantSpec, ...] = (
    VariantSpec("human-replay", "file", needs_human_patch=True),
    VariantSpec("stub-default", "stub"),
    VariantSpec("stub-bloated", "stub", stub_bloated=True),
)


def resolve_harvest_db(cli_db: str | None) -> Path:
    return _single.resolve_harvest_db(cli_db)


def load_jsonl_instances(path: Path) -> list[BatchInstance]:
    """Load metadata rows from django_eval JSONL (prefer patch_in_db)."""
    out: list[BatchInstance] = []
    if not path.is_file():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        iid = str(row["instance_id"])
        repo, pr_s = iid.split("#", 1)
        out.append(
            BatchInstance(
                instance_id=iid,
                repo=repo,
                pr_number=int(pr_s),
                html_url=row.get("html_url"),
                title=row.get("title"),
                source="jsonl",
                patch_in_db=bool(row.get("patch_in_db", True)),
            )
        )
    return out


def pad_from_db(
    store: PatternStore,
    *,
    already: set[str],
    need: int,
    repo: str = "django/django",
    min_files: int = 1,
    max_files: int = 8,
    merged_before: str = "2021-01-01",
) -> list[BatchInstance]:
    """Pad instance list from frozen/live harvest using export-style filters."""
    if need <= 0:
        return []
    candidates = store.fetch_eval_candidates(
        repo=repo,
        min_files=min_files,
        max_files=max_files,
        merged_before=merged_before,
        limit=None,
    )
    by_fc: dict[int, list] = {}
    for p in candidates:
        iid = f"{p.repo}#{p.pr_number}"
        if iid in already:
            continue
        if not p.patch_text:
            continue
        by_fc.setdefault(p.file_count, []).append(p)
    for bucket in by_fc.values():
        bucket.sort(
            key=lambda pat: (
                0 if touches_tests(pat.files) else 1,
                pat.merged_at or "",
                pat.pr_number,
            )
        )
    selected: list[BatchInstance] = []
    buckets = [by_fc.get(fc, []) for fc in range(min_files, max_files + 1)]
    idxs = [0] * len(buckets)
    while len(selected) < need:
        progressed = False
        for i, bucket in enumerate(buckets):
            if idxs[i] < len(bucket):
                p = bucket[idxs[i]]
                idxs[i] += 1
                selected.append(
                    BatchInstance(
                        instance_id=f"{p.repo}#{p.pr_number}",
                        repo=p.repo,
                        pr_number=p.pr_number,
                        html_url=p.html_url,
                        title=p.title,
                        source="db",
                        patch_in_db=True,
                    )
                )
                progressed = True
                if len(selected) >= need:
                    break
        if not progressed:
            break
    return selected


def select_instances(
    *,
    jsonl_path: Path,
    store: PatternStore,
    limit: int,
    repo: str = "django/django",
) -> list[BatchInstance]:
    """Prefer JSONL (with patch), then pad from DB to ``limit``."""
    from_jsonl = [
        inst
        for inst in load_jsonl_instances(jsonl_path)
        if inst.patch_in_db and inst.repo == repo
    ]
    # Verify patch still present in DB.
    verified: list[BatchInstance] = []
    for inst in from_jsonl:
        human = store.get_pattern(inst.repo, inst.pr_number)
        if human is None or not human.patch_text:
            continue
        verified.append(inst)
    already = {i.instance_id for i in verified}
    pad = pad_from_db(store, already=already, need=max(0, limit - len(verified)), repo=repo)
    selected = (verified + pad)[:limit]
    return selected


def _median(values: list[float]) -> float | None:
    if not values:
        return None
    return float(statistics.median(values))


def _pct(values: list[float], p: float) -> float | None:
    if not values:
        return None
    xs = sorted(values)
    if len(xs) == 1:
        return float(xs[0])
    k = (len(xs) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return float(xs[int(k)])
    return float(xs[f] * (c - k) + xs[c] * (k - f))


def _fmt(v: float | None, digits: int = 4) -> str:
    if v is None:
        return "n/a"
    return f"{v:.{digits}f}"


def extract_human_patch(
    store: PatternStore,
    inst: BatchInstance,
    patches_dir: Path,
) -> Path:
    human = store.get_pattern(inst.repo, inst.pr_number)
    if human is None or not human.patch_text:
        raise RuntimeError(f"no patch_text for {inst.instance_id}")
    patches_dir.mkdir(parents=True, exist_ok=True)
    safe = f"{inst.repo.replace('/', '__')}__{inst.pr_number}.patch"
    path = patches_dir / safe
    path.write_text(human.patch_text, encoding="utf-8")
    return path


def run_one(
    *,
    inst: BatchInstance,
    variant: VariantSpec,
    harvest_db: Path,
    eval_db: Path,
    mode: str,
    skip_sandbox: bool,
    human_patch: Path | None,
    save_patch_dir: Path,
    no_pr_artifact: bool,
) -> dict[str, Any]:
    argv: list[str] = [
        "--instance",
        inst.instance_id,
        "--model",
        variant.model_name,
        "--agent",
        variant.agent,
        "--passed-tests",
        "true",
        "--mode",
        mode,
        "--db",
        str(harvest_db),
        "--eval-db",
        str(eval_db),
        "--save-patch-dir",
        str(save_patch_dir),
        "--json",
    ]
    if skip_sandbox:
        argv.append("--skip-sandbox")
    if no_pr_artifact:
        argv.append("--no-pr-artifact")
    if variant.stub_bloated:
        argv.append("--stub-bloated")
    if variant.needs_human_patch:
        if human_patch is None:
            raise RuntimeError(f"human patch required for {variant.model_name}")
        argv.extend(["--agent-patch", str(human_patch)])

    # Capture stdout from JSON mode.
    import io
    from contextlib import redirect_stdout

    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = _single.main(argv)
    text = buf.getvalue().strip()
    if rc != 0:
        return {
            "ok": False,
            "instance_id": inst.instance_id,
            "model_name": variant.model_name,
            "rc": rc,
            "stdout": text[-500:],
        }
    try:
        summary = json.loads(text)
    except json.JSONDecodeError:
        return {
            "ok": False,
            "instance_id": inst.instance_id,
            "model_name": variant.model_name,
            "rc": rc,
            "stdout": text[-500:],
        }
    summary["ok"] = True
    summary["html_url"] = inst.html_url or (
        f"https://github.com/{inst.repo}/pull/{inst.pr_number}"
    )
    summary["title"] = inst.title
    summary["source"] = inst.source
    return summary


def aggregate(results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in results:
        if not r.get("ok"):
            continue
        by_model[str(r["model_name"])].append(r)

    out: dict[str, dict[str, Any]] = {}
    for model, rows in sorted(by_model.items()):
        aces = [float(r["ace_score"]) for r in rows if r.get("ace_score") is not None]
        drifts = [float(r["file_drift"]) for r in rows if r.get("file_drift") is not None]
        churns = [
            float(r["churn_ratio"])
            for r in rows
            if r.get("churn_ratio") is not None
        ]
        crafts = [
            float(r["craft_score"])
            for r in rows
            if r.get("craft_score") is not None
        ]
        out[model] = {
            "n": len(rows),
            "ace_median": _median(aces),
            "ace_p10": _pct(aces, 10),
            "ace_p90": _pct(aces, 90),
            "drift_median": _median(drifts),
            "drift_p90": _pct(drifts, 90),
            "churn_median": _median(churns),
            "craft_median": _median(crafts),
            "craft_p10": _pct(crafts, 10),
            "ace_mean": float(statistics.mean(aces)) if aces else None,
        }
    return out


def write_report(
    path: Path,
    *,
    instances: list[BatchInstance],
    results: list[dict[str, Any]],
    stats: dict[str, dict[str, Any]],
    mode: str,
    harvest_db: Path,
    eval_db: Path,
    patches_dir: Path,
    save_patch_dir: Path,
    paid_ran: bool,
    paid_note: str,
) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ok = [r for r in results if r.get("ok")]
    fail = [r for r in results if not r.get("ok")]

    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in ok:
        by_model[str(r["model_name"])].append(r)

    human_rows = by_model.get("human-replay", [])
    stub_rows = by_model.get("stub-default", [])
    bloat_rows = by_model.get("stub-bloated", [])

    # Where stubs tank: farthest from ACE=1 (over-surgical stub-default) and
    # lowest craft / ACE for bloated sprawl.
    def _ace_distance(r: dict[str, Any]) -> float:
        ace = float(r.get("ace_score") or 1e-9)
        return abs(math.log10(max(ace, 1e-9)))

    stub_tank = sorted(
        stub_rows,
        key=lambda r: (
            -_ace_distance(r),
            -float(r.get("file_drift") or 0),
            float(r.get("craft_score") if r.get("craft_score") is not None else 1),
        ),
    )[:15]
    bloat_tank = sorted(
        bloat_rows,
        key=lambda r: (
            float(r.get("craft_score") if r.get("craft_score") is not None else 1),
            float(r.get("ace_score") or 0),
            -float(r.get("file_drift") or 0),
        ),
    )[:15]
    human_shine = [
        r
        for r in human_rows
        if r.get("ace_score") is not None and abs(float(r["ace_score"]) - 1.0) < 1e-6
    ]

    # Pairwise: human ACE=1 vs stub ACE for same instance
    human_by_id = {r["instance_id"]: r for r in human_rows}
    contrast: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for s in stub_rows:
        h = human_by_id.get(s["instance_id"])
        if h is None:
            continue
        contrast.append((h, s))
    contrast.sort(
        key=lambda pair: abs(math.log10(max(float(pair[1].get("ace_score") or 1e-9), 1e-9)))
    )
    contrast_worst = contrast[-12:][::-1]  # largest |log10 ACE| from 1

    lines: list[str] = []
    lines.append("# Eval batch ~100 — stub agents vs human-replay")
    lines.append("")
    lines.append(f"_Generated {now} (UTC)._")
    lines.append("")
    lines.append("## Disclaimer")
    lines.append("")
    lines.append(
        "**`stub-default` and `stub-bloated` are synthetic harness agents**, not "
        "LLM products. They exist to exercise ACE / drift / churn / craft plumbing "
        "and to illustrate over-surgical vs sprawl failure modes. "
        "**`human-replay`** (`--agent file`) replays the stored human PR patch and "
        "should score ACE ≈ 1.0 (and craft ≈ 1.0 in thorough mode). "
        "This batch was run **offline** (`--skip-sandbox`) with **no paid API calls** "
        "unless noted below."
    )
    lines.append("")
    lines.append(f"- Paid LLM sample: **{'yes — ' + paid_note if paid_ran else 'no'}**")
    lines.append(f"- Eval mode: `{mode}`")
    lines.append(f"- Instances: **{len(instances)}** "
                 f"(jsonl={sum(1 for i in instances if i.source=='jsonl')}, "
                 f"db-pad={sum(1 for i in instances if i.source=='db')})")
    lines.append(f"- Successful runs: **{len(ok)}** / {len(results)} "
                 f"(failures: {len(fail)})")
    lines.append(f"- Harvest DB: `{harvest_db}`")
    lines.append(f"- Eval runs DB: `{eval_db}`")
    lines.append(f"- Human patches dir: `{patches_dir}`")
    lines.append(f"- Agent patch / AGENT_PR.md dir: `{save_patch_dir}`")
    lines.append("")
    lines.append("## Headline stats (medians)")
    lines.append("")
    lines.append("| Model | n | median ACE | p10 ACE | p90 ACE | median drift | median churn | median craft |")
    lines.append("|-------|---|------------|---------|---------|--------------|--------------|--------------|")
    for model, s in stats.items():
        lines.append(
            f"| `{model}` | {s['n']} | {_fmt(s['ace_median'])} | {_fmt(s['ace_p10'])} | "
            f"{_fmt(s['ace_p90'])} | {_fmt(s['drift_median'], 1)} | "
            f"{_fmt(s['churn_median'])} | {_fmt(s['craft_median'])} |"
        )
    lines.append("")
    lines.append("### How to read the numbers")
    lines.append("")
    lines.append(
        "- **ACE ≈ 1**: agent patch size×files matches the human patch for that PR.\n"
        "- **ACE ≫ 1** (`stub-default`): tiny stub vs real human — *over-surgical* vs baseline.\n"
        "- **ACE ≪ 1** (`stub-bloated`): multi-file sprawl vs surgical human — *bloat*.\n"
        "- **file_drift**: symmetric set difference of touched paths (|F_A Δ F_H|).\n"
        "- **craft** (thorough only): path/line/symbol overlap shape similarity (not correctness)."
    )
    lines.append("")
    lines.append("## Where humans shine")
    lines.append("")
    lines.append(
        f"Human-replay reached ACE = 1.0 on **{len(human_shine)} / {len(human_rows)}** "
        "successful instances (identical stored patch). Representative links:"
    )
    lines.append("")
    lines.append("| Instance | PR | ACE | craft | patch / AGENT_PR |")
    lines.append("|----------|----|-----|-------|------------------|")
    for r in human_shine[:20]:
        url = r.get("html_url") or ""
        pr_art = r.get("pr_artifact") or ""
        patch = r.get("patch_path") or ""
        craft = _fmt(r.get("craft_score") if isinstance(r.get("craft_score"), (int, float)) else None)
        lines.append(
            f"| `{r['instance_id']}` | [{r['instance_id'].split('#')[-1]}]({url}) | "
            f"{_fmt(float(r['ace_score']))} | {craft} | "
            f"`{Path(patch).name if patch else '—'}` / "
            f"`{Path(pr_art).name if pr_art else '—'}` |"
        )
    if len(human_shine) > 20:
        lines.append("")
        lines.append(f"_…and {len(human_shine) - 20} more with ACE=1.0._")
    lines.append("")
    lines.append("## Where stub agents “tank”")
    lines.append("")
    lines.append(
        "Synthetic stubs are **designed** to miss human shape. "
        "`stub-default` rows farthest from ACE=1 (typically **ACE ≫ 1**, high path "
        "drift, near-zero craft):"
    )
    lines.append("")
    lines.append("| Instance | PR | ACE | drift | churn | craft |")
    lines.append("|----------|----|-----|-------|-------|-------|")
    for r in stub_tank:
        url = r.get("html_url") or ""
        craft = _fmt(r.get("craft_score") if isinstance(r.get("craft_score"), (int, float)) else None)
        lines.append(
            f"| `{r['instance_id']}` | [PR]({url}) | {_fmt(float(r['ace_score']))} | "
            f"{r.get('file_drift')} | {_fmt(r.get('churn_ratio') if isinstance(r.get('churn_ratio'), (int, float)) else None)} | "
            f"{craft} |"
        )
    lines.append("")
    lines.append("### Contrast: human ACE=1 vs stub-default (largest |log₁₀ ACE|)")
    lines.append("")
    lines.append("| Instance | PR | human ACE | stub ACE | stub drift | stub craft |")
    lines.append("|----------|----|-----------|----------|------------|------------|")
    for h, s in contrast_worst:
        url = h.get("html_url") or s.get("html_url") or ""
        lines.append(
            f"| `{h['instance_id']}` | [PR]({url}) | {_fmt(float(h['ace_score']))} | "
            f"{_fmt(float(s['ace_score']))} | {s.get('file_drift')} | "
            f"{_fmt(s.get('craft_score') if isinstance(s.get('craft_score'), (int, float)) else None)} |"
        )
    lines.append("")
    lines.append("## Bloat — `stub-bloated` vs human")
    lines.append("")
    lines.append(
        "`--stub-bloated` emits multi-file sprawl. Expect **ACE ≪ 1**, high path drift, "
        "and **low craft** vs the same-PR human patch."
    )
    lines.append("")
    hs = stats.get("human-replay", {})
    bs = stats.get("stub-bloated", {})
    lines.append("| Metric | human-replay | stub-bloated |")
    lines.append("|--------|--------------|--------------|")
    lines.append(f"| median ACE | {_fmt(hs.get('ace_median'))} | {_fmt(bs.get('ace_median'))} |")
    lines.append(f"| median drift | {_fmt(hs.get('drift_median'), 1)} | {_fmt(bs.get('drift_median'), 1)} |")
    lines.append(f"| median craft | {_fmt(hs.get('craft_median'))} | {_fmt(bs.get('craft_median'))} |")
    lines.append(f"| median churn | {_fmt(hs.get('churn_median'))} | {_fmt(bs.get('churn_median'))} |")
    lines.append("")
    lines.append("Lowest craft / ACE bloated runs:")
    lines.append("")
    lines.append("| Instance | PR | ACE | drift | craft | AGENT_PR / patch |")
    lines.append("|----------|----|-----|-------|-------|------------------|")
    for r in bloat_tank:
        url = r.get("html_url") or ""
        pr_art = r.get("pr_artifact") or ""
        patch = r.get("patch_path") or ""
        craft = _fmt(r.get("craft_score") if isinstance(r.get("craft_score"), (int, float)) else None)
        lines.append(
            f"| `{r['instance_id']}` | [PR]({url}) | {_fmt(float(r['ace_score']))} | "
            f"{r.get('file_drift')} | {craft} | "
            f"`{Path(pr_art).name if pr_art else '—'}` / `{Path(patch).name if patch else '—'}` |"
        )
    lines.append("")
    lines.append("## Per-instance index (all selected)")
    lines.append("")
    lines.append(
        "GitHub PR URLs use `https://github.com/{repo}/pull/{n}`. "
        f"Local artifacts under `{save_patch_dir}` "
        "(filenames like `django__django__{n}__{model}.patch` and `AGENT_PR.md` "
        "when not suppressed)."
    )
    lines.append("")
    lines.append("| # | Instance | source | PR | title (truncated) |")
    lines.append("|---|----------|--------|----|-----------------|")
    for i, inst in enumerate(instances, 1):
        url = inst.html_url or f"https://github.com/{inst.repo}/pull/{inst.pr_number}"
        title = (inst.title or "").replace("|", "/")
        if len(title) > 60:
            title = title[:57] + "…"
        lines.append(
            f"| {i} | `{inst.instance_id}` | {inst.source} | "
            f"[#{inst.pr_number}]({url}) | {title} |"
        )
    lines.append("")
    lines.append("## Re-run")
    lines.append("")
    lines.append("```bash")
    lines.append("cd /path/to/ace-bench")
    lines.append("source .venv/bin/activate")
    lines.append("export ACE_DB_PATH=data/frozen/ace_patterns_django_pre2021_6125.sqlite")
    lines.append("python3 scripts/run_batch_eval.py \\")
    lines.append("  --limit 100 --mode thorough --skip-sandbox \\")
    lines.append("  --write-report docs/EVAL_BATCH_100.md \\")
    lines.append("  --eval-db ~/ace-bench-data/eval_runs.sqlite")
    lines.append("```")
    lines.append("")
    if fail:
        lines.append("## Failures")
        lines.append("")
        for r in fail[:30]:
            lines.append(
                f"- `{r.get('instance_id')}` / `{r.get('model_name')}` "
                f"rc={r.get('rc')}: `{str(r.get('stdout', ''))[:120]}`"
            )
        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--db", default=None, help="harvest / frozen SQLite")
    p.add_argument(
        "--eval-db",
        default=None,
        help=f"eval_runs SQLite (default: {default_eval_runs_db_path()})",
    )
    p.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL)
    p.add_argument("--limit", type=int, default=100, help="target instance count")
    p.add_argument(
        "--mode",
        choices=sorted(EVAL_MODES),
        default="thorough",
        help="immediate or thorough (default thorough for batch craft stats)",
    )
    p.add_argument("--skip-sandbox", action="store_true", default=True)
    p.add_argument("--no-skip-sandbox", action="store_false", dest="skip_sandbox")
    p.add_argument(
        "--patches-dir",
        type=Path,
        default=None,
        help="dir for extracted human patches (default: ~/ace-bench-data/eval_batch/human_patches)",
    )
    p.add_argument(
        "--save-patch-dir",
        type=Path,
        default=None,
        help="dir for agent patches + AGENT_PR.md (default: ~/ace-bench-data/eval_batch/agent_patches)",
    )
    p.add_argument("--write-report", type=Path, default=None, help="markdown report path")
    p.add_argument("--no-pr-artifact", action="store_true")
    p.add_argument(
        "--dry-select",
        action="store_true",
        help="only print selected instance ids and exit",
    )
    p.add_argument(
        "--allow-paid",
        action="store_true",
        help="permit openai/anthropic on a small sample (max 5); default off",
    )
    p.add_argument(
        "--paid-agent",
        choices=sorted(PAID_AGENTS),
        default=None,
        help="with --allow-paid: run this agent on first N instances",
    )
    p.add_argument(
        "--paid-model",
        default=None,
        help="model_name for paid sample (required with --paid-agent)",
    )
    p.add_argument(
        "--paid-limit",
        type=int,
        default=PAID_INSTANCE_CAP,
        help=f"max paid instances (hard cap {PAID_INSTANCE_CAP})",
    )
    p.add_argument("--json", action="store_true", help="print aggregate JSON to stdout")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    # Bill safety gate for accidental paid agents via env.
    if not args.allow_paid:
        for key in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY"):
            if os.environ.get(key):
                # Keys may be present; we still refuse paid agents unless flagged.
                pass

    try:
        harvest_db = resolve_harvest_db(args.db)
        eval_db = resolve_allowed_path(
            args.eval_db or default_eval_runs_db_path(),
            purpose="--eval-db",
        )
        jsonl_path = resolve_allowed_path(args.jsonl, purpose="--jsonl")
        home_batch = Path.home() / "ace-bench-data" / "eval_batch"
        patches_dir = resolve_allowed_path(
            args.patches_dir or (home_batch / "human_patches"),
            purpose="--patches-dir",
        )
        save_patch_dir = resolve_allowed_path(
            args.save_patch_dir or (home_batch / "agent_patches"),
            purpose="--save-patch-dir",
        )
        report_path = None
        if args.write_report is not None:
            report_path = resolve_allowed_path(args.write_report, purpose="--write-report")
    except (PathEscapeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not harvest_db.is_file():
        print(f"error: harvest DB not found: {harvest_db}", file=sys.stderr)
        return 2

    with PatternStore(harvest_db) as store:
        instances = select_instances(
            jsonl_path=jsonl_path,
            store=store,
            limit=args.limit,
        )
        if args.dry_select:
            print(
                json.dumps(
                    {
                        "n": len(instances),
                        "instances": [i.instance_id for i in instances],
                        "sources": {
                            "jsonl": sum(1 for i in instances if i.source == "jsonl"),
                            "db": sum(1 for i in instances if i.source == "db"),
                        },
                    },
                    indent=2,
                )
            )
            return 0

        if not instances:
            print("error: no instances selected", file=sys.stderr)
            return 2

        variants = list(DEFAULT_VARIANTS)
        paid_ran = False
        paid_note = ""
        if args.allow_paid and args.paid_agent:
            if not args.paid_model:
                print("error: --paid-model required with --paid-agent", file=sys.stderr)
                return 2
            n_paid = min(max(1, args.paid_limit), PAID_INSTANCE_CAP, len(instances))
            # Only attach paid variant metadata; runs happen below on a slice.
            paid_ran = True
            paid_note = (
                f"{args.paid_agent}/{args.paid_model} on first {n_paid} instances "
                f"(COST WARNING: real API spend)"
            )
            print(f"warning: {paid_note}", file=sys.stderr)
        elif args.paid_agent or args.paid_model:
            print(
                "error: paid agents require --allow-paid (and stay ≤5 instances)",
                file=sys.stderr,
            )
            return 2

        results: list[dict[str, Any]] = []
        total = len(instances) * len(variants)
        done = 0
        for inst in instances:
            human_patch = extract_human_patch(store, inst, patches_dir)
            for variant in variants:
                if variant.agent not in BILL_SAFE_AGENTS:
                    raise RuntimeError(f"non-bill-safe variant in default set: {variant}")
                summary = run_one(
                    inst=inst,
                    variant=variant,
                    harvest_db=harvest_db,
                    eval_db=eval_db,
                    mode=args.mode,
                    skip_sandbox=args.skip_sandbox,
                    human_patch=human_patch if variant.needs_human_patch else None,
                    save_patch_dir=save_patch_dir,
                    no_pr_artifact=args.no_pr_artifact,
                )
                results.append(summary)
                done += 1
                status = "ok" if summary.get("ok") else "FAIL"
                ace = summary.get("ace_score")
                ace_s = f"{ace:.4f}" if isinstance(ace, (int, float)) else "—"
                print(
                    f"[{done}/{total}] {status} {inst.instance_id} "
                    f"{variant.model_name} ACE={ace_s}",
                    flush=True,
                )

        if paid_ran and args.paid_agent and args.paid_model:
            n_paid = min(max(1, args.paid_limit), PAID_INSTANCE_CAP, len(instances))
            paid_variant = VariantSpec(
                model_name=args.paid_model,
                agent=args.paid_agent,
            )
            for inst in instances[:n_paid]:
                summary = run_one(
                    inst=inst,
                    variant=paid_variant,
                    harvest_db=harvest_db,
                    eval_db=eval_db,
                    mode=args.mode,
                    skip_sandbox=args.skip_sandbox,
                    human_patch=None,
                    save_patch_dir=save_patch_dir,
                    no_pr_artifact=args.no_pr_artifact,
                )
                results.append(summary)
                print(
                    f"[paid] {'ok' if summary.get('ok') else 'FAIL'} "
                    f"{inst.instance_id} {args.paid_model}",
                    flush=True,
                )

    stats = aggregate(results)
    payload = {
        "n_instances": len(instances),
        "n_results": len(results),
        "n_ok": sum(1 for r in results if r.get("ok")),
        "mode": args.mode,
        "stats": stats,
        "paid_ran": paid_ran,
        "paid_note": paid_note,
        "eval_db": str(eval_db),
        "harvest_db": str(harvest_db),
    }

    if report_path is not None:
        write_report(
            report_path,
            instances=instances,
            results=results,
            stats=stats,
            mode=args.mode,
            harvest_db=harvest_db,
            eval_db=eval_db,
            patches_dir=patches_dir,
            save_patch_dir=save_patch_dir,
            paid_ran=paid_ran,
            paid_note=paid_note,
        )
        payload["report"] = str(report_path)
        print(f"wrote report: {report_path}", flush=True)

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print("---")
        print(f"instances: {len(instances)}")
        for model, s in stats.items():
            print(
                f"{model}: n={s['n']} median_ACE={_fmt(s['ace_median'])} "
                f"median_drift={_fmt(s['drift_median'], 1)} "
                f"median_craft={_fmt(s['craft_median'])}"
            )
        print(f"eval_db: {eval_db}")
        if report_path:
            print(f"report:  {report_path}")
        print(f"paid:    {paid_ran}")

    return 0 if all(r.get("ok") for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
