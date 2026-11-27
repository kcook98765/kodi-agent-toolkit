# Kodi Lab managed-v2 MCP contract

Authenticated `tools/list` establishes the actual credential-filtered capabilities. These are the managed-v2 contracts. Use a current compatible Lab revision for bulk transfer, generated-file review and disposable public testing. Tools are listed here without their OpenCode connection prefix.

## Managed tools

Every argument is a string. Runtime-scoped operations take optional `generation` with one of `matrix`, `nexus`, `omega`, or preview `piers`. Omission selects Omega. For installation, `version` means the add-on version. Arguments are closed. Text replies contain JSON with `result` and `elapsed_seconds`. The screen tool returns PNG content.

The server needs a Trusted Managed Lab credential. Acquire the one shared owner for runtime actions and native inspection. Source workspaces, package admissions and named snapshots are private to the credential's agent. Native startup reports the Kodi version and authenticated Bridge. The global status and private lookups can establish which work is needed before making a runtime change.

| Tool | Required inputs | Runtime scoped | Result |
| --- | --- | --- | --- |
| `managed_status` | — | Yes | `state`, `generation`, `available_generations[]`, `owner`, `view_control`, `view_target`, optional authorized `operation`, native `version` and `bridge` when ready |
| `managed_acquire` | — | Global | `owner`, `idle_timeout_seconds` |
| `managed_release` | — | Global | `owner` |
| `managed_prepare` | — | Yes | `state`, `profile` |
| `managed_start` | — | Yes | `state`, native `version`, authenticated `bridge` |
| `managed_stop` | — | Yes | `state` |
| `managed_reset` | — | Yes | `state`, `profile` |
| `managed_logs` | — | Yes | `text` from bounded Kodi log tail |
| `managed_gui` | Optional `include_player: "true"`, `expected_local_media_sha256` when supported | Yes | Kodi window, focus and skin. Opt-in player observation. |
| `managed_screen` | — | Yes | PNG image content where native capture is supported. Piers X11/GLES reports `screenshot_capture_failed`. |
| `managed_navigate` | `action` | Yes | `state=dispatched` |
| `managed_skin` | `addon` | Yes | Skin activation result for an enabled development skin. The stock Estuary ID is reserved. Native installation switches internally when needed. |
| `managed_snapshot_list` | Optional `include_capacity: "true"` | Global | Array of private entries with `name` and `bytes` by default. Opt in to `snapshots` and `snapshot_capacity` with `used`, `capacity` and `remaining`. |
| `managed_snapshot_save` | `name` | Yes | `name`, `bytes`, `entries`, `sha256`. The exact image is bound in private metadata. |
| `managed_snapshot_load` | `name` | Yes | Restored snapshot and profile state |
| `managed_snapshot_delete` | `name` | Global | Snapshot deletion result |
| `managed_workspace_open` | `digest` | Global | `addon`, `version`. Optional `replace` is the string `true` for a full replacement of the existing private workspace. |
| `managed_workspace_tree` | `addon` | Global | Array of relative file path strings |
| `managed_workspace_read` | `addon`, `path` | Global | `content`, `digest` |
| `managed_workspace_edit` | `addon`, `path`, `content`, `expected_digest` | Global | `digest` |
| `managed_workspace_package` | `addon` | Global | `addon`, `version`, `digest` |
| `managed_workspace_deploy` | `addon` | Yes | Applied with verified files and version, or `review_required` with exact generated-file identities. Optional `baseline` and `review` are SHA-256 digests. |
| `managed_package_import` | `encoded`, `digest` | Global | `addon`, `version`, `digest` |
| `managed_addon_install` | `addon`, `version`, `digest` | Yes | `state`, verified `package`, verified `dependencies[]`, and native action/skin observations. Optional `allow_services` takes string `true` or `false`. |
| `managed_addon_inventory` | — | Yes | Native Kodi add-on rows including `addonid`, `name`, `version`, `enabled` |
| `managed_addon_launch` | `addon` | Yes | Bounded native launch dispatch result |
| `managed_addon_setting` | `addon`, `key`, `value` | Yes | Signed add-on setting result |

`managed_addon_install` can report unconfirmed or failed installation. Check the verified bytes, origin, enablement, dependency results and native observations. `managed_addon_launch` reports dispatch. Observe fresh execution through relevant logs or UI. Settings readback uses add-on behavior or authorized Kodi inspection.

Snapshot names and capacity are shared across versions in each private scope.
Use the list result to check capacity before saving. Kodi Lab administrators set
the limits, and agents use the effective capacity returned by their server.
At or above capacity, `remaining` is zero and a new name returns
`snapshot_quota_exhausted`. A duplicate name returns `snapshot_name_exists`.
Existing snapshots remain available to list, restore, and explicitly delete
with the usual permissions.

### Disposable Omega public repository tools

Use the managed owner and the separate operator approval described in the
[managed workflow](managed-agent-workflow.md#optional-public-repository-release-test).
These calls use `generation="omega"`.

| Tool | Required fields | Purpose |
| --- | --- | --- |
| `managed_public_repository_status` | — | Read the approval identities and selection state. |
| `managed_public_repository_select` | `repository` | Select the operator-approved repository on an unprepared disposable site. |
| `managed_public_catalog` | — | Verify the approved catalog through native Kodi. |
| `managed_public_install` | `addon`, `version`, `digest` | Install the approved passive repository or exact update. Optional `allow_services` is the string `true` or `false`. |

## External tools

These use external grants independently of managed authorization. Discover exact nested actions, limits and input shapes from the connected server before use.

| Tool | Required fields | Optional fields |
| --- | --- | --- |
| `addon_list` | `target_id` | `cursor`, `limit` |
| `inspect_ui_state` | `target_id` | — |
| `log_read` | `target_id` | `before`, `log`, `max_bytes`, `max_lines`, `mode`, `snapshot_id` |
| `log_scan` | `target_id` | `context_records`, `cursor`, `end_time`, `logs`, `max_matches`, `severities`, `start_time`, `text` |
| `remote_action` | `request_id`, `target_id`, `action` | — |
| `screenshot_capture` | `target_id` | `request_id` |
| `system_info` | `target_id` | — |
| `target_list` | — | `cursor`, `limit` |
| `target_status` | `target_id` | — |
| `workspace_deploy` | `request_id`, `workspace_id`, `expected_generation`, `target_id` | `deployment_mode` |
| `workspace_deploy_preflight` | `workspace_id`, `expected_generation`, `target_id` | `deployment_mode` |
| `workspace_execute` | `request_id`, `workspace_id`, `expected_generation`, `target_id` | `execution_kind` |
| `workspace_validate` | `workspace_id`, `expected_generation` | — |

For external `system_info`, use the exact authorized target. Native Kodi metrics and optional trusted Bridge enrichment have different provenance. Missing enrichment and null fields remain unknown. For managed diagnostics use `managed_status` for release/readiness, `managed_gui` for window, control and skin, and `managed_logs` for a bounded tail.

[Managed workflow](managed-agent-workflow.md) · [External workflow and grants](mcp.md)


### Managed playback checks

Discover `managed_gui` and check that it declares `include_player`. Use the
active managed lease and explicit generation. Pass `include_player: "true"`
before playback, immediately after selection and again after explicit Stop.
`idle` means the running Kodi reported no active players. `playing` and
`paused` can include player ID, media type and a stable `media_key`. Compare
keys within the returned `incarnation` to distinguish a replacement from a
resume. `unavailable` or `uncertain` is insufficient to confirm playback or Stop.

For known synthetic local media, hash the exact UTF-8 absolute path with no
trailing newline and pass it as `expected_local_media_sha256`. A true
`matches_expected_local_media` confirms what Kodi reported for the path.
The optional keys disclose no raw path, URL or title. A missing key or match
leaves the media identity unverified. Use supported authorized native
controls for Pause, replacement and Stop. Verify idle while Kodi is still
running before requesting managed shutdown.
