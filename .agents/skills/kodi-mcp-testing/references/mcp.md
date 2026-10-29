# MCP test boundary

For current input/result shapes, preflight, receipt ordering, activation limits and failure handling, read [current contracts and recovery](current-contract.md).
The server enforces client preset, exact target grants, credential validity and target policy. Client filtering minimizes schemas and cannot replace those boundaries. Use discovery then stable UUIDs. On a rejected saved UUID, discover once; do not infer existence or bypass authorization.
Recommended read-only profiles:
- Health/UI: target_list, target_status, inspect_ui_state.
- Add-on support: those plus addon_list.
- Visual: target_list, inspect_ui_state, screenshot_capture with a verified image model.
A deployment smoke test requires authorized deployment tools, target isolation, revision receipt, install/launch evidence, observations and a documented cleanup plan. Do not broaden server permissions as part of a skill.
UI controls are semantic: select can remove a menu item or toggle a setting. A no-settings navigation task needs separate narrowly scoped authority and state guards; read-only defaults never navigate. Stop at arrival. Do not use extra request IDs just because they are supplied.
Bug evidence: target/version/revision, reproduction, tool and arguments, bounded sanitized result, expected behavior, uncertainty and retry count. Keep sensitive screenshots/logs private.
Historical workstation pilot: only Kodi 20.5 was runtime-tested in that pilot. It predates the current contract audit and does not describe current installed infrastructure. The external runtime environment and credentials are never copied to this toolkit.

## Efficient development loop

Use the installed server's exposed schemas and existing grants. Discover the intended target/version with `target_list` and the source with `development_source_list`; use `workspace_status` to find or resume the matching owned workspace before creating another. Inspect only the tree/files needed for the task. Missing source registration, grants or target setup is an operator blocker; report it without inventing IDs, changing permissions or recreating infrastructure.

1. Record the workspace, source, target and current generation. Record existing validation/deployment evidence and assess current prerequisites. If a source baseline is missing, follow the preflight's stated administrator preparation path only with applicable mutation authority; do not automatically deploy or repeat a verified baseline on resume.
2. Group related edits, carrying forward the generation returned by each edit. Validate the resulting generation with `workspace_validate`; static validation does not prove runtime behavior.
3. Read `workspace_deploy_preflight` for that workspace, exact generation and target. Its durable-prerequisite verdict is blocked or unknown, never ready; follow the stated actor/preconditions without treating it as admission. When separately authorized and eligible, deploy that exact validated generation with `workspace_deploy`. Confirm completed deployment and matching target/add-on evidence before executing. An accepted request, healthy target or unchanged add-on version alone is not deployment proof.
4. Run one authorized, relevant smoke test against the same target/generation, using `workspace_execute` when its fixed smoke operation fits the task. Record its completed outcome; deployment alone is not functional acceptance.
5. Recheck only changed behavior or failed/stale evidence. On an ordinary generation conflict, refresh status and the affected file before editing again; revalidate the new generation before deployment.

For an in-progress operation, retain its request/operation ID and inspect status using the installed server's documented completion mechanism. A timeout or ambiguous result does not prove failure. Preserve the receipt and uncertainty; do not dispatch another mutation, create a replacement workspace or invent a new request ID to force progress. Report any reconciliation or administrator action required. Stop once the requested result is verified.

## Registered-source batch import

When reviewed changes are already in the registered source mirror, prefer
`workspace_import_preview(workspace_id, expected_generation)` over individual
file edits. Lab does not read arbitrary paths on the agent's computer. Import
requires workspace edit and source inspection permissions, the exact source
grant and the client's workspace binding; an available tool grants none of these.

Review the preview's paths, sizes, hashes and rejections. Pass its `source_digest`
and `preview_digest` to `workspace_import` with the same workspace/generation and
a fresh UUID `request_id`. The accepted batch creates one generation; validate
and deploy that exact returned generation separately. Import does not run Kodi.
A changed source or workspace requires a fresh preview.

At the audited source revision the limits are 32 changed entries and 256 KiB per UTF-8 file; use the preview's advertised bounds. Parents must already exist.
Default `changes` mode rejects deletions, binary files, identity/mode changes and overlapping private edits without partial application. A later import can update a previously
imported file while its workspace bytes still match the prior import receipt.
Use `workspace_edit` for eligible focused private changes; preserve existing
private edits and import history instead of resetting them to force an import.

When exposed and explicitly intended, `mode="reviewed_tree"` in both preview and apply supports reviewed workspace file removals and exact per-path conflict choices (`take_source` or `keep_private`). Review the resolved preview and repeat its mode, resolutions, source and preview digests exactly in apply. No wildcard force exists; directory/type/mode/identity changes remain unsupported. `matches_source=true` describes the staged private tree, while retained private choices describe a reviewed merge. These removals do not authorize deletion of installed Kodi destination files. See the maintained [batch-import contract](https://github.com/kcook98765/kodi-lab/blob/main/docs/WORKSPACE-BATCH-IMPORT.md).

After a lost import response, repeat only the identical request UUID and
parameters to recover its receipt through the documented idempotent recovery.
That recovery does not capture newer source bytes or dispatch the import again.
Retain `reconciliation_required` outcomes for administrator review; do not replay
an uncertain import with a new request ID.

## Launching and relaunching an add-on

Identify the manifest-declared script/plugin entry point and intended destination before navigating. A package with both extensions can open its plugin directory from a generic Run action even when the test needs its custom script window. Verify the actual destination rather than treating any successful invocation as GUI acceptance.

For an already deployed add-on on a managed disposable development target, prefer
`workspace_launch` when exposed and authorized. Use a fresh `request_id`,
`workspace_id`, exact `expected_generation`, `target_id` and the chosen
`extension_ordinal` from validation's `launch_entries`. Ordinals follow manifest
order starting at zero; discover them instead of assuming the script/plugin order.
Reuse valid validation/deployment evidence for unchanged bytes. A legacy validation
may need one refresh to publish launch entries.

Launch requires target control and development execution authority, current
workspace/source bindings, usable Kodi, enabled matching installed bytes and a
compatible trusted managed Bridge. It cannot launch external/production targets
or start Kodi. Updating Lab alone does not upgrade an installed Bridge. An
`accepted` receipt proves dispatch only; inspect the intended destination and
feature behavior. Recover an uncertain launch using its identical request and
documented receipt mechanism; do not issue a new launch or menu invocation while
dispatch remains ambiguous.

If deployment is independently verified and a direct launch is definitively
rejected before dispatch, such as `launch_not_deployed`, retain the rejection and
use an already authorized, verified menu route when available. Do not repeatedly
redeploy unchanged bytes, reset the workspace or alter the manifest to force the
launcher. Missing authority or unverified deployment remains a blocker.

`workspace_execute` is a bounded smoke workflow, not a generic launcher: check its documented eligibility before using it for a script or multi-extension package. Record an unsupported entry point once and use the supported fallback; do not repeat the incompatible operation after each edit or change the manifest merely to satisfy it.

When menu navigation is required, find the shortest working route once and retain its labels, starting state and expected destination with the test evidence. Reuse an add-on-provided launch item, or a verified favourite if creating one is within the task's authority. Confirm that the shortcut opens the intended entry point. Before replaying a route, check current UI state; adapt if a dialog, skin or menu changed. Reuse deployment evidence and the route across iterations without rediscovering the whole add-on inventory.

Use structured UI state for navigation decisions and screenshots for visual questions. Keep remote actions ordered; use a bounded action sequence only if the exposed interface explicitly supports it, otherwise call actions sequentially. Observe at state transitions and before a consequential selection; do not add a screenshot/model round trip after every arrow by habit. Neither successful dispatch nor a plugin listing proves the expected custom window loaded. Keep launch latency separate from add-on callback/render measurements.

## Action observations and correlated screenshots

On managed development targets, request `remote_action(observe_ui=true)` when the
installed schema supports it and the client has inspection authority as well as
control. Reuse a fresh, sufficient `post_action_observation` for the next decision
instead of immediately requesting the same UI state again. Observation status,
time and `changed_during_collection` still determine whether the result is usable;
observation failure does not change the action's outcome.

When pixels are needed, use `screenshot_retrieve` on the original client connection
with that action's exact `target_id`, original `request_id` and `capture_id`.
Current visual authority and the same runtime identity are required. Retrieval
returns the correlated frame without a new capture or navigation. Images expire
after two minutes and can be replaced sooner; an unavailable frame is not newer
visual evidence and does not justify repeating the action. Recover the original
receipt through its documented mechanism or request a fresh authorized observation
when needed. These capture-reuse tools initially cover managed development only.

Capture metadata alone is not an image. For a capture-in-progress result, follow
documented status/retry semantics without resending navigation to recover pixels.
Generic custom-window state or null labels may still require a visual check.

Keep full receipts, logs and inventories in the appropriate private/project evidence store. Carry a concise checkpoint containing the current/deployed generations, operation IDs, unresolved outcomes, next test and verified launch route across long sessions. Limit routine tool output to results, retained warnings and artifact references; read full details for the failure or visual question being investigated. Preserve required checks and exact-generation provenance.

Contract references: [batch import](https://github.com/kcook98765/kodi-lab/blob/main/docs/WORKSPACE-BATCH-IMPORT.md), [manifest-entry launch](https://github.com/kcook98765/kodi-lab/blob/main/docs/MANIFEST-ENTRY-LAUNCH.md), [action observations](https://github.com/kcook98765/kodi-lab/blob/main/docs/REMOTE-ACTION-OBSERVATIONS.md). Discover the installed schemas and contract when they differ.

## Retained development-version selection

The Lab `0089` feature is administrator opt-in and keeps four approved version profiles with at most one running. To switch, use `managed_release` for the current use hold, verify all Kodi instances are stopped (release is not guaranteed stop), and settle all pending/ambiguous operations. In the already selected owned workspace, call `managed_selection_preview(target_id, workspace_id)`, then `managed_select` with a fresh request UUID, the exact preview `identity` and `expected_generation=latest_generation`. Historical replay can report `selected=false`. Selection never starts or provisions; separately authorized `managed_ensure_ready` may start an already provisioned selected instance. No source/workspace/Bridge/baseline/receipt is copied between versions. Both selection calls need `managed.lifecycle` and `workspace.inspect`, exact grants and admin-enabled retained mode; see [pinned contract](current-contract.md) and the [Lab workflow](https://github.com/kcook98765/kodi-lab/blob/main/docs/RETAINED-DEVELOPMENT-WORKFLOW.md).
