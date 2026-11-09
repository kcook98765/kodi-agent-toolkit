# Current Kodi Lab contract and recovery

## 2026-11-09 contract checkpoint

Source: Kodi Lab `683738e7fd40d96b671efe7889d4ab2480cbc009`, migration
`0007_production_navigation`. Installed source/schema inspection found 35
registered tools; authenticated discovery was unavailable during this checkpoint.
This is not a 35-tool client acceptance claim. Discover the permission-filtered
catalog with the receiving installation's own credential before runtime work.
The October checkpoints below remain historical evidence.

The endpoint uses stateless HTTP POST. The current transport supports
`2026-07-28` and legacy `2025-11-25`; ordinary OpenCode remote MCP uses its
streamable-HTTP SDK's compatible initialization flow. Do not substitute a GET SSE
endpoint after a 405. Connection aliases are private settings: a server tool
`workspace_status` becomes `kodi_lab_dev_workspace_status` when the configured
alias is `kodi_lab_dev`. Changing the alias requires matching permission changes.

### Opt-in managed version lifecycle

| Tool | Closed input | Required client and canonical-target policy |
|---|---|---|
| `managed_status` | `{}` | `managed.versions`; authorized slot/target state is filtered |
| `managed_start` | `version`, `request_id` | `managed.versions` and exact target grant |
| `managed_stop` | `version`, `request_id` | `managed.versions` and exact target grant |
| `managed_reset` | `version`, `request_id`, optional `restart` (default false) | Both `managed.versions` and destructive `managed.reset`, exact target grant and explicit task authority |

`version` is one of `matrix`, `nexus`, `omega`, `piers`; `request_id` is a UUID.
No container/path/image/force parameter exists. Persist the original intent and
use the same UUID/version/restart value for documented polling or lost-response
recovery. Never retry uncertainty under a new identity.

Start resumes the retained profile or composes an empty approved cached slot;
it does not download, approve or repin runtimes. Continue native work only when
`status.native_ready` is true. Bridge trust/capability and source/workspace
authority remain separate. Stop retains the writable profile; require
`stop_confirmed`. Release of a use hold is not proof of Stop. Respect other users,
viewers, input ownership, leases, uncertainty fences and the configured concurrent
running limit. No automatic eviction/version switch is implied.

Reset deliberately replaces Kodi's writable settings/databases/installed add-ons
from the approved cached image. It preserves independent Git/source/workspace and
retained Lab evidence; it is not an ordinary iteration/recovery shortcut. It
invalidates Bridge and profile-bound deployment/enablement evidence and closes
a disposed Current Kodi selection. Default Reset leaves the replacement stopped;
`restart:true` requests native Start, not full agent readiness.

After Reset, existing MCP selection cannot bootstrap the disposed Current Kodi
binding. An authorized Web administrator must select the replacement/workspace
while Kodi are stopped, copy a fresh registered-source baseline, establish
reviewed Bridge trust and enable the intended add-on through supported setup.
Existing grants survive but do not provide those preparation powers. Resume the
workspace loop only after that separate preparation. Native-ready alone is not
Bridge-ready or workspace-ready. Preserve original Reset/child receipts if any
replacement stage is uncertain; neither elapsed time nor an empty inventory
unlocks an uncertain removal.

Legacy `managed_selection_preview`/`managed_select` and
`managed_ensure_ready`/`managed_release` remain separately opt-in
`managed.lifecycle` tools. The version interface requires `managed.versions`;
old presets do not acquire it, Reset, source-import or settings authority
automatically. Default Toolkit agents grant none of these lifecycle operations.

### Source, workspace and screenshots

Lab sees only administrator-registered sources below its configured development
root. Synchronize a reviewed local source mirror explicitly; workspace creation
takes `source_id`, not an arbitrary workstation path. Source grants, client-owned
workspace binding, selected-session identity and current generation remain
independent. Import/preview require `development_source.inspect` plus
`workspace.edit`; they are not implied by the ordinary Add-on Development preset.
Preflight still reserves nothing and returns `blocked` or `unknown`, not ready.
Deployment performs current admission, baseline/ownership/readiness and exact
runtime/profile checks. A stale source baseline after workspace deployment is
not by itself a request to overwrite the workspace or recopy source.

At this checkpoint screenshot capture/retrieval registry permissions are
**`target.inspect`**, not a mandatory extra `target.visual` permission. Exact
target grants, target policy and technical readiness still apply; external Kodi
also requires its separate screenshots preference. Do not port older visual
permission assumptions onto this contract or grant production access for a
development test. The inspector connection must use its own restricted client.

`screenshot_capture` takes `target_id` and optional `request_id`.
`screenshot_retrieve` takes exact `target_id`, original action `request_id` and
`capture_id`, on the original authorized managed-development client. Retrieval
requires the same current runtime identity and an unexpired retained frame;
it never recaptures or selects newer pixels. `remote_action` needs control
authority; `observe_ui:true` adds independently authorized UI/capture evidence.
Capture/retrieve return image content plus metadata/text. Verify that actual
image input reaches an image-capable model before making visual claims.

Current deployment/launch inputs in the table below remain applicable. Closed
schemas reject extra parameters. Preserve exact request/generation/receipt
identities after timeout or client output-schema rejection, inspect the durable
server outcome first, then refresh only the affected idle MCP connection when
needed. A new conversation need not refresh cached schemas. No bypass, automatic
credential rotation, duplicate deployment or new-UUID recovery is authorized.

Pinned maintained contracts: [managed loop](https://github.com/kcook98765/kodi-lab/blob/683738e7fd40d96b671efe7889d4ab2480cbc009/docs/MANAGED-AGENT-LOOP.md),
[version lifecycle](https://github.com/kcook98765/kodi-lab/blob/683738e7fd40d96b671efe7889d4ab2480cbc009/docs/MANAGED-VERSION-LIFECYCLE.md),
[clean Reset](https://github.com/kcook98765/kodi-lab/blob/683738e7fd40d96b671efe7889d4ab2480cbc009/docs/MANAGED-CLEAN-RESET.md).

## Historical source checkpoints

Source audit: Kodi Lab `56517d3abd6faf661b990d58e574a94193f8b532`, schema
`0088_service_enable_start` (2026-10-29). This is a dated contract reference,
not a promise that every installed server, client or target exposes these tools.
Discover `tools/list` on the actual authenticated connection. OpenCode normally
prefixes names with the configured MCP server name, for example
`kodi_lab_workspace_deploy_preflight`; use its discovered spelling.

## 2026-10-30 source contract delta

Kodi Lab `b92a14d2c5a2ab292fc0c9100d101b3877fcb1d0`, schema
`0090_verified_noop_deployment`, adds the following scoped behavior. This source
reference does not establish that an installed server was upgraded or that a
particular OpenCode agent received image metadata or passed native acceptance.
The earlier audit remains a historical checkpoint. Discover the actual
connection and retain observed receipts.

- A new managed `workspace_deploy` request can return
  `result_classification=verified_existing`, `deployment_work_skipped=true` and
  `managed_verification` with the exact reused deployment ID, runtime/container,
  current source/installed digests, readiness, scanned/hashed/readback counts,
  zero staged/uploaded bytes and zero native restarts. This is a new verification
  receipt, not a new native deployment, activation or execution. Authorization,
  generation, selected session, rate admission, leases and uncertainty fences
  still apply. Full current installed-tree/ownership and native/Bridge checks
  are required; an old digest alone is insufficient. Older receipts without
  proof, stopped Kodi, changed runtime epochs or insufficient eligibility use
  the existing full deployment/refusal path. Exact UUID replay stays historical.
- `screenshot_capture` and `screenshot_retrieve` retain the same bounded PNG
  `ImageContent` and structured metadata, and additionally return identical
  metadata as text for adapters that discard `structuredContent`. OpenCode
  1.19.3 kept image attachments but discarded that structured object. Associate
  image and text from the same tool result; check actual pixels, MIME/dimensions,
  capture/target/time and, for action-bound retrieval, original request identity,
  runtime revision and frame age. Retrieval preserves the original capture and
  existing expiry checks; it does not authorize recapture. Digest and explicit
  expiry timestamp are not supplied metadata fields; do not invent them.
- Fixed video smoke recognizes only the reviewed Piers `22.0-rc.1` Python API
  `3.1.0` / compatible ABI `3.0.0`. Unsupported dependencies, unknown releases
  and non-video extension shapes retain their refusal. GUI launch alone does
  not establish fixed-smoke acceptance.

See [verified reuse](https://github.com/kcook98765/kodi-lab/blob/b92a14d2c5a2ab292fc0c9100d101b3877fcb1d0/docs/VERIFIED-NOOP-DEPLOYMENT.md).
No tool, ordinary client permission or generic execution capability is added.

## Calls and evidence

Resource IDs below are discovered UUIDs; create a caller-generated request UUID for each genuinely new authorized operation and retain it for recovery. `expected_generation` is the existing observed
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

Full managed direct deployment uses the guarded stopped-copy/restart workflow;
eligible verified reuse uses the separately described current verification path.
Retain the complete receipt with exact target, workspace,
generation, source and server-bound runtime/container evidence. `iteration_evidence`
separates file application (`verified_at_operation`) and Kodi restart
(`observed_at_operation`) from unobserved fresh code and unrun functional smoke.
Selective staging still hashes/compares full trees, retains destination-only files
and refuses type replacement. Neither a no-op transfer nor a workspace removal
proves exact installed mirroring.

For unchanged bytes, reuse valid current exact-generation evidence. A separately
requested same-generation deployment may be supported; it still performs admission
and verification. Completed successful duplicate requests return historical receipts without
probing current runtime; failed or unresolved attempts retain their error/ambiguity rather than becoming successful receipts. Execution/launch use the latest authoritative deployment
for the selected profile: a newer failed, pending, incomplete or ambiguous attempt
blocks fallback to an older success; tied newest times cannot prove order. Legacy
unbound receipts need fresh verification through the supported workflow, not a
manual receipt edit.

Registered-source copy evidence and workspace deployment evidence describe
different installed content. After successful workspace deployment, the registered
source baseline may appropriately be `stale`. Preserve the workspace receipt and
assess current installed content through supported preflight/deployment admission
and status evidence, including current runtime/container/tree and authority proof.
`prior_workspace_requires_container_proof` alone calls for supported live admission,
not source recopy, workspace reset or reconciliation. Genuinely missing, unknown or
mismatched provenance and reconciliation fences still require their stated checks.

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
For an authorized retained development/testing profile, use
`managed_selection_preview(target_id, workspace_id)`, then
`managed_select(request_id, target_id, workspace_id, expected_generation, identity)`
with the preview's `latest_generation` and exact opaque `identity`. This is the
selection-session generation, not the workspace generation; a stale preview needs
a fresh preview. Selection preserves retained profiles and does not install or
start Kodi. Current policy permits one selected active managed Kodi at a time.
Absent runtimes require explicit administrator acquisition/provisioning;
`managed_ensure_ready` starts only an existing provisioned selected target, and
`managed_release` may retain a protected/busy target. These tools require their
explicit authority and applicable workspace, source and Bridge prerequisites.
A Web Current Kodi choice creates no grants. Fresh Test/Switch may replace state
and is not a routine retry. Standard noVNC is a human viewer, initially view-only;
Take Control acquires human input ownership and excludes conflicting agent input.

External Kodi uses supported JSON-RPC and narrow reviewed Bridge capabilities
under separate exact-target grants, permissions, identity and readiness checks.
Lab has no managed Docker/runtime ownership, retained selection or profile
lifecycle control over that device. External-development repository approval and
installation remain separately qualified; external production is excluded from
workspace deployment/launch and never inherits managed development authority.

## Failure decisions

| Observed condition | Safe next step |
|---|---|
| Empty targets, `target_not_found_or_not_authorized`, absent tools or missing source grant | Report unavailable under this credential. Rediscover a rejected saved ID once; do not change presets/grants, rotate credentials or infer a stopped target caused a permission denial. |
| Missing source baseline/attachment | Retain preflight checks. An administrator must use the existing exact stopped-source-copy preparation workflow, after resolving leases/reconciliation and with separate mutation authority. Workspace validation does not establish that baseline. |
| Source baseline `stale` after workspace deployment / `prior_workspace_requires_container_proof` | Preserve qualifying workspace deployment provenance and obtain current supported runtime/container/tree proof at admission. This state alone does not request source recopy, workspace reset or reconciliation; actual missing/mismatched proof still blocks. |
| `workspace_generation_conflict` / stale validation | Refresh workspace status and affected content; review competing changes. Validate the actual current generation before a new operation. Do not reset or discard private work. |
| Busy lease, rate limit or selected-session mismatch | Preserve operation identity. Wait/read status as documented, or report administrator review. No forced release, parallel workaround, repeated deployment or target switch. |
| Bridge unavailable, untrusted, incompatible or identity mismatch | Native responsiveness and stored trust are insufficient. Retain exact identities and report the blocked Bridge-dependent stage. No re-pair, direct RPC, alternate credential or implicit upgrade. |
| Lost response / pending / ambiguous mutation | Preserve original request and parameters. Read status; use only documented identical-request receipt recovery. Never mint a new identity to replay an unresolved action, deploy, launch or execution. |
| Client rejects an MCP output schema (observed examples: `deployment_work_skipped`, `managed_verification`) | The server operation may have succeeded. Preserve the original request/parameters; inspect its receipt through supported read-only status tools and determine the server-side outcome before any retry. Avoid duplicate mutations. Compare the returned response with the currently advertised schema. If stale connection metadata is suspected, have the authorized operator refresh/reconnect only that MCP connection through supported controls when idle, then reverify compatibility. A new conversation alone need not refresh metadata. Other validation errors may have other causes; never disable validation, modify responses or rotate credentials to bypass them. |
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
