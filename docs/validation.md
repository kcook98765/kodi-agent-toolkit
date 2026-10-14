# Deterministic validation
Run from the toolkit root after the README's isolated, hash-locked installation.

```sh
.venv/bin/python -B scripts/fetch-indexes.py
.venv/bin/python -m kodi_agent_toolkit.cli validate fixtures/valid/script.toolkit.sample --branch nexus --cache .local/index-cache
.venv/bin/python -m kodi_agent_toolkit.cli validate fixtures/invalid-xml/script.toolkit.sample --branch nexus --cache .local/index-cache
.venv/bin/python -m kodi_agent_toolkit.cli validate fixtures/invalid-api/script.toolkit.sample --branch nexus --cache .local/index-cache
.venv/bin/python -m unittest discover -s tests -v
```

The first command is an explicit network setup action. It acquires only ten official HTTPS addons.xml.gz metadata indexes, validates gzip/XML and records sources, acquisition time and SHA-256. No add-on ZIPs or Kodi packages are downloaded. Refresh requires --refresh; it replaces only the named cache snapshot. On another machine choose --cache PATH and pass the same --cache to validation. A hash detects corruption against this locally trusted manifest, not malicious replacement of both files.

Why replay? Official kodi-addon-checker 0.0.36 fetches all ten indexes even with --skip-dependency-checks and sends metadata HEAD requests. No documented offline switch exists in this version. The original wrapper runs the installed official CLI entry point in a fresh subprocess/scratch copy and replays only exact index GETs. Other network/child-process requests fail closed. HEAD checks become the checker's original warnings and remain unverified. No installed checker source is patched or vendored. This guard is an application-level restriction for the reviewed checker, not a sandbox for hostile third-party programs.

AST parsing, XML/manifest paths, package identity/license and mypy are separate stages. Kodi source is never imported or executed. Symlinks, traversal, oversized trees and .tests-config.json are rejected; the latter can disable checks. Type coverage requires a matching stub major. Only Nexus with Kodistubs 20.0.1 was qualified; other targets need their own isolated matching environment and runtime tests.

JSON retains original checker stdout/stderr, official exit code, individual diagnostics, counts, cache provenance and coverage limits. Exit 0 means all requested static stages passed; warnings are still reported. Validation preserves its reported returncode: failed checks ordinarily use 1; infrastructure/cache setup failures can use 2. Review contract failure uses 1 and uncaught CLI infrastructure exceptions use 2. Missing cache, a traceback, a skipped stage or a timeout is never a pass. Upstream malformed XML can crash: the wrapper preserves that original failure while separately reporting its XML parse error.

Expected fixtures:
- valid: pass; unverified example.org source URL and advised Nexus xbmc.python 3.0.1 are two official warnings.
- invalid-xml: malformed closing tag at addon.xml:3, parse failure and upstream traceback.
- invalid-api: default.py:7 passes a string where xbmc.log expects an integer; mypy fails.
- review: deterministic checks pass with the same two warnings; contextual privacy data flow requires source review.

The OpenCode adapter preserves original diagnostics but has narrower authority than shell: fixed Python/CLI, fixture-only paths and an explicit pre-existing cache. It never installs dependencies, deploys or executes add-on code.

The optional adapter removes duplicate streams and per-index metadata from the model response to reduce context. It retains original diagnostic stdout/stderr, failures and counts, cache snapshot hash/time and all coverage limits. Full provenance remains available through the independent CLI. Every adapter response records full_cli_bytes and compact_payload_bytes (the compact JSON payload, not the whole transport envelope); byte savings are not claimed as tokenizer savings.

Canonical combined review: review-compose runs the checker independently, discards draft deterministic claims and takes literal official error/warning messages from the original checker. It returns the complete validation/contract reports and marks model semantics human-required. The compose adapter accepts a verified branch and defaults to Nexus; it reports compact statuses while the CLI retains full original streams. Coordinate checks cannot certify severity, confidence or semantic truth.

Discovery: `kodi-toolkit discover [DIRECTORY]` is a read-only bounded scan of actual project markers, manifests and files. `entry_points[].exists` distinguishes a declared existing file from an unresolved reference. `passed` means a manifest was found, not that it parses or validates; inspect `manifest_error`, `complete` and `omitted`. Source location records are inventories, not runtime evidence. The optional adapter exposes this as `kodi_validate operation=discover`; omit addon_dir to discover within its fixed fixtures root. Adapter paths resolve against the actual worktree rather than a nested session directory.

Review schema 1.3 keeps source-supported input compatible and optionally records `requirement_basis`. Demonstrated claims require reproduction steps/observed/expected; unresolved claims can only be advisory and source-supported claims cannot be blockers. `accepted_findings` means structural acceptance only; composition's `finding_categories` independently separates supported conditional observations from recommendations, duplicates and unverified claims. Composition distinguishes `static_passed`, `contract_passed`, status and `passed_scope`; a rejected draft never changes canonical checker success into an official failure.

The OpenCode review adapter accepts a preferred structured `report` draft (the four top-level schema fields), or legacy `report_json`; supplying both is rejected. Native serialization avoids the extra escaped-JSON parsing layer. Structural acceptance still checks every finding in the Python contract; a valid transport object is not a valid finding. Static/source-supported findings omit `reproduction`. Only demonstrated claims may supply steps/observed/expected, and these remain author claims until independently tested.

For agents the context adapter supplies numbered files, scalar field descriptions and an empty data-shaped report template. The complete JSON Schema remains in `review-context` CLI output. This avoids reproducing schema `type/const/properties` objects as finding values. The small semantic helper independently supports only adjacent direct reads/logs of a UI-concealed setting; it emits a canonical conditional observation, never proves a secret or execution, and downgrades unsupported severity/requirements. See [beta scope](public-beta.md).

`report-build ADDON --validation RESULT.json [--review COMPOSED.json] [--execution RUN.json] [--before SNAPSHOT.json] [--markdown]` builds concise status from trusted tool records. Saved validation includes hashes of the checked source snapshot. Missing/stale checks are BLOCKED, failing deterministic stages FAIL, incomplete agent work or unresolved review claims PARTIAL, and completed recorded scope PASS. Warnings remain literal. JSON input supports UTF-8 and BOM-encoded UTF-16, including Windows PowerShell redirection. Records are not authenticated; never supply model-authored summaries as tool evidence.

Contextual review remains PARTIAL pending independent general semantic review, even for an empty contract-valid draft. `static_outcome` separately reports actual static checks. This avoids treating a model's claimed coverage or empty findings as proof that the requested contextual review is complete.
