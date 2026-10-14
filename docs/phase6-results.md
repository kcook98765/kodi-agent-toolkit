# Phase 6 qualification

> Historical qualification record. Original judgments and counts are preserved. The public beta uses a separate reviewed initial snapshot; old development commit IDs are provenance references, not public Git objects. Use the current README and docs/github-publication.md for installation and publication; historical publishing proposals below were not executed.


Decision: **READY FOR PUBLIC BETA**, limited to the [supported standalone scope](public-beta.md). AI review, autonomous repair and Kodi Lab workflows remain experimental. Runtime deployment qualification: **BLOCKED**, not a code failure. Nothing was pushed or published.

The starting clean checkout was `phase5/reliability-release` at `c71b69e842b53710a8885a3a74f9b517b4b2ea2a`. Work used local branch `phase6/evidence-beta`. The workstation's external PHASE6-RESULTS.md records the ending full commit SHA; a document cannot contain its own commit hash. Repository reports are sanitized; raw transcripts, credentials and machine details remain private.

## Evidence boundary

`evidence.py` independently classifies anchored model claims. Existing exact-quote, single-line and path checks now also reject reparse roots/ancestors and junctions. Ranges are unsupported and rejected rather than guessed. A real file and correct line establish structure, not the truth of a consequence.

The categories are confirmed deterministic error, evidence-supported contextual issue, recommendation and unverified observation; duplicates are retained separately. The official checker's literal errors/warnings remain canonical. Model checker claims are discarded and cannot override them. Exact diagnostic duplicates and repeated anchor/category findings are removed from the issue count; semantically reworded duplicates still need review.

One small conservative AST recognizer independently supports a conditional direct flow from a UI-concealed setting to logging. It requires the matching reviewed settings declaration and excludes transformations, intervening statements, decorated/parameterized functions, aliases and shadowed Kodi imports. Its canonical observation says **if sensitive and executed**; it establishes neither actual secret contents nor runtime exposure. Everything outside that pattern remains unverified or advisory. A model-written reproduction cannot certify severity. Known primary documentation identifiers establish a possible policy basis, never its applicability. No general semantic rule engine was added.

`reporting.py` and CLI `report-build` assemble bounded factual reports from trusted tool/operator records: source hashes, actual changes, all six static stages, original warnings, test exits, observations and completion gates. Hashes detect stale results, not forged records. Runtime observations cannot establish a runtime repair. JSON and Markdown preserve rejection reasons and artifact references. UTF-8 and PowerShell UTF-16 input records work.

The evaluation runner writes these reports after OpenCode exits, including incomplete runs. Raw model prose is separately unverified. Every general contextual review remains PARTIAL while semantics/coverage need independent review, even when an empty draft passes its schema. Static checks have a separate `static_outcome`. Bounded repairs can PASS when actual reproduction, the intended edit and target-consistent rechecks are recorded.

## Changes and regressions

Only the validation skill's short workflow and its reference changed; the other four skills were reviewed and retained. Supporting changes add source hashes to validator/adapter outputs, independent categories to composition, automatic reports, an expected-issue evaluation gate, bounded composition attempts and a compact data-shaped context template. The complete CLI schema remains available. No integrations, general skills, dependencies, hosted services or model tuning were added.

| Check | Result |
|---|---|
| Verified Phase 5 Linux baseline | 148 passed |
| Final Linux suite | 170 run: 169 passed, 1 native-Windows junction test skipped |
| Final native Windows full suite | 170 run: 159 passed, 11 explicitly classified skips |
| Focused evidence/report tests | 20 passed, including adversarial paths, wrong lines, range rejection, fabricated requirements, severity inflation, duplicates and valid controls |
| Focused harness suite | 47 passed |
| Actual official checker + installed stubs, Ubuntu and Windows | Valid Nexus sample passes all six stages; invalid API sample fails types with exit 1 as expected |
| Dependency consistency | Fresh isolated installs and pip check pass; all 24 inventory versions match |
| Historical evidence preservation | 320 report/transcript/artifact hashes unchanged before journal append; original journal retained as byte prefix |

Additional cases cover renamed unseen setting flows, redaction/constant-message controls, public settings, import shadowing, missing/stale checks, failed tests, false completion gates, absent replies, real Windows junctions and source changes. Final source was also checked in an isolated checkout/venv; no Kodi or model server is needed for the deterministic suite.

## Controlled agent results

Thirteen sequential, bounded trials used OpenCode 1.19.0, explicit native skill loading, narrow task tools, 150-second deadlines and the existing 14-step budget. Models were Qwen3-Coder-Next, Mellum2.1 Q4 and the DGX Spark Qwen3.8-27B endpoint. Model/provider configuration was unchanged. No Vision task was relevant. No operator intervened inside a trial.

| Trial | Independent answer/task judgment | Final recorded workflow | Main observation |
|---|---|---|---|
| Coder clean review | FAIL | PARTIAL | Empty valid draft; prose invents value exposure in a constant-message control |
| Mellum clean review | FAIL | PARTIAL | Rejected draft; invented privacy/manifest criticism |
| Spark clean review | FAIL | BLOCKED | Length termination, no usable final reply or composition |
| Coder defective review | PARTIAL | PARTIAL | Rejected schema fragments and unsupported policy/reproduction |
| Mellum defective review | PARTIAL | PARTIAL | Path recovery; empty draft omits issue; inaccurate warning coordinates |
| Spark defective review | PASS | PARTIAL | One recovered argument error; conditional supported flow and bounded severity |
| Coder API repair | PARTIAL | PASS | Exact repair verified; model prose omits warnings and mislabels pre-check table |
| Mellum API repair | PASS | PASS | Exact repair verified; summary acknowledges warnings/static limit |
| Coder unseen redacted control | PARTIAL | PARTIAL | No recorded defect; unsupported advisory in prose about ordinary value memory |
| Mellum unseen redacted control | PARTIAL | PARTIAL | Recovered path error; incomplete coverage and inaccurate warning prose |
| Corrective Coder defective review | PARTIAL | PARTIAL | Simpler context still produced rejected findings; no accepted expected issue |
| Corrective Mellum clean review | FAIL | PARTIAL | Recovered errors; still claimed value logging in valid control |
| Corrective Spark clean review | FAIL | BLOCKED | Simpler context still ended at length without final/composition |

Independent judgments: 2 PASS, 6 PARTIAL, 5 FAIL. Recorded workflow outcomes: 2 PASS repairs, 9 PARTIAL reviews, 2 BLOCKED runs. These answer grades and recorded statuses measure different things. A recorded repair PASS does not endorse every sentence of the model's summary.

There were 72 completed and 9 failed tool events, 7 missing-path errors (1 repeated), 3 identical-input repeats and 2 length-truncated final responses. Revalidation after editing is necessary; identical calls are not automatically waste. The initial Coder defective review made three completed composition calls, exceeding the two-attempt bound. Explicit inline `fixtures/` citations contained 7 mentions and no invalid files; this narrow metric excludes generic prose and line accuracy, where independent review found errors. No invented path became a verified file. Only Spark's defective review yielded an independently supported conditional issue; no model blocker or fabricated policy was certified. Human intervention within trials: zero; Codex prepared fixtures, audited results and changed tooling between trials.

The first ten trials used evolving prototypes; the final three used the compact context format. Per-trial source/skill/cache hashes are in [the numeric scorecard](../evaluation/phase6-results.json). Do not treat all trials as final-identical bytes or calculate statistical improvement. Three prototype review reports incorrectly showed PASS for recorded structure/static success; final qualification corrects that scope to PARTIAL. Original reports remain intact, with additional qualification artifacts. One initial reassessment accidentally used system Python without installed dependencies; the resulting errors are retained, and the isolated installed environment produced the final assessments. No agent trial was rerun to hide that harness error.

Phase 5's 34 trials remain 14 PASS, 15 PARTIAL, 5 FAIL under their original judgments. All 20 relevant non-PASS cases are in [the failure matrix](phase6-failure-matrix.md). Offline replay of ten preserved review submissions is [separately recorded](../evaluation/phase6-replay.json): one invalid transport, six formerly retained candidates reduced to two structurally accepted candidates, with only one supported conditional issue; the benign false positive remains unverified. Replay tests containment, not model improvement. Smaller-model reasoning, schema use, coverage and concise factual prose remain unreliable; the improvement is a deterministic reporting boundary, not a claim to have fixed the models.

## Runtime debugging

Managed Kodi 20.5 inspection was verified. The smallest candidate authorization was a disposable registered-source/workspace flow with source inspection, deploy/replace, run, bounded diagnostics and uninstall on that one managed instance, plus removal of the workspace/source and revocation of its short-lived credential. Server-side source/target constraints and narrow tool filtering would both be required. The existing grant was read-only.

After approval to proceed, inspection found no configured development-source root/mount and no registered sources. Current MCP workspace creation accepts registered local-directory sources, not the uploaded ZIP artifact. A permission grant alone could not complete the flow; infrastructure/configuration changes and restart were outside the bounded authorization. No new grant, preset, credential, target ceiling, registered source or workspace was created. No deployment, reproduction, log diagnosis, repair, redeployment or uninstall occurred. There was no autonomous OpenCode runtime trial and no Codex fix counted as one.

Codex prepared a private disposable `plugin.video.toolkit.phase6.runtime` with a reproducible missing-label exception and uploaded one ZIP through the Web API. It remains an immutable private audit artifact because the API supplies no deletion mechanism. Nothing was installed. Final presets, target policies, sources and workspaces match their pre-test snapshots; the existing read-only authorization is unchanged and no temporary credential needs revocation. A future runtime evaluation requires a separately approved, configured disposable development-source root before any narrower temporary grant is useful.

## Portability and fresh setup

The four Phase 5 Windows skips were three unavailable symlink-creation tests (Windows privileges/environment) and one POSIX drive-path boundary test (test-harness applicability). They were not missing optional dependencies or evidence that validation itself was unsupported. The first full native run exposed two more unguarded symlink assumptions in tests; those were corrected without changing Windows security settings. Cache corruption/absence/incompleteness checks were split out so they still execute. A real native junction test now rejects both internal and escaping junctions at source/evidence boundaries.

The final eleven Windows skips comprise seven symlink-creation tests, two POSIX drive-path tests, one Linux `/proc` process-deadline test and one POSIX newline-filename test. Actual validation, installed mypy/Kodistubs, official checker replay, discovery, report input handling and junction rejection ran on Windows. Native Windows OpenCode/runner process cleanup remains unqualified. macOS was not executed.

A fresh Ubuntu checkout and isolated dependency install passed the documented setup, installed stubs, pip check, metadata acquisition, actual valid/invalid checks, skill discovery, evaluation harness startup and standalone example parsing. All five skills were discovered in actual OpenCode. Effective OpenCode config merges global configuration; the standalone example contains no MCP, but an example cannot disable an existing user's global MCP configuration. No provider request was made for that check.

Native Windows installed the locked distributions in an isolated venv and exercised actual functionality. Its concurrent initial metadata fetch was rate-limited with HTTP 429 after six downloads; no valid partial-cache manifest was published. Actual native validation used an explicitly copied and hash-verified complete official snapshot from the successful fresh Linux acquisition. Windows network metadata bootstrap is therefore not claimed as passing. Offline operation needs installed dependencies plus that explicitly trusted complete cache; no hidden fallback is used. No duplicate Docker engine or system software was installed.

## Release review and acceptance

README, quick start, installation/platform scope, five skill manifests, OpenCode example, optional MCP instructions, Kodi version scope, MIT LICENSE, CONTRIBUTING, SECURITY and ignore rules were reviewed. Toolkit code/fixtures are original MIT; independently installed Kodistubs/addon-checker retain GPL-3.0-only. All 24 pinned dependency versions match their inventory. No proprietary KodiAI code/prompts or Kodi binaries are bundled. The only binary candidates are generated fixture PNG icons; the new control uses the existing fixture icon. No private configurations or media-library data were found.

Working-tree, actual staged-index and full reachable Git-history scans passed, including exact matches for three known private credentials, with no findings. Manual candidate/diff review found no personal endpoints, production data or sensitive transcripts. This is a bounded scan and review, not proof against every possible secret or unreachable Git object. Private evidence remains outside Git. There is no serious known licensing problem in the source-only release; combining/redistributing dependency distributions requires their own notices and obligations.

| Mandatory criterion | Qualification |
|---|---|
| Existing deterministic regressions pass | PASS, with platform skips explicitly scoped |
| Faithful official addon-check results | PASS; actual errors/warnings and infrastructure failures retained |
| Insufficient review evidence identified | PASS; arbitrary semantic claims unverified, never structurally confirmed |
| Invalid paths cannot be verified files | PASS for tested traversal, missing paths, symlink/reparse/junction boundaries |
| Incomplete agent tasks cannot report success | PASS for recorded reports/gates; raw prose remains unverified |
| Clean standalone setup works | PASS on Ubuntu; actual Windows core also tested with explicit cache |
| No known credentials/serious licensing blockers | PASS within the scan/source-only distribution scope |
| Tested/untested capabilities documented | PASS; runtime/native agent/macOS limits explicit |
| Model limitations disclosed | PASS; failures and prototype scope corrections retained |
| No serious Phase 6 regression | PASS in applicable regression/controlled tests |

There are no remaining blockers for the selected standalone public beta. Broader runtime support is blocked by missing authorized infrastructure; Windows native agent execution, macOS and other Kodi majors require actual qualification before support claims. General contextual correctness, spontaneous skill routing and small-model autonomy remain experimental, not release guarantees. The toolkit cannot guarantee AI code correctness or compatibility with every Kodi version.

## Reproduction and publication proposal

Use the README's Python 3.12 isolated hash-locked installation first, then:

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/fetch-indexes.py --cache .local/index-cache
.venv/bin/python -m kodi_agent_toolkit.cli validate fixtures/valid/script.toolkit.sample --branch nexus --cache .local/index-cache > .local/validation.json
.venv/bin/python -m kodi_agent_toolkit.cli report-build fixtures/valid/script.toolkit.sample --validation .local/validation.json --markdown
.venv/bin/python -m kodi_agent_toolkit.cli validate fixtures/invalid-api/script.toolkit.sample --branch nexus --cache .local/index-cache
.venv/bin/python evaluation/scorecard.py
.venv/bin/python evaluation/run.py --help
```

The invalid API command intentionally returns 1. Native Windows substitutes `.venv\Scripts\python.exe`. A fetch failure is incomplete setup, not an add-on defect; use a separately verified complete snapshot explicitly or retry later. Model reproduction uses a new private label, the evaluation guide's narrow scope, `--condition skill`, and `--task review-clean`, `review-composed`, `review-redacted` or `api-fix-nexus` with a privately configured model ID. Preserve all generated artifacts and independently review the answer. A fresh label does not guarantee an identical model response.

Proposed future publication steps, **not executed**:

1. Review the committed candidate and external workstation results, then explicitly authorize publication.
2. Create an empty public `kcook98765/kodi-agent-toolkit` repository, without generated README, license or ignore file. Enable a private security-reporting channel and update SECURITY/README to its actual URLs in a reviewed local commit.
3. Fast-forward the local `main` branch to the approved Phase 6 commit; add `https://github.com/kcook98765/kodi-agent-toolkit.git` as origin. Re-run the staged/history scans and standalone quick start on the final approved bytes.
4. Push `main` only after that authorization. Create an annotated `v0.1.0-beta.1` tag on the approved commit, then publish a GitHub prerelease describing supported/experimental scope and runtime BLOCKED status. Do not attach venvs, dependency wheels, caches, private evidence or Kodi binaries.
5. Test the public clone URL and installation instructions, then invite bounded beta feedback with sanitized reproduction fixtures.
