# Eval batch ~100 — stub agents vs human-replay

_Generated 2026-09-25T17:33:05Z (UTC)._

## Disclaimer

**`stub-default` and `stub-bloated` are synthetic harness agents**, not LLM products. They exist to exercise ACE / drift / churn / craft plumbing and to illustrate over-surgical vs sprawl failure modes. **`human-replay`** (`--agent file`) replays the stored human PR patch and should score ACE ≈ 1.0 (and craft ≈ 1.0 in thorough mode). This batch was run **offline** (`--skip-sandbox`) with **no paid API calls** unless noted below.

- Paid LLM sample: **no**
- Eval mode: `thorough`
- Instances: **100** (jsonl=50, db-pad=50)
- Successful runs: **300** / 300 (failures: 0)
- Harvest DB: `/Users/rachitkumarrastogi/github/Startup/rachit/ace-bench/data/frozen/ace_patterns_django_pre2021_6125.sqlite`
- Eval runs DB: `/Users/rachitkumarrastogi/ace-bench-data/eval_runs.sqlite`
- Human patches dir: `/Users/rachitkumarrastogi/ace-bench-data/eval_batch/human_patches`
- Agent patch / AGENT_PR.md dir: `/Users/rachitkumarrastogi/ace-bench-data/eval_batch/agent_patches`

## Headline stats (medians)

| Model | n | median ACE | p10 ACE | p90 ACE | median drift | median churn | median craft |
|-------|---|------------|---------|---------|--------------|--------------|--------------|
| `human-replay` | 100 | 1.0000 | 1.0000 | 1.0000 | 0.0 | 1.0000 | 1.0000 |
| `stub-bloated` | 100 | 0.3899 | 0.0265 | 1.9875 | 8.0 | 2.1013 | 0.0000 |
| `stub-default` | 100 | 131.0000 | 8.9000 | 667.8000 | 5.0 | 0.0250 | 0.0000 |

### How to read the numbers

- **ACE ≈ 1**: agent patch size×files matches the human patch for that PR.
- **ACE ≫ 1** (`stub-default`): tiny stub vs real human — *over-surgical* vs baseline.
- **ACE ≪ 1** (`stub-bloated`): multi-file sprawl vs surgical human — *bloat*.
- **file_drift**: symmetric set difference of touched paths (|F_A Δ F_H|).
- **craft** (thorough only): path/line/symbol overlap shape similarity (not correctness).

## Where humans shine

Human-replay reached ACE = 1.0 on **100 / 100** successful instances (identical stored patch). Representative links:

| Instance | PR | ACE | craft | patch / AGENT_PR |
|----------|----|-----|-------|------------------|
| `django/django#22` | [22](https://github.com/django/django/pull/22) | 1.0000 | 1.0000 | `django__django__22__human-replay.patch` / `—` |
| `django/django#216` | [216](https://github.com/django/django/pull/216) | 1.0000 | 1.0000 | `django__django__216__human-replay.patch` / `—` |
| `django/django#494` | [494](https://github.com/django/django/pull/494) | 1.0000 | 1.0000 | `django__django__494__human-replay.patch` / `—` |
| `django/django#94` | [94](https://github.com/django/django/pull/94) | 1.0000 | 1.0000 | `django__django__94__human-replay.patch` / `—` |
| `django/django#357` | [357](https://github.com/django/django/pull/357) | 1.0000 | 1.0000 | `django__django__357__human-replay.patch` / `—` |
| `django/django#16` | [16](https://github.com/django/django/pull/16) | 1.0000 | 1.0000 | `django__django__16__human-replay.patch` / `—` |
| `django/django#25` | [25](https://github.com/django/django/pull/25) | 1.0000 | 1.0000 | `django__django__25__human-replay.patch` / `—` |
| `django/django#751` | [751](https://github.com/django/django/pull/751) | 1.0000 | 1.0000 | `django__django__751__human-replay.patch` / `—` |
| `django/django#109` | [109](https://github.com/django/django/pull/109) | 1.0000 | 1.0000 | `django__django__109__human-replay.patch` / `—` |
| `django/django#283` | [283](https://github.com/django/django/pull/283) | 1.0000 | 1.0000 | `django__django__283__human-replay.patch` / `—` |
| `django/django#642` | [642](https://github.com/django/django/pull/642) | 1.0000 | 1.0000 | `django__django__642__human-replay.patch` / `—` |
| `django/django#123` | [123](https://github.com/django/django/pull/123) | 1.0000 | 1.0000 | `django__django__123__human-replay.patch` / `—` |
| `django/django#218` | [218](https://github.com/django/django/pull/218) | 1.0000 | 1.0000 | `django__django__218__human-replay.patch` / `—` |
| `django/django#958` | [958](https://github.com/django/django/pull/958) | 1.0000 | 1.0000 | `django__django__958__human-replay.patch` / `—` |
| `django/django#817` | [817](https://github.com/django/django/pull/817) | 1.0000 | 1.0000 | `django__django__817__human-replay.patch` / `—` |
| `django/django#972` | [972](https://github.com/django/django/pull/972) | 1.0000 | 1.0000 | `django__django__972__human-replay.patch` / `—` |
| `django/django#690` | [690](https://github.com/django/django/pull/690) | 1.0000 | 1.0000 | `django__django__690__human-replay.patch` / `—` |
| `django/django#360` | [360](https://github.com/django/django/pull/360) | 1.0000 | 1.0000 | `django__django__360__human-replay.patch` / `—` |
| `django/django#809` | [809](https://github.com/django/django/pull/809) | 1.0000 | 1.0000 | `django__django__809__human-replay.patch` / `—` |
| `django/django#159` | [159](https://github.com/django/django/pull/159) | 1.0000 | 1.0000 | `django__django__159__human-replay.patch` / `—` |

_…and 80 more with ACE=1.0._

## Where stub agents “tank”

Synthetic stubs are **designed** to miss human shape. `stub-default` rows farthest from ACE=1 (typically **ACE ≫ 1**, high path drift, near-zero craft):

| Instance | PR | ACE | drift | churn | craft |
|----------|----|-----|-------|-------|-------|
| `django/django#807` | [PR](https://github.com/django/django/pull/807) | 2705.0000 | 6 | 0.0009 | 0.0000 |
| `django/django#3885` | [PR](https://github.com/django/django/pull/3885) | 1632.0000 | 9 | 0.0045 | 0.0000 |
| `django/django#1443` | [PR](https://github.com/django/django/pull/1443) | 1608.0000 | 9 | 0.0029 | 0.0000 |
| `django/django#3879` | [PR](https://github.com/django/django/pull/3879) | 1552.0000 | 9 | 0.0047 | 0.0000 |
| `django/django#817` | [PR](https://github.com/django/django/pull/817) | 847.0000 | 8 | 0.0081 | 0.0000 |
| `django/django#3220` | [PR](https://github.com/django/django/pull/3220) | 832.0000 | 9 | 0.0057 | 0.0000 |
| `django/django#1166` | [PR](https://github.com/django/django/pull/1166) | 763.0000 | 8 | 0.0072 | 0.0000 |
| `django/django#3293` | [PR](https://github.com/django/django/pull/3293) | 700.0000 | 8 | 0.0078 | 0.0000 |
| `django/django#2736` | [PR](https://github.com/django/django/pull/2736) | 690.0000 | 7 | 0.0076 | 0.0000 |
| `django/django#1084` | [PR](https://github.com/django/django/pull/1084) | 684.0000 | 7 | 0.0074 | 0.0000 |
| `django/django#1582` | [PR](https://github.com/django/django/pull/1582) | 666.0000 | 7 | 0.0076 | 0.0000 |
| `django/django#4107` | [PR](https://github.com/django/django/pull/4107) | 623.0000 | 8 | 0.0056 | 0.0000 |
| `django/django#2468` | [PR](https://github.com/django/django/pull/2468) | 584.0000 | 9 | 0.0081 | 0.0000 |
| `django/django#1799` | [PR](https://github.com/django/django/pull/1799) | 574.0000 | 8 | 0.0115 | 0.0000 |
| `django/django#4303` | [PR](https://github.com/django/django/pull/4303) | 568.0000 | 9 | 0.0135 | 0.0000 |

### Contrast: human ACE=1 vs stub-default (largest |log₁₀ ACE|)

| Instance | PR | human ACE | stub ACE | stub drift | stub craft |
|----------|----|-----------|----------|------------|------------|
| `django/django#807` | [PR](https://github.com/django/django/pull/807) | 1.0000 | 2705.0000 | 6 | 0.0000 |
| `django/django#3885` | [PR](https://github.com/django/django/pull/3885) | 1.0000 | 1632.0000 | 9 | 0.0000 |
| `django/django#1443` | [PR](https://github.com/django/django/pull/1443) | 1.0000 | 1608.0000 | 9 | 0.0000 |
| `django/django#3879` | [PR](https://github.com/django/django/pull/3879) | 1.0000 | 1552.0000 | 9 | 0.0000 |
| `django/django#817` | [PR](https://github.com/django/django/pull/817) | 1.0000 | 847.0000 | 8 | 0.0000 |
| `django/django#3220` | [PR](https://github.com/django/django/pull/3220) | 1.0000 | 832.0000 | 9 | 0.0000 |
| `django/django#1166` | [PR](https://github.com/django/django/pull/1166) | 1.0000 | 763.0000 | 8 | 0.0000 |
| `django/django#3293` | [PR](https://github.com/django/django/pull/3293) | 1.0000 | 700.0000 | 8 | 0.0000 |
| `django/django#2736` | [PR](https://github.com/django/django/pull/2736) | 1.0000 | 690.0000 | 7 | 0.0000 |
| `django/django#1084` | [PR](https://github.com/django/django/pull/1084) | 1.0000 | 684.0000 | 7 | 0.0000 |
| `django/django#1582` | [PR](https://github.com/django/django/pull/1582) | 1.0000 | 666.0000 | 7 | 0.0000 |
| `django/django#4107` | [PR](https://github.com/django/django/pull/4107) | 1.0000 | 623.0000 | 8 | 0.0000 |

## Bloat — `stub-bloated` vs human

`--stub-bloated` emits multi-file sprawl. Expect **ACE ≪ 1**, high path drift, and **low craft** vs the same-PR human patch.

| Metric | human-replay | stub-bloated |
|--------|--------------|--------------|
| median ACE | 1.0000 | 0.3899 |
| median drift | 0.0 | 8.0 |
| median craft | 1.0000 | 0.0000 |
| median churn | 1.0000 | 2.1013 |

Lowest craft / ACE bloated runs:

| Instance | PR | ACE | drift | craft | AGENT_PR / patch |
|----------|----|-----|-------|-------|------------------|
| `django/django#690` | [PR](https://github.com/django/django/pull/690) | 0.0030 | 5 | 0.0000 | `—` / `django__django__690__stub-bloated.patch` |
| `django/django#864` | [PR](https://github.com/django/django/pull/864) | 0.0030 | 5 | 0.0000 | `—` / `django__django__864__stub-bloated.patch` |
| `django/django#1622` | [PR](https://github.com/django/django/pull/1622) | 0.0030 | 5 | 0.0000 | `—` / `django__django__1622__stub-bloated.patch` |
| `django/django#109` | [PR](https://github.com/django/django/pull/109) | 0.0060 | 5 | 0.0000 | `—` / `django__django__109__stub-bloated.patch` |
| `django/django#1088` | [PR](https://github.com/django/django/pull/1088) | 0.0060 | 5 | 0.0000 | `—` / `django__django__1088__stub-bloated.patch` |
| `django/django#1616` | [PR](https://github.com/django/django/pull/1616) | 0.0060 | 5 | 0.0000 | `—` / `django__django__1616__stub-bloated.patch` |
| `django/django#1143` | [PR](https://github.com/django/django/pull/1143) | 0.0089 | 5 | 0.0000 | `—` / `django__django__1143__stub-bloated.patch` |
| `django/django#1743` | [PR](https://github.com/django/django/pull/1743) | 0.0149 | 5 | 0.0000 | `—` / `django__django__1743__stub-bloated.patch` |
| `django/django#791` | [PR](https://github.com/django/django/pull/791) | 0.0238 | 6 | 0.0000 | `—` / `django__django__791__stub-bloated.patch` |
| `django/django#1232` | [PR](https://github.com/django/django/pull/1232) | 0.0268 | 7 | 0.0000 | `—` / `django__django__1232__stub-bloated.patch` |
| `django/django#1178` | [PR](https://github.com/django/django/pull/1178) | 0.0268 | 5 | 0.0000 | `—` / `django__django__1178__stub-bloated.patch` |
| `django/django#216` | [PR](https://github.com/django/django/pull/216) | 0.0298 | 6 | 0.0000 | `—` / `django__django__216__stub-bloated.patch` |
| `django/django#466` | [PR](https://github.com/django/django/pull/466) | 0.0298 | 6 | 0.0000 | `—` / `django__django__466__stub-bloated.patch` |
| `django/django#1127` | [PR](https://github.com/django/django/pull/1127) | 0.0327 | 5 | 0.0000 | `—` / `django__django__1127__stub-bloated.patch` |
| `django/django#22` | [PR](https://github.com/django/django/pull/22) | 0.0446 | 5 | 0.0000 | `—` / `django__django__22__stub-bloated.patch` |

## Per-instance index (all selected)

GitHub PR URLs use `https://github.com/{repo}/pull/{n}`. Local artifacts under `/Users/rachitkumarrastogi/ace-bench-data/eval_batch/agent_patches` (filenames like `django__django__{n}__{model}.patch` and `AGENT_PR.md` when not suppressed).

| # | Instance | source | PR | title (truncated) |
|---|----------|--------|----|-----------------|
| 1 | `django/django#22` | jsonl | [#22](https://github.com/django/django/pull/22) | Added regression test for #17967. |
| 2 | `django/django#216` | jsonl | [#216](https://github.com/django/django/pull/216) | Fixed #18644 -- Made urlize trim trailing period followed… |
| 3 | `django/django#494` | jsonl | [#494](https://github.com/django/django/pull/494) | model_split: Fixed #19236 - fixed error for abstract mode… |
| 4 | `django/django#94` | jsonl | [#94](https://github.com/django/django/pull/94) | Fixed #18393 -- Prevented blocktrans to crash when a vari… |
| 5 | `django/django#357` | jsonl | [#357](https://github.com/django/django/pull/357) | Remove Admin's swallowing of AttributeError (#16655, #185… |
| 6 | `django/django#16` | jsonl | [#16](https://github.com/django/django/pull/16) | Made table_names() output sorted. |
| 7 | `django/django#25` | jsonl | [#25](https://github.com/django/django/pull/25) | Made get_indexes() consistent across backends. |
| 8 | `django/django#751` | jsonl | [#751](https://github.com/django/django/pull/751) | Use `token.split_contents()` in tags that can take variab… |
| 9 | `django/django#109` | jsonl | [#109](https://github.com/django/django/pull/109) | Fix test error. |
| 10 | `django/django#283` | jsonl | [#283](https://github.com/django/django/pull/283) | Fixed #18779 -- URLValidator can't validate url with ipv6. |
| 11 | `django/django#642` | jsonl | [#642](https://github.com/django/django/pull/642) | Send post_delete signals immediately |
| 12 | `django/django#123` | jsonl | [#123](https://github.com/django/django/pull/123) | Don't escape object ids when passing to the contenttypes.… |
| 13 | `django/django#218` | jsonl | [#218](https://github.com/django/django/pull/218) | BaseCache now has a no-op close method as per ticket #18582 |
| 14 | `django/django#958` | jsonl | [#958](https://github.com/django/django/pull/958) | Fixed #20138 -- Added BCryptSHA256PasswordHasher |
| 15 | `django/django#817` | jsonl | [#817](https://github.com/django/django/pull/817) | Add sqldropindexes to manage |
| 16 | `django/django#972` | jsonl | [#972](https://github.com/django/django/pull/972) | Fixed spelling errors |
| 17 | `django/django#690` | jsonl | [#690](https://github.com/django/django/pull/690) | Fixed #19711 -- Typo in __all__ declaration in django/tes… |
| 18 | `django/django#360` | jsonl | [#360](https://github.com/django/django/pull/360) | Ticket #12836 - Added a test to assure permalink wraps me… |
| 19 | `django/django#809` | jsonl | [#809](https://github.com/django/django/pull/809) | Fixed #19526 |
| 20 | `django/django#159` | jsonl | [#159](https://github.com/django/django/pull/159) | Fixed GIS testsuite. |
| 21 | `django/django#546` | jsonl | [#546](https://github.com/django/django/pull/546) | Fixed #19325 -- Make E-Mail Connection Overridable in Adm… |
| 22 | `django/django#1084` | jsonl | [#1084](https://github.com/django/django/pull/1084) | Fixed #13546 -- Easier handling of localize field options… |
| 23 | `django/django#1081` | jsonl | [#1081](https://github.com/django/django/pull/1081) | Enable the use of any two item iterable within an iterabl… |
| 24 | `django/django#1443` | jsonl | [#1443](https://github.com/django/django/pull/1443) | Fixed #20867 -- Added the Form.add_error() method. |
| 25 | `django/django#847` | jsonl | [#847](https://github.com/django/django/pull/847) | Fixed #18176 -- Added test for year lookups with year < 1000 |
| 26 | `django/django#456` | jsonl | [#456](https://github.com/django/django/pull/456) | Fixed #19151 -- Added missing methods to EmptyQuerySet. |
| 27 | `django/django#819` | jsonl | [#819](https://github.com/django/django/pull/819) | Fixed #16302 -- Ensure contrib.comments is IPv6 capable |
| 28 | `django/django#288` | jsonl | [#288](https://github.com/django/django/pull/288) | Fixed #3542 -- Add support for changing granularity on Ar… |
| 29 | `django/django#796` | jsonl | [#796](https://github.com/django/django/pull/796) | Fixes #17866: Vary: Accept-Language header when language … |
| 30 | `django/django#1245` | jsonl | [#1245](https://github.com/django/django/pull/1245) | Fixed #19080 -- Fine-grained control over select_related … |
| 31 | `django/django#1166` | jsonl | [#1166](https://github.com/django/django/pull/1166) | Fixed #15961 -- Added get_search_results to ModelAdmin |
| 32 | `django/django#2468` | jsonl | [#2468](https://github.com/django/django/pull/2468) | Deal with connection close (client- or server-initiated) … |
| 33 | `django/django#864` | jsonl | [#864](https://github.com/django/django/pull/864) | use the real path to fix OS X /var/folders vs /private/va… |
| 34 | `django/django#444` | jsonl | [#444](https://github.com/django/django/pull/444) | Allow reversed iteration over SortedDict. |
| 35 | `django/django#717` | jsonl | [#717](https://github.com/django/django/pull/717) | Fixed #19746 -- Allow deserialization of pk-less data |
| 36 | `django/django#467` | jsonl | [#467](https://github.com/django/django/pull/467) | Add 'page_kwarg' attribute to `MultipleObjectMixin`, remo… |
| 37 | `django/django#778` | jsonl | [#778](https://github.com/django/django/pull/778) | Fixed #19609: admin Inlines doesn't display help_text for… |
| 38 | `django/django#1280` | jsonl | [#1280](https://github.com/django/django/pull/1280) | Fixed #20079 -- Improve security of password reset tokens |
| 39 | `django/django#1799` | jsonl | [#1799](https://github.com/django/django/pull/1799) | Fixed #9523 -- Restart runserver after translation MO fil… |
| 40 | `django/django#2775` | jsonl | [#2775](https://github.com/django/django/pull/2775) | Gave unique names to SpatialRefSysModels. |
| 41 | `django/django#1088` | jsonl | [#1088](https://github.com/django/django/pull/1088) | #20432: Fix for GroupAdmin test |
| 42 | `django/django#495` | jsonl | [#495](https://github.com/django/django/pull/495) | Fixed #18949 -- Improve performance of model_to_dict with… |
| 43 | `django/django#931` | jsonl | [#931](https://github.com/django/django/pull/931) | Fixed #20088 -- Changed get_admin_log not to depend on Us… |
| 44 | `django/django#1083` | jsonl | [#1083](https://github.com/django/django/pull/1083) | Fixes #20235 - MultipleObjectMixin requires object_list i… |
| 45 | `django/django#824` | jsonl | [#824](https://github.com/django/django/pull/824) | Fixes #19763 - LocaleMiddleware should check for supporte… |
| 46 | `django/django#1582` | jsonl | [#1582](https://github.com/django/django/pull/1582) | Fixed #12756: Improved error message when yaml module is … |
| 47 | `django/django#2692` | jsonl | [#2692](https://github.com/django/django/pull/2692) | #22667 replaced occurrences of master/slave terminology w… |
| 48 | `django/django#3045` | jsonl | [#3045](https://github.com/django/django/pull/3045) | Fixed #23269 -- Deprecated django.utils.remove_tags() and… |
| 49 | `django/django#1127` | jsonl | [#1127](https://github.com/django/django/pull/1127) | Fixed #20142 -- Added error handling for fixture setup |
| 50 | `django/django#490` | jsonl | [#490](https://github.com/django/django/pull/490) | Fixed #18210 -- Escaped special characters in reverse pre… |
| 51 | `django/django#1143` | db | [#1143](https://github.com/django/django/pull/1143) | A simple docstring to clarify a part of the code that mig… |
| 52 | `django/django#466` | db | [#466](https://github.com/django/django/pull/466) | #19025 Add `form` to formwizard context (includes tests) |
| 53 | `django/django#943` | db | [#943](https://github.com/django/django/pull/943) | Added some class attributes to pass initial form lists to… |
| 54 | `django/django#1116` | db | [#1116](https://github.com/django/django/pull/1116) | Ticket 20234 20236 |
| 55 | `django/django#807` | db | [#807](https://github.com/django/django/pull/807) | Fixed #12674 -- provide a way to override admin validation |
| 56 | `django/django#2736` | db | [#2736](https://github.com/django/django/pull/2736) | Fixed #22725 - Migration.run_before does nothing |
| 57 | `django/django#3293` | db | [#3293](https://github.com/django/django/pull/3293) | Fixed #15089 -- Allowed contrib.sites to lookup the curre… |
| 58 | `django/django#3220` | db | [#3220](https://github.com/django/django/pull/3220) | #22340  -- Moved more DDL to schema editors |
| 59 | `django/django#1178` | db | [#1178](https://github.com/django/django/pull/1178) | Fix for test failure |
| 60 | `django/django#573` | db | [#573](https://github.com/django/django/pull/573) | #19070 urlize template filter raises exception in some cases |
| 61 | `django/django#1062` | db | [#1062](https://github.com/django/django/pull/1062) | Recommend using the bcrypt library instead of py-bcrypt |
| 62 | `django/django#1134` | db | [#1134](https://github.com/django/django/pull/1134) | Fixed #18990: Loaddata now complains if fixture doesn't e… |
| 63 | `django/django#1294` | db | [#1294](https://github.com/django/django/pull/1294) | Fixed #18872 -- Added prefix to FormMixin |
| 64 | `django/django#2992` | db | [#2992](https://github.com/django/django/pull/2992) | Fixed #23074 -- Avoided leaking savepoints in atomic. |
| 65 | `django/django#3884` | db | [#3884](https://github.com/django/django/pull/3884) | Fixed #17785 -- Preferred column names in get_relations i… |
| 66 | `django/django#3885` | db | [#3885](https://github.com/django/django/pull/3885) | Fixed #24118 -- Added --debug-sql option for tests. |
| 67 | `django/django#1194` | db | [#1194](https://github.com/django/django/pull/1194) | Fixed a Python 2.6 regression (GzipFile can't act as a co… |
| 68 | `django/django#769` | db | [#769](https://github.com/django/django/pull/769) | Fixed #19816: pre-evaluate queryset on m2m set |
| 69 | `django/django#1147` | db | [#1147](https://github.com/django/django/pull/1147) | Added TransRealMixin to fix i18n global state pollution i… |
| 70 | `django/django#1152` | db | [#1152](https://github.com/django/django/pull/1152) | Fixed #11915: generic Accept-Language matches country-spe… |
| 71 | `django/django#1515` | db | [#1515](https://github.com/django/django/pull/1515) | Fixed #20972 -- Make messages cookie follow session cooki… |
| 72 | `django/django#3403` | db | [#3403](https://github.com/django/django/pull/3403) | Removed unneeded override_system_checks |
| 73 | `django/django#4107` | db | [#4107](https://github.com/django/django/pull/4107) | Refs #14030 -- Improved expression support for python values |
| 74 | `django/django#3879` | db | [#3879](https://github.com/django/django/pull/3879) | Fixed #9893 -- Allowed using a field's max_length in the … |
| 75 | `django/django#1616` | db | [#1616](https://github.com/django/django/pull/1616) | Fixed failing test introduced by 87d2750b39. |
| 76 | `django/django#777` | db | [#777](https://github.com/django/django/pull/777) | Fixed #19811 - Added language code fallback in get_langua… |
| 77 | `django/django#1094` | db | [#1094](https://github.com/django/django/pull/1094) | Fix for Ticket #11160 |
| 78 | `django/django#1181` | db | [#1181](https://github.com/django/django/pull/1181) | Changed API to disable ATOMIC_REQUESTS per view. |
| 79 | `django/django#1579` | db | [#1579](https://github.com/django/django/pull/1579) | Fix debug view blowing up when a template is not given to… |
| 80 | `django/django#3718` | db | [#3718](https://github.com/django/django/pull/3718) | Fixed #23982 -- Added doc note on generating Python 2/3 c… |
| 81 | `django/django#4502` | db | [#4502](https://github.com/django/django/pull/4502) | Fixed #24595 -- Prevented loss of null info in MySQL fiel… |
| 82 | `django/django#4161` | db | [#4161](https://github.com/django/django/pull/4161) | Set context.template instead of context.engine while rend… |
| 83 | `django/django#1622` | db | [#1622](https://github.com/django/django/pull/1622) | Fixed #21099 - Skip DistinctOnTests unless backend can_di… |
| 84 | `django/django#791` | db | [#791](https://github.com/django/django/pull/791) | Changed %r to %s in get_language_info error message |
| 85 | `django/django#1164` | db | [#1164](https://github.com/django/django/pull/1164) | Integrity problems when using get_or_create through M2M |
| 86 | `django/django#1198` | db | [#1198](https://github.com/django/django/pull/1198) | Fixed #20478 – Added support for HTTP PATCH method in gen… |
| 87 | `django/django#1644` | db | [#1644](https://github.com/django/django/pull/1644) | Increase default PBKDF2 iterations |
| 88 | `django/django#3874` | db | [#3874](https://github.com/django/django/pull/3874) | Fixed #24097 -- Prevented AttributeError in redirect_to_l… |
| 89 | `django/django#4548` | db | [#4548](https://github.com/django/django/pull/4548) | Fixed #24649 -- Allowed using Avg aggregate on non-numeri… |
| 90 | `django/django#4179` | db | [#4179](https://github.com/django/django/pull/4179) | Faster staticfiles tests |
| 91 | `django/django#1853` | db | [#1853](https://github.com/django/django/pull/1853) | Fixed failing test around DST change. |
| 92 | `django/django#812` | db | [#812](https://github.com/django/django/pull/812) | Fixed #19872 |
| 93 | `django/django#1232` | db | [#1232](https://github.com/django/django/pull/1232) | Don't hard-code class names when calling static methods |
| 94 | `django/django#1401` | db | [#1401](https://github.com/django/django/pull/1401) | Updated contrib.admin to use Email/URLInputs; refs #16630 |
| 95 | `django/django#2126` | db | [#2126](https://github.com/django/django/pull/2126) | Introduced as_bytes for SafeMIMEText (and other SafeMIME-… |
| 96 | `django/django#3895` | db | [#3895](https://github.com/django/django/pull/3895) | Fixed #24133 -- Replaced formatting syntax in success_url… |
| 97 | `django/django#4617` | db | [#4617](https://github.com/django/django/pull/4617) | Fixed #24207 -- Added 25D-type geometry field support to … |
| 98 | `django/django#4303` | db | [#4303](https://github.com/django/django/pull/4303) | Fixed #24122 -- Added redirection to translated url after… |
| 99 | `django/django#1743` | db | [#1743](https://github.com/django/django/pull/1743) | Fixed #21172 -- have LiveServerThread follow the semantic… |
| 100 | `django/django#820` | db | [#820](https://github.com/django/django/pull/820) | Fixed #11295: If ModelAdmin.queryset returns a filtered Q… |

## Re-run

```bash
cd /path/to/ace-bench
source .venv/bin/activate
export ACE_DB_PATH=data/frozen/ace_patterns_django_pre2021_6125.sqlite
python3 scripts/run_batch_eval.py \
  --limit 100 --mode thorough --skip-sandbox \
  --write-report docs/EVAL_BATCH_100.md \
  --eval-db ~/ace-bench-data/eval_runs.sqlite
```

