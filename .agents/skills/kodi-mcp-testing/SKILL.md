---
name: kodi-mcp-testing
description: "Verify Kodi Lab MCP runtime workflows on explicitly authorized disposable targets, from read-only smoke tests to permitted deployment checks."
license: MIT
---

Read [the workflow reference](references/mcp.md) when authority, pagination, deployment, add-on launch/relaunch or UI controls matter. Read [current contracts and recovery](references/current-contract.md) for exact inputs, preflight, repeated deployments, activation limits or failure decisions. It covers registered-source batch import, exact manifest-entry launch, and action observations with correlated screenshot retrieval when the installed Lab exposes them. For launch tests, identify the manifest entry point and intended window first; retain a verified launch route across iterations. A stopped managed target is not usable; report its state without starting or replacing it unless lifecycle action is separately authorized. Discover and verify the disposable target UUID/version. Never invent an ID; recover from a rejected saved UUID by one discovery. Server capabilities are distinct from client grants.

Use only tools needed for the completion criterion: list then status for health; UI state for window/focus; paginated addon_list for inventory; screenshot only for actual image analysis. Null/unassociated fields are unknown. Do not retrieve UI/inventory merely because tools are exposed.

Read-only grants do not permit navigation, Python execution, profile changes or deployment. Generic select can mutate settings. Deployment requires task authorization plus existing server grants, isolated target, exact revision receipt and reproducible smoke/cleanup evidence. Report an unavailable stage without broadening permissions or bypassing policy.

Stop when the requested goal is verified or a required step is unavailable. State target/version, actual observations, failed operations, tested revision and uncertainty; concise summaries normally fit within 150 words. Keep credentials, user media, sensitive screenshots and logs outside shared artifacts. Standalone development/validation does not require Kodi Lab.
