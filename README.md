# ACE-Bench

**Agent Code Efficiency Benchmark** — measure whether AI coding agents match *human structural efficiency*, not just whether tests pass.

> Current agent evals ask: *Did the patch work?*  
> ACE-Bench asks: *Did the agent solve it like a senior engineer — or inflate the diff?*

---

## Three-step flow

```
[1. Human harvest]  →  [2. Agent sandbox]  →  [3. ACE compare]
 merged pre-AI PRs      issue-only prompt       score vs human structure
 → SQLite               (Docker next)           (CLI live; sandbox stubbed)
```

1. **Harvest** — merged PRs before the AI era → SQLite (`human_patterns`).
2. **Sandbox** — checkout `base_sha`, give the agent the issue only, capture \(P_A\).
3. **Score** — ACE Index vs human \(P_H\) / \(F_H\) (pass/fail is a gate, not the score).

\[
\text{ACE Score} =
\left( \frac{\text{AST Nodes}(P_H)}{\text{AST Nodes}(P_A)} \right)
\times
\left( \frac{\lvert F_H\rvert}{\lvert F_A\rvert} \right)
\times
\text{Pass/Fail Multiplier}
\]

| Score | Meaning |
|-------|---------|
| **1.0** | Matched human efficiency |
| **&lt; 1.0** | Bloat / scope creep |
| **&gt; 1.0** | More concise than the human baseline |
| **0.0** | Failed tests |

---

## Quick start

```bash
export GITHUB_TOKEN=...   # or GH_TOKEN
pip install -e .

# harvest (pilot or full windowed Django baseline)
python3 scripts/run_harvest.py --repos django/django --max-prs 100
./scripts/dgx_full_harvest.sh          # monthly windows 2012→2021
./scripts/dgx_corpus_harvest.sh        # curated Tier A→D master list (sequential; first wave A–C)

# eval v0 — export instances + score an agent patch vs human
export ACE_DB_PATH=$HOME/ace-bench/data/frozen/ace_patterns_django_pre2021_6125.sqlite
python3 scripts/export_eval_instances.py --limit 50
python3 scripts/score_against_human.py --instance django/django#22 --self-smoke --passed-tests true
```

DB: `ACE_DB_PATH` or `./data/ace_patterns.sqlite`. Frozen copies under `data/frozen/` (see [docs/CORPUS.md](docs/CORPUS.md)).

---

## Design principles

1. **Human baseline is ground truth for efficiency**, not correctness alone.
2. **Pass/fail is a gate**, not the score — failing tests → ACE = 0.
3. **Prefer AST metrics over line diffs** — v0 uses `ace_bench.ast_metrics` (`max(added_lines, 1)` until tree-sitter lands).
4. **Agent-agnostic harness** — any agent that emits a patch against a checkout.

---

## Docs

| Doc | Role |
|-----|------|
| [docs/CORPUS.md](docs/CORPUS.md) | Curated repos, Django freeze, human baseline headlines |
| [docs/CORPUS_STATUS.md](docs/CORPUS_STATUS.md) | Living harvest coverage table (`scripts/refresh_corpus_status.py`) |
| [docs/EVAL.md](docs/EVAL.md) | Score CLI (v0) + future dual-execution loop |
| [docs/OPS.md](docs/OPS.md) | DGX / tmux harvest, tokens, rate limits, DB size |
| [docs/SECURITY.md](docs/SECURITY.md) | Threat model, hardening findings, residual risks |
| [AGENTS.md](AGENTS.md) | Commit identity for agents |

Machine source of truth for the **~1000-repo** master list: [`data/corpus_repos.json`](data/corpus_repos.json) (first harvest wave was Tier A–C ~110; Tier D is backlog).

Helpers: `scripts/check_db_size.py` (exit 2 over ~1 GiB), `scripts/rotate_shard_if_needed.py`, `scripts/dgx_shard_watch.sh`, `scripts/dgx_refresh_status.sh`, `REFRESH_STATUS=1 ./scripts/dgx_corpus_harvest.sh`. Mac shard mirror: `~/ace-bench-data/shards/` (see [docs/OPS.md](docs/OPS.md)).

---

## Status (v1)

| Item | State |
|------|--------|
| Django harvest | **6125** rows frozen |
| Kickoff multi-repo | Flask / Express / Cobra / Clap done; master list ~1000 (A–C wave in progress; D backlog) |
| Eval v0 CLI | Live — [docs/EVAL.md](docs/EVAL.md) |
| Docker sandbox | Next |

---

## Market gap

SWE-bench-style evals score task completion; linters score static rules. Neither compares agent diffs to **human structural intent**. ACE-Bench fills that gap.

**Who it's for:** model providers, eng leadership quantifying “codebase tax,” and tool builders targeting human-like patch shape.

## Roadmap

1. [x] Schema + Django pilot → SQLite (**6125** frozen)
2. [ ] Multi-repo pre-AI harvest (Tier A→C in progress)
3. [ ] Sandbox runner (agent-agnostic)
4. [ ] tree-sitter AST metrics + ACE Index
5. [ ] Public leaderboard

## License

MIT — see [LICENSE](LICENSE).

## Author

[Rachit Rastogi](https://github.com/rachitkumarrastogi) · `rachitrastogi777@gmail.com`
