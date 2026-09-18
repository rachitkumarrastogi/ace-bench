# ACE-Bench

**Agent Code Efficiency Benchmark** — measure whether AI coding agents match *human structural efficiency*, not just whether tests pass.

> Current agent evals ask: *Did the patch work?*  
> ACE-Bench asks: *Did the agent solve it like a senior engineer — or inflate the diff?*

---

## Status (v1 first pass)

| Item | State |
|------|--------|
| **Django harvest** | Done — **6125** rows; frozen snapshot documented in [docs/CORPUS_DJANGO.md](docs/CORPUS_DJANGO.md) |
| **Multi-repo batch** | In flight — Flask / Express / Cobra / Clap (pre-AI, windowed) via `scripts/dgx_multi_harvest.sh` |
| **Curated Top ~100** | [docs/CORPUS_TOP100.md](docs/CORPUS_TOP100.md) + [`data/corpus_repos.json`](data/corpus_repos.json) — Tier A next after current batch |
| Default repo | `django/django` (`2012-01-01` → `2021-01-01`, monthly windows) |
| Linux kernel | Deferred / excluded as primary (see corpus exclusions) |
| Agent sandbox / ACE compare | Next — see [docs/EVAL_LOOP.md](docs/EVAL_LOOP.md) |

DGX overnight how-to: [docs/DGX_FIRST_PASS.md](docs/DGX_FIRST_PASS.md).

```bash
export GITHUB_TOKEN=...   # or GH_TOKEN
# full django baseline (monthly windows):
./scripts/dgx_full_harvest.sh
# multi-repo curated batch (same live DB, upsert on repo+pr_number):
./scripts/dgx_multi_harvest.sh
# pilot cap only:
python3 scripts/run_harvest.py --repos django/django --max-prs 100
```

DB path: `ACE_DB_PATH` or `./data/ace_patterns.sqlite`. Keep the live DB;
freeze copies live under `data/frozen/` (see [data/FROZEN.md](data/FROZEN.md)).

---

## The Core Premise

Prior to ~2012, blogs were judged on utility, clarity, and authority. After SEO mills and generative AI, the web filled with **content bloat**: 2,000-word articles for queries that needed 50 words.

A software engineering counterpart is happening now.

AI coding agents maximize likelihoods and pass tests. Asked to fix a bug or add a feature, an agent often generates **150 lines across 4 files** — redundant helpers, unnecessary abstractions, duplicated logic — for a problem a senior engineer fixes in **12 lines in one file**.

Benchmarks that treat code generation as binary pass/fail ignore **code rot, maintenance debt, and context-window bloat**.

---

## Pipeline

```
[GitHub Merged PRs] ──> [Dual-Execution Engine] ──> [AST & Diff Analyzer] ──> [Efficiency Score (ACE Index)]
  (Human Baseline)         (Agent Generated)           (Structural Metrics)        (Leaderboard / Report)
```

### 1. Data pipeline & baseline ingestion (this pass)

- Harvest resolved, merged PRs from high-quality open-source repos (pilot: Django).
- Store: issue description, human patch \(P_H\), human file set \(F_H\), crude diff metrics in `metrics_json`, and base SHA.

### 2. Isolated agent execution (sandbox) — next

- Containerized environment (Docker / microVM) at the pre-PR commit.
- Give the agent the issue description only.
- Capture agent patch \(P_A\), file set \(F_A\), and traces.

### 3. Comparative structural analysis (AST & static analysis)

Prefer tree-sitter ASTs over raw line diffs (first pass uses cheap diff proxies until AST lands):

| Signal | What it captures |
|--------|------------------|
| **AST node overhead** | Syntactic size of \(P_A\) vs \(P_H\) |
| **Scope creep** | Files outside the human touch-set: \(F_A \setminus F_H\) |
| **Redundancy** | Logic reimplemented instead of reusing existing utilities |
| **Cyclomatic complexity Δ** | Net increase in decision branches |

### 4. Scoring — the ACE Index

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
| **&lt; 1.0** | Bloat, unnecessary files, or over-engineering |
| **&gt; 1.0** | More concise structural fix than the human baseline |
| **0.0** | Failed the unit test suite |

---

## Market gap

```
                               FUNCTIONAL VALIDATION
                              (Does the patch work?)
                                  │          │
                     ┌────────────┘          └────────────┐
                     ▼                                    ▼
           [SWE-bench / SWE-bench Lite]            [Static Linters / SonarQube]
           • Binary Pass/Fail                      • Static rule checking
           • Ignores code quality                  • No comparison to human diff
           • Ignores verbosity                     • Doesn't measure intent efficiency
                     │                                    │
                     └────────────┬───────────────────────┘
                                  ▼
                    ┌──────────────────────────┐
                    │    THE UNADDRESSED GAP   │
                    │   Structural Efficiency  │
                    │   vs. Human Baselines    │
                    │        (ACE-Bench)       │
                    └──────────────────────────┘
```

| Approach | Strength | Blind spot |
|----------|----------|------------|
| **SWE-bench & peers** | Task completion | Same score for 5 clean lines vs 500 spaghetti, if tests pass |
| **Linters / SonarQube** | Static quality rules | No *human intent ratio* — can't tell if 100 lines should have been 5 |
| **Enterprise telemetry** | Org-level churn | Not an agent/LLM evaluation harness |

---

## Who this is for

- **Researchers & model providers** — spot models that hallucinate architecture or emit verbose boilerplate.
- **Engineering leadership** — quantify “codebase tax”: does an agent buy short-term velocity at long-term maintenance cost?
- **Tool builders** — a target for prompts, system instructions, and AST-pruning post-processors that compress agent output toward human structural quality.

---

## Roadmap

1. [x] Dataset schema + Django pilot harvest → SQLite (**6125** frozen)
2. [ ] Multi-repo pre-AI harvest (Flask / Express / Cobra / Clap)
3. [ ] Sandbox runner (agent-agnostic interface)
4. [ ] tree-sitter AST metrics + ACE Index (formula stub in `scoring.py`)
5. [ ] Public leaderboard + paper-ready report format

---

## License

MIT — see [LICENSE](LICENSE).

## Author

[Rachit Rastogi](https://github.com/rachitkumarrastogi) · `rachitrastogi777@gmail.com`
