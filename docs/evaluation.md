# Repeatable pilot evaluation
Run from the toolkit's isolated environment with an existing authorized private OpenCode provider/MCP configuration. No cloud comparison is enabled. Pass `--model PROVIDER/MODEL_API_ID` from your verified private OpenCode configuration. The public harness includes no workstation aliases or observer routes. Standalone regression, scorecard and harness-help checks need no provider.

```sh
.venv/bin/python evaluation/run.py --model PROVIDER/MODEL_API_ID --task xml --condition baseline --label new-coder-xml-baseline
.venv/bin/python evaluation/run.py --model PROVIDER/MODEL_API_ID --task xml --condition skill --label new-coder-xml-skill
```
Use new labels. Each run copies original fixtures into a new Git repository under the private evaluation directory, preserving source fixtures. Baseline and skill conditions use the same task/target/model/settings; skill availability/routing is the intended difference. The native skill call and its returned body are recorded, not inferred from a mention in prose. Original no-invocation failures are retained. Timers bound each run and CLI zero exit alone never proves task success.

Acceptance:
- explain: identify actual manifest dependency, script entry point and source behavior with correct coordinates; state static/runtime boundary.
- xml: report the actual malformed closing tag; official checker execution/output expected; no edits.
- api-fix: smallest correction to the typed logging API, independently rerun validation and prove the fixture passes.
- validate: official checker/stubs/package stages ran; accurately distinguish warnings and failure/coverage status.
- debug: grounded process/UI, unknown selection, no unauthorized calls or inferred absence of errors.
- review: actual privacy data flow supported by Python and settings evidence; separate checker findings; validate source locations and uncertainty.

Record tool completions/failures, repeated/unnecessary calls, first useful action, total time, native skill loads, usage/cache counts and reported context. Wire schema byte count is not a token estimate. Cumulative input includes repeated context, and SDK reasoning may be folded into output. Note prompt/routing changes, output/step caps, caches and human intervention. Few trials do not establish model superiority.

Security: no arbitrary host command tool, no runtime add-on execution, no Kodi mutations. File edits only in a disposable api-fix fixture. Server read-only MCP authority is unchanged. Custom validation runs a fixed trusted Python entry point with bounded add-on path and offline cache. On another OS, qualify the runner's OpenCode/SDK environment; current evaluation uses WSL paths and SDK symlink reuse.

Workflow changes retained for comparison: initial available-skill trials skipped loading; system-only routing was insufficient. The current skill condition prepends a user-level instruction to load the most relevant native skill first. This is a controlled instruction intervention, not proof of spontaneous invocation. Optional KODI_EVAL_SKILL_CATALOG=all exposes all five skills for selection trials. No-reference baselines retain identical AGENTS.md and deterministic tools.

The first adapter version passed an omitted branch as undefined; the fixed adapter uses a runtime Nexus default. The first edit permission used an absolute pattern and failed closed; the current runner allows only fixtures/script.toolkit.sample/default.py relative to its disposable workspace. These harness failures are separated from model quality and require paired reruns. A repeat of two denied operations terminates the trial rather than permitting a retry loop or escalating authority. No blanket edit/shell permission is granted.

After runs, independently inspect artifacts:
```sh
.venv/bin/python evaluation/assess.py NEW_LABEL
```
Automatic gates verify actual skill events, typed logging repair, fresh validation and review coordinates. Human judgment remains required for explanation quality, grounding, false positives and supported severity. Evidence is private by default; public summaries contain no target IDs or private endpoints.

KODI_EVAL_TOOL_SCOPE=narrow removes glob/grep from file tasks while retaining direct read and bounded validation/review. For a known fixture path this reduces tool ambiguity; pair trials with the same setting and inspect actual wire schemas. Kodi authority is unchanged. Native skill metadata plus tool descriptions can outweigh a small skill body, so measure both startup schemas and cumulative usage rather than counting SKILL.md words alone.

Final runner records initial fixture tree/file hashes, copied skill/validator/adapter/harness hashes and cache identity before edits. Older retained trials have copied skills/tools and event/version evidence but lack this complete initial provenance record; do not treat them as identical source revisions. Independent reassessment records current validator hashes separately. Labels are restricted to one component. Deadlines stop only the created process tree, escalate and record termination. Unix cleanup has dummy-process regression coverage; Windows cleanup remains unqualified.

The logging acceptance gate compares the whole fixture AST against the intended minimal INFO-level repair, rejecting removed calls or dead-code substitutes. Skill-first acceptance requires the expected successful native load before other tools. Checker findings and model judgments remain separate; human review is required even for a coordinate-contract pass.

## Phase 5 comparisons and targeted cases

Set `KODI_EVAL_PRIVATE` to a private evidence directory outside Git. The current default is `~/.local/share/kodi-agent-toolkit/evaluation`; original Phase 4 evidence is not reassessed in place. Set `OPENCODE_SDK_DIR` when the installed SDK is elsewhere, `OPENCODE_BIN` if needed, and `KODI_TOOLKIT_INDEX_CACHE` for an explicit existing cache. Invoke with the installed toolkit environment so `sys.executable` selects its dependencies. Read docs/installation.md first.

```sh
KODI_EVAL_TOOL_SCOPE=narrow .venv/bin/python evaluation/run.py --model PROVIDER/MODEL_ID --task api-fix-nexus --condition baseline --label new-A
KODI_EVAL_TOOL_SCOPE=narrow .venv/bin/python evaluation/run.py --model PROVIDER/MODEL_ID --task api-fix-nexus --condition skill --skill-revision BASELINE_COMMIT --label new-B
KODI_EVAL_TOOL_SCOPE=narrow .venv/bin/python evaluation/run.py --model PROVIDER/MODEL_ID --task api-fix-nexus --condition skill --label new-C
.venv/bin/python evaluation/assess.py new-A new-B new-C
```

B requires a baseline commit present in your own local history. The original Phase 4 commit IDs in historical reports are provenance identifiers, not objects included in this initial public snapshot. To compare future skill revisions, use a local baseline commit containing those skills. B copies skill files from that local commit; tools, harness, prompts, fixture and permissions remain current and comparable across A/B/C. This measures skill changes under current deterministic helpers, not an exact rerun of historical Phase 4 tooling or remote server state. Provenance records source/skill/task/cache hashes and routing. The historical baseline includes conservative overlapping failure categories, not an accuracy rate.

Added scenarios preserve every established task: `path-recovery`, `wrong-root`, `version-ambiguous`, `missing-manifest`, `checker-failure`, `review-clean`, `mcp-health`, `runtime-addon`, and unrelated `generic`. Wrong-root starts inside a directory with spaces; missing-manifest/cache removes only disposable inputs. The clean review control must not attract a secret-leak finding merely because a variable is read. Independent holdout regressions were written by a separate reviewer after implementation and run without giving their answers to the skill author first.

`KODI_EVAL_SKILL_ROUTING=auto` removes forced native loading; use `KODI_EVAL_SKILL_CATALOG=all` to measure selection/no unnecessary trigger. Forced loading demonstrates loading/following, not autonomous triggering. `KODI_EVAL_MCP_SCOPE=broad` additionally exposes existing authorized inventory/screenshot tools for inspection comparisons; no state-changing tool is allowed and server grants are preserved. Do not pass image tools to a text model unless the task can use their results appropriately.

New output-aware gates require the actual pre-edit type diagnostic, all six passing post-edit stages, a completed official checker and consistent target. Legacy event-order gates remain labelled for historical comparison. Final completion needs a nonempty reply, a stop reason and no step-cap notice; a process exit of zero alone is insufficient. Path/schema/repeated-input counters are observational: identical revalidation after an edit can be necessary. Review anchors/severity contracts cannot establish semantic truth; significant review claims need independent judgment using explicit criteria.

The runner passes an explicit `--dir`, matching PWD and a disposable-project guard to prevent directory drift. A Phase 5 pre-fix pilot switched into the source checkout before model execution; write permissions denied changes. That failed pilot is retained and excluded from matched comparisons. All subsequent comparisons use the fixed directory selection; no model/server/output-budget tuning was performed.

Phase 6 adds automatic `final-report.json` and `final-report.md` after the process exits. They use actual tool payloads, independent completion gates and initial/current source hashes, not the model's final prose. Failed/missing composition, stale checks, incomplete replies and exceeded composition-attempt bounds cannot become a workflow PASS. Natural explanations remain in events.json as separately unverified prose. Required gates describe the evaluated task; report status describes recorded workflow/check completion, not general code correctness or the independent reviewer grade.

`review-redacted` is a further clean control where a value is replaced before logging. Controlled phases preserve original A/B/C results and record source/adapter versions per trial. The full CLI schema is compacted to a data-shaped template in agent context only; corrective trials must use fresh labels. Transcript replay with a new validator is not evidence that a model improved. Unsupported semantic observations cannot be counted as verified defects. An absent required record produces BLOCKED/PARTIAL instead of silently assuming success.

Verify baseline invariants with `.venv/bin/python evaluation/scorecard.py`. After independent task review, collect sanitized numbers with `evaluation/scorecard.py --runs PRIVATE_EVIDENCE_ROOT --output PUBLIC_SUMMARY.json`; raw transcripts remain private. Per-trial `independent-verdict.json` must name PASS/PARTIAL/FAIL and explain the judgment. Automatic final-path observations cover explicit inline backtick `fixtures/` citations only; they do not prove every prose or absolute-path reference. Missing/stale examples are conservatively excluded.

## Private artifacts and redaction

The runner never searches for credentials. Optional `KODI_EVAL_SECRET_FILES` lists explicitly chosen private plaintext exact-value files, separated by the platform path separator (`:` on Linux, `;` on Windows). These values are redacted in event strings; authorization/cookie/token object fields and inline image data are also redacted. Keep all raw output outside Git even after redaction; heuristics cannot remove every sensitive value. Capture the runner console privately. No model trial or paid provider call is required to reproduce the deterministic release checks.
