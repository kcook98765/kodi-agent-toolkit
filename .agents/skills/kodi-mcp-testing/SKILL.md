---
name: kodi-mcp-testing
description: "Verify Kodi Lab MCP runtime workflows on explicitly authorized managed development profiles, from read-only smoke tests to permitted deployment checks."
license: MIT
---

For current Kodi Lab (44 documented MCP tools), first read [the trusted managed agent workflow](references/managed-agent-workflow.md) when an explicitly authorized agent-owned project, autonomous Reset or Bridge preparation is involved. Default inspection and testing roles remain narrow; no additional permission is implied by loading a skill. Discover the installed server's credential-filtered schemas and source/runtime identity.

Read [role boundaries](references/agent-roles.md) when choosing developer, tester or inspector responsibilities. Read [the workflow reference](references/mcp.md) for authority, pagination, deployment, launch and UI controls, and [current contracts and recovery](references/current-contract.md) for exact inputs, managed version lifecycle, retained profiles, explicit destructive Reset, admission and uncertainty. For launch tests identify the manifest entry and intended window first. A stopped target is not usable; do not start or replace it without separate lifecycle authority. Discover the exact version/target and current profile identity; recover a rejected saved UUID with one discovery. Server capabilities are distinct from client grants.

When reporting static evidence before runtime testing, identify the intended release and its documented isolated interpreter. Run that interpreter with `-m kodi_agent_toolkit.cli stub-lanes`, record actual Python/platform, packages and qualification/readiness limits, then validate with that same interpreter and intended checker branch. Use version-compatibility for lane locks and Matrix/Piers limits. Retain errors, warnings and unsupported coverage. Keep this evidence separate from native acceptance; it grants no runtime authority.

Use only tools needed for the completion criterion: list then status for health; UI state for window/focus; paginated addon_list for inventory; screenshot only for actual image analysis. Null/unassociated fields are unknown. Do not retrieve UI/inventory merely because tools are exposed.

Read-only grants do not permit navigation, Python execution, profile changes or deployment. Generic select can mutate settings. Deployment requires task authorization plus existing server grants, isolated target, exact revision receipt and reproducible smoke/cleanup evidence. Report an unavailable stage without broadening permissions or bypassing policy.

Stop when the requested goal is verified or a required step is unavailable. State target/version, actual observations, failed operations, tested revision and uncertainty; concise summaries normally fit within 150 words. Keep credentials, user media, sensitive screenshots and logs outside shared artifacts. Standalone development/validation does not require Kodi Lab.
