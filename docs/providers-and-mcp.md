# OpenCode providers and Kodi Lab connections

The Toolkit CLI works without an AI provider or Kodi Lab. For OpenCode use the provider and exact model already authorized for the project. The example provider configurations are optional starting points. Keep actual endpoints and credentials in a private configuration and preserve working provider settings.

[Connection examples](../examples/opencode/connections.example.json) deliberately start disabled. Enable only the required connection. `kodi_lab_dev` needs a Trusted Managed Lab credential from the intended disposable lab. Use `kodi_lab` for authorized external inspection and `kodi_lab_external_dev` for a separately granted external development target. Endpoint placeholders expect the complete MCP URL. Keep bearer tokens private.

Review [roles and effective configuration](opencode-agents.md) before calling a tool. Verify actual authenticated discovery and keep an external production inspection role separate from development. OpenCode tool allowlists and server grants are independent.

[OpenCode MCP documentation](https://opencode.ai/docs/mcp-servers/)
