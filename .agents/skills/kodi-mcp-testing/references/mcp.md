# External Kodi workflow

Use authenticated discovery and the exact external target UUID returned by `target_list`. Use `target_status`, `system_info` and `inspect_ui_state` as needed. Use `addon_list` with its next cursor when inventory must be complete. A null or unassociated field means the response did not establish a value.

Use bounded `log_read` for a tail or metadata, and `log_scan` for counts or a filtered search. Continue only with the returned cursor and the identical query. Record target, time and source identity. Available logs and screenshots depend on the external grant and the capabilities of that target's trusted Bridge. `screenshot_capture` must yield actual image content before making visual claims. [Debugging details](../../kodi-addon-debugging/references/debugging.md)

Use `remote_action` only under the target's navigation grant. Supply the discovered action shape and request ID. Inspect the result before another action. Read-only external inspection has no navigation or development authority.

The separately authorized external developer uses `workspace_validate`, `workspace_deploy_preflight`, `workspace_deploy` and `workspace_execute` for the assigned workspace and exact workspace generation. Follow the live input schemas and inspect application and fresh behavior separately. External production targets retain their own inspection policy. Neither an external development credential nor a production inspection grant confers managed authority.

[Tool inventory](current-contract.md) · [Managed developer workflow](managed-agent-workflow.md)
