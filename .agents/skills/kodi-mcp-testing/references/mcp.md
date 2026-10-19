# MCP test boundary
The server enforces client preset, exact target grants, credential validity and target policy. Client filtering minimizes schemas and cannot replace those boundaries. Use discovery then stable UUIDs. On a rejected saved UUID, discover once; do not infer existence or bypass authorization.
Recommended read-only profiles:
- Health/UI: target_list, target_status, inspect_ui_state.
- Add-on support: those plus addon_list.
- Visual: target_list, inspect_ui_state, screenshot_capture with a verified image model.
A deployment smoke test requires authorized deployment tools, target isolation, revision receipt, install/launch evidence, observations and a documented cleanup plan. Do not broaden server permissions as part of a skill.
UI controls are semantic: select can remove a menu item or toggle a setting. A no-settings navigation task needs separate narrowly scoped authority and state guards; read-only defaults never navigate. Stop at arrival. Do not use extra request IDs just because they are supplied.
Bug evidence: target/version/revision, reproduction, tool and arguments, bounded sanitized result, expected behavior, uncertainty and retry count. Keep sensitive screenshots/logs private.
Workstation pilot: only Kodi 20.5 was runtime-tested. The external runtime environment and credentials are never copied to this toolkit.

## Efficient development loop

Use the installed server's exposed schemas and existing grants. Discover the intended target/version with `target_list` and the source with `development_source_list`; use `workspace_status` to find or resume the matching owned workspace before creating another. Inspect only the tree/files needed for the task. Missing source registration, grants or target setup is an operator blocker; report it without inventing IDs, changing permissions or recreating infrastructure.

1. Record the workspace, source, target and current generation. For a new workspace, establish its initial validation/deployment baseline before diagnosing a later change; do not repeat a verified baseline on resume.
2. Group related edits, carrying forward the generation returned by each edit. Validate the resulting generation with `workspace_validate`; static validation does not prove runtime behavior.
3. Deploy that exact validated generation with `workspace_deploy`. Confirm completed deployment and matching target/add-on evidence before executing. An accepted request, healthy target or unchanged add-on version alone is not deployment proof.
4. Run one authorized, relevant smoke test against the same target/generation, using `workspace_execute` when its fixed smoke operation fits the task. Record its completed outcome; deployment alone is not functional acceptance.
5. Recheck only changed behavior or failed/stale evidence. On an ordinary generation conflict, refresh status and the affected file before editing again; revalidate the new generation before deployment.

For an in-progress operation, retain its request/operation ID and inspect status using the installed server's documented completion mechanism. A timeout or ambiguous result does not prove failure. Preserve the receipt and uncertainty; do not resubmit a mutation, create a replacement workspace or invent a new request ID to force progress. Report any reconciliation or administrator action required. Stop once the requested result is verified.

## Launching and relaunching an add-on

Identify the manifest-declared script/plugin entry point and intended destination before navigating. A package with both extensions can open its plugin directory from a generic Run action even when the test needs its custom script window. Verify the actual destination rather than treating any successful invocation as GUI acceptance.

Prefer an authorized managed launch operation when the installed server supports the intended entry point. `workspace_execute` is a bounded smoke workflow, not a generic launcher: check its documented eligibility before using it for a script or multi-extension package. Record an unsupported entry point once and use the supported fallback; do not repeat the incompatible operation after each edit or change the manifest merely to satisfy it.

When menu navigation is required, find the shortest working route once and retain its labels, starting state and expected destination with the test evidence. Reuse an add-on-provided launch item, or a verified favourite if creating one is within the task's authority. Confirm that the shortcut opens the intended entry point. Before replaying a route, check current UI state; adapt if a dialog, skin or menu changed. Reuse deployment evidence and the route across iterations without rediscovering the whole add-on inventory.

Use structured UI state for navigation decisions and screenshots for visual questions. Keep remote actions ordered; use a bounded action sequence only if the exposed interface explicitly supports it, otherwise call actions sequentially. Observe at state transitions and before a consequential selection; do not add a screenshot/model round trip after every arrow by habit. Neither successful dispatch nor a plugin listing proves the expected custom window loaded. Keep launch latency separate from add-on callback/render measurements.

If an action response already contains fresh, sufficient UI state, use it rather than immediately requesting the same observation again. Reuse an action's screenshot only through a supported authorized retrieval mechanism; capture metadata alone is not an image. For a capture-in-progress result, follow documented status/retry semantics and never resend a navigation action just to recover its image. Generic custom-window state or null labels may still require a visual check.

Keep full receipts, logs and inventories in the appropriate private/project evidence store. Carry a concise checkpoint containing the current/deployed generations, operation IDs, unresolved outcomes, next test and verified launch route across long sessions. Limit routine tool output to results, retained warnings and artifact references; read full details for the failure or visual question being investigated. Preserve required checks and exact-generation provenance.
