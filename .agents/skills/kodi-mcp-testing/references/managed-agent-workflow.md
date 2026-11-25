# Everyday managed development

1. Use `managed_status` to discover generations. Choose `matrix` (19.4, legacy), `nexus` (20.5), `omega` (21.3) or `piers` (22.0 RC2, preview). Matrix's installed media libraries have known maintenance gaps. Piers supports live noVNC and navigation. Its reviewed X11/GLES build cannot return native screenshots. Use an exact available reviewed runtime. Call `managed_acquire` once per work period. With that lease, `managed_prepare` creates an unprepared working profile and `managed_start` returns native Kodi and authenticated Bridge readiness. Reuse a ready profile when appropriate.
2. Create or edit source locally at the actual add-on root, or use an existing ZIP. Validate on the intended [static lane](../../kodi-version-compatibility/references/versions.md). Package under one top-level add-on ID directory. Use the Toolkit's local `managed-package-import` command with the operator's approved connection. It uploads the exact ZIP bytes and returns an admitted digest. The managed transfer limit is 32 MiB. For server-side source, call `managed_workspace_open` with that digest. `managed_workspace_package` admits a ZIP from an existing private workspace. For an intentional full workspace update, admit the new complete ZIP and open its digest with `replace="true"`. Deploy separately.
3. Call `managed_addon_install` once with the admitted `addon`, `version` and `digest` and explicit `generation`. The operator provisions the reviewed private dependency catalog. The application stages the private managed repository, selects the exact package, handles authorized native confirmations and any temporary Estuary switch, and asks Kodi to resolve dependencies. Check the verified package, dependency results and enablement. The same operation supports higher versions and changed-content replacements at the same version. A verified package receipt can include `interaction.state=dialog_observed`. Check a known first-run prompt and configure the add-on separately. Confirm execution separately with `managed_addon_launch` and fresh `managed_logs` or UI evidence.
4. For ordinary source edits, use `managed_workspace_read` and `managed_workspace_edit` with the current file digest. Validate changed source with the matching Toolkit interpreter on a local tree representing the intended edit. When the supplied MCP contract requires a stopped profile, use `managed_stop`, `managed_workspace_deploy`, then `managed_start`. If deploy reports `review_required`, review the exact generated paths and digests before using its `review` digest. Launch and observe fresh results. Keep the version and existing dependencies for ordinary edits. Use native installation again to change dependency declarations or test package behavior.
5. Configure a setting by declared key with `managed_addon_setting`. Confirm readback using add-on behavior, a purpose-built harmless log marker, or authorized settings UI. The managed operation writes a known value and verifies it. Inspect unexpected first-run dialogs with `managed_gui` and `managed_screen`, then take only authorized interaction actions. Missing dependencies, an unapproved origin or incompatible packages are reasons to inspect the result and correct the inputs.
6. Before a significant change or project switch, stop Kodi and save a named checkpoint with `managed_snapshot_save`. Save when the profile is worth reusing. `managed_snapshot_list` shows your private snapshots. Stop before `managed_snapshot_load` or `managed_reset`. Load requires the exact compatible runtime image. Reset replaces the working profile with its clean baseline. Your admitted packages, independent source and named snapshots remain available.
7. To switch versions, keep the lease, stop the running generation, and start the other prepared generation. Each has its own working profile. No Bridge pairing step is needed. Stop when the task calls for it, then `managed_release` to let another agent use the lab. A human Take Control conflict requires release of the existing owner through the normal workflow.

An installation result can be unknown even after dispatch. Preserve the observed result and relevant status and report the unresolved step. Ask the operator to recover a pending operation before repeating a mutation. Bootstrap and acquisition of a missing reviewed image belong to the site's normal admin flow.

## Optional public repository release test

Use this workflow only when the operator explicitly approves release testing
on a separate disposable Linux Lab site. Read authenticated `tools/list`
for the four `managed_public_*` tools. Ask the operator for the exact
repository installer, target version and archive digests, and approved Omega
catalog. Approval and revocation are local operator actions. The normal
private-feed workflow still rejects repository installer ZIPs.

1. Acquire the managed owner. Use `managed_public_repository_status` and
   `managed_public_repository_select` for the approved `repository.ai.kodi`.
   The disposable site must have no prepared working profiles.
2. Prepare and Start Omega. Install the reviewed baseline and non-system
   dependencies through the private feed.
3. Use `managed_public_install` for the exact passive installer, then
   `managed_public_catalog` for the reviewed metadata, then
   `managed_public_install` for the reviewed add-on ID, version and digest.
   Supply service consent only when authorized. Check the enabled version,
   original repository origin, verified bytes and dependencies in the result.
4. Stop any playback, Stop Omega and release ownership. If Stop or the
   operation outcome is unconfirmed, report the receipt and have the operator
   verify teardown and recover. Do not replay the install to clear a receipt.

The relay restricts CONNECT and visible TLS server names. Encrypted paths and
authority headers on shared Pages infrastructure are outside that boundary.
Public content can change before installation, and a native service can start
before verification. Keep this test on the approved disposable site. Scope
any client permissions to the four exact tools on the disposable connection.
[Operator guide](https://github.com/kcook98765/kodi-lab/blob/main/docs/MANAGED-PUBLIC-REPOSITORY.md)

[Exact tool contract](current-contract.md) · [External Kodi](mcp.md)
