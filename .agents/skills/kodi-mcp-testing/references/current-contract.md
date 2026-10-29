# Current Kodi Lab contract and recovery

Source audit: Kodi Lab `56517d3abd6faf661b990d58e574a94193f8b532`, schema
`0088_service_enable_start` (2026-10-29). This is a dated contract reference,
not a promise that every installed server, client or target exposes these tools.
Discover `tools/list` on the actual authenticated connection. OpenCode normally
prefixes names with the configured MCP server name, for example
`kodi_lab_workspace_deploy_preflight`; use its discovered spelling.

## Calls and evidence

All IDs below are discovered UUIDs. `expected_generation` is the existing observed
generation, never the desired next generation. Inputs are closed: no `force`,
arbitrary command, host path or generic JSON-RPC field exists. Successful tools
normally return `structuredContent`; inspect `isError` and text diagnostics first.
An error may have no success-shaped structured content. Preserve unknown/null
fields rather than fabricating a successful receipt.

| Tool | Inputs to use | Result to retain |
|---|---|---|
| `target_list` / `target_status` | Optional list cursor; status `target_id` | `targets[]` / `target`, `target_id`, class/profile/version, process/JSON-RPC/usability/readiness states, capabilities. Discovery is grant-filtered. |
| `development_source_list` | Optional `cursor`, `limit` | `sources[]`, `source_id`, add-on identity, `availability`, `next_cursor`; registration is not current byte validation. |
| `workspace_status` | Optional `workspace_id`, `cursor`, `limit` | `workspaces[]`, generation, source binding and latest operation evidence. Complete pagination; an empty list supplies no deployable workspace. |
| `workspace_create` | `request_id`, `source_id` | Workspace UUID, creation operation/state and owner binding; no local-path argument. |
| `workspace_tree` / `workspace_read` | `workspace_id`; tree relative path/cursor/limit; read `relative_path`, optional `start_line`, `max_lines` | Observed generation; read SHA-256, truncation/next line; tree next cursor. |
| `workspace_edit` | `workspace_id`, `expected_generation`, `relative_path`, `operation` | `prior_generation`, `new_generation`; create/replace uses only `content`, exact_patch uses only full `expected_text` and `replacement_text`. |
| `workspace_source_scan` / `workspace_capture` (opt-in) | Scan `workspace_id`; capture also `expected_generation` | Source/workspace/capture digests and private-edit indication; capture result operation UUID, generation, tree digest and changed flag. Refresh only through the installed admitted source-capture contract; preserve private edits and history. |
| `workspace_import_preview` / `workspace_import` (opt-in) | Workspace/current generation, mode and exact resolutions; apply additionally request UUID and resolved source/preview digests | Advertised bounds, paths/preimages/rejections and exact staged generation/receipt. See [import workflow](mcp.md#registered-source-batch-import); workspace removals do not imply destination removal. |
| `workspace_validate` | `workspace_id`, `expected_generation` | `observed_generation`, identity classifications, `launch_entries`, `fixed_smoke_eligible`, unsupported reason. Closed structural validation is separate from toolkit official checker/types and runtime testing. |
| `workspace_deploy_preflight` | `workspace_id`, `expected_generation`, `target_id`, optional `deployment_mode` (`auto`/`direct`/`repository`) | `requested_generation`, `current_generation`, `verdict`, typed `checks`, `next_actions`, trust/live-readiness distinctions, optional `activation_assessment`, `reservation_created=false`. |
| `workspace_deploy` | Same scope/mode plus `request_id` | `deployment_id`, source/workspace/target/generation/add-on identities, state/classification, phase/failure/recovery, reconciliation flag, inventory/enabled state and optional `iteration_evidence`. |
| `workspace_launch` | `request_id`, workspace/generation/target, validated `extension_ordinal` | `launch_id`, dispatch/state, completion/UI classifications, replay flag/code/next action. Dispatch is not fresh execution. |
| `workspace_execute` | `request_id`, workspace/generation/target; optional `execution_kind` from discovered enum | `execution_id`, linked `deployment_id`, exact generation, state/classifications, item count and reconciliation flag. `smoke` is the fixed eligible video-plugin check, not generic Python execution. |
| `workspace_execution_recover` | `request_id`, existing `execution_operation_id` | Separate recovery operation UUID and `outcome`; this can stop/start Kodi and is a mutation, not a receipt read. |

Deployment preflight reports durable prerequisites only. Its verdict is **blocked
or unknown**, never ready. It checks stored workspace/validation/source/baseline,
leases, reconciliation and selected-session scope; native/add-on/live Bridge state
remains unobserved. Historical trust and `verified_at_last_operation` do not prove
current bytes/liveness. Bridge absence alone is not a managed direct-copy blocker.
Preflight creates no reservation, performs no preparation and cannot guarantee
later admission. Follow the actor and preconditions in `next_actions`.

Managed direct deployment uses the guarded stopped-copy/restart workflow; it is
not live apply. Retain the complete receipt with exact target, workspace,
generation, source and server-bound runtime/container evidence. `iteration_evidence`
separates file application (`verified_at_operation`) and Kodi restart
(`observed_at_operation`) from unobserved fresh code and unrun functional smoke.
Selective staging still hashes/compares full trees, retains destination-only files
and refuses type replacement. Neither a no-op transfer nor a workspace removal
proves exact installed mirroring.

For unchanged bytes, reuse valid current exact-generation evidence. A separately
requested same-generation deployment may be supported; it still performs admission
and verification. Exact duplicate requests return historical receipts without
probing current runtime. Execution/launch use the latest authoritative deployment
for the selected profile: a newer failed, pending, incomplete or ambiguous attempt
blocks fallback to an older success; tied newest times cannot prove order. Legacy
unbound receipts need fresh verification through the supported workflow, not a
manual receipt edit.

## Separate success states

Report each observed stage independently: target exists; runtime responsive;
Bridge authenticated/trusted/capable; source/workspace validated; durable
prerequisites assessed; deployment admitted; source files applied; activation
dispatched; fresh code observed; functional smoke passed. A stage does not imply
the next one. UI arrival, enabled inventory, restart and unchanged version strings
do not prove fresh callbacks, interpreter state, dependent-module reload or service
health. Use a changed-code marker or task-specific behavior when authorized.

Script/plugin manifest launch is qualified only within its discovered constraints.
Live replacement, generic service stop/reload, selected-skin reload, exact obsolete
file removal and one-call `workspace_apply` are unavailable here. Do not synthesize
them from builtins or direct Bridge access. Existing copied-source Web enablement
has a separate explicit Python-service consent, installed-descriptor proof and
bounded Omega policy. It is not an MCP service-enable tool; enabled state leaves
`service_execution=not_observed`. Native ZIP install retains its human gates;
it is not a generic unattended installation API.

Managed selection/lifecycle and settings tools are separate opt-in capabilities.
A Web Current Kodi selection neither grants access nor supplies an arbitrary MCP
selection API. `managed_ensure_ready` / `managed_release`, when exposed, require
explicit lifecycle authority; Fresh Test/Switch may replace state and is not a
routine retry. External-development repository approval/installation remains
separate from managed direct semantics; production/external targets never inherit
disposable authority.

## Failure decisions

| Observed condition | Safe next step |
|---|---|
| Empty targets, `target_not_found_or_not_authorized`, absent tools or missing source grant | Report unavailable under this credential. Rediscover a rejected saved ID once; do not change presets/grants, rotate credentials or infer a stopped target caused a permission denial. |
| Missing source baseline/attachment | Retain preflight checks. An administrator must use the existing exact stopped-source-copy preparation workflow, after resolving leases/reconciliation and with separate mutation authority. Workspace validation does not establish that baseline. |
| `workspace_generation_conflict` / stale validation | Refresh workspace status and affected content; review competing changes. Validate the actual current generation before a new operation. Do not reset or discard private work. |
| Busy lease, rate limit or selected-session mismatch | Preserve operation identity. Wait/read status as documented, or report administrator review. No forced release, parallel workaround, repeated deployment or target switch. |
| Bridge unavailable, untrusted, incompatible or identity mismatch | Native responsiveness and stored trust are insufficient. Retain exact identities and report the blocked Bridge-dependent stage. No re-pair, direct RPC, alternate credential or implicit upgrade. |
| Lost response / pending / ambiguous mutation | Preserve original request and parameters. Read status; use only documented identical-request receipt recovery. Never mint a new identity to replay an unresolved action, deploy, launch or execution. |
| Managed deployment reconciliation required | Web administrator reviews exact retained operation and performs supported stopped-tree inspection. Contained requested/prior tree proves containment only. A later start/deployment needs its own authority and request after resolution. No workspace reset, DB edit or copy around the fence. |
| Ambiguous execution | Do not re-execute. Explicitly authorized `workspace_execution_recover` addresses the retained execution operation through bounded stop/start and verification, without rerunning the add-on. Its new recovery request is a different operation; retain both identities. `contained_but_not_ready` / `still_requires_admin` are not success. |
| Repeated completed deployment receipt | Check target/workspace/generation/runtime and newest authoritative attempt; retain historical status. Replay is not a new install or liveness test. |
| Unsupported live activation or execution entry point | Report the stage unqualified. Use only an already authorized supported route after a definite pre-dispatch refusal; never fall back while outcome is ambiguous. Restart requires separate applicable authority. |

Maintained contracts: [preflight](https://github.com/kcook98765/kodi-lab/blob/main/docs/DEPLOYMENT-PREFLIGHT.md),
[managed loop](https://github.com/kcook98765/kodi-lab/blob/main/docs/MANAGED-AGENT-LOOP.md),
[recovery](https://github.com/kcook98765/kodi-lab/blob/main/docs/MANAGED-DEPLOYMENT-RECOVERY.md),
[lifecycle qualification](https://github.com/kcook98765/kodi-lab/blob/main/docs/FAST-LOOP-LIFECYCLE-QUALIFICATION.md),
[selective staging](https://github.com/kcook98765/kodi-lab/blob/main/docs/FAST-LOOP-SELECTIVE-STAGING.md),
[service consent](https://github.com/kcook98765/kodi-lab/blob/main/docs/FAST-LOOP-SERVICE-ENABLEMENT.md).
These moving documents contain historical checkpoints; installed schemas and exact
current implementation determine availability. Source/native test evidence remains
separate from authenticated MCP and agent acceptance.
