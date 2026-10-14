# Private provider and MCP setup
OpenCode 1.19.0 is the qualified reference. Keep real settings in a private OPENCODE_CONFIG or existing user config. Do not replace a working global file with these templates. Configuration objects merge, so a task overlay can retain already-authorized providers/MCP. Inspect the effective agent permissions before testing.

Copy examples/opencode/inspection.json into a private location, replace provider/model placeholders with endpoint-discovered IDs and verified capabilities, and replace REPLACE_WITH_PRIVATE_TOKEN_PATH with the literal path to a mode-0600 token file outside Git. A model's OpenAI-compatible API must pass chat and synthetic tool calls first. Do not guess context sizes, image support or reasoning behavior. Use one explicit model per trial. Authentication, HTTP framing and model tool-selection failures are separate categories.

Read-only security requires BOTH an existing Kodi Lab server-side target-scoped grant and client tool permissions. Client tool filtering alone is not authorization. Establish grants using the installed Lab's documented client registration; this toolkit creates none automatically. The narrow inspection agent allows target discovery, health and UI state only. Screenshots require a separately exposed authorized tool and actual visual input to a vision-capable model. Null UI fields do not prove absence.

For file validation, set KODI_TOOLKIT_PYTHON, KODI_TOOLKIT_CLI and KODI_TOOLKIT_INDEX_CACHE to trusted absolute paths. Copy the optional custom tools into the disposable evaluation project. The bundled adapter only accepts add-ons under its fixtures. Portable skills and the Python CLI also work without OpenCode or Kodi Lab; other agents can call the CLI using their own bounded tools.

Cloud examples are credential-free preparation only. Put credentials in private environment/auth storage and use supported built-in providers. No cloud account, authentication workaround or billable comparison is enabled by this toolkit. Verify the selected model/provider's current terms and capabilities before an authorized trial.

References: [skills](https://opencode.ai/docs/skills/), [configuration](https://opencode.ai/docs/config/), [providers](https://opencode.ai/docs/providers/), [MCP](https://opencode.ai/docs/mcp-servers/), [custom tools](https://opencode.ai/docs/custom-tools/).

The inspection template leaves MCP disabled and has no selected active model. Replace placeholders privately, choose `--model PROVIDER/MODEL_ID`, and enable MCP only after configuring the intended server-side grant. Optional model trials require a provider; the standalone CLI does not.
