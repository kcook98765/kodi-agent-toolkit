---
name: kodi-mcp-testing
description: "Run authorized Kodi Lab managed-v2 development, installation, snapshots, and native tests, or inspect an authorized external Kodi."
license: MIT
---

For managed development read [the everyday workflow](references/managed-agent-workflow.md). Use the exact tools shown by authenticated discovery. Check [the current contract](references/current-contract.md) for arguments and result meanings. For external Kodi use [the external workflow](references/mcp.md) with its own credential and target grant.

One working profile exists per version, with one running Kodi across versions. Acquire the managed owner before using native tools and release it when done. Use an existing approved runtime and explicit generation. Keep source workspaces and saved snapshots private. A Reset replaces the working profile and needs task authorization.

Import a validated ZIP or package the private workspace, then request native installation once. Kodi handles installation and dependencies. After a focused source edit, use direct deployment and independently observe fresh execution. Treat an add-on's first-run configuration as a separate step. Never blindly approve a third-party dialog.

Use [mixed Python guidance](references/mixed-python-addons.md) for scripts, plugins and services. Use the version-compatibility skill for the appropriate static lane. Report static validation, file application, launch dispatch and observed execution distinctly. Keep logs, images and credentials private.
