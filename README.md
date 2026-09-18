# ACE-Bench

**Agent Code Efficiency Benchmark** — measure whether AI coding agents match *human structural efficiency*, not just whether tests pass.

> Current agent evals ask: *Did the patch work?*  
> ACE-Bench asks: *Did the agent solve it like a senior engineer — or inflate the diff?*

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

### 1. Data pipeline & baseline ingestion

- Harvest resolved, merged PRs from high-quality open-source repos (Python, TypeScript, Rust, …).
- Store: issue description, human patch \(P_H\), human file set \(F_H\), and pre-PR repo state.

### 2. Isolated agent execution (sandbox)

- Containerized environment (Docker / microVM) at the pre-PR commit.
- Give the agent the issue description only.
- Capture agent patch \(P_A\), file set \(F_A\), and traces.

### 3. Comparative structural analysis (AST & static analysis)

Prefer tree-sitter ASTs over raw line diffs:

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

## Status

Early blueprint / scaffold. Roadmap:

1. [ ] Dataset schema + sample human baselines
2. [ ] Sandbox runner (agent-agnostic interface)
3. [ ] tree-sitter AST metrics + ACE Index
4. [ ] Public leaderboard + paper-ready report format

---

## License

MIT — see [LICENSE](LICENSE).

## Author

[Rachit Rastogi](https://github.com/rachitkumarrastogi) · `rachitrastogi777@gmail.com`
