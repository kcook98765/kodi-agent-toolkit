# Everyday add-on development with optional Kodi Lab

Use OpenCode → relevant Kodi skill → toolkit validation → authorized Kodi Lab
MCP inspection/testing. The toolkit CLI and portable skills remain useful without
OpenCode, a model or Kodi Lab. Do not replace an existing working agent profile
with an example configuration.

1. Load `kodi-addon-development` for edits, `kodi-addon-validation` for static
   checks, `kodi-version-compatibility` for release questions, and
   `kodi-addon-debugging` for symptoms. Load `kodi-mcp-testing` before a Lab
   workflow. Resolve references from the loaded skill directory. Use the actual
   add-on manifest/entry points and explicitly selected Kodi version.
2. Make a focused change. Run standalone discovery and validation with the trusted
   isolated Python environment and explicit metadata cache. Inspect all stages
   and warnings; our pinned Nexus lane does not qualify Matrix/Omega/22. Static
   PASS leaves runtime untested. Optional fixture adapters accept only their
   documented roots; existing local adapters may have different schemas/scopes.
3. For Lab work, discover authenticated tools and the authorized exact target UUID,
   version/class/profile and current states. UI selection, native responsiveness,
   stored Bridge trust and authenticated Bridge capability are separate facts.
   Confirm the intended source and owned workspace/current generation. A Web
   Current Kodi choice neither creates grants nor authorizes lifecycle actions.
   Stopped Kodi stays stopped without separately applicable lifecycle authority.
4. Prepare reviewed workspace changes through the exposed edit/import/capture
   workflow. Lab reads registered sources, never arbitrary agent-local paths.
   Keep private work and exact returned generations/digests. Run Lab's structural
   validation separately from toolkit checking, then `workspace_deploy_preflight`
   for the same generation and target. It assesses durable prerequisites, returns
   blocked/unknown and reserves nothing. Follow the specified agent/administrator
   next actions; a missing baseline may require the existing stopped-source-copy
   preparation, not another guessed MCP command.
5. Apply only through an authorized admitted `workspace_deploy`. Managed direct
   copy uses its guarded stop/copy/restart sequence. Reuse current exact-generation
   validation/deployment evidence on unchanged bytes; avoid resets, rebuilds or
   redundant deployment. New same-generation deployments still have checks and
   lifecycle effects; replayed receipts are historical. Retained destination-only
   files mean selective staging is not exact mirroring or arbitrary deletion.
6. Use qualified manifest-entry launch or fixed video smoke only where eligible
   and authorized. File application, restart, activation dispatch, fresh code and
   feature acceptance are distinct. Observe the intended result and correlate
   bounded logs/UI evidence with exact source/runtime identity. Reuse valid
   action observations/captures to avoid repeated navigation. Screenshots need
   visual authority and actual image analysis. Never navigate under read-only
   authority merely because tools are listed.

Restart is not a routine cure. Current managed direct deployment performs its own
qualified restart. Live replacement, generic service stop/reload, selected-skin
reload, dependent-module invalidation and one-call apply remain unqualified in the
audited contract. Use a supported stopped-copy/restart route only with authority;
native code must never be replaced while loaded. Existing Web Python-service
enablement has separate verified consent and does not prove execution. ZIP and
repository installation/publication retain their separate human gates.

On timeout or ambiguous outcome, keep the original request UUID, parameters and
receipt. Read status or use documented same-request recovery; do not generate a
new UUID to retry an unresolved mutation. Recovery can itself mutate lifecycle
state and requires authority. A containment receipt is not successful deployment
or execution. Missing grants, Bridge identity mismatch, busy leases and required
reconciliation remain blockers. Retain a concise checkpoint of target/source/
workspace/generation, receipts, unresolved outcomes and next test.

OpenCode installation: keep one complete shared skill source (including
references), inspect config precedence/permissions and verify discovery from each
actual project with `opencode debug skill --pure`. Ask for explicit loading;
discovery is not use. Existing project profiles may disable MCP or permit only
inspection even when the server advertises deployment. Preserve those limits,
private token-file interpolation, model/provider identities and custom tools.
Fresh skill loading should be verified before considering an OpenCode restart;
restart only through its existing service manager when no active work is disrupted.

See [current input/result and recovery reference](../.agents/skills/kodi-mcp-testing/references/current-contract.md),
[Kodi Lab managed loop](https://github.com/kcook98765/kodi-lab/blob/main/docs/MANAGED-AGENT-LOOP.md),
[OpenCode setup](providers-and-mcp.md) and [qualification scope](public-beta.md).

## Qualification dates

The original beta and Phase 4–7 evaluations remain historical, including failed
and blocked runtime trials. The original 2026-10-29 contract audit targeted Lab
`56517d3abd6faf661b990d58e574a94193f8b532` / schema
`0088_service_enable_start`; the current source-only refresh targets
`3015a5c294bfb3140df29ce1717218735b1c396f` / schema `0089`; it distinguishes deployed authenticated discovery
from source-only and saved native evidence. OpenCode 1.19.3 discovery on Claw
uses one existing shared skill source. These facts do not retroactively turn
historical trials into passes or establish new live deployment/agent repair,
Windows/physical-device or cross-version acceptance. A current stopped target and
missing source/workspace grants leave those live stages unqualified.

## Optional retained-version development loop (Lab schema 0089)

Newer Kodi Lab can retain four reviewed Kodi profiles while enforcing one running version, but this is **administrator opt-in**, not a default or a runtime acceptance claim. The new `managed_selection_preview` / `managed_select` MCP tools require the exact target/source/workspace grant intersection and both `managed.lifecycle` and `workspace.inspect`; a Web administrator must first select the owned workspace. Finish a test, release the use hold, confirm all instances stopped, resolve pending/ambiguous work, preview exact target/profile identity, then select with a fresh request UUID and preview `latest_generation`. Selection does not provision/start/stop/retire. After an independently authorized `managed_ensure_ready`, establish that version's own Bridge/baseline/deployment evidence and rerun appropriate runtime tests. Replay of a historical selection does not restore it. Read [the current contract](../.agents/skills/kodi-mcp-testing/references/current-contract.md) and [Lab workflow](https://github.com/kcook98765/kodi-lab/blob/main/docs/RETAINED-DEVELOPMENT-WORKFLOW.md); discover the installed tool list and local agent allowlist.
