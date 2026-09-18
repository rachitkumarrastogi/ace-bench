# ACE-Bench corpus status

_Generated: **2026-09-18T20:20:32Z** (UTC)_

Per-repo GitHub Search `total_count` for `is:pr is:merged merged:<2021-01-01` vs rows in `human_patterns`.

## Summary

| Metric | Value |
|--------|-------|
| Total harvested rows | **8928** |
| Repos with data | **6** / 110 |
| Status: done | 5 |
| Status: harvesting | 1 |
| Status: queued / pending | 104 |
| Status: skipped | 0 |
| GitHub counts known | 104 / 110 (sum of known = 547378) |
| Active harvest (log) | `psf/requests` |
| DB | `/home/arnavrastogi/ace-bench/data/ace_patterns.sqlite` |
| Corpus JSON | `data/corpus_repos.json` |
| Harvest log | `/home/arnavrastogi/ace-bench/data/corpus_harvest.log` |
| GitHub Search fetches this run | 86 |

**Done** when harvested &gt; 0 and harvest finished for the repo in logs, or coverage ≥ 95% of the GitHub count (or within ±5 PRs).

Refresh:

```bash
export ACE_DB_PATH=$HOME/ace-bench/data/ace_patterns.sqlite
python3 scripts/refresh_corpus_status.py --fetch-github
```

## Per-repo table

| repo | tier | status | github_pre2021 | harvested | coverage % | notes |
|------|------|--------|----------------|-----------|------------|-------|
| `django/django` | kickoff | done | 6125 | 6125 | 100.0% | See docs/CORPUS_DJANGO.md; coverage ≥95% of GitHub Search |
| `pallets/flask` | kickoff | done | 1054 | 1054 | 100.0% | Harvested into live ace_patterns.sqlite; skip re-queue; coverage ≥95% of GitHub Search |
| `expressjs/express` | kickoff | done | 196 | 196 | 100.0% | Harvested into live ace_patterns.sqlite; skip re-queue; coverage ≥95% of GitHub Search |
| `spf13/cobra` | kickoff | done | 343 | 343 | 100.0% | Harvested into live ace_patterns.sqlite; skip re-queue; coverage ≥95% of GitHub Search |
| `clap-rs/clap` | kickoff | done | 967 | 967 | 100.0% | Harvested into live ace_patterns.sqlite; skip re-queue; coverage ≥95% of GitHub Search |
| `psf/requests` | A | harvesting | 1349 | 243 | 18.0% | Best first post-batch target; active in corpus_harvest.log |
| `encode/httpx` | A | queued | 688 | 0 | 0.0% | Complements Requests |
| `pydantic/pydantic` | A | queued | 707 | 0 | 0.0% | v1-era pre-2021 useful |
| `axios/axios` | A | queued | 360 | 0 | 0.0% | Browser+Node patterns |
| `reduxjs/redux` | A | queued | 1353 | 0 | 0.0% | Avoid redux-toolkit monorepo first |
| `lodash/lodash` | A | queued | 568 | 0 | 0.0% | Docs churn — filter path noise |
| `gin-gonic/gin` | A | queued | 652 | 0 | 0.0% | Strong PR culture |
| `stretchr/testify` | A | queued | 309 | 0 | 0.0% | High signal, low monorepo risk |
| `sirupsen/logrus` | A | queued | 374 | 0 | 0.0% | Mid volume |
| `serde-rs/serde` | A | queued | 527 | 0 | 0.0% | Often multi-crate; still tractable |
| `BurntSushi/ripgrep` | A | queued | 387 | 0 | 0.0% | Single-purpose, testable |
| `sinatra/sinatra` | A | queued | 625 | 0 | 0.0% | Ruby without Rails weight |
| `square/okhttp` | A | queued | TBD | 0 | — | JVM + Kotlin mix; Search unavailable (422 / not searchable with token) |
| `fmtlib/fmt` | A | queued | 480 | 0 | 0.0% | Prefer over mailing-list C++ |
| `jekyll/jekyll` | A | queued | 2851 | 0 | 0.0% | Some docs-heavy PRs |
| `aio-libs/aiohttp` | B | queued | 2354 | 0 | 0.0% | Larger than Tier A HTTP libs |
| `scrapy/scrapy` | B | queued | 1606 | 0 | 0.0% | Good issue linkage |
| `celery/celery` | B | queued | 1398 | 0 | 0.0% | Multi-package layout |
| `pytest-dev/pytest` | B | queued | 3194 | 0 | 0.0% | Plugin ecosystem noise |
| `pallets/click` | B | queued | 434 | 0 | 0.0% | Small, high quality |
| `encode/django-rest-framework` | B | queued | 2525 | 0 | 0.0% | Complements frozen Django |
| `HypothesisWorks/hypothesis` | B | queued | 1412 | 0 | 0.0% | Niche but clean |
| `psf/black` | B | queued | 462 | 0 | 0.0% | Style-only PRs — filter carefully |
| `eslint/eslint` | B | queued | 4609 | 0 | 0.0% | Rule churn; path filters help |
| `prettier/prettier` | B | queued | 4375 | 0 | 0.0% | Snapshot/fixture heavy |
| `mochajs/mocha` | B | queued | 1051 | 0 | 0.0% | Mid-size |
| `jquery/jquery` | B | queued | 496 | 0 | 0.0% | Legacy + docs |
| `webpack/webpack` | B | queued | 3320 | 0 | 0.0% | Complex; upper-B |
| `babel/babel` | B | queued | 3798 | 0 | 0.0% | Monorepo — stricter filters |
| `nestjs/nest` | B | queued | 2339 | 0 | 0.0% | TS coverage |
| `remix-run/react-router` | B | queued | 1179 | 0 | 0.0% | Was ReactTraining/react-router |
| `go-chi/chi` | B | queued | 153 | 0 | 0.0% | Complements Gin |
| `gorilla/mux` | B | queued | 162 | 0 | 0.0% | Maintenance-mode era still useful |
| `spf13/viper` | B | queued | 151 | 0 | 0.0% | After Cobra harvest |
| `urfave/cli` | B | queued | 481 | 0 | 0.0% | Diversity vs Cobra |
| `go-gorm/gorm` | B | queued | 365 | 0 | 0.0% |  |
| `etcd-io/etcd` | B | queued | 6092 | 0 | 0.0% | Large; near Tier C |
| `tokio-rs/tokio` | B | queued | 1669 | 0 | 0.0% | Multi-crate workspace |
| `hyperium/hyper` | B | queued | 913 | 0 | 0.0% |  |
| `actix/actix-web` | B | queued | 596 | 0 | 0.0% |  |
| `diesel-rs/diesel` | B | queued | 1096 | 0 | 0.0% |  |
| `rust-lang/mdBook` | B | queued | 551 | 0 | 0.0% | Smaller Rust target |
| `rust-lang/rust-clippy` | B | queued | 2825 | 0 | 0.0% | Many small lint PRs |
| `square/retrofit` | B | queued | TBD | 0 | — | Pairs with OkHttp; Search unavailable (422 / not searchable with token) |
| `google/gson` | B | queued | 203 | 0 | 0.0% | Focused |
| `google/guava` | B | queued | 286 | 0 | 0.0% | Large surface |
| `junit-team/junit4` | B | queued | 441 | 0 | 0.0% | Prefer junit4 over junit5 volume |
| `nlohmann/json` | B | queued | 408 | 0 | 0.0% | Header-heavy but GitHub PRs |
| `catchorg/Catch2` | B | queued | 404 | 0 | 0.0% |  |
| `protocolbuffers/protobuf` | B | queued | 2761 | 0 | 0.0% | Multi-language monorepo |
| `Alamofire/Alamofire` | B | queued | 479 | 0 | 0.0% | Swift coverage |
| `ReactiveX/RxSwift` | B | queued | 690 | 0 | 0.0% |  |
| `discourse/discourse` | B | queued | 9359 | 0 | 0.0% | App-scale Ruby before Rails |
| `Homebrew/brew` | B | queued | 5790 | 0 | 0.0% | Formula noise — code PRs only |
| `hashicorp/consul` | B | queued | 4529 | 0 | 0.0% | Upper-B / near C |
| `facebook/react` | C | queued | TBD | 0 | — | Monorepo; exclude bots; cap files/diff; Search unavailable (422 / not searchable with token) |
| `microsoft/vscode` | C | queued | 6016 | 0 | 0.0% | Huge volume; rate-limit time; extension noise |
| `kubernetes/kubernetes` | C | queued | 45430 | 0 | 0.0% | Massive; SIG bots; aggressive filters |
| `rails/rails` | C | queued | 17522 | 0 | 0.0% | Multi-gem monorepo |
| `spring-projects/spring-boot` | C | queued | 41 | 0 | 0.0% | After smaller JVM Tier B |
| `spring-projects/spring-framework` | C | queued | 610 | 0 | 0.0% |  |
| `golang/go` | C | queued | 0 | 0 | — | Some non-GitHub history |
| `rust-lang/rust` | C | queued | 31932 | 0 | 0.0% | Enormous; submodule/tooling noise |
| `rust-lang/cargo` | C | queued | 3499 | 0 | 0.0% | More tractable than rustc |
| `python/cpython` | C | queued | 19117 | 0 | 0.0% | Huge; many misc/doc PRs |
| `nodejs/node` | C | queued | 2738 | 0 | 0.0% | Core + deps noise |
| `numpy/numpy` | C | queued | 6993 | 0 | 0.0% |  |
| `scipy/scipy` | C | queued | 4954 | 0 | 0.0% |  |
| `pytorch/pytorch` | C | queued | 4299 | 0 | 0.0% | Monorepo; CUDA/build noise |
| `tensorflow/tensorflow` | C | queued | 11132 | 0 | 0.0% | Extreme monorepo risk |
| `huggingface/transformers` | C | queued | 3068 | 0 | 0.0% | Model card / docs heavy |
| `ansible/ansible` | C | queued | 32367 | 0 | 0.0% | Extreme volume — sample windows |
| `home-assistant/core` | C | queued | 21563 | 0 | 0.0% | Integration sprawl |
| `microsoft/TypeScript` | C | queued | 10230 | 0 | 0.0% | Compiler + tests huge |
| `angular/angular` | C | queued | 2918 | 0 | 0.0% |  |
| `vuejs/core` | C | queued | 1137 | 0 | 0.0% | Pre-2021 may be thinner |
| `vuejs/vue` | C | queued | 986 | 0 | 0.0% | Stronger pre-2021 history |
| `hashicorp/terraform` | C | queued | 8638 | 0 | 0.0% | Provider noise |
| `hashicorp/vault` | C | queued | 5633 | 0 | 0.0% |  |
| `prometheus/prometheus` | C | queued | 3460 | 0 | 0.0% |  |
| `grafana/grafana` | C | queued | 9530 | 0 | 0.0% | Frontend+backend |
| `elastic/elasticsearch` | C | queued | 34080 | 0 | 0.0% |  |
| `apache/kafka` | C | queued | 3713 | 0 | 0.0% |  |
| `apache/spark` | C | queued | 5 | 0 | 0.0% | Build-heavy |
| `electron/electron` | C | queued | 10822 | 0 | 0.0% |  |
| `facebook/react-native` | C | queued | TBD | 0 | — | Multi-platform monorepo; Search unavailable (422 / not searchable with token) |
| `flutter/flutter` | C | queued | 17877 | 0 | 0.0% | Engine + framework |
| `godotengine/godot` | C | queued | 13698 | 0 | 0.0% |  |
| `opencv/opencv` | C | queued | 9295 | 0 | 0.0% |  |
| `llvm/llvm-project` | C | queued | 1 | 0 | 0.0% | Monorepo extreme |
| `dotnet/runtime` | C | queued | 7360 | 0 | 0.0% |  |
| `dotnet/aspnetcore` | C | queued | 6700 | 0 | 0.0% |  |
| `JetBrains/kotlin` | C | queued | 1674 | 0 | 0.0% |  |
| `apple/swift` | C | queued | TBD | 0 | — | Partial GitHub mirror dynamics; Search unavailable (422 / not searchable with token) |
| `redis/redis` | C | queued | 1512 | 0 | 0.0% | Historically mixed contribution paths |
| `postgresql/postgres` | C | queued | TBD | 0 | — | Mailing-list heavy; sample only; Search unavailable (422 / not searchable with token) |
| `git/git` | C | queued | 2 | 0 | 0.0% | Mailing-list primary — low priority within C |
| `moby/moby` | C | queued | 16428 | 0 | 0.0% | Renames/history quirks |
| `docker/cli` | C | queued | 1607 | 0 | 0.0% | Smaller than engine |
| `helm/helm` | C | queued | 3041 | 0 | 0.0% | After smaller Go Tier A/B |
| `istio/istio` | C | queued | 13036 | 0 | 0.0% |  |
| `envoyproxy/envoy` | C | queued | 8088 | 0 | 0.0% |  |
| `clickhouse/clickhouse` | C | queued | 10490 | 0 | 0.0% |  |
| `pingcap/tidb` | C | queued | 13403 | 0 | 0.0% |  |
| `cockroachdb/cockroach` | C | queued | 25862 | 0 | 0.0% |  |

## Exclusions (not harvested as primary)

| repo_or_class | reason |
|---------------|--------|
| torvalds/linux | Mailing-list / patch-email primary; GitHub is not the real review surface |
| GNU / savannah GitHub mirrors | Incomplete PR history; mirror noise |
| awesome-* lists | Not product code; no meaningful patches |
| Pure documentation / book-only repos | Low ACE dual-exec value |
| sqlalchemy/sqlalchemy (early) | Only ~53 verified pre-2021 GitHub merges; history lived elsewhere |
| tiangolo/fastapi (early) | Search invalid/empty in this pass; rose late — verify before enqueue |
| chromium/chromium without filters | Volume + process mismatch for ACE v1 |
