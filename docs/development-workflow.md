# Kodi add-on development

Choose the target Kodi release and use its [static validation lane](stubs.md). Find the actual add-on root and inspect declared entries before changes. Use `kodi-toolkit discover`, then `kodi-toolkit validate ADDON --branch GENERATION --cache INDEX_DIR` under the matching interpreter. A checker branch does not select a different interpreter or stubs.

For managed native work, use the [managed-v2 workflow](../.agents/skills/kodi-mcp-testing/references/managed-agent-workflow.md). Admit a ZIP, install through native Kodi, check the verified package and dependencies, then run and observe it. An ordinary source edit uses the private workspace and direct deploy. Keep matched static checks and fresh native observation with the change.

For a local ZIP, use an operator-approved endpoint and private token file.

```sh
kodi-toolkit managed-package-import ./script.example.zip \
  --url "$KODI_LAB_MANAGED_URL" --token-file "$KODI_LAB_MANAGED_TOKEN_FILE"
```

The command sends one authenticated binary upload using the configured Lab MCP address. It prints the admitted add-on ID, version and verified digest. The server accepts ZIPs up to 32 MiB and expanded trees up to 64 MiB. The separate 64 KiB JSON request limit still applies.

For an intentional full source refresh, admit the complete updated ZIP, then open it with `managed_workspace_open` using the digest and `replace="true"`. This exchanges only the private workspace. Deploy separately if needed. Use digest-guarded workspace edits for ordinary text changes.

Check private snapshot capacity and reuse a matching snapshot before saving a stopped environment. See the managed skill's [snapshot checkpoint workflow](../.agents/skills/kodi-mcp-testing/references/managed-agent-workflow.md#snapshot-checkpoints) for naming and closeout. One shared working profile per version can be reset or restored explicitly. Stop the running version before starting a different prepared one. Keep add-on source outside the profile.

Use [OpenCode roles](opencode-agents.md) and the [bounded integration smoke](integration-smoke.md) with a disposable lab. External development has its own credential, target and workflow.

For the optional [public repository release test](../.agents/skills/kodi-mcp-testing/references/managed-agent-workflow.md#optional-public-repository-release-test), use a separately approved disposable Omega site. The ordinary managed workflow uses the internal network and the operator-reviewed private dependency catalog.

The [earlier integration campaign](evaluation.md#2026-11-18-kodi-labopencode-integration-acceptance) records the previous application and tool catalog as historical evidence.

Use the [recording skills and video tools](recording.md) when the owner asks
for a private demonstration or a captioned development record.
