# ACE-Bench corpus status

_Generated: **2026-09-23T02:51:29Z** (UTC)_

Per-repo GitHub Search `total_count` for `is:pr is:merged merged:<2021-01-01` vs rows in `human_patterns` (live DB + completed shards when present).

## Summary

| Metric | Value |
|--------|-------|
| Total harvested rows | **176637** |
| Repos with data | **66** / 1000 |
| Status: done | 66 |
| Status: harvesting | 1 |
| Status: queued / pending | 933 |
| Status: skipped | 0 |
| GitHub counts known | 144 / 1000 (sum of known = 573681) |
| Active harvest (log) | `ansible/ansible` |
| DB | `/home/arnavrastogi/ace-bench/data/ace_patterns.sqlite (+1 shard)` |
| Completed shards | 1 |
| Corpus JSON | `/home/arnavrastogi/ace-bench/data/corpus_repos.json` |
| Harvest log | `/home/arnavrastogi/ace-bench/data/corpus_harvest.log` |
| GitHub Search fetches this run | 0 |

**Done** when harvested &gt; 0 and harvest finished for the repo in logs, or coverage ≥ 95% of the GitHub count (or within ±5 PRs).

Refresh:

```bash
export ACE_DB_PATH=$HOME/ace-bench/data/ace_patterns.sqlite
python3 scripts/refresh_corpus_status.py --fetch-github
```

## Per-repo table

| repo | tier | status | github_pre2021 | harvested | coverage % | notes |
|------|------|--------|----------------|-----------|------------|-------|
| `django/django` | kickoff | done | 6125 | 6125 | 100.0% | See docs/CORPUS.md (frozen Django); coverage ≥95% of GitHub Search |
| `pallets/flask` | kickoff | done | 1054 | 1054 | 100.0% | Harvested into live ace_patterns.sqlite; skip re-queue; coverage ≥95% of GitHub Search |
| `expressjs/express` | kickoff | done | 196 | 196 | 100.0% | Harvested into live ace_patterns.sqlite; skip re-queue; coverage ≥95% of GitHub Search |
| `spf13/cobra` | kickoff | done | 343 | 343 | 100.0% | Harvested into live ace_patterns.sqlite; skip re-queue; coverage ≥95% of GitHub Search |
| `clap-rs/clap` | kickoff | done | 967 | 967 | 100.0% | Harvested into live ace_patterns.sqlite; skip re-queue; coverage ≥95% of GitHub Search |
| `psf/requests` | A | done | 1349 | 1247 | 92.4% | Best first post-batch target; finished_repo in harvest log |
| `encode/httpx` | A | done | 688 | 688 | 100.0% | Complements Requests; finished_repo in harvest log |
| `pydantic/pydantic` | A | done | 707 | 707 | 100.0% | v1-era pre-2021 useful; finished_repo in harvest log |
| `axios/axios` | A | done | 360 | 360 | 100.0% | Browser+Node patterns; finished_repo in harvest log |
| `reduxjs/redux` | A | done | 1353 | 1353 | 100.0% | Avoid redux-toolkit monorepo first; finished_repo in harvest log |
| `lodash/lodash` | A | done | 568 | 568 | 100.0% | Docs churn — filter path noise; finished_repo in harvest log |
| `gin-gonic/gin` | A | done | 652 | 652 | 100.0% | Strong PR culture; finished_repo in harvest log |
| `stretchr/testify` | A | done | 309 | 309 | 100.0% | High signal, low monorepo risk; finished_repo in harvest log |
| `sirupsen/logrus` | A | done | 374 | 374 | 100.0% | Mid volume; finished_repo in harvest log |
| `serde-rs/serde` | A | done | 527 | 527 | 100.0% | Often multi-crate; still tractable; finished_repo in harvest log |
| `BurntSushi/ripgrep` | A | done | 387 | 387 | 100.0% | Single-purpose, testable; finished_repo in harvest log |
| `sinatra/sinatra` | A | done | 625 | 533 | 85.3% | Ruby without Rails weight; finished_repo in harvest log |
| `square/okhttp` | A | queued | TBD | 0 | — | JVM + Kotlin mix; Search unavailable (422 / not searchable with token); Search unavailable (GitHub API 422 for https) |
| `fmtlib/fmt` | A | queued | 480 | 0 | 0.0% | Prefer over mailing-list C++ |
| `jekyll/jekyll` | A | queued | 2851 | 0 | 0.0% | Some docs-heavy PRs |
| `aio-libs/aiohttp` | B | queued | 2354 | 0 | 0.0% | Larger than Tier A HTTP libs |
| `scrapy/scrapy` | B | done | 1606 | 473 | 29.5% | Good issue linkage; finished_repo in harvest log |
| `celery/celery` | B | done | 1398 | 1321 | 94.5% | Multi-package layout; finished_repo in harvest log |
| `pytest-dev/pytest` | B | done | 3194 | 3194 | 100.0% | Plugin ecosystem noise; finished_repo in harvest log |
| `pallets/click` | B | done | 434 | 434 | 100.0% | Small, high quality; finished_repo in harvest log |
| `encode/django-rest-framework` | B | done | 2525 | 2501 | 99.0% | Complements frozen Django; finished_repo in harvest log |
| `HypothesisWorks/hypothesis` | B | done | 1412 | 1412 | 100.0% | Niche but clean; finished_repo in harvest log |
| `psf/black` | B | done | 462 | 462 | 100.0% | Style-only PRs — filter carefully; finished_repo in harvest log |
| `eslint/eslint` | B | done | 4609 | 4609 | 100.0% | Rule churn; path filters help; finished_repo in harvest log |
| `prettier/prettier` | B | done | 4375 | 4375 | 100.0% | Snapshot/fixture heavy; finished_repo in harvest log |
| `mochajs/mocha` | B | done | 1051 | 1029 | 97.9% | Mid-size; finished_repo in harvest log |
| `jquery/jquery` | B | done | 496 | 330 | 66.5% | Legacy + docs; finished_repo in harvest log |
| `webpack/webpack` | B | done | 3320 | 3320 | 100.0% | Complex; upper-B; finished_repo in harvest log |
| `babel/babel` | B | done | 3798 | 3798 | 100.0% | Monorepo — stricter filters; finished_repo in harvest log |
| `nestjs/nest` | B | done | 2339 | 2339 | 100.0% | TS coverage; finished_repo in harvest log |
| `remix-run/react-router` | B | done | 1179 | 1179 | 100.0% | Was ReactTraining/react-router; finished_repo in harvest log |
| `go-chi/chi` | B | done | 153 | 153 | 100.0% | Complements Gin; finished_repo in harvest log |
| `gorilla/mux` | B | done | 162 | 162 | 100.0% | Maintenance-mode era still useful; finished_repo in harvest log |
| `spf13/viper` | B | done | 151 | 151 | 100.0% | After Cobra harvest; finished_repo in harvest log |
| `urfave/cli` | B | done | 481 | 481 | 100.0% | Diversity vs Cobra; finished_repo in harvest log |
| `go-gorm/gorm` | B | done | 365 | 365 | 100.0% | finished_repo in harvest log |
| `etcd-io/etcd` | B | done | 6092 | 6092 | 100.0% | Large; near Tier C; finished_repo in harvest log |
| `tokio-rs/tokio` | B | done | 1669 | 1669 | 100.0% | Multi-crate workspace; finished_repo in harvest log |
| `hyperium/hyper` | B | done | 913 | 913 | 100.0% | finished_repo in harvest log |
| `actix/actix-web` | B | done | 596 | 596 | 100.0% | finished_repo in harvest log |
| `diesel-rs/diesel` | B | done | 1096 | 1096 | 100.0% | finished_repo in harvest log |
| `rust-lang/mdBook` | B | done | 551 | 551 | 100.0% | Smaller Rust target; finished_repo in harvest log |
| `rust-lang/rust-clippy` | B | done | 2825 | 2825 | 100.0% | Many small lint PRs; finished_repo in harvest log |
| `square/retrofit` | B | queued | TBD | 0 | — | Pairs with OkHttp; Search unavailable (422 / not searchable with token); Search unavailable (GitHub API 422 for https) |
| `google/gson` | B | queued | 203 | 0 | 0.0% | Focused |
| `google/guava` | B | queued | 286 | 0 | 0.0% | Large surface |
| `junit-team/junit4` | B | done | 441 | 331 | 75.1% | Prefer junit4 over junit5 volume; finished_repo in harvest log |
| `nlohmann/json` | B | done | 408 | 408 | 100.0% | Header-heavy but GitHub PRs; finished_repo in harvest log |
| `catchorg/Catch2` | B | done | 404 | 401 | 99.3% | finished_repo in harvest log |
| `protocolbuffers/protobuf` | B | done | 2761 | 2761 | 100.0% | Multi-language monorepo; finished_repo in harvest log |
| `Alamofire/Alamofire` | B | done | 479 | 479 | 100.0% | Swift coverage; finished_repo in harvest log |
| `ReactiveX/RxSwift` | B | done | 690 | 690 | 100.0% | finished_repo in harvest log |
| `discourse/discourse` | B | done | 9359 | 6353 | 67.9% | App-scale Ruby before Rails; finished_repo in harvest log |
| `Homebrew/brew` | B | done | 5790 | 5790 | 100.0% | Formula noise — code PRs only; finished_repo in harvest log |
| `hashicorp/consul` | B | done | 4529 | 4529 | 100.0% | Upper-B / near C; finished_repo in harvest log |
| `facebook/react` | C | queued | TBD | 0 | — | Monorepo; exclude bots; cap files/diff; Search unavailable (422 / not searchable with token); Search unavailable (GitHub API 422 for https) |
| `microsoft/vscode` | C | queued | 6016 | 0 | 0.0% | Huge volume; rate-limit time; extension noise |
| `kubernetes/kubernetes` | C | queued | 45430 | 0 | 0.0% | Massive; SIG bots; aggressive filters |
| `rails/rails` | C | done | 17522 | 2496 | 14.2% | Multi-gem monorepo; finished_repo in harvest log |
| `spring-projects/spring-boot` | C | done | 41 | 41 | 100.0% | After smaller JVM Tier B; finished_repo in harvest log |
| `spring-projects/spring-framework` | C | done | 610 | 609 | 99.8% | finished_repo in harvest log |
| `golang/go` | C | done | 0 | 0 | — | Some non-GitHub history; finished_repo in harvest log |
| `rust-lang/rust` | C | done | 31932 | 31827 | 99.7% | Enormous; submodule/tooling noise; finished_repo in harvest log |
| `rust-lang/cargo` | C | done | 3499 | 3499 | 100.0% | More tractable than rustc; finished_repo in harvest log |
| `python/cpython` | C | done | 19117 | 19117 | 100.0% | Huge; many misc/doc PRs; finished_repo in harvest log |
| `nodejs/node` | C | done | 2738 | 2738 | 100.0% | Core + deps noise; finished_repo in harvest log |
| `numpy/numpy` | C | done | 6993 | 6961 | 99.5% | finished_repo in harvest log |
| `scipy/scipy` | C | done | 4954 | 4936 | 99.6% | finished_repo in harvest log |
| `pytorch/pytorch` | C | done | 4299 | 4299 | 100.0% | Monorepo; CUDA/build noise; finished_repo in harvest log |
| `tensorflow/tensorflow` | C | done | 11132 | 11132 | 100.0% | Extreme monorepo risk; finished_repo in harvest log |
| `huggingface/transformers` | C | done | 3068 | 3068 | 100.0% | Model card / docs heavy; finished_repo in harvest log |
| `ansible/ansible` | C | harvesting | 32367 | 1952 | 6.0% | Extreme volume — sample windows; active in corpus_harvest.log |
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
| `facebook/react-native` | C | queued | TBD | 0 | — | Multi-platform monorepo; Search unavailable (422 / not searchable with token); Search unavailable (GitHub API 422 for https) |
| `flutter/flutter` | C | queued | 17877 | 0 | 0.0% | Engine + framework |
| `godotengine/godot` | C | queued | 13698 | 0 | 0.0% |  |
| `opencv/opencv` | C | queued | 9295 | 0 | 0.0% |  |
| `llvm/llvm-project` | C | queued | 1 | 0 | 0.0% | Monorepo extreme |
| `dotnet/runtime` | C | queued | 7360 | 0 | 0.0% |  |
| `dotnet/aspnetcore` | C | queued | 6700 | 0 | 0.0% |  |
| `JetBrains/kotlin` | C | queued | 1674 | 0 | 0.0% |  |
| `apple/swift` | C | queued | TBD | 0 | — | Partial GitHub mirror dynamics; Search unavailable (422 / not searchable with token); Search unavailable (GitHub API 422 for https) |
| `redis/redis` | C | queued | 1512 | 0 | 0.0% | Historically mixed contribution paths |
| `postgresql/postgres` | C | queued | TBD | 0 | — | Mailing-list heavy; sample only; Search unavailable (422 / not searchable with token); Search unavailable (GitHub API 422 for https) |
| `git/git` | C | queued | 2 | 0 | 0.0% | Mailing-list primary — low priority within C |
| `moby/moby` | C | queued | 16428 | 0 | 0.0% | Renames/history quirks |
| `docker/cli` | C | queued | 1607 | 0 | 0.0% | Smaller than engine |
| `helm/helm` | C | queued | 3041 | 0 | 0.0% | After smaller Go Tier A/B |
| `istio/istio` | C | queued | 13036 | 0 | 0.0% |  |
| `envoyproxy/envoy` | C | queued | 8088 | 0 | 0.0% |  |
| `clickhouse/clickhouse` | C | queued | 10490 | 0 | 0.0% |  |
| `pingcap/tidb` | C | queued | 13403 | 0 | 0.0% |  |
| `cockroachdb/cockroach` | C | queued | 25862 | 0 | 0.0% |  |
| `urllib3/urllib3` | D | queued | 969 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `python-pillow/Pillow` | D | queued | 2696 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `python-attrs/attrs` | D | queued | 233 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `tox-dev/tox` | D | queued | 601 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `pyca/cryptography` | D | queued | 3625 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `paramiko/paramiko` | D | queued | 121 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `benoitc/gunicorn` | D | queued | 529 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `kludex/uvicorn` | D | queued | 345 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `encode/starlette` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave; Search unavailable (GitHub API 422 for https) |
| `pallets/jinja` | D | queued | 374 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `pallets/werkzeug` | D | queued | 740 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `pallets/itsdangerous` | D | queued | 85 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `pallets/markupsafe` | D | queued | 77 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `sqlalchemy/sqlalchemy` | D | queued | 53 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `marshmallow-code/marshmallow` | D | queued | 573 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `python-jsonschema/jsonschema` | D | queued | 101 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `kevin1024/vcrpy` | D | queued | 184 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `freezegun/freezegun` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave; Search unavailable (GitHub API 422 for https) |
| `factoryboy/factory_boy` | D | queued | 234 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `pytest-dev/pytest-asyncio` | D | queued | 33 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `pytest-dev/pytest-xdist` | D | queued | 195 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `coveragepy/coveragepy` | D | queued | 65 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `nedbat/coveragepy` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave; Search unavailable (GitHub API 422 for https) |
| `python/mypy` | D | queued | 3461 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `astral-sh/ruff` | D | queued | 0 | 0 | — | Tier D backlog; queued after A–C wave |
| `PyCQA/flake8` | D | queued | 7 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `PyCQA/isort` | D | queued | 686 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `PyCQA/pylint` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave; Search unavailable (GitHub API 422 for https) |
| `PyCQA/bandit` | D | queued | 139 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `pre-commit/pre-commit` | D | queued | 632 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `python-poetry/poetry` | D | queued | 598 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `pypa/pip` | D | queued | 2877 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `pypa/setuptools` | D | queued | 522 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `pypa/wheel` | D | queued | 53 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `pypa/virtualenv` | D | queued | 646 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `pypa/twine` | D | queued | 320 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `sphinx-doc/sphinx` | D | queued | 2991 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `mkdocs/mkdocs` | D | queued | 624 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `Textualize/rich` | D | queued | 169 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `Textualize/textual` | D | queued | 0 | 0 | — | Tier D backlog; queued after A–C wave |
| `tqdm/tqdm` | D | queued | 221 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `psf/cachetools` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave; Search unavailable (GitHub API 422 for https) |
| `jaraco/keyring` | D | queued | 84 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `cherrypy/cherrypy` | D | queued | 136 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `bottlepy/bottle` | D | queued | 304 | 0 | 0.0% | Tier D backlog; queued after A–C wave |
| `falconry/falcon` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `sanic-org/sanic` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `tornadoweb/tornado` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `aio-libs/aioredis` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `redis/redis-py` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `mongodb/mongo-python-driver` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `elastic/elasticsearch-py` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `boto/boto3` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `aws/aws-cli` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `google/google-api-python-client` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `googleapis/google-cloud-python` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Azure/azure-sdk-for-python` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `huggingface/datasets` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `huggingface/accelerate` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `huggingface/tokenizers` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `explosion/spaCy` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `nltk/nltk` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `scikit-learn/scikit-learn` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `pandas-dev/pandas` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `matplotlib/matplotlib` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `plotly/plotly.py` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `pydata/xarray` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `dask/dask` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `streamlit/streamlit` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `gradio-app/gradio` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `PrefectHQ/prefect` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `apache/airflow` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `dagster-io/dagster` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `great-expectations/great_expectations` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `jazzband/django-debug-toolbar` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `django-commons/django-filter` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `encode/httpcore` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `python-websockets/websockets` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `SupervisedThinking/channels` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `django/channels` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `getmoto/moto` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `jonashaag/bjoern` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `uWSGI/uwsgi` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `gevent/gevent` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `eventlet/eventlet` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `python-greenlet/greenlet` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `MagicStack/uvloop` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `aio-libs/aiosignal` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `python-hyper/h11` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `python-hyper/h2` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `pgjones/hypercorn` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `emmett-framework/emmett` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `masoniteframework/masonite` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `beeware/toga` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `pyinstaller/pyinstaller` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `sindresorhus/got` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `node-fetch/node-fetch` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `request/request` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `visionmedia/superagent` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `ladjs/superagent` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `axios/axios-mock-adapter` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `expressjs/multer` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `expressjs/cors` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `expressjs/compression` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `expressjs/session` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `expressjs/body-parser` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `expressjs/serve-static` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `expressjs/morgan` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `expressjs/cookie-parser` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `koajs/koa` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `fastify/fastify` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `hapijs/hapi` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `socketio/socket.io` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `websockets/ws` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `mqttjs/MQTT.js` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `redis/node-redis` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `brianc/node-postgres` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `mysqljs/mysql` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `mongodb/node-mongodb-native` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `sequelize/sequelize` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `typeorm/typeorm` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `prisma/prisma` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `knex/knex` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Automattic/mongoose` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `jaredhanson/passport` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `auth0/node-jsonwebtoken` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `express-validator/express-validator` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `hapijs/joi` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `colinhacks/zod` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `ajv-validator/ajv` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `yargs/yargs` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `tj/commander.js` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `SBoudrias/Inquirer.js` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `chalk/chalk` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `sindresorhus/ora` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `debug-js/debug` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `winstonjs/winston` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `pinojs/pino` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `bunyan-logger/node-bunyan` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `trentm/node-bunyan` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `uuidjs/uuid` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `moment/moment` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `iamkun/dayjs` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `date-fns/date-fns` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `jashkenas/underscore` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `ramda/ramda` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `immutable-js/immutable-js` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `immerjs/immer` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `ReactiveX/rxjs` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `mobxjs/mobx` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `reduxjs/redux-thunk` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `reduxjs/reselect` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `remix-run/remix` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `vercel/next.js` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `nuxt/nuxt` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `sveltejs/svelte` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `sveltejs/kit` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `solidjs/solid` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `preactjs/preact` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `emberjs/ember.js` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `backbone/backbone` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `jashkenas/backbone` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `marionettejs/backbone.marionette` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Handlebars-Lang/handlebars.js` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `pugjs/pug` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `markedjs/marked` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `markdown-it/markdown-it` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `showdownjs/showdown` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `highlightjs/highlight.js` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `PrismJS/prism` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `microsoft/monaco-editor` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `quilljs/quill` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `facebook/draft-js` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `slatejs/slate` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `d3/d3` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `chartjs/Chart.js` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `apache/echarts` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `plotly/plotly.js` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `visjs/vis-network` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `cytoscape/cytoscape.js` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `mrdoob/three.js` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `BabylonJS/Babylon.js` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `pixijs/pixijs` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `phaserjs/phaser` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `webpack/webpack-dev-server` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `webpack/webpack-cli` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `rollup/rollup` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `evanw/esbuild` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `parcel-bundler/parcel` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `vitejs/vite` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `browserify/browserify` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `gulpjs/gulp` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `gruntjs/grunt` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `eslint/eslint-plugin-react` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `typescript-eslint/typescript-eslint` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `prettier/prettier-eslint` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `stylelint/stylelint` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `postcss/postcss` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `sass/sass` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `less/less.js` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `stylus/stylus` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `tailwindlabs/tailwindcss` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `styled-components/styled-components` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `emotion-js/emotion` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `css-modules/css-modules` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `facebook/jest` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `vitest-dev/vitest` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `jasmine/jasmine` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `karma-runner/karma` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `puppeteer/puppeteer` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `microsoft/playwright` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `SeleniumHQ/selenium` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `webdriverio/webdriverio` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `nx/nx` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `changesets/changesets` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `pnpm/pnpm` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `nvm-sh/nvm` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `jaredpalmer/formik` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `react-hook-form/react-hook-form` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `TanStack/query` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `TanStack/table` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `TanStack/router` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `apollographql/apollo-client` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `apollographql/apollo-server` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `prisma/prisma-engines` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `urql-graphql/urql` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `vuejs/pinia` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `vuejs/devtools` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `angular/angular-cli` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `angular/components` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `ngrx/platform` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `DefinitelyTyped/DefinitelyTyped` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `microsoft/TypeScript-DOM-lib-generator` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `libuv/libuv` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `joyent/libuv` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `taskforcesh/bullmq` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `google/closure-compiler` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `expo/expo` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `software-mansion/react-native-reanimated` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `software-mansion/react-native-gesture-handler` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `react-navigation/react-navigation` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Shopify/flash-list` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `callstack/react-native-paper` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `recharts/recharts` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `airbnb/visx` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `nivo/nivo` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `react-dnd/react-dnd` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `clauderic/dnd-kit` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `radix-ui/primitives` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `chakra-ui/chakra-ui` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `ant-design/ant-design` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `alibaba/ice` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `NervJS/taro` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Tencent/tdesign-react` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Shopify/polaris` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `primer/react` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `palantir/blueprint` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `react-bootstrap/react-bootstrap` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `bulma-css/bulma` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `jgthms/bulma` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `purecss/pure` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `necolas/normalize.css` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `sindresorhus/modern-normalize` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `go-yaml/yaml` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `BurntSushi/toml` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `pelletier/go-toml` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `spf13/afero` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `spf13/cast` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `spf13/jwalterweatherman` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `spf13/pflag` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `mitchellh/mapstructure` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `mitchellh/go-homedir` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `mitchellh/cli` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `hashicorp/hcl` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `hashicorp/go-multierror` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `hashicorp/go-retryablehttp` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `hashicorp/go-plugin` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `hashicorp/memberlist` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `hashicorp/raft` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `hashicorp/serf` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `hashicorp/nomad` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `hashicorp/packer` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `hashicorp/waypoint` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `hashicorp/boundary` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `hashicorp/terraform-provider-aws` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `golang/protobuf` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `protocolbuffers/protobuf-go` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `grpc/grpc-go` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `go-kit/kit` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `go-kratos/kratos` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `zeromicro/go-zero` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `labstack/echo` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `gofiber/fiber` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `gorilla/websocket` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `gorilla/sessions` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `gorilla/csrf` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `gorilla/handlers` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `gorilla/schema` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `go-chi/cors` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `go-chi/httplog` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `rs/cors` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `rs/zerolog` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `uber-go/zap` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `go-logr/logr` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `prometheus/client_golang` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `opentracing/opentracing-go` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `open-telemetry/opentelemetry-go` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `jaegertracing/jaeger` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `grafana/loki` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `grafana/tempo` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `grafana/mimir` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `influxdata/influxdb` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `influxdata/telegraf` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `victoriametrics/VictoriaMetrics` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `etcd-io/bbolt` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `syndtr/goleveldb` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `dgraph-io/badger` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `dgraph-io/dgraph` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `cockroachdb/pebble` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `go-redis/redis` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `redis/go-redis` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Shopify/sarama` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `segmentio/kafka-go` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `nats-io/nats.go` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `nats-io/nats-server` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `rabbitmq/amqp091-go` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `streadway/amqp` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `go-sql-driver/mysql` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `lib/pq` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `jackc/pgx` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `mattn/go-sqlite3` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `jmoiron/sqlx` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Masterminds/squirrel` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `volatiletech/sqlboiler` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `ent/ent` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `upper/db` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `pressly/goose` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `golang-migrate/migrate` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `rubenv/sql-migrate` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `ory/hydra` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `ory/kratos` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `ory/fosite` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `coreos/go-oidc` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `golang-jwt/jwt` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `dgrijalva/jwt-go` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `casbin/casbin` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `open-policy-agent/opa` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `dexidp/dex` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `keycloak/keycloak` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `go-playground/validator` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `asaskevich/govalidator` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `google/uuid` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `satori/go.uuid` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `oklog/ulid` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `google/go-cmp` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `onsi/ginkgo` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `onsi/gomega` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `golang/mock` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Kong/kong` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `osquery/osquery` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `elastic/logstash` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `fluent/fluent-bit` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `fluent/fluentd` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `vector-dev/vector` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `spinnaker/spinnaker` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `airbnb/aerosolve` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `microsoft/SynapseML` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `apache/groovy` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `facebook/Haxl` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `facebook/duckling` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Netflix/atlas` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `apache/openwhisk` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `phoenixframework/phoenix_live_view` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `apache/couchdb` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `apache/grails-core` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `symfony/css-selector` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `laravel/tinker` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `google/draco` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `laravel/lumen` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `symfony/routing` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `mozilla/sccache` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `github/scientist` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `facebook/litho` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `microsoft/Windows-driver-samples` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `microsoft/ailab` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `cloudflare/agentic-inbox` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `uber/RIBs` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Netflix/SimianArmy` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `apache/trafficserver` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `aws/amazon-q-developer-cli` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `microsoft/PowerApps-Samples` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `symfony/http-client-contracts` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `apple/swift-openapi-generator` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Shopify/identity_cache` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `BurntSushi/rust-csv` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `laravel/dusk` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Shopify/shopify_app` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `BurntSushi/erd` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `google/protobuf-gradle-plugin` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `apache/pekko` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `elixir-lang/ex_doc` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `apache/gluten` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `airbnb/okreplay` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Shopify/liquid` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `apache/predictionio` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `apache/apisix` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `facebook/fresco` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `square/picasso` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `JetBrains/compose-multiplatform` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `google/filament` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `JetBrains/intellij-community` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `apache/shardingsphere` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `microsoft/onnxruntime` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `google/ExoPlayer` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `apache/rocketmq` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `facebook/lexical` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Netflix/Hystrix` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `vuejs/devtools-v6` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `apache/skywalking` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `lukas-reineke/indent-blankline.nvim` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `sbt/sbt` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `exiftool/exiftool` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `dgiot/dgiot` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `bepass-org/oblivion` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `rrrene/credo` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `FluxML/Flux.jl` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `deckerst/aves` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `hledgerorg/hledger` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `scala-js/scala-js` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `blockscout/blockscout` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `digitallyinduced/ihp` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `stevearc/conform.nvim` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `fzyzcjy/flutter_rust_bridge` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `PathOfBuildingCommunity/PathOfBuilding` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `typelevel/cats` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `leoafarias/fvm` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `day8/re-frame` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `jiangtian616/JHenTai` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `christopheradams/elixir_style_guide` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `zio/zio` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `absinthe-graphql/absinthe` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `nvim-neo-tree/neo-tree.nvim` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `akinsho/toggleterm.nvim` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `tonsky/datascript` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `tuist/tuist` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `folke/noice.nvim` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `sindrets/diffview.nvim` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `weavejester/compojure` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `ben-manes/gradle-versions-plugin` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `commercialhaskell/stack` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `flutterchina/flukit` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `happi/theBeamBook` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `d2iq-archive/marathon` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `HujiangTechnology/gradle_plugin_android_aspectjx` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `TheHive-Project/TheHive` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `unclebob/swarm-forge` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `ring-clojure/ring` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `felixonmars/dnsmasq-china-list` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `jimsalterjrs/sanoid` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `ryanb/cancan` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `norman/friendly_id` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `input-output-hk/cardano-sl` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `scala/scala3` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `rundeck/rundeck` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `rsnapshot/rsnapshot` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `spotiflacapp/SpotiFLAC-Mobile` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `awslabs/deequ` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `vernemq/vernemq` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `lite-xl/lite-xl` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `hanami/hanami` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `namidaco/namida` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `guard/guard` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `ddclient/ddclient` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `twitter/scalding` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `ueberauth/guardian` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `joernio/joern` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `elixir-ecto/ecto` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `sdiehl/write-you-a-haskell` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `mamaral/Onboard` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `saghen/blink.cmp` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `adrienverge/openfortivpn` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `swisspol/GCDWebServer` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `swannodette/mori` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `curl/trurl` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `kezong/fat-aar-android` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `ghc/ghc` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `processone/ejabberd` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `ktlint/ktlint` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `GuidoBartoli/sherloq` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `AloneMonkey/MonkeyDev` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `igorwojda/android-showcase` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `jsonmodel/jsonmodel` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `pry/pry` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `sqitchers/sqitch` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `SciML/DifferentialEquations.jl` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `facebookarchive/xctool` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `MacPass/MacPass` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `sqldelight/sqldelight` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Difegue/LANraragi` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `folke/trouble.nvim` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `sergiotapia/magnetissimo` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `MortimerGoro/MGSwipeTableCell` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `mylxsw/aidea` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `xtdb/xtdb` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `quil/quil` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `gatling/gatling` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `qvacua/vimr` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Ji4n1ng/OpenInTerminal` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `ChenYilong/CYLTabBarController` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `haskell/haskell-language-server` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `CEWendel/SWTableViewCell` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Dimillian/IceCubesApp` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `louthy/language-ext` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Juanpe/About-SwiftUI` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `NancyFx/Nancy` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `sstephenson/bats` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `renzifeng/ZFPlayer` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `bhauman/lein-figwheel` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `jaspervdj/hakyll` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `jverdi/JVFloatLabeledTextField` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `hwdsl2/docker-ipsec-vpn-server` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `weavejester/hiccup` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `facebookarchive/three20` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `actuallymentor/battery` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `roundcube/roundcubemail` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Tencent/QMUI_iOS` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `alibaba/flutter_boost` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `satijalab/seurat` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `spiritLHLS/ecs` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `pedestal/pedestal` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `kean/Pulse` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `zetbaitsu/Compressor` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `thechangelog/changelog.com` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Prowlarr/Prowlarr` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `mojolicious/mojo` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `mfussenegger/nvim-dap` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `maderix/ANE` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `alibaba/fish-redux` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `OpenXiangShan/XiangShan` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `yesodweb/yesod` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `jfcoz/postgresqltuner` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `fideloper/TrustedProxy` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `AbdBarho/stable-diffusion-webui-docker` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `marcosgriselli/ViewAnimator` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `caiorss/Functional-Programming` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `plotly/plotly.R` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Moham3dRiahi/Th3inspector` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `WenchaoD/FSPagerView` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `nextcloud/docker` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `RicoSuter/NSwag` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `adamtornhill/code-maat` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `processone/tsung` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `google-deepmind/lab` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `rrousselGit/riverpod` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Col-E/Recaf` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `timvisee/ffsend` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `jerryscript-project/jerryscript` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `moodle/moodle` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `EcoPasteHub/EcoPaste` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `sebastianbergmann/php-text-template` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `gocd/gocd` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Droid-ify/client` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `xM4ddy/OFGB` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `enso-org/enso` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `phar-io/version` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `arkime/arkime` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `phar-io/manifest` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `lcobucci/jwt` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `r-lib/devtools` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `FastLED/FastLED` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `antirez/smallchat` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `TigerVNC/tigervnc` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `jepsen-io/jepsen` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `ash-project/ash` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `asciinema/asciinema-server` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Alex313031/thorium` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `ninenines/cowboy` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `phoboslab/qoi` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `opsnull/follow-me-install-kubernetes-cluster` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `swagger-api/swagger-core` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `koush/AndroidAsync` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `yihui/knitr` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Sequel-Ace/Sequel-Ace` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Lona/Lona` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `SwiftKickMobile/SwiftMessages` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `ithewei/libhv` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `d4rken-org/sdmaid-se` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `boa-dev/boa` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `lecho/hellocharts-android` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `veloren/veloren` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `flutter-team-archive/engine` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `imaNNeo/fl_chart` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `mullvad/mullvadvpn-app` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `mgdm/htmlq` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Kitura/Kitura` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `OpenMathLib/OpenBLAS` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `GenieFramework/Genie.jl` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `PureLayout/PureLayout` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `PHPOffice/PHPWord` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `ElectronNET/Electron.NET` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `logisim-evolution/logisim-evolution` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `htrgouvea/nipe` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `youki-dev/youki` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `j-hc/revanced-magisk-module` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `vipshop/vjtools` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Cenmrev/V2RayX` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `lballabio/QuantLib` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `rustls/rustls` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `ipkn/crow` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `chrisbanes/cheesesquare` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `P3TERX/Actions-OpenWrt` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `trello-archive/RxLifecycle` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `patchthecode/JTAppleCalendar` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `mob-sakai/UIEffect` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `mufeedvh/code2prompt` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `libfuse/sshfs` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `sschmid/Entitas` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `parcel-bundler/lightningcss` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `malcommac/SwiftDate` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `goldze/MVVMHabit` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `rovo89/Xposed` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `edgurgel/httpoison` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `ohmybash/oh-my-bash` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `guzzle/promises` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `zaphoyd/websocketpp` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `nginx-proxy/acme-companion` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `dotnet/wpf` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `thangchung/clean-code-dotnet` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `curl/everything-curl` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `prefix-dev/pixi` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `yaklang/yakit` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `MystenLabs/sui` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `thebookisclosed/ViVe` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `ever-co/ever-gauzy` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `2FastLabs/agent-squad` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `visualfc/liteide` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `traccar/traccar` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `idea4good/GuiLite` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `maharmstone/btrfs` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Laravel-Lang/lang` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `zhu1090093659/dsh-web` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `predis/predis` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `gsd-build/gsd-2` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `MinecraftForge/MinecraftForge` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `sahat/satellizer` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `pentacent/keila` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `sequinstream/sequin` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `panva/jose` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `MassTransit/MassTransit` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `ovh/the-bastion` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `bartobri/no-more-secrets` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `weolar/miniblink49` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `stride3d/stride` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `wang-xinyu/tensorrtx` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `rstudio/gt` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `DevinVinson/WordPress-Plugin-Boilerplate` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `octokit/octokit.js` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `digint/btrbk` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `doctrine/cache` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `alibaba/x-render` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `juliencrn/usehooks-ts` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `SimoneAvogadro/android-reverse-engineering-skill` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `arktypeio/arktype` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `svenstaro/miniserve` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `gilbarbara/react-joyride` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `ggerganov/ggwave` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Stengo/DeskPad` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `tsconfig/bases` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `elsa-workflows/elsa-core` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `JakeWharton/hugo` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `vrana/adminer` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `datahaven-xyz/datahaven` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `top-think/think` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `elm/compiler` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `puma/puma` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `shadowsocks/shadowsocks-qt5` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `toddwschneider/nyc-taxi-data` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `recastnavigation/recastnavigation` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `anse-app/chatgpt-demo` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `puppetlabs/puppet` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `warp-tech/warpgate` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `napi-rs/napi-rs` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `fujiapple852/trippy` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Flipboard/FLAnimatedImage` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `OpenCoworkAI/open-codesign` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `railsadminteam/rails_admin` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `haad/proxychains` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `fontforge/fontforge` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `osaurus-ai/osaurus` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `zeek/zeek` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `focus-creative-games/hybridclr` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `nst/iOS-Runtime-Headers` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Squirrel/Squirrel.Windows` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `longhorn/longhorn` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `ranile/gloo` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `mil-tokyo/webdnn` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `pravega/pravega` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `mchoe/SwiftSVG` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `keijiro/Klak` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Corvusoft/restbed` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `TypeStrong/fork-ts-checker-webpack-plugin` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `dahlia/logtape` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `justcoding121/titanium-web-proxy` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `charto/nbind` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `libharu/libharu` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `omnimind-ai/OmniBot` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `gorules/zen` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `fede1024/rust-rdkafka` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `slapperwan/gh4a` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `patterns-ai-core/langchainrb` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `win4r/AISuperDomain` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Codeusa/SteamCleaner` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Shmoopi/iOS-System-Services` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `opral/inlang` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `keeferrourke/la-capitaine-icon-theme` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `WireGuard/wireguard-linux` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `miroiu/nodify` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `mtrebi/memory-allocators` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `ardera/flutter-pi` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `thx/resvg-js` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `anomalyco/ion` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Ramotion/expanding-collection-android` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `eslint-stylistic/eslint-stylistic` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `willowtreeapps/Hyperion-Android` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `quickfix/quickfix` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `mfontanini/libtins` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `orangeduck/Corange` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `TrestleAdmin/trestle` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `oblitum/Interception` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `rangle/augury` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `mozilla-mobile/android-components` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `bsnes-emu/bsnes` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `hj01857655/kiro-account-manager` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `blend2d/blend2d` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `nfc-tools/libnfc` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `ejoy/ejoy2d` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `KyryloKuzyk/PrimeTween` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `sewenew/redis-plus-plus` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `rust-av/Av1an` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `zhegexiaohuozi/SeimiCrawler` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Cysharp/MessagePipe` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `folke/neodev.nvim` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `alibaba/compileflow` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Unity-Technologies/com.unity.multiplayer.samples.coop` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Tencent/sluaunreal` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `librats/rats-search` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Ramotion/fluid-slider` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `guanshuicheng/invoice` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `sil-org/ecs-deploy` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `validator/validator` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `AcademySoftwareFoundation/OpenTimelineIO` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `mborgerding/kissfft` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Fadi002/unshackle` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `pantor/inja` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `mewebstudio/Purifier` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Relm4/Relm4` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `brotandgames/ciao` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `OtterBrowser/otter-browser` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `patrikhuber/eos` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `malcommac/Hydra` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `ruyo/VRM4U` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `stclib/STC` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `j4mie/idiorm` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `h3xduck/TripleCross` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Start9Labs/start-technologies` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `myrtille-rdp/myrtille` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `drewm/mailchimp-api` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `arimger/Unity-Editor-Toolbox` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `openmm/openmm` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `chobits/ngx_http_proxy_connect_module` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `cossacklabs/themis` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `rafi/vim-config` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Macchina-CLI/macchina` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `shzlw/poli` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `TeamNewPipe/NewPipeExtractor` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `GIScience/openrouteservice` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `armcha/Space-Navigation-View` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `MichaelGrafnetter/DSInternals` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `lapce/lapdev` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `white-cat/ThinkAndroid` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `xamarin/XamarinComponents` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `facebookincubator/spectrum` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `beikeshop/beikeshop` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `sotrh/learn-wgpu` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `davidfantasy/mybatis-plus-generator-ui` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `dahliaOS/pangolin_desktop` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `stevearc/dressing.nvim` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `oetiker/SmokePing` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `itsjunetime/tdf` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `FriendsOfPHP/Sami` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `typelevel/scalacheck` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `r00t-3xp10it/venom` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `marin-m/SongRec` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `tobie/ua-parser` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `vhakulinen/gnvim` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `dotnet/dotNext` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `MahApps/MahApps.Metro.IconPacks` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `sangria-graphql/sangria` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `beam-community/bamboo` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Ragnt/AngryOxide` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `saket/InboxRecyclerView` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `fossasia/open-event-attendee-android` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `cimgui/cimgui` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `JohnTroony/php-webshells` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `openresty/lua-resty-redis` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `UnityTech/UIWidgets` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `thoughtbot/capybara-webkit` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `liuhaopen/UnityMMO` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `sauliusgrigaitis/Swifton` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `MortyFx/speedtest-x` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `BleuBleu/FamiStudio` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `marijnz/unity-toolbar-extender` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `snozbot/fungus` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `tweag/asterius` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `singro/v2ex` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `steipete/PSStackedView` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `dotnetcore/NPOI` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `williamboman/nvim-lsp-installer` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `aspnet/Identity` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `rtomayko/tilt` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `php-school/cli-menu` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `erichoracek/MSCollectionViewCalendarLayout` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `feathr-ai/feathr` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `JuliaAI/MLJ.jl` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Cosmo/TinyConsole` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Stichoza/google-translate-php` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `jeremyevans/rodauth` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `crazywhalecc/static-php-cli` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Flutter-Bounty-Hunters/super_editor` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `zalando/SwiftMonkey` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `SimformSolutionsPvtLtd/showcaseview` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `yob/pdf-reader` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `phpactor/phpactor` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `mix-php/mix` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `stevearc/overseer.nvim` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `brick/money` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `KasperskyLab/Kaspresso` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `facebookresearch/ResNeXt` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Hamza417/Inure` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `mtrudel/bandit` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `cognitect/transit-format` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Clean-Swift/CleanStore` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `indragiek/InAppViewDebugger` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Sky24n/flustars` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `gregnavis/active_record_doctor` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `cortinico/kotlin-android-template` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `gocardless/statesman` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Yalantis/PullToMakeSoup` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `RxSwiftCommunity/RxFlow` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `jivesoftware/PDTSimpleCalendar` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `wbthomason/packer.nvim` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Codeux-Software/Textual` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `toptal/chewy` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `ingbyr/vdm` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `fossasia/susi_iOS` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `intellij-elixir/intellij-elixir` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `tyron12233/CodeAssist` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `Sub6Resources/flutter_html` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `mochi/mochiweb` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `biokoda/actordb` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `massivemadness/Squircle-CE` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `replikativ/datahike` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `fluttercommunity/plus_plugins` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `anmonteiro/lumo` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `ptrpaws/Oculess` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `mikavilpas/yazi.nvim` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `nvim-lualine/lualine.nvim` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `walmartlabs/lacinia` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `agentjido/jido` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `clj-kondo/clj-kondo` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `byzer-org/byzer-lang` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `dakrone/clj-http` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `angulardart/angular` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `erlang/rebar3` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `media-kit/media-kit` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `JHubi1/ollama-app` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `bitwalker/timex` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `elixir-wallaby/wallaby` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `elixir-desktop/desktop` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `taoensso/sente` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `nccgroup/sobelow` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `entronad/graphic` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `iampawan/Flutter-Music-Player` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `syncfusion/flutter-widgets` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `olivierverdier/zsh-git-prompt` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `elixir-lsp/elixir-ls` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `scotty-web/scotty` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `metosin/malli` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `esl/MongooseIM` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |
| `foundweekends/giter8` | D | queued | TBD | 0 | — | Tier D backlog; queued after A–C wave |

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
