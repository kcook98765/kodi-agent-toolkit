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
