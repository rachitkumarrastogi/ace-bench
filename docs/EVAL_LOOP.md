# Eval loop (future) — human baseline → agent → ACE compare

This is the intended long-term loop. **v1 first pass only implements human harvest into SQLite.** Agent sandbox and full ACE compare are stubs / future work.

```
┌─────────────────────┐
│ 1. Harvest humans   │  merged PRs (pre-AI cutoff) → SQLite
│    PatternStore     │  files, patch, metrics_json
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│ 2. Task instance    │  issue/title/body + base_sha + human F_H / P_H
│    (from DB row)    │
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│ 3. Agent sandbox    │  checkout base_sha; give issue only; capture P_A, F_A
│    (NOT built yet)  │
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│ 4. ACE compare      │  AST / file ratios vs human; pass-fail gate → ACE Index
│    (scoring.py v0)  │
└─────────────────────┘
```

## Phase status

| Phase | Status |
|-------|--------|
| Human PR harvest → SQLite | **Live** (Django pilot) |
| First-pass diff metrics in `metrics_json` | **Live** (AST/GNN replace later) |
| Agent sandbox / dual execution | Stub / docs only |
| tree-sitter / GNN metrics | Deferred |
| Public leaderboard | Deferred |

## Compare inputs (when agent exists)

From each `human_patterns` row:

- **Task**: `title` + `body` (and linked issue text when added)
- **Baseline**: `files_json`, `patch_text`, `metrics_json`, `base_sha`
- **Agent output**: patch + file list + test pass/fail
- **Score**: `ace_bench.scoring.compute_ace_score` (v0 formula)

Do not treat pass/fail alone as the score — efficiency vs human structure is the point of ACE-Bench.
