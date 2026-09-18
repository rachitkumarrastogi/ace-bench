# What does human code change look like? (Django baseline)

Read-only analysis of the frozen/live ACE-Bench human-pattern corpus for **`django/django`**.

| Field | Value |
|-------|--------|
| **Source DB** | DGX `$HOME/ace-bench/data/ace_patterns.sqlite` (table `human_patterns`) |
| **Frozen twin** | See [CORPUS_DJANGO.md](CORPUS_DJANGO.md) |
| **Rows** | **6125** PRs |
| **Window** | Merged ~2012-04-28 → 2020-12-31 (`merged:<2021-01-01`) |
| **Analyzed** | 2026-09-18 (UTC) |

## Not an agentic app yet — pattern corpus; agent compare is next

This document is a **statistical snapshot of human PR structure**, not an agent product. ACE-Bench v1 harvests and freezes pre-AI human diffs so later scoring has a ground-truth distribution. **Agent sandbox + ACE compare** (checkout `base_sha`, issue-only prompt, score agent patch vs human) is the next phase — see [EVAL_LOOP.md](EVAL_LOOP.md). Until then, treat these numbers as the **human efficiency prior**, not a live leaderboard.

---

## Headline

Human Django PRs are **small and surgical**:

- **Median files touched: 2** (p90 = 8; p99 ≈ 64)
- **Median churn (additions + deletions): 20** lines (p90 = 136)
- **57% of PRs touch ≤2 files**; **84% touch ≤5**; only **3.3% touch >20**

Most merged work is a one- or two-file fix (often code + test or docs), not a multi-directory rewrite. Complexity metrics are sparse: **median decision-points / loops / functions added are all 0** — humans often change behavior without adding new branches or definitions.

---

## 1. Size distributions

| Metric | min | mean | p50 | p90 | p99 | max |
|--------|-----|------|-----|-----|-----|-----|
| `file_count` | 0 | 5.66 | **2** | 8 | 63.8 | 1059 |
| `directories_touched` | 0 | 3.85 | **2** | 6 | 35 | 382 |
| `additions` | 0 | 61.8 | **13** | 91 | 853 | 19132 |
| `deletions` | 0 | 38.6 | **4** | 45 | 650 | 9872 |
| churn (`additions+deletions`) | 0 | 100.4 | **20** | 136 | 1475 | 22954 |

Notes:

- 27 PRs have `file_count = 0`; 33 have zero churn (empty / metadata edge cases in harvest). They do not move the median.
- Means are pulled up by rare mega-PRs (translations, version bootstraps, mechanical style sweeps). Prefer **p50 / p90** for scoring thresholds.

### File-count histogram

| Files | PRs | % |
|-------|-----|---|
| 1 (incl. 0) | 2319 | 37.9% |
| 2 | 1184 | 19.3% |
| 3–5 | 1613 | 26.3% |
| 6–10 | 600 | 9.8% |
| 11–20 | 204 | 3.3% |
| 21–50 | 134 | 2.2% |
| 51+ | 71 | 1.2% |

---

## 2. Surgical vs sprawling

| Bucket | Count | Share |
|--------|-------|-------|
| `file_count ≤ 2` | 3503 | **57.2%** |
| `file_count ≤ 5` | 5116 | **83.5%** |
| `file_count > 20` | 205 | **3.3%** |

**Interpretation for ACE scoring:** an agent that routinely lands 8–15 files for bugfix tasks is already past human p90. Sprawl (>20 files) is a human rarity (~1 in 30) and often mechanical (line-length, flake8, i18n, version bootstrap) — not the modal “fix a ticket” shape.

---

## 3. Complexity metrics (`metrics_json`)

All 6125 rows carry: `decision_points_added`, `loops_added`, `functions_added` (plus line/file aggregates).

| Metric | mean | p50 | p90 | p99 | max |
|--------|------|-----|-----|-----|-----|
| `decision_points_added` | 1.46 | **0** | 3 | 20 | 321 |
| `loops_added` | 0.46 | **0** | 1 | 7 | 158 |
| `functions_added` | 2.41 | **0** | 5 | 31 | 279 |

- **65% of PRs add zero decision points** (no new `if`/`elif`/`except`/`and`/`or`-style branches counted in the harvest).
- Complexity tails are real but rare — use p90/p99 as soft caps when comparing agents, not means.

---

## 4. Extension / role mix

Across **34,637** file paths in `files_json`:

| Role (heuristic) | File paths | Notes |
|------------------|------------|-------|
| Tests | 13,319 | `/tests/`, `test_*` |
| Production `.py` (non-test) | 11,270 | |
| Docs | 6,643 | `docs/`, `.rst`/`.md` |
| Other | 3,405 | `.po`/`.mo`, JS/CSS, assets, … |

Top extensions by path count: `.py` (69%), `.txt` (docs), `.po`/`.mo` (i18n), `.html`, `.js`.

**PR-level touch rates** (a PR may hit multiple roles):

| Touches ≥1 … | PRs | % |
|--------------|-----|---|
| Non-test `.py` | 3803 | 62% |
| Test path | 3553 | **58%** |
| Docs path | 2917 | 48% |

~1273 PRs are docs-only by extension set; ~4621 touch `.py`. Humans often ship **code + test together** at median size (2 files) — a completeness signal beyond raw LOC.

---

## 5. Correlation: file_count vs decision points

Pearson (linear) on all rows with DP present (n=6125):

| Pair | r |
|------|---|
| `file_count` ↔ `decision_points_added` | **0.18** (weak) |
| `file_count` ↔ churn | **0.55** (moderate) |
| churn ↔ `decision_points_added` | **0.28** (weak–moderate) |

Mean / median DP by file-count bucket:

| Files | n | mean DP | p50 DP |
|-------|---|---------|--------|
| 1 | 2292 | 0.17 | 0 |
| 2 | 1184 | 0.70 | 0 |
| 3–5 | 1613 | 1.45 | 1 |
| 6–10 | 600 | 2.44 | 1 |
| 11–20 | 204 | 5.67 | 2 |
| 21–50 | 134 | 8.82 | 2 |
| 51+ | 71 | 22.58 | 1 |

**High file_count does not reliably mean high decision density.** PRs with `file_count > 20` have mean DP **13.6** vs **0.35** for ≤2 files, but median DP for sprawl is still only **2** — many sprawling PRs are bulk mechanical edits (translations, formatting) with little new control flow. Score **boundary (files/dirs)**, **size (churn)**, and **complexity (DP/loops/funcs)** as **separate axes**, not one proxy.

---

## 6. Exemplar PRs (intuition)

Five exemplars: tiny surgical, typical surgical, two near-median, one true code sprawl.

### Tiny surgical (1 file, 1 line)

| | |
|--|--|
| **PR** | [#9941](https://github.com/django/django/pull/9941) — *Fixed #29480 -- Made MySQL backend retrieve constraint columns in their defined order.* |
| **Stats** | files=1, dirs=1, +1/−0, churn=1, DP=0, loops=0, funcs=0 |
| **Files** | `django/db/backends/mysql/introspection.py` |

### Typical surgical (~p50 of ≤2-file set)

| | |
|--|--|
| **PR** | [#7869](https://github.com/django/django/pull/7869) — *Refs #23919 -- Removed Python 2 workaround for hashing Oracle params.* |
| **Stats** | files=1, dirs=1, +2/−7, churn=9, DP=0, loops=0, funcs=0 |
| **Files** | `django/db/backends/oracle/base.py` |

### Median shape (2 files ≈ p50 files, ~20-line churn)

| | |
|--|--|
| **PR** | [#7584](https://github.com/django/django/pull/7584) — *Fixed #27516 -- Made test client's response.json() cache the parsed JSON* |
| **Stats** | files=2, dirs=2, +12/−6, churn=18, DP=2, loops=0, funcs=2 |
| **Files** | `django/test/client.py`, `tests/test_client_regress/tests.py` |

| | |
|--|--|
| **PR** | [#13281](https://github.com/django/django/pull/13281) — *Fixed #31863 -- Prevented mutating model state by copies of model instances.* |
| **Stats** | files=2, dirs=2, +19/−1, churn=20, DP=0, loops=0, funcs=1 |
| **Files** | `django/db/models/base.py`, `tests/model_regress/tests.py` |

### Sprawl (real feature / large refactor — not translations)

| | |
|--|--|
| **PR** | [#376](https://github.com/django/django/pull/376) — *Schema alteration* |
| **Stats** | files=111, dirs=44, +6334/−403, churn=6737, DP=321, loops=158, funcs=279 |

Contrast: translation mega-PRs (e.g. [#12167](https://github.com/django/django/pull/12167), 529 files, 23k churn, DP=0) inflate size without complexity — another reason to keep axes separate and optionally filter i18n/mechanical classes when scoring “agent vs human fix.”

---

## 7. How these baselines score agent PRs (next)

When agent compare lands, use this corpus as the **human prior** per task (or global percentile gates):

| Axis | Human signal (Django) | Agent scoring idea |
|------|----------------------|--------------------|
| **Boundary** | p50 files=2, p90=8; dirs p50=2 | Penalize file/dir count above human percentile for the task class; flag >20 as sprawl |
| **Size** | p50 churn=20, p90=136 | Ratio `churn_agent / churn_human` or percentile rank on churn |
| **Complexity** | p50 DP/loops/funcs = 0; p90 DP=3 | Penalize excess new branches/funcs relative to human patch / task prior |
| **Completeness / tests** *(future)* | ~58% of human PRs touch tests | Beyond LOC: did the agent add/adjust tests when humans did? Docs touch rate (~48%) as a softer secondary |

Suggested v0 compare (aligned with [EVAL_LOOP.md](EVAL_LOOP.md)):

1. Gate on **correctness** (tests pass).
2. Compute deviation on **boundary**, **size**, **complexity** vs the matched human row (and/or vs global p50/p90).
3. Fold into ACE Index — efficiency vs human structure, not pass/fail alone.
4. Later: **completeness** axis (tests/docs presence) independent of churn.

Do **not** treat mean churn (~100) or mean files (~5.7) as targets; they are mean-skewed. Prefer medians and upper percentiles.

---

## Reproduce (DGX, read-only)

```bash
ssh LocalModelRunner
python3 - <<'PY'
# open file:$HOME/ace-bench/data/ace_patterns.sqlite?mode=ro
# SELECT COUNT(*), AVG(file_count), ... FROM human_patterns WHERE repo='django/django';
PY
```

Frozen snapshot path and freeze procedure: [CORPUS_DJANGO.md](CORPUS_DJANGO.md).
