# Kodi add-on development

Choose the target Kodi release and use its [static validation lane](stubs.md). Find the actual add-on root and inspect declared entries before changes. Use `kodi-toolkit discover`, then `kodi-toolkit validate ADDON --branch GENERATION --cache INDEX_DIR` under the matching interpreter. A checker branch does not select a different interpreter or stubs.

For managed native work, use the [managed-v2 workflow](../.agents/skills/kodi-mcp-testing/references/managed-agent-workflow.md). Admit a ZIP, install through native Kodi, check the verified package and dependencies, then run and observe it. An ordinary source edit uses the private workspace and direct deploy. Keep matched static checks and fresh native observation with the change.

For a local ZIP, use an operator-approved endpoint and private token file.

```sh
kodi-toolkit managed-package-import ./script.example.zip \
  --url "$KODI_LAB_MANAGED_URL" --token-file "$KODI_LAB_MANAGED_TOKEN_FILE"
```

The command sends one authenticated `managed_package_import` call and prints the add-on ID, version and confirmed digest. It keeps encoded bytes and the bearer token out of agent output. The Stage 8 server caps the entire request at 64 KiB, leaving just under 48 KiB for the ZIP. Use the lab's approved intake path for larger packages if available. Workspace packages already live in the lab and have a separate admission operation.

Save a stopped snapshot when a configured environment is worth reusing. One shared working profile per version can be reset or restored explicitly. Stop the running version before starting a different prepared one. Keep add-on source outside the profile.

Use [OpenCode roles](opencode-agents.md) and the [bounded integration smoke](integration-smoke.md) with a disposable lab. External development has its own credential, target and workflow.

The [earlier integration campaign](evaluation.md#2026-11-18-kodi-labopencode-integration-acceptance) records the previous application and tool catalog as historical evidence.
