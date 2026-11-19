# Opt-in OpenCode–Kodi Lab integration smoke

This recipe is instructions, not recorded test execution. Installing Toolkit or loading a skill runs none of these steps. It checks one configured environment; it does not replace Lab regression tests or the [509-call acceptance campaign](https://github.com/kcook98765/kodi-lab/issues/384). Keep [historical/model evaluation](evaluation.md) separate.

## Prerequisites and bounds

The operator supplies an existing authorized Lab connection, explicit exact target/scope, private credentials and a working OpenCode provider/model. Do not issue credentials, change client/server permissions, install/upgrade software or replace global/project configuration to pass. Preserve existing sessions and user settings. No physical/household Kodi is needed; do not contact one under an assumed grant.

Use one target and one read-only scenario first, at most 10 MCP calls and 10 minutes; stop earlier at the existing agent step/cost limit. Have the operator set a model-spend ceiling before invocation. An optional managed fixture is one further scenario, at most 20 calls and 15 minutes plus separately authorized cleanup. One optional negative check takes one call. No unbounded polling: at most one refresh for a stale read. A budget stop is PARTIAL. Missing required authority/setup is BLOCKED; it does not authorize repair. Ambiguous mutations stop dependent work and retain original identity.

## Read-only scenario

1. From the intended existing project, check the installed CLI's help before using syntax. The following command forms were checked with OpenCode 1.19.3; receiving versions may differ:

   ```sh
   opencode --version
   opencode debug --help
   opencode mcp --help
   opencode run --help
   opencode debug config --pure
   opencode debug agent kodi-inspect --pure
   opencode debug skill --pure
   opencode mcp list --pure
   ```

   Keep resolved output private: it may contain credentials. Review all merged configurations, actual agent/model, ordered permissions and connection aliases. Verify `kodi-mcp-testing` and its complete references are discovered, then explicitly load the skill and retain the actual successful skill event. Discovery alone is not loading. Use an already configured inspection role; if missing, stop rather than copying a preset over working configuration. Debug loading can initialize local SDK dependencies; if setup would require changes, stop. Do not restart/dispose a service or touch existing sessions. A Web service can resolve different configuration from a shell; inspect the actual context you will test.
2. Confirm authenticated MCP tool discovery through that OpenCode connection. Retain exact tool names/input schemas from its `tools/list` catalog in existing supported client diagnostics or tool events; `mcp list` status alone is not a tool inventory. If the catalog cannot be verified, record BLOCKED at discovery. The pinned [current source inventory](../.agents/skills/kodi-mcp-testing/references/current-contract.md#current-source-inventory-46) has 46 tools; a credential-filtered catalog can legitimately contain fewer. Do not widen permissions to reach 46.
3. Call `target_list({})` through the inspection alias; follow pagination only within the budget. Select only the operator-authorized exact UUID and confirm class/runtime. An empty list is a valid filtered observation, but blocks a target smoke. Do not start stopped Kodi.
4. Call `target_status({"target_id":"<authorized discovered UUID>"})`. If exposed and permitted, call `system_info` with the same sole argument. Standard inspection uses `kodi_lab_system_info`; the separately authorized managed role uses `kodi_lab_dev_system_info`. Native 54 metrics require no Bridge; optional seven-field enrichment has independent status. Preserve complete/partial/unavailable and per-field limits, provenance and Kodi-visible resource scope. Missing/older Bridge enrichment does not fail native collection; do not install/pair/upgrade a Bridge.
5. Perform **one additional authorized inspection**: `inspect_ui_state`, `addon_list` or one bounded `log_read` tail, chosen for existing grants and capabilities. Record any pagination/incomplete coverage. Prefer UI/inventory if Bridge logs are unavailable. Screenshots are unnecessary. Do not navigate, deploy, execute, Reset or change settings.

An optional initial OpenCode prompt is: “Load kodi-mcp-testing. Inspect only the operator-specified exact target through the existing inspection connection: discovery, target_status, system_info if permitted, then one UI/inventory/log inspection. Limit to 10 MCP calls/10 minutes and the agreed spend ceiling. Preserve raw results privately, report limitations, and make no Kodi or configuration changes.” Supply private target identity only in the authorized private session. Actual tool-use/result events, not this prompt or the model's final prose, establish the calls.

## Optional managed development — separate affirmative authorization

The operator must explicitly authorize fixture creation/import, workspace edits/validation, deployment, launch, any required Start/Stop and cleanup on a named disposable managed profile **before this scenario**. Read-only smoke authorization is insufficient. Confirm existing Trusted Managed Lab or exact narrower grants and [role permissions](opencode-agents.md); loading that preset does not enable a server role. Respect storage/project quotas, one-running policy and human holds. Missing current reviewed Bridge/runtime/source preparation is an operator blocker. **No automatic Reset.**

1. Inspect existing owned projects/workspaces first. If creation is authorized, use `project_create` for one tiny private inert Program/video fixture, or import reviewed private source with checksum/provenance using supported `project_import` limits. Do not adopt another client's project. Registered-source clients use only their existing authorized source path.
2. Record exact workspace/generation and fixture bytes. Use a unique harmless run marker (for example `SMOKE_<private-run-id>`) in the declared entry so fresh native output can distinguish this run from old logs. Run release-matched Toolkit static checks separately, then `workspace_validate`; retain `launch_entries` and its structural result.
3. Preflight the exact generation/target. `blocked`/`unknown` reserves nothing; follow only already authorized prerequisites. If admitted and authorized, `workspace_deploy` that validated generation and retain its original request/operation IDs and application/verified-existing proof. No unchanged redeploy solely to recover smoke eligibility.
4. Choose the validated `extension_ordinal` and existing authorized `development_launch` or `workspace_launch` path. Their permissions differ; see [Program launch](../.agents/skills/kodi-mcp-testing/references/mcp.md#launching-and-relaunching-an-add-on). A Program/mixed-manifest `workspace_execute` refusal is legitimate, not a reason to Reset or navigate menus. Retain dispatch receipt, then verify fresh marker/output and intended UI/feature behavior independently. Static PASS, deployment and accepted dispatch alone cannot pass native execution.
5. After response loss or ambiguity, keep original UUID/arguments and inspect documented receipts/status; do not mint a replacement request or relaunch. Preserve failed results too. Recovery is separately authorized where it mutates state. Stop dependent work if unresolved.

## Optional negative check

With **already appropriately restricted authority**, make one safe read-only call expected to be denied (for example a known, operator-approved exact target outside that credential's grant). Record client-side refusal versus server typed denial separately; client refusal does not test server enforcement. If the tool is filtered out, record that observation rather than bypassing it. Do not create credentials or change permissions to manufacture a result, probe unknown targets, or attempt a destructive negative operation. Missing suitable restricted authority means skip this optional check and record why.

## Evidence and cleanup checklist

Keep raw outputs and identities in an owner-only evidence directory outside Git. Share only sanitized summaries: no credential values, endpoints, private target IDs, runtime logs or screenshots in public artifacts. For each stage record:

| Field | Record |
|---|---|
| Source and client | Toolkit revision; Lab source/version/schema (or unknown); actual credential-filtered tool/schema inventory; OpenCode version, model, agent and private session reference |
| Target | Authorized class, exact private target/runtime/profile identity, Kodi version; keep public labels generic |
| Actions | Actual tool name/arguments/result and call count; separate skill/config checks from MCP calls; original request/operation/deployment/launch IDs and unresolved receipts |
| Evidence | Static result; exact-generation structural validation; preflight; applied/verified bytes; dispatch; fresh native execution; functional/UI result, each separately |
| Verdict | PASS = requested bounded observation proven; PARTIAL = incomplete/limited evidence or budget stop; BLOCKED = required prerequisite unavailable; EXPECTED DENIAL = the intended refusal actually observed, with enforcing layer |
| Cleanup | Owned runtime/fixture disposition, authorized actions, retained state, receipts and unresolved operations; explicitly record no cleanup when none was needed |

Stop only a campaign-owned managed Kodi process when explicitly authorized and currently identified as that same runtime. Never stop pre-existing or another user's runtime. Use original Stop receipts to confirm current outcome; release of a hold is not Stop. Retain private fixture/workspace/profile evidence unless the operator explicitly authorized supported disposal; no automatic deletion or Reset. Preserve global configuration, providers, credentials and existing sessions. Cleanup limits stay visible in the final verdict.

## Validation of this recipe

The 2026-11-18 Toolkit alignment campaign checked this document, offline guardrails, links and the installed OpenCode 1.19.3 version/help syntax. **It did not run this live smoke, call Kodi Lab MCP, create a fixture or perform native acceptance.** The linked Lab campaign is separate prior evidence, not execution of this recipe.
