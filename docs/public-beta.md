# Bounded public beta scope

This toolkit assists an individual Kodi add-on developer. It cannot guarantee AI-generated code correctness, repository acceptance, runtime behavior, or compatibility with every Kodi release.

| Scope | Capabilities and evidence |
|---|---|
| Supported | Five portable Agent Skills with valid discovery/frontmatter and documented explicit loading; Kodi 20 stubs setup; pinned official addon-check integration; standalone static validation/discovery; deterministic fixtures and regression tests; reports built from trusted recorded results. |
| Experimental | AI contextual review, autonomous add-on repair, smaller-model workflows and optional Kodi Lab inspection/development integration. Models still fabricate claims, misuse schemas, omit steps, exceed budgets and produce inaccurate explanations. |
| Not yet supported | Qualified end-to-end Kodi Lab deployment/repair; native Windows OpenCode agent execution/process cleanup; macOS execution; other Kodi major-version environments; guaranteed spontaneous skill routing; exhaustive semantic or compatibility validation. |

The full static CLI/dependency installation was exercised on Ubuntu 24.04 WSL2 and native Windows 11 with Python 3.12. Other Python/OS versions require qualification. Linux is the OpenCode reference environment (1.19.0 with matching separately installed SDK). Native Windows junction rejection is tested without enabling symlink privileges. Platform-specific skipped tests remain disclosed in the Phase 6 results.

Contextual input has four output categories: confirmed deterministic error, evidence-supported contextual issue, recommendation and unverified observation. Structural acceptance proves only safe existing paths, in-range individual lines and exact quotes. The independent helper supports one conservative adjacent setting-to-log pattern with a matching concealed settings declaration. It emits conditional canonical prose, retains model prose separately and never proves actual sensitive content or execution. All other defect interpretations require independent review. Documentation basis IDs identify sources, not applicability. Duplicate anchor/category records and exact checker messages are recorded separately; arbitrary paraphrase equivalence is unverified.

Use `finding_categories` and recorded final reports as the factual result. Do not quote the model's final answer as validation evidence. A source/contract pass cannot override official checker results, certify runtime impact or establish blocker severity. `report-build` accepts trusted operator/tool records; hashes detect stale source rather than forged input. A hand-written or model-authored record is not verified by becoming JSON.

AI contextual reports remain PARTIAL while general semantics require independent review; static checks have their own `static_outcome`. An empty valid draft and a complete model reply do not certify complete contextual review. Repairs can report PASS when the recorded reproduction, exact change, target-consistent rechecks and completion gates establish that bounded task.

Recommended installation: use the README's Python 3.12 venv and hash lock, acquire the official metadata snapshot once, validate the sample, then copy only the relevant skill directory into your add-on project. The CLI is useful before configuring any model. OpenCode adapters are optional fixture-scoped evaluation tools; ordinary projects can use the independent CLI. Keep provider credentials private and explicitly load the relevant skill. Kodi Lab remains optional and requires separately scoped server authorization.

Dependencies/network: initial wheel and metadata acquisition needs network access. Later CLI validation, discovery, review anchoring and deterministic regressions operate offline with installed dependencies and an explicit trusted metadata cache. Metadata acquisition can fail due to network/server limits (including an observed HTTP 429); retain the failure and use a separately verified existing cache explicitly or retry setup later. No incomplete snapshot is accepted and no implicit fallback/download occurs during validation.

Historical beta runtime deployment qualification is reported separately as BLOCKED: the tested lab had a read-only grant and no configured registered-development-source root. User approval for a bounded temporary test did not make that infrastructure available. No deployment, execution or agent runtime repair occurred. This limits the experimental integration; it does not block the supported standalone beta.

The [2026-10-29 workflow refresh](development-workflow.md) updates instructions against the installed Lab contract and OpenCode 1.19.3 discovery. It preserves this beta's CLI/schema/dependency guarantees and original evaluation artifacts. Source/native Lab acceptance is separate evidence; no new live toolkit deployment or agent runtime repair is claimed. Existing grants and agent permissions continue to determine availability.
