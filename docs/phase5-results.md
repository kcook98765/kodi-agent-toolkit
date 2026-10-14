# Phase 5 reliability results — 2026-10-13

> Historical qualification record. Original judgments and counts are preserved. The public beta uses a separate reviewed initial snapshot; old development commit IDs are provenance references, not public Git objects. Use the current README and docs/github-publication.md for installation and publication; historical publishing proposals below were not executed.


**NEEDS ANOTHER HARDENING PASS.** Static workflows and installation are useful and reproducible; material small-model review errors remain. Benign controls still attract unsupported criticism, and Mellum cannot reliably submit a valid contextual report. Final artifact paths and runtime pagination also remain model-dependent. Nothing has been published or pushed.

## Verified starting state and preservation

Started clean on `main` at `a6860ccb1d7bb18cfe4809782133c65d9e770265` with no remotes. Created `phase5/reliability-release` from that baseline before source changes. Existing Phase 4 report, handoff, journal, README, five skills, source/tests, OpenCode configuration and all 42 transcripts/results were inspected. The 75-test baseline replay and an actual valid-fixture checker run passed before improvements.

The original 42 results remain **10 PASS, 23 PARTIAL, 9 FAIL**. `248` selected historical artifact/report/journal hashes matched before the journal append; original four fixtures and `evaluation/pilot-results.json` remain unchanged (SHA-256 `25e246592ba0ba149a58b89b6c66038eacd7b442aadcf9e064637485dec1a615`). The new baseline scorecard is an annotation, not a replacement of historical judgments. Ending full Git SHA is recorded in the external workstation Phase 5 report after the local commit; this document belongs to that commit.

## Baseline failure analysis

| Category | Trials |
|---|---:|
| context or tool overhead | 4 |
| failed error recovery | 2 |
| guessed or nonexistent paths | 6 |
| harness defect | 4 |
| incomplete responses | 6 |
| incorrect working directory | 3 |
| invalid tool arguments | 3 |
| missing or inaccurate evidence | 4 |
| severity inflation | 3 |
| skill loading | 4 |
| unnecessary tool calls | 2 |
| unsupported kodi findings | 14 |
| wrong tool selection | 1 |

Categories overlap and are conservative manual annotations from notes and transcripts, not accuracy rates. Call-level replay found eight missing-path errors in six trials, one repeated missing-path error, one native schema error, five length endings, three step-cap replies and 34/42 complete final replies. Only five of ten historical repair trials observed the actual pre-edit type defect; seven had all required post-check stages completed. Legacy tool order alone had overstated completion.

Representative success: Coder's explicit Nexus repair recovered an entry-point guess and retained INFO with LOGINFO. Representative failures: guessed numeric severity changed behavior despite static acceptance; Mellum guessed root manifests/repeated paths; review elevated suggestions or hid missing evidence; null UI selection was treated as absence. Origins differ: model interpretation/path/format errors, insufficient discovery/severity/stop guidance, and harness permission/default/cwd/completion issues. No confirmed Kodi Lab MCP API or authorization defect was found. Checker crashes are pinned third-party infrastructure failures, retained as incomplete checks.

## Focused changes

- Added stdlib bounded discovery with actual workspace/manifest/file/entry inventories, project-relative origins, spaces, missing-root recovery, POSIX rejection of untranslated Windows paths, omitted link/budget reporting, normalized `./` declarations and module directories. Global `.agents` alone is not a workspace; default ancestor scans cannot escape a nearer repository.
- Shared fixture-path checks in both adapters verify actual component/root containment. Discovery needs Python/CLI but no checker cache. Validation still needs an explicit cache. Review compose timeout now matches validation at 90 seconds.
- Schema 1.2 and manual contracts agree: unresolved observations are advisory; blocker needs demonstrated impact; demonstrated requires steps/observed/expected; static source-supported findings omit reproduction. Accepted classifications remain model claims. Composition exposes `static_passed`, `contract_passed`, status and pass scope; model rejection never converts official warnings into deterministic errors.
- Added preferred native structured review `report`, retaining legacy `report_json` and rejecting dual inputs. This removes a nested escaping layer, while the independent Python validator still rejects malformed records. It does not certify semantics.
- Revised all five core skills: discover/read/reproduce/focused change/recheck/stop; explicit limits and short summaries; use detailed references on demand. Clarified minimum dependency semantics against the [official addon.xml reference](https://kodi.wiki/view/Addon.xml#version_attribute). No new skill or dependency was added.
- Extended the existing harness rather than replacing tasks: stale/missing paths, space-containing nested cwd, absent manifest/cache, target ambiguity, benign review, scope/trigger controls and read-only runtime inspection. Added original-skill copying, explicit `--dir`/PWD and project guard, completed stage/target/final gates, source/fixture/cache provenance, structured submission grading, source isolation and conservative final fixture-path observations. The future runner records the configured cache; the intentional missing-cache pilot's old reference-cache hash is explicitly qualified in the public data.
- Hardened secret scanning for worktree, actual index and all reachable history blobs, including binary/exact-token checks; added release/security/contribution/installation documentation and credential-free standalone configuration. Dependencies remain hash locked.

The initial Phase 5 pilot drifted into the source checkout before model execution; write permissions denied edits. That retained harness FAIL is excluded from matched comparisons. Explicit directory selection and fixture guard corrected it. No permission escalation was used.

## Skill qualification

| Skill | Original / final words | Verification |
|---|---:|---|
| kodi-addon-debugging | 249 / 207 | Native forced loading in health/UI/runtime trials. |
| kodi-addon-development | 265 / 207 | Native forced loading in repair/path trials. |
| kodi-addon-validation | 225 / 226 | Native forced loading in XML/review/nested-root trials. |
| kodi-mcp-testing | 205 / 195 | Native forced loading in mcp-health; automatic routing skipped it. |
| kodi-version-compatibility | 175 / 234 | Native forced loading in compatibility; automatic routing skipped it. |

Core files total 1119 → 1069 whitespace-delimited words (frontmatter included). All five validate as portable skills and appear in actual OpenCode discovery. Loading is measured from native events. Automatic routing skipped both relevant compatibility/MCP skills in two trials; the unrelated arithmetic control used zero tools/skills. Explicit loading remains the reliable reference mode; spontaneous triggering is unproven. Compatibility guidance grew because actual trials confused minimum versions with upper bounds.

## Controlled model evidence

Actual model IDs were discovered from configured endpoint `/models`: `qwen3-coder-next`, `mellum2.1-q4-trial`, `qwen3.8-27b`; the existing vision endpoint advertised `qwen3-vl-8b-instruct` but no visual task was needed. OpenCode 1.19.0 and Python 3.12 are the executed reference environment. No weights, engine/quantization/context/output settings or remote servers were changed. Models ran sequentially, each bounded at 150 seconds, without operator intervention inside a trial.

34 trials: **14 PASS, 15 PARTIAL, 5 FAIL**, including the excluded harness failure. These heterogeneous, nonblinded Codex artifact judgments are **not** a statistical comparison to 10/42 historical PASS. Criteria require actual workflow steps, existing locations, retained warnings, supported mechanism/severity, static/runtime separation, useful recovery and granted scope. Automatic gates never replace semantic judgment. All per-trial judgments, counters, token usage and hashes are in [the sanitized scorecard](../evaluation/phase5-results.json); transcripts/configurations remain private.

A has no copied skill/native load; B copies original skill/reference files from the Phase 4 commit; C uses revised skills. Core task prompts, fixtures and permissions match within the twelve A/B/C trials, with the explicit preload instruction only in skill conditions. All use current Phase 5 deterministic tools/harness, so B is not an exact historical server/tool replay. A2 predates the added workspace guard but uses corrected explicit directory selection; later runs record the guard in provenance. Every correction stage has skill/tool/source hashes; not every intermediate Python source is packaged as a separate Git commit. C2/C3 corrective runs are separated below.

| Trial | Grade | Seconds | Completed / failed tools | Path errors | Final words | Input + cache / output tokens |
|---|---|---:|---:|---:|---:|---:|
| coder-repair-A2 | PARTIAL | 39.08 | 4 / 2 | 1 | 113 | 3484 + 11210 / 757 |
| coder-repair-B | PASS | 51.27 | 7 / 1 | 1 | 99 | 5692 + 24660 / 823 |
| coder-repair-C | PASS | 45.45 | 7 / 0 | 0 | 85 | 5435 + 22349 / 563 |
| mellum-repair-A | PASS | 66.03 | 7 / 0 | 0 | 311 | 10744 + 24156 / 4329 |
| mellum-repair-B | PASS | 64.81 | 8 / 1 | 1 | 192 | 6042 + 49355 / 4438 |
| mellum-repair-C | PARTIAL | 55.95 | 6 / 0 | 0 | 243 | 5276 + 29021 / 3655 |
| coder-review-A | PARTIAL | 44.95 | 4 / 0 | 0 | 113 | 6267 + 16920 / 762 |
| coder-review-B | PARTIAL | 49.05 | 4 / 0 | 0 | 121 | 7094 + 13663 / 883 |
| coder-review-C | PARTIAL | 51.26 | 3 / 1 | 0 | 113 | 6636 + 16871 / 1064 |
| spark-xml-A | PASS | 29.68 | 2 / 0 | 0 | 73 | 6361 + 0 / 723 |
| spark-xml-B | PASS | 32.11 | 4 / 0 | 0 | 88 | 12098 + 0 / 859 |
| spark-xml-C | PASS | 30.87 | 3 / 0 | 0 | 70 | 11136 + 0 / 739 |

The two updated repair pilots had zero missing-path errors versus one in each original-skill repair pilot. All four repaired fixtures passed independent checks. Coder's updated trial completed the full requested workflow; Mellum omitted warnings and invented a coverage caveat despite a correct repair. Mellum remained too verbose. Spark's bounded XML explanation passed in all three conditions; the revised skill did not establish a new correctness advantage.

All three initial Coder review conditions passed static/source contracts but invented unexecuted reproduction observations. That drove the stricter schema; the later Coder report omitted reproduction, yet overstated sensitivity. Review severity/semantic quality is not proven improved by a structural gate.

| Trial | Grade | Seconds | Completed / failed tools | Path errors | Final words | Input + cache / output tokens |
|---|---|---:|---:|---:|---:|---:|
| coder-review-C2 | PARTIAL | 44.50 | 3 / 0 | 0 | 116 | 7061 + 10850 / 696 |
| mellum-review-C2 | FAIL | 126.51 | 8 / 5 | 3 | 295 | 24039 + 124267 / 8782 |
| coder-clean-C2 | PARTIAL | 52.75 | 4 / 0 | 0 | 210 | 7426 + 14263 / 961 |
| mellum-review-C3 | PARTIAL | 66.82 | 6 / 0 | 0 | 236 | 17348 + 17484 / 4066 |
| mellum-clean-C3 | FAIL | 76.08 | 4 / 0 | 0 | 246 | 17435 + 9731 / 5038 |
| compat-forced-C2 | PARTIAL | 27.67 | 4 / 0 | 0 | 75 | 3625 + 10325 / 339 |
| compat-forced-C3 | PASS | 27.22 | 4 / 0 | 0 | 86 | 3760 + 7433 / 312 |
| mcp-forced-C2 | PASS | 21.99 | 3 / 0 | 0 | 37 | 2505 + 6592 / 214 |

Structured transport reduced Mellum's same defective-review task from 126.51 to 66.82 seconds, failed tool events from five to zero, and removed its step-cap reply; cumulative input/cache/output also fell. The malformed report still failed its contract, so this is recovery/overhead evidence, not successful review. Its benign structured report still invented setting/source evidence. Coder's benign follow-up stopped claiming literal secret output but retained an unsupported privacy advisory and inconsistent warning coordinate. Minimum-dependency clarification corrected Coder's next compatibility conclusion. Single reruns cannot establish general reliability.

| Trial | Grade | Seconds | Completed / failed tools | Path errors | Final words | Input + cache / output tokens |
|---|---|---:|---:|---:|---:|---:|
| checker-failure-C | PASS | 23.42 | 3 / 0 | 0 | 69 | 2955 + 6259 / 199 |
| coder-clean-C | FAIL | 50.12 | 4 / 0 | 0 | 137 | 7115 + 13977 / 896 |
| coder-debug-broad-C | PARTIAL | 36.57 | 5 / 0 | 0 | 185 | 5609 + 11105 / 600 |
| coder-debug-narrow-C | PARTIAL | 29.64 | 4 / 0 | 0 | 198 | 2685 + 9353 / 517 |
| coder-repair-A | FAIL | 75.61 | 4 / 4 | 2 | 93 | 4367 + 11296 / 595 |
| compat-auto-C | PARTIAL | 22.91 | 3 / 0 | 0 | 65 | 2580 + 6386 / 264 |
| generic-auto-C | PASS | 13.76 | 0 / 0 | 0 | 5 | 1842 + 0 / 9 |
| mcp-auto-C | PASS | 20.80 | 2 / 0 | 0 | 54 | 2398 + 4471 / 206 |
| mellum-clean-C | FAIL | 141.89 | 4 / 2 | 0 | 267 | 7183 + 61806 / 12762 |
| mellum-path-B | PASS | 27.67 | 5 / 0 | 0 | 92 | 4012 + 14713 / 1325 |
| mellum-path-C | PASS | 27.91 | 5 / 0 | 0 | 88 | 3951 + 15153 / 1305 |
| missing-manifest-C | PARTIAL | 26.56 | 5 / 1 | 1 | 62 | 2714 + 17806 / 1707 |
| runtime-addon-C | PARTIAL | 33.37 | 5 / 0 | 0 | 92 | 5657 + 13605 / 396 |
| wrong-root-C | PARTIAL | 25.53 | 3 / 0 | 0 | 71 | 3357 + 7481 / 1137 |

Task-specific MCP scope used list/status/UI: four completed events including skill, 29.64 seconds. Broader existing read-only scope used five events, 36.57 seconds, including an unnecessary first inventory page and unsupported all-enabled conclusion. No invalid arguments or unauthorized mutations occurred in either. Narrow scope had fewer calls and less tool output; one pair is not causal proof. Phase 3 measured five/three MCP schemas at 2424/1427 bytes; Phase 4 API full/narrow at 8242/5943 bytes. These preserved historical byte counts are not new tokenizer measurements. Phase 5 uses actual cumulative SDK tokens/tool output; hidden context and wire schemas were not remeasured. Cache/startup/model behavior limit latency comparisons.

## Real workflows

**A — repair completed.** Disposable invalid-API fixture: discovery verified manifest and `default.py:7`; original mypy `[arg-type]` diagnostic reproduced; focused change replaced string `"info"` with verified target constant `xbmc.LOGINFO`; syntax, manifest, paths, package, types and official addon-check completed afterward. Official checker had zero errors and the original two warnings (offline URL unverified and Nexus Python-version recommendation). Source changes were confined to that line and verified independently. Runtime deployment/execution was not performed.

**B — runtime reproduction blocked; inspection completed independently.** Existing exact-target read-only grant on disposable Kodi 20.5 returned running process/responsive RPC, Home/Movies focus, selection unknown. Independent paging fetched 50+50+6 = 106 unique add-ons and confirmed `script.toolkit.sample` absent. Model trial fetched only one page and falsely claimed complete pagination; its absence conclusion was not verified by its own evidence. No log-reading, install, launch, navigation or Python-execution permission was added. The focused next test is to deploy the disposable fixture under separately granted authority, reproduce the logging-level issue, apply the static repair and re-run the same launch with actual logs. Runtime correction/outcome remains untested. Production/native Kodi was untouched.

## Validation, portability, security and resources

- Final Linux full regression: **148 passed**, retaining original 75. Independent holdout: **9/9** on first execution after initial implementation; answers were not supplied during initial skill edits, but later regression runs are no longer unseen. `pip check` passed.
- Isolated fresh Linux Git-index export/new venv installed all hash-locked wheels offline from the preserved cache, installed toolkit editable without build isolation, passed full regressions and actual valid-fixture official checker. Original index snapshot explicitly copied. This qualifies a fresh local install, not a new network bootstrap, public clone URL, macOS or other architectures.
- Native Windows 11/Python 3.12.3: source-only CLI discovery/review with spaces/missing path, and selected stdlib path/review/severity suites total **46 passed, 4 skips**. Initial CLI source loading and severity-test optional dependency imports failed, then were corrected; failed artifacts retained. No Windows dependency install or second toolkit checkout. Full native checker/OpenCode runner and macOS untested; docs distinguish them.
- Candidate worktree/index/reachable-history scans plus exact private MCP token and independent additional credential/home-path checks passed. Original icons manually assessed as non-sensitive generated images; no profiles/media/logs/screenshots/private model configuration/binaries are tracked. MIT retained for original toolkit, GPL-3.0-only dependencies separate; KodiAI proprietary material not copied. Dependency inventory corrected colorama BSD-3-Clause, mypy_extensions MIT and pathspec MPL-2.0 metadata. No licensing/security blocker identified; heuristic scans are not a universal credential guarantee.
- Twelve 10-second selected-pilot samples: WSL total 5928.58 MiB, used 1903.20–2093.45 MiB, swap 67.19–68.33 MiB; point container usage about 440 MiB. Post-run WSL used 1393 MiB, available 4535 MiB; Windows free about 2.05 GiB. These are samples, not continuous peaks. Model-server resource consumption unmeasured; no laptop inference. WSL 6 GiB/4 CPU/2 GiB swap cap and configuration hash unchanged.
- Kodi Lab remained clean on its original compatibility branch/commit, four healthy containers; no upstream pull, restart, source/API/grant change or Web interruption. Private OpenCode configuration, credentials and model settings unchanged. No remote repository created or push made.

## Reproduction and remaining work

From the Linux toolkit root with the documented venv and explicit official cache:

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m pip check
.venv/bin/python -m kodi_agent_toolkit.cli discover fixtures
.venv/bin/python -m kodi_agent_toolkit.cli validate fixtures/valid/script.toolkit.sample --branch nexus --cache .local/index-cache
.venv/bin/python evaluation/scorecard.py
# Requires your existing private provider and SDK setup; use a fresh label:
KODI_EVAL_TOOL_SCOPE=narrow .venv/bin/python evaluation/run.py --model PROVIDER/MODEL_ID --task api-fix-nexus --condition skill --label NEW-REPAIR --timeout 150
.venv/bin/python evaluation/assess.py NEW-REPAIR
.venv/bin/python scripts/secret-scan.py
.venv/bin/python scripts/secret-scan.py --staged
.venv/bin/python scripts/secret-scan.py --history
```

Next hardening should concentrate on small-model report construction, counterevidence/benign-review specificity, final artifact coordinates, diagnostic uncertainty and inventory pagination. Preserve the separate static/model statuses and bounded tasks. Qualify actual network installation/other platforms and an authorized deployed runtime fixture before claiming them. Do not solve these limits with larger model contexts or permissive grants. The toolkit is stronger for path discovery/static repair and clearer about failed validation, but autonomous contextual review remains materially unreliable.
