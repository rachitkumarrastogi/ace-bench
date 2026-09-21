# ACE-Bench

**Agent Code Efficiency Benchmark** — measure whether AI coding agents match *human structural efficiency*, not just whether tests pass.

> Current agent evals ask: *Did the patch work?*  
> ACE-Bench asks: *Did the agent solve it like a senior engineer — or inflate the diff?*

---

## Flow

```
[1. Human harvest]  →  [2. Pattern prior]  →  [3. Sandbox + agent]  →  [4. ACE compare]
 merged pre-AI PRs      cross-repo p50/p90      checkout @ base_sha      vs human + model_name
 → harvest SQLite       → patterns SQLite       → agent.patch            → eval_runs.sqlite
```

1. **Harvest** — merged PRs before the AI era → harvest SQLite (`human_patterns`).
2. **Pattern prior** — read-only aggregates → dedicated `ace_patterns_prior.sqlite`.
3. **Sandbox + agent** — shallow checkout at `base_sha`, named `--model` / `--agent` → patch.
4. **Score** — ACE Index vs human \(P_H\) / \(F_H\) (+ optional prior); store `model_name`.

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

# eval — score + agent sandbox (model_name required)
export ACE_DB_PATH=data/frozen/ace_patterns_django_pre2021_6125.sqlite
python3 scripts/score_against_human.py --instance django/django#22 --self-smoke --passed-tests true \
  --agent-patch /tmp/django22_human.patch
python3 scripts/run_agent_eval.py \
  --instance django/django#22 --model human-replay --agent file \
  --agent-patch /tmp/django22_human.patch \
  --passed-tests true --skip-sandbox --db "$ACE_DB_PATH"
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
| [docs/EVAL.md](docs/EVAL.md) | Sandbox + agent eval (step 3) + score CLI |
| [docs/OPS.md](docs/OPS.md) | DGX / tmux harvest, tokens, rate limits, DB size |
| [docs/SECURITY.md](docs/SECURITY.md) | Threat model, hardening findings, residual risks |
| [AGENTS.md](AGENTS.md) | Commit identity for agents |

Machine source of truth for the **~1000-repo** master list: [`data/corpus_repos.json`](data/corpus_repos.json) (first harvest wave was Tier A–C ~110; Tier D is backlog).

Helpers: `scripts/check_db_size.py` (exit 2 over ~1 GiB), `scripts/rotate_shard_if_needed.py`, `scripts/dgx_shard_watch.sh`, `scripts/dgx_refresh_status.sh`, `REFRESH_STATUS=1 ./scripts/dgx_corpus_harvest.sh`. Pattern prior (step 2): `scripts/build_pattern_db.py` / `scripts/dgx_build_patterns.sh` → `~/ace-bench/data/patterns/` (Mac: `~/ace-bench-data/patterns/`). Mac shard mirror: `~/ace-bench-data/shards/` (see [docs/OPS.md](docs/OPS.md)).

---

## Status (v1)

| Item | State |
|------|--------|
| Django harvest | **6125** rows frozen |
| Kickoff multi-repo | Flask / Express / Cobra / Clap done; master list ~1000 (A–C wave in progress; D backlog) |
| Pattern prior DB | Live — cross-repo baselines from shards ([docs/CORPUS.md](docs/CORPUS.md)) |
| Eval + agent sandbox MVP | Live — [docs/EVAL.md](docs/EVAL.md) (`model_name` required) |
| Docker test runner | Next (`--network none` + pytest gate) |

---

## Market gap

SWE-bench-style evals score task completion; linters score static rules. Neither compares agent diffs to **human structural intent**. ACE-Bench fills that gap.

**Who it's for:** model providers, eng leadership quantifying “codebase tax,” and tool builders targeting human-like patch shape.

## Roadmap

1. [x] Schema + Django pilot → SQLite (**6125** frozen)
2. [ ] Multi-repo pre-AI harvest (Tier A→C in progress)
3. [x] Sandbox + pluggable agents MVP (`file`/`stub`/`openai`/`anthropic`)
4. [ ] Docker test runner + full-repo LLM context
5. [ ] tree-sitter AST metrics + public leaderboard

## License

MIT — see [LICENSE](LICENSE).

## Author

[Rachit Rastogi](https://github.com/rachitkumarrastogi) · `rachitrastogi777@gmail.com`
