# ACE-Bench curated corpus (~100 repos)

Curated for **multi-language human-pattern harvest** (`merged:<2021-01-01`), not a raw GitHub-stars top-100.

Machine-readable twin: [`data/corpus_repos.json`](../data/corpus_repos.json).

## Status (do not re-queue as “next”)

| Repo | Status | Lang | Risk | Pre-2021 merged PRs | Notes |
|------|--------|------|------|---------------------|-------|
| `django/django` | **DONE / frozen** | Python | M | 6125 (harvested) | See [CORPUS_DJANGO.md](CORPUS_DJANGO.md) |
| `pallets/flask` | **DONE** | Python | S | 1054 (harvested) | Live DB; do not re-queue |
| `expressjs/express` | **DONE** | JavaScript | S | 196 (harvested) | Live DB; do not re-queue |
| `spf13/cobra` | **DONE** | Go | S | 343 (harvested) | Live DB; do not re-queue |
| `clap-rs/clap` | **DONE** | Rust | S | 967 (harvested) | Live DB; do not re-queue |

Remaining Tier A/B/C: run `./scripts/dgx_corpus_harvest.sh` on DGX (sequential; log `~/ace-bench/data/corpus_harvest.log`).

**Live coverage table:** [CORPUS_STATUS.md](CORPUS_STATUS.md) — regenerate with `python3 scripts/refresh_corpus_status.py --fetch-github`.

**Cutoff (default for all rows below):** `merged:<2021-01-01`  
**Suggested windowing:** monthly or quarterly slices (same pattern as Django).

---

## Curation principles

- Prefer repos with **clear GitHub PR history before 2021**, issue-linked merges, and eventual testability.
- Diversify: Python, JS/TS, Go, Rust, Java, C/C++, Ruby, Kotlin/Swift.
- Skip mailing-list-primary workflows as **primary** harvest targets (kernel, many GNU projects).
- Heavyweights (React, VS Code, etc.) stay **in scope** but land in **Tier C** with stricter filters.
- Counts marked **verified** were sampled via GitHub Search (`is:pr is:merged merged:<2021-01-01`). Others are **TBD** (re-check before harvest; Search secondary rate limits are tight).

---

## Harvest order (mandatory)

1. Kickoff batch (`flask`, `express`, `cobra`, `clap`) is **done** in the live DB.
2. Run **Tier A → B → C** via `scripts/dgx_corpus_harvest.sh` (**one repo at a time**, continue-on-failure).
3. **Tier C** still expects stricter filters later (bot authors, issue-linked, size caps) — full windowed harvest first is intentional and slow.
4. **Never** parallelize repos — shared Search + REST rate budget.

Recommended cadence: the corpus script already spot-checks `--summary-only` after each repo.

---

## Tier A — next 15 (mid-size, high signal, parse-friendly)

Run these **after** the current 4 finish. Prefer S risk first.

| # | Repo | Lang | Why included | Risk | Cutoff | Pre-2021 PRs | Notes |
|---|------|------|--------------|------|--------|--------------|-------|
| 1 | `psf/requests` | Python | Canonical HTTP client; issue-linked PRs | S | `merged:<2021-01-01` | **1349** verified | Small surface; excellent first post-batch target |
| 2 | `encode/httpx` | Python | Modern async/sync HTTP; clean diffs | S | same | **688** verified | Complements Requests |
| 3 | `pydantic/pydantic` | Python | Validation core; typed PRs | S | same | **707** verified | v1-era pre-2021 is useful |
| 4 | `axios/axios` | JavaScript | Ubiquitous HTTP client | S | same | TBD | Browser+Node patterns |
| 5 | `reduxjs/redux` | JavaScript | Small core; high review bar | S | same | TBD | Avoid `redux-toolkit` monorepo first |
| 6 | `lodash/lodash` | JavaScript | Utility lib; many small PRs | S | same | TBD | Docs churn — filter path noise |
| 7 | `gin-gonic/gin` | Go | Popular web framework | S | same | TBD | Strong Go PR culture |
| 8 | `stretchr/testify` | Go | Test helpers; focused patches | S | same | TBD | High signal, low monorepo risk |
| 9 | `sirupsen/logrus` | Go | Logging lib; mature history | S | same | TBD | Mid volume |
| 10 | `serde-rs/serde` | Rust | Serialization ecosystem hub | S | same | TBD | Often multi-crate; still tractable |
| 11 | `BurntSushi/ripgrep` | Rust | Search tool; excellent reviews | S | same | TBD | Single-purpose, testable |
| 12 | `sinatra/sinatra` | Ruby | Micro-framework; classic PRs | S | same | TBD | Ruby coverage without Rails weight |
| 13 | `square/okhttp` | Kotlin/Java | HTTP client; strong review culture | S | same | TBD | JVM + Kotlin mix |
| 14 | `fmtlib/fmt` | C++ | Formatting library; GitHub-native | S | same | TBD | Prefer over Boost/mailing-list C++ |
| 15 | `jekyll/jekyll` | Ruby | SSG; long PR history | S | same | TBD | Some docs-heavy PRs |

---

## Tier B — next ~35 (larger / more languages)

| # | Repo | Lang | Why included | Risk | Cutoff | Pre-2021 PRs | Notes |
|---|------|------|--------------|------|--------|--------------|-------|
| 16 | `aio-libs/aiohttp` | Python | Async HTTP server/client | M | `merged:<2021-01-01` | **2354** verified | Larger than Tier A HTTP libs |
| 17 | `scrapy/scrapy` | Python | Crawler framework | S | same | **1606** verified | Good issue linkage |
| 18 | `celery/celery` | Python | Task queue | M | same | **1398** verified | Multi-package layout |
| 19 | `pytest-dev/pytest` | Python | Test runner; dense PR culture | M | same | **3194** verified | Plugin ecosystem noise |
| 20 | `pallets/click` | Python | CLI (pairs with Flask/Cobra/Clap) | S | same | TBD | Small, high quality |
| 21 | `encode/django-rest-framework` | Python | DRF; Django-adjacent | M | same | TBD | Complements frozen Django |
| 22 | `HypothesisWorks/hypothesis` | Python | Property-based testing | S | same | TBD | Niche but clean |
| 23 | `psf/black` | Python | Formatter; many small PRs | S | same | TBD | Style-only PRs — filter carefully |
| 24 | `eslint/eslint` | JavaScript | Linter platform | M | same | TBD | Rule churn; path filters help |
| 25 | `prettier/prettier` | JavaScript | Formatter | M | same | TBD | Snapshot/fixture heavy |
| 26 | `mochajs/mocha` | JavaScript | Classic test runner | S | same | TBD | Mid-size |
| 27 | `jquery/jquery` | JavaScript | Long history, pre-AI era | M | same | TBD | Legacy + docs |
| 28 | `webpack/webpack` | JavaScript | Bundler | L | same | TBD | Complex; treat as upper-B |
| 29 | `babel/babel` | JavaScript | Compiler monorepo | L | same | TBD | Monorepo — stricter filters |
| 30 | `nestjs/nest` | TypeScript | Node framework | M | same | TBD | TS coverage |
| 31 | `remix-run/react-router` | TypeScript | Routing | M | same | TBD | Was `ReactTraining/react-router` |
| 32 | `go-chi/chi` | Go | Lightweight router | S | same | TBD | Complements Gin |
| 33 | `gorilla/mux` | Go | Classic router | S | same | TBD | Maintenance-mode era still useful |
| 34 | `spf13/viper` | Go | Config (Cobra sibling) | S | same | TBD | After Cobra harvest |
| 35 | `urfave/cli` | Go | Alternate CLI | S | same | TBD | Diversity vs Cobra |
| 36 | `go-gorm/gorm` | Go | ORM | M | same | TBD | |
| 37 | `etcd-io/etcd` | Go | Distributed KV | L | same | TBD | Large; near Tier C |
| 38 | `tokio-rs/tokio` | Rust | Async runtime | M | same | TBD | Multi-crate workspace |
| 39 | `hyperium/hyper` | Rust | HTTP | M | same | TBD | |
| 40 | `actix/actix-web` | Rust | Web framework | M | same | TBD | |
| 41 | `diesel-rs/diesel` | Rust | ORM | M | same | TBD | |
| 42 | `rust-lang/mdBook` | Rust | Docs tool | S | same | TBD | Smaller Rust target |
| 43 | `rust-lang/rust-clippy` | Rust | Lints | M | same | TBD | Many small lint PRs |
| 44 | `square/retrofit` | Java | HTTP client | S | same | TBD | Pairs with OkHttp |
| 45 | `google/gson` | Java | JSON | S | same | TBD | Focused |
| 46 | `google/guava` | Java | Core libs | M | same | TBD | Large surface |
| 47 | `junit-team/junit4` | Java | Classic tests | S | same | TBD | Prefer junit4 over junit5 volume |
| 48 | `nlohmann/json` | C++ | JSON for Modern C++ | S | same | TBD | Header-heavy but GitHub PRs |
| 49 | `catchorg/Catch2` | C++ | Test framework | S | same | TBD | |
| 50 | `protocolbuffers/protobuf` | C++/multi | IDL + runtimes | L | same | TBD | Multi-language monorepo |
| 51 | `Alamofire/Alamofire` | Swift | HTTP client | S | same | TBD | Swift coverage |
| 52 | `ReactiveX/RxSwift` | Swift | Reactive | M | same | TBD | |
| 53 | `discourse/discourse` | Ruby | Forum app | L | same | TBD | App-scale Ruby before Rails |
| 54 | `Homebrew/brew` | Ruby | Package manager | M | same | TBD | Formula noise — code PRs only |
| 55 | `hashicorp/consul` | Go | Service mesh/discovery | L | same | TBD | Upper-B / near C |

---

## Tier C — heavyweights (harvest last; stricter filters)

Size/risk flags: monorepo, huge PR volume, Search/API time, bot spam.

| # | Repo | Lang | Why included | Risk | Cutoff | Pre-2021 PRs | Notes |
|---|------|------|--------------|------|--------|--------------|-------|
| 56 | `facebook/react` | JavaScript | **User-requested heavyweight** | L | `merged:<2021-01-01` | TBD | Monorepo; exclude bots; cap files/diff |
| 57 | `microsoft/vscode` | TypeScript | **User-requested heavyweight** | L | same | TBD | Huge volume; rate-limit time; extension noise |
| 58 | `kubernetes/kubernetes` | Go | Orchestration standard | L | same | TBD | Massive; SIG bots; need aggressive filters |
| 59 | `rails/rails` | Ruby | Framework heavyweight | L | same | TBD | Multi-gem monorepo |
| 60 | `spring-projects/spring-boot` | Java | Boot ecosystem | L | same | TBD | Prefer after smaller JVM Tier B |
| 61 | `spring-projects/spring-framework` | Java | Core Spring | L | same | TBD | |
| 62 | `golang/go` | Go | Language + stdlib | L | same | TBD | Some non-GitHub history; still valuable |
| 63 | `rust-lang/rust` | Rust | Compiler | L | same | TBD | Enormous; submodule/tooling noise |
| 64 | `rust-lang/cargo` | Rust | Package manager | M–L | same | TBD | More tractable than `rustc` |
| 65 | `python/cpython` | Python | Language | L | same | **19117** verified | Huge; many misc/doc PRs |
| 66 | `nodejs/node` | JavaScript | Runtime | L | same | TBD | Core + deps noise |
| 67 | `numpy/numpy` | Python | Array compute | L | same | **6993** verified | SciPy-stack sibling next |
| 68 | `scipy/scipy` | Python | Scientific | L | same | TBD | |
| 69 | `pytorch/pytorch` | Python | ML framework | L | same | **4299** verified | Monorepo; CUDA/build noise |
| 70 | `tensorflow/tensorflow` | C++/Python | ML framework | L | same | TBD | Extreme monorepo risk |
| 71 | `huggingface/transformers` | Python | NLP models | L | same | **3068** verified | Model card / docs heavy |
| 72 | `ansible/ansible` | Python | Automation | L | same | **32367** verified | Extreme volume — sample windows |
| 73 | `home-assistant/core` | Python | Home automation | L | same | **21563** verified | Integration sprawl |
| 74 | `microsoft/TypeScript` | TypeScript | Language | L | same | TBD | Compiler + tests huge |
| 75 | `angular/angular` | TypeScript | Framework monorepo | L | same | TBD | |
| 76 | `vuejs/core` | TypeScript | Vue 3 core | M–L | same | TBD | Pre-2021 may be thinner; also consider `vuejs/vue` |
| 77 | `vuejs/vue` | JavaScript | Vue 2 | M | same | TBD | Stronger pre-2021 history |
| 78 | `hashicorp/terraform` | Go | IaC | L | same | TBD | Provider noise |
| 79 | `hashicorp/vault` | Go | Secrets | L | same | TBD | |
| 80 | `prometheus/prometheus` | Go | Metrics | L | same | TBD | |
| 81 | `grafana/grafana` | TypeScript/Go | Observability UI | L | same | TBD | Frontend+backend |
| 82 | `elastic/elasticsearch` | Java | Search | L | same | TBD | |
| 83 | `apache/kafka` | Java/Scala | Streaming | L | same | TBD | |
| 84 | `apache/spark` | Scala | Data | L | same | TBD | Build-heavy |
| 85 | `electron/electron` | TypeScript/C++ | Desktop shell | L | same | TBD | |
| 86 | `facebook/react-native` | JS/Java/ObjC | Mobile | L | same | TBD | Multi-platform monorepo |
| 87 | `flutter/flutter` | Dart | UI toolkit | L | same | TBD | Engine + framework |
| 88 | `godotengine/godot` | C++ | Game engine | L | same | TBD | |
| 89 | `opencv/opencv` | C++ | Vision | L | same | TBD | |
| 90 | `llvm/llvm-project` | C++ | Compiler infra | L | same | TBD | Monorepo extreme |
| 91 | `dotnet/runtime` | C# | Runtime | L | same | TBD | |
| 92 | `dotnet/aspnetcore` | C# | Web stack | L | same | TBD | |
| 93 | `JetBrains/kotlin` | Kotlin | Language | L | same | TBD | |
| 94 | `apple/swift` | Swift/C++ | Language | L | same | TBD | Partial GitHub mirror dynamics |
| 95 | `redis/redis` | C | Datastore | M–L | same | TBD | Historically mixed contribution paths |
| 96 | `postgresql/postgres` | C | RDBMS | L | same | TBD | **Caution:** much history is mailing-list; GitHub PRs incomplete — sample only |
| 97 | `git/git` | C | VCS | L | same | TBD | Mailing-list primary — low priority within C |
| 98 | `moby/moby` | Go | Docker engine | L | same | TBD | Renames/history quirks |
| 99 | `docker/cli` | Go | Docker CLI | M | same | TBD | Smaller than engine |
| 100 | `helm/helm` | Go | K8s packaging | M–L | same | TBD | After smaller Go Tier A/B |
| 101 | `istio/istio` | Go | Service mesh | L | same | TBD | |
| 102 | `envoyproxy/envoy` | C++ | Proxy | L | same | TBD | |
| 103 | `clickhouse/clickhouse` | C++ | OLAP DB | L | same | TBD | |
| 104 | `pingcap/tidb` | Go | Distributed SQL | L | same | TBD | |
| 105 | `cockroachdb/cockroach` | Go | Distributed SQL | L | same | TBD | |

*Total listed corpus rows (status + A + B + C): **110** (5 status + 15 A + 40 B + 50 C). Target band 90–110.*

### Tier C filter checklist (apply before enqueue)

- [ ] Exclude authors matching bot patterns (`dependabot[bot]`, `renovate`, `github-actions`, `googlebot`, etc.)
- [ ] Prefer `linked:issue` / issue-closing keywords when Search allows
- [ ] Cap changed files (e.g. ≤8) and net lines (e.g. ≤400) for ACE dual-exec tractability
- [ ] Skip pure docs/changelog/CI-only paths when classifying “code human patterns”
- [ ] Use longer date windows + sleep; expect multi-day harvests

---

## Exclusion list (do not use as primary harvest)

| Repo / class | Reason |
|--------------|--------|
| `torvalds/linux` | Mailing-list / patch-email primary; GitHub is not the real review surface |
| GNU / many `git.savannah` mirrors on GitHub | Incomplete PR history; mirror noise |
| `awesome-*` lists | Not product code; no meaningful patches |
| Pure documentation sites / book-only repos | Low ACE dual-exec value |
| Crypto-miner / malware / joke repos | Out of scope |
| Brand-new post-2021-only projects | Fail pre-AI cutoff by construction |
| `sqlalchemy/sqlalchemy` (as early target) | Only **~53** verified pre-2021 GitHub merges (history lived elsewhere) — revisit later or skip |
| `tiangolo/fastapi` (as early target) | Search returned invalid/empty for pre-2021 sample in this pass; project rose late — verify before enqueue |
| Mega-mirrors (`chromium/chromium` without filters) | Volume + process mismatch for ACE v1 |
| Generated-code dumps / vendored trees | Inflates diffs; not human design signal |

---

## Language mix (primary language per repo)

| Language | Count (status+A+B+C) | Role |
|----------|----------------------|------|
| Go | 22 | Cobra in-flight + cloud/infra heavyweights |
| Python | 20 | Strong base (Django done + many A/B) |
| JavaScript | 14 | Express in-flight + clients/tools + React |
| Rust | 11 | Clap in-flight + serde/tokio + rustc/cargo |
| C++ | 10 | fmt/json → LLVM/Envoy/Godot |
| TypeScript | 8 | VS Code / Angular / Nest / TS itself |
| Java | 8 | Retrofit → Spring / ES / Kafka |
| Ruby | 5 | Sinatra/Jekyll → Rails/Discourse |
| Swift | 3 | Alamofire / RxSwift / Swift |
| C | 3 | Redis / Postgres / Git (cautious) |
| Kotlin | 2 | OkHttp + Kotlin language |
| C# | 2 | .NET runtime / ASP.NET |
| Scala | 1 | Spark |
| Dart | 1 | Flutter |

*Counts are by the `lang` field in `data/corpus_repos.json` (one primary language per repo). Total = 110.*

---

## Sanity-check notes (this curation pass)

Verified via `gh` Search as user `rachitkumarrastogi` (token never logged):

| Repo | `merged:<2021-01-01` count |
|------|----------------------------|
| `pallets/flask` | 1100 |
| `psf/requests` | 1349 |
| `encode/httpx` | 688 |
| `pydantic/pydantic` | 707 |
| `aio-libs/aiohttp` | 2354 |
| `scrapy/scrapy` | 1606 |
| `celery/celery` | 1398 |
| `pytest-dev/pytest` | 3194 |
| `python/cpython` | 19117 |
| `numpy/numpy` | 6993 |
| `pytorch/pytorch` | 4299 |
| `huggingface/transformers` | 3068 |
| `ansible/ansible` | 32367 |
| `home-assistant/core` | 21563 |
| `sqlalchemy/sqlalchemy` | 53 (too thin for early harvest) |

Search secondary rate limits (~30/min, often stricter bursts) blocked a full 100-repo recount in one sitting. Re-run counts per repo immediately before harvest enqueue.

---

## Related docs

- [CORPUS_DJANGO.md](CORPUS_DJANGO.md) — frozen Django snapshot  
- [DGX_FIRST_PASS.md](DGX_FIRST_PASS.md) — DGX harvest how-to  
- [HUMAN_PATTERN_BASELINE_DJANGO.md](HUMAN_PATTERN_BASELINE_DJANGO.md) — Django ACE scoring baseline  
