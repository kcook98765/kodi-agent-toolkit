# Phase 7 — public beta release preparation

Recommendation: **READY TO PUBLISH — AWAITING USER APPROVAL**, for the documented standalone scope only. No repository, push, published tag or release has been created. Fresh Phase 7 metadata network acquisition failed; actual checker verification used an explicitly trusted complete Phase 6 official snapshot. This limitation is retained below, not counted as a network setup pass.

## Starting state and preservation

Verified clean `phase6/evidence-beta` at `a64c11e846314677feb08ab2179d20d244c01f0b`, with zero remotes. Read the external Phase 5/6 reports and installation journal, repository reports, skills, installation/validation documentation, dependencies, security and licensing evidence. Phase 6 remains ready for its bounded standalone beta; runtime deployment remains BLOCKED/unvalidated and 13 agent judgments remain 2 PASS, 6 PARTIAL, 5 FAIL. Phase 5's 34 judgments and Phase 4's 42 original judgments are preserved.

The original development repository/branches remain unchanged. A separate public snapshot uses `main` with one new root commit and no parent development commits. The exact final SHA, local paths, audit manifests and private logs are recorded in the external PHASE7-RESULTS.md; a committed report cannot contain its own commit hash. No Kodi Lab checkout/service, native Kodi profile, model endpoint, provider credential, operating-system security setting, or WSL resource setting was changed or contacted by this phase.

## Complete history audit and publication decision

Audited all three reachable development commits, all commit metadata, each historical tree/path, all 123 distinct reachable file blobs and all 225 existing Git objects (200 reachable, 25 dangling blobs). There are no removed historical file paths. Byte scans include three known private credential values, common tokens/private keys, private IP/host forms, personal home paths, emails, endpoint URLs and credential assignment candidates. Author identities are generic `Kodi Toolkit`/`Kodi-Toolkit` with `toolkit@localhost`. No known secret or personal home path was detected. The largest blob is a sanitized numeric Phase 5 scorecard (168,489 bytes); one 2,200-byte generated PNG blob is the only nontext content, shared by six fixture paths, visually inspected with no metadata. No Kodi package/binary or third-party vendored code was found.

The public release uses a **reviewed initial snapshot**, because historical harness source contains workstation provider aliases, loopback observer routing and implicit token-file discovery that do not belong in a portable first release. This is a conservative publication choice, not a claim that a live credential was committed. Original history is neither deleted nor rewritten. The new harness requires explicit provider/model IDs, removes the private observer hook and reads exact redaction values only from explicitly named private files. Its existing workflow and deterministic modules are preserved. Original scorecards, fixtures, skill bodies, validation/evidence/reporting source, dependency lock/inventory and MIT LICENSE remain byte-identical; historical report headers identify provenance-only commit references. No new model-optimization work or feature phase was conducted. `.gitattributes` preserves LF text and binary PNG bytes so Windows Git checkout does not invalidate recorded hashes.

## Intended public contents

The exact reviewed candidate paths are in [publication-files.txt](publication-files.txt). Include all five portable skill directories/references; Python source and fixed helper scripts; optional OpenCode fixture adapters; original sample/invalid/review fixtures; deterministic tests; evaluation runner, tasks, scorecards and sanitized Phase 4–6 reports; safe example configs; README/environment/stubs/validation/skills/evaluation/licensing/limitations documents; MIT license; contribution/security/conduct policies; issue/PR templates; funding metadata; minimal CI; changelog and beta notes.

Exclude ignored environments, downloaded dependency wheels, SDK/node_modules, official metadata caches, private configuration/credentials, model endpoints, raw transcripts, runtime diagnostics, library metadata, Kodi profiles/packages/binaries, machine state and the external workstation journal. The snapshot is copied only from reviewed tracked source and explicitly prepared publication files; no original `.git` or ignored state is copied. Future push must target only snapshot `main`, never mirror the development repository.

## Installation and regression results

| Check | Executed result |
|---|---|
| Clean Ubuntu 24.04 / Python 3.12.3 snapshot + venv | Public PyPI hash-locked installation, editable install and pip check PASS; no private dependency index/config used |
| Clean native Windows 11 / Python 3.12.3 snapshot + venv | Same installation and pip check PASS; independent native venv |
| Linux regressions | 172 tests: **171 passed, 1 native-Windows junction case skipped** |
| Windows regressions | 172 tests: **161 passed, 11 explained platform skips** |
| Actual Kodi stubs/mypy | Valid fixture passes; invalid logging-level fixture returns expected 1 on both platforms |
| Actual official checker and factual report | Valid Nexus fixture passes six stages with two original warnings; trusted report PASS, on both platforms |
| Negative controls | Invalid API/XML fixtures return 1; missing cache returns 2, on both platforms |
| Discovery/review context | CLI enumeration and numbered context PASS on both platforms |
| Evaluation harness | Help/startup, historical scorecard invariant, offline dummy process deadline and private-redaction regressions PASS; no new inference batch |
| Example configs | All three valid JSON and current official OpenCode schema; all parsed by isolated reference OpenCode 1.19.0 with synthetic placeholders; no private settings or provider calls |
| Portable skills | Five frontmatters/references valid and five actually discovered by isolated OpenCode |
| Community/CI files | YAML parsed; issue forms and permissions reviewed; hosted Actions run pending publication |
| Metadata network bootstrap | **Did not pass in Phase 7**: Ubuntu mirror routing failed with network-unreachable errors; Windows got HTTP 429 after nine indexes; no partial-cache manifest accepted |

Checker runs explicitly copied the complete official snapshot acquired by Phase 6's successful fresh Ubuntu network setup, verified all ten sizes/SHA-256 values, then validated the cache with the toolkit loader. Manifest SHA-256: `7dafd8864d6740d9efaa307ef880a6b2b57390f2ac68651965458806a71a9bd8`; acquisition `2026-10-14T00:44:05.791208+00:00`. This is explicit offline setup with a trusted official snapshot, not new Phase 7 network bootstrap. README instructs users to stop/retain fetch errors, retry or explicitly supply a separately trusted complete cache. The unchanged fetch script passed fresh network setup in Phase 6; current external routing/rate-limit failures do not make offline validation a code failure. Public clone/download availability awaits publication.

An initial Linux regression still patched the removed workstation model-alias table; it failed and was retained, then the existing deadline test was updated to pass an explicit dummy provider/model ID. Initial checker commands were attempted before network acquisition completed and correctly returned incomplete-cache failure; those results were retained separately before the explicit cache rerun. A later real native Git clone converted text to CRLF: the suite passed but the immutable scorecard correctly failed. `.gitattributes` now enforces LF and preserves PNG bytes; final native clone verification uses the corrected source. Local UNC Git-clone attempts also failed ownership checks; a verified one-ref Git bundle was used for the native clone instead, without changing any global Git trust setting. Neither is a model trial or a hidden pass. Windows skips: seven unavailable symlink-creation cases, two POSIX drive-path cases, one Linux process-deadline case, one POSIX newline-filename case. Real Windows junction rejection ran. macOS, independent Linux hosts, native Windows OpenCode execution/cleanup and other Kodi major environments were not tested.

## Security and licensing

Original history working-tree/index/reachable scans passed with three known private values. Final candidate worktree/index and actual initial-snapshot history scans and object audit are recorded after the local commit in the external report. Scans are bounded heuristics/exact-value checks plus content review, not proof against every possible secret or future vulnerable dependency. Public examples contain env/file placeholders only; optional inspection MCP is disabled until privately configured and authorized. All 24 installed distribution versions match the lock/inventory. MIT LICENSE is unchanged; GPL-3.0-only Kodistubs/checker are installed separately, not vendored. KodiAI proprietary code/prompts are absent; factual Kodi references and optional SDK attribution are documented in [licensing](licensing.md). Redistribution of dependency/runtime bundles would require separate license review. No unqualified claim of vulnerability-free dependencies is made.

## GitHub readiness and proposed release

Authenticated owner `kcook98765` verified. Proposed name `kodi-agent-toolkit` returned authenticated 404 and was absent from the owner's repository listing. Sponsors listing exists and its public page returned 200; `.github/FUNDING.yml` uses `kcook98765`. Availability is not reserved and must be rechecked. Metadata, settings and exact proposed operations are in [github-publication.md](github-publication.md). Version recommendation: `v0.1.0-beta.1`, Python metadata `0.1.0b1`. [Release notes](release-notes-v0.1.0-beta.1.md) cover installation, separately installed dependencies, supported scope, experimental integrations and retained failures.

The two small CI jobs need only public locked dependencies and offline fixtures; no secrets, model APIs, Kodi Lab, Docker or Kodi. Official Actions are pinned, token permissions read-only, job timeout 10 minutes; no scheduled model runs or release automation. Actual GitHub-hosted CI remains unexecuted until approval/publication.

## Limits and approval gate

No dependable autonomous development claim. General contextual correctness, coverage and model prose remain unverified; structural anchors do not establish semantics or runtime exposure. Latest runtime deployment/reproduction remains unvalidated because required registered-source infrastructure was absent. Deterministic success supports only its observed static scope. Fresh network setup can fail at mirrors/rate limits and did so here. No macOS/native Windows agent or broad Kodi-major support is claimed.

After explicit approval: recheck owner/name and approved SHA; create an empty public repository; enable private security reporting and apply metadata; push snapshot `main`; verify public clone/installation and hosted CI; then, only within approved operations, publish the annotated beta tag and GitHub prerelease with no extra binary assets. If source changes are required, review the new commit first. Nothing remote has been written in Phase 7.
