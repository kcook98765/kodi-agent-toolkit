# OpenCode agents for Kodi Lab managed-v2

The presets target OpenCode 1.19.3 and the [managed-v2 MCP contract](../.agents/skills/kodi-mcp-testing/references/current-contract.md). They inherit the user's model. Copy the five [skill directories](skills.md) into the project’s supported skill path, and build an explicit private config using the relevant preset. Copy only the connections the project needs. Keep the bearer tokens and real endpoints private.

| Agent | Use | Connection |
| --- | --- | --- |
| `kodi-managed-lab` | Opt-in disposable managed development, installation, deployment and snapshots | `kodi_lab_dev`, credential with Trusted Managed Lab |
| `kodi-develop` | Local source and static validation | None |
| `kodi-inspect` | External status, diagnostics, UI, logs and authorized screenshots | `kodi_lab`, narrowly scoped inspection credential |
| `kodi-support` | External structured diagnostics and logs | `kodi_lab`, narrowly scoped inspection credential |
| `kodi-external-develop` | Registered external development with per-target grants | `kodi_lab_external_dev`, authorized development credential |

The [base role preset](../examples/opencode/agents.json), [opt-in managed preset](../examples/opencode/trusted-managed-lab.json) and [disabled connection template](../examples/opencode/connections.example.json) are ordinary OpenCode configuration objects. Select only the intended role in the private config. Preserve working model and provider settings. Use a fresh project and session when qualifying changes. For a disposable client, place its config, cache, state and session data in private XDG directories and use the existing provider settings without copying a production session database.

Verify `opencode debug skill --pure`, `opencode debug agent AGENT --pure` and `opencode mcp list --pure` there. CLI checks should show only the expected skills, permissions and enabled connections. Treat output from `debug config` as private because it can reveal expanded secrets. The tool names prefixed by `kodi_lab_dev_` belong to the managed connection. Target-based external tool names use a different prefix. An allowed client action must still pass server-side authorization.

OpenCode shell policy remains operator-controlled. Use a bounded local packaging or validation command for the known project, and use authenticated MCP for native operations. Active global tool rules may merge into a project overlay. Verify the effective profile and connection before live use. Git, credentials, publication, external navigation and profile replacement require their own task authority.

Use [the smoke recipe](integration-smoke.md) to check actual model tool choices and runtime results. A connected server and discovered skill only establish setup. Retain private tool observations and report failed or untested steps.

For a disposable qualification run, hand off the exact run ID, site, observed
result, Stop and release outcomes, and verified private evidence to the run
owner. The run owner owns infrastructure closeout. Leave retained profiles,
unique source, unrelated OpenCode sessions, and operator configuration under
their existing ownership. The same handoff applies after failures and
cancellations. [Qualification closeout](integration-smoke.md#handoff-to-the-qualification-run-owner)

## Check an installed role

Run the readiness command as the OpenCode service user against its local HTTP
listener. Set the project to the directory in which the role will run and the
skills root to the reviewed installation that should supply its skills.

```sh
kodi-toolkit opencode-readiness \
  --project /path/to/project \
  --skills-root /path/to/toolkit/.agents/skills \
  --role kodi-develop \
  --skill kodi-version-compatibility \
  --skill kodi-addon-validation
```

Authenticated local servers use the existing `OPENCODE_SERVER_USERNAME` and
`OPENCODE_SERVER_PASSWORD` environment variables. The command reads the effective
skill discovery and role for that project. For a managed role, also provide
`--managed-connection kodi_lab_dev` and, for each required tool, `--managed-tool
TOOL` using the Lab name such as `managed_gui`. Pass `--mcp-catalog` pointing to a
fresh JSON `tools/list` result captured with the same Lab connection and
credential. The check compares the named capability, current connection status
and the exact prefixed OpenCode permission. Keep the catalog private.

If discovery resolves to an old installation, correct the selected
`skills.paths` or project installation. If loading or a linked reference is
denied, review the exact skill name and reference directory in the intended
role. Rerun the check and verify an actual skill load, reference read and any
required MCP call in a new session.
