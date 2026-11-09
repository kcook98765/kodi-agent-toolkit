# Portable OpenCode agents

[Agent presets](../examples/opencode/agents.json) provide selectable OpenCode roles
for another installation. They generalize a workstation's development and
inspection roles, and add a dedicated runtime tester. They contain prompts,
permissions and iteration limits, not models, conversation history or credentials.
The existing [portable skills](skills.md) contain the reusable workflows; agents
choose which of those skills and tools to use.

These are optional OpenCode 1.x examples. They do not change your running
installation. The original presets were checked with OpenCode 1.19.0; the
consolidated configuration was checked with the installed 1.19.3 loader. This is
configuration verification, not model-driven or Kodi runtime qualification.
Check the installed version and configuration format before using another release.

## Choose a role

Use `kodi-develop` and `kodi-test` for daily work, with `kodi-inspect` as the
preferred read-only primary when needed. The compatibility alias and narrower
diagnostic variants are hidden subagents, preserving their names and distinct
permission sets without filling the daily selector. All inherit
the model selected by the receiving OpenCode installation or `--model`; there is
no embedded provider, endpoint, context-size claim or default-agent override.

| Agent | Intended use | Extra tools | Step limit |
|---|---|---|---|
| `kodi-develop` | Local add-on changes and static validation; optional Lab development | Local edits, shell commands subject to approval, explicit Lab workspace operations | 75 |
| `kodi-test` | Runtime test of an existing authorized disposable workspace; no source edits | Workspace reads/validation, preflight, deployment, launch and eligible smoke execution | 40 |
| `kodi-readonly` | Hidden compatibility subagent; prefer `kodi-inspect` | Health, UI, inventory, bounded logs and screenshots | 15 |
| `kodi-inspect` | Preferred read-only inspection | Same inspection tools as `kodi-readonly` | 10 |
| `kodi-narrow` | Hidden subagent: health and structured UI only | Target list, status and UI state | 10 |
| `kodi-visual` | Hidden subagent: UI and images only | Health/UI, screenshot capture and eligible retrieval | 10 |
| `kodi-support` | Hidden subagent: inventory and logs, no images | Health/UI, paginated inventory and bounded logs | 10 |

Inspection roles can read local project instructions and load their two relevant
skills, but deny shell commands, file edits, other-agent delegation and runtime
mutations. The developer can edit local files; terminal commands use `ask` until
the operator configures a trusted, appropriately scoped command policy. Runtime
development/testing uses explicit tool names, not a blanket MCP allowlist. Server
grants and task authorization are still required for each mutation.

`kodi-test` is a new convenience role, not an export of a workstation agent named
`kodi-tester`. `kodi-inspect` retains the familiar name with a shorter budget;
the old `kodi-readonly` name remains available as a hidden subagent. Do not
activate both as daily primaries. An operator can deliberately override a variant
for a task; hidden status is a visibility choice, not an authorization boundary.
These presets deny delegation by default; they do not silently grant `task` access.
Preserve existing independent reviewer/repository and fixture roles in their
actual projects rather than installing additional global agents. Short prompts
route reusable behavior to the [skill role reference](../.agents/skills/kodi-mcp-testing/references/agent-roles.md).

The older [standalone.json](../examples/opencode/standalone.json) separately
provides `kodi-validation` and `kodi-review` through fixture-scoped custom adapters.
Those adapters require the documented SDK/tool setup and accept only fixture
paths. The new developer preset instead calls the ordinary Python CLI for real
add-on projects and does not require those adapters.

## Install on another OpenCode instance

1. Install the toolkit with its [standalone quick start](../README.md#quick-start)
   if local validation is needed. Confirm the intended Kodi release: the default
   lock targets Kodi 20/Nexus; [Omega has a separate option](stubs.md#isolated-omega-option).
   Another major needs matching isolated tooling and evidence. OpenCode needs its
   own working provider/model login.
2. Use the actual add-on project as the working directory. Inspect any existing
   instructions, skills and agent definitions before copying. For a new project,
   copy the skill directories below, including all their references. The full
   catalog is advertised; agents load only the skills needed for the task.
3. Copy `agents.json` into a private configuration location. Prefer the two daily
   roles and optional inspector; keep narrower variants only when useful.
   Set `OPENCODE_CONFIG` to that file for this invocation/session, or merge its
   `agent` object into the project's existing `opencode.json`. Do not replace an
   existing global configuration.
4. Record the receiving project's actual add-on path, intended Kodi release,
   toolkit interpreter and metadata-cache paths in its local `AGENTS.md` or task
   instructions. Port only relevant instructions from an old workstation;
   historical target IDs, production authorizations, credentials, launch scripts
   and previous incident notes are not part of these templates.
5. For runtime roles, perform the separate Lab connection setup below. Local
   development and validation can run with no Lab connection.
6. Inspect the resolved configuration and run the verification steps below before
   relying on a role's permissions.

For a **new project without existing skill directories or conflicting agents**,
these commands install a private per-project overlay. Replace the example paths
with actual absolute paths. Keep the `.local` directory outside version control.

Linux/WSL shell:

```sh
export KODI_TOOLKIT_ROOT=/absolute/path/to/kodi-agent-toolkit
export KODI_ADDON_PROJECT=/absolute/path/to/addon-project
mkdir -p "$KODI_ADDON_PROJECT/.agents/skills" "$KODI_ADDON_PROJECT/.local"
cp -R "$KODI_TOOLKIT_ROOT/.agents/skills/." "$KODI_ADDON_PROJECT/.agents/skills/"
cp "$KODI_TOOLKIT_ROOT/examples/opencode/agents.json" "$KODI_ADDON_PROJECT/.local/kodi-agents.json"
export OPENCODE_CONFIG="$KODI_ADDON_PROJECT/.local/kodi-agents.json"
cd "$KODI_ADDON_PROJECT"
opencode --agent kodi-develop --model PROVIDER/MODEL_ID
```

Windows PowerShell (use native Windows paths and a native toolchain):

```powershell
$toolkitRoot = 'C:\path\to\kodi-agent-toolkit'
$addonProject = 'C:\path\to\addon-project'
New-Item -ItemType Directory -Force "$addonProject\.agents\skills", "$addonProject\.local"
Copy-Item -Recurse "$toolkitRoot\.agents\skills\*" "$addonProject\.agents\skills\"
Copy-Item "$toolkitRoot\examples\opencode\agents.json" "$addonProject\.local\kodi-agents.json"
$env:OPENCODE_CONFIG = "$addonProject\.local\kodi-agents.json"
Set-Location $addonProject
opencode --agent kodi-develop --model PROVIDER/MODEL_ID
```

`PROVIDER/MODEL_ID` is a placeholder for a model actually configured on that
installation. Selecting `kodi-visual` also requires verified image input support.
Native Windows agent execution remains unqualified; copying configuration is not
evidence of runtime compatibility.

OpenCode merges configuration objects. Project configuration can override a
private `OPENCODE_CONFIG`; old same-named agent keys can survive a merge. Review
all contributing configs and the final permissions, rather than assuming this
overlay erases old settings. For an existing install, merge deliberately or first
verify in a fresh project with no same-named agent overrides. Startup wrappers
may also select different configs, working directories or environment values.

## Optional private Kodi Lab connections

[connections.example.json](../examples/opencode/connections.example.json) contains
two disabled connection definitions. Merge its `mcp` object into your private
agent overlay without removing the `agent` object. Keep each connection disabled
until its URL, credential and existing server-side grants are configured.

| Connection name | URL variable | Private credential variable | Intended server authority |
|---|---|---|---|
| `kodi_lab` | `KODI_LAB_INSPECT_URL` | `KODI_LAB_INSPECT_TOKEN` | Read-only inspection of the selected disposable target |
| `kodi_lab_dev` | `KODI_LAB_DEV_URL` | `KODI_LAB_DEV_TOKEN` | Development on the exact disposable target/source/workspace |

Supply secrets through private environment/auth storage, not a committed file or
literal shell command saved in history. Where supported, replace an environment
reference with an explicit `{file:/absolute/private/credential-file}` reference;
protect the file with owner-only permissions (or the corresponding Windows ACL).
These examples use the installed Lab's Bearer-token flow with `oauth: false`;
follow the receiving server's actual authentication contract if it differs.
An old private token is not valid in a new credential store just because its file
still exists. Preserve it until a separately approved replacement; never enable
clients or issue grants as a side effect of installing these presets.
They do not create clients, pair Kodi, register sources, grant authority or start
instances. Inspect each connection's grants and exposed schemas before enabling
it. Missing tool support or registration is an operator setup requirement.

Connection names determine tool prefixes: `kodi_lab_target_list` and
`kodi_lab_dev_workspace_status`, for example. Preserve these names or update every
matching agent permission and prompt. The inspector must use the inspection
credential; do not silently substitute the development credential. Unsupported
tools in a permission list do not become available merely by being named there.

All runtime presets target **managed disposable development instances**. No
production/household target ID, control connection, navigation, host command,
lifecycle grant or standing authorization is copied from the source workstation.
If testing needs navigation or a different lifecycle operation, the operator must
configure that separate supported workflow and its permissions; these presets
report the missing capability. See [private setup](providers-and-mcp.md) and the
[current development workflow](development-workflow.md).

## Verify the receiving installation

From the intended project, with the chosen overlay active:

```sh
opencode --version
opencode debug config --pure
opencode debug skill --pure
opencode debug agent kodi-develop --pure
opencode debug agent kodi-inspect --pure
```

Run these checks in an isolated HOME/XDG profile and disposable Git root first;
HOME isolation alone does not prevent ancestor project configs from merging.
Config loading can
initialize local SDK dependencies; do not use the running service as a disposable
test harness. A Web service and a shell may have different OPENCODE_CONFIG,
OPENCODE_CONFIG_DIR and working directories. Inventory both. Removing an agent
from one file does not disable a same-named definition merged from another file;
review the final ordered permissions and explicit `disable`/visibility settings.

Inspect debug output locally: resolved configuration can contain credentials.
Do not attach raw configuration or agent dumps to public issues. Verify the role
names, prompts, inherited model, step limits and ordered permission rules. Confirm
that inspection agents deny shell/edit/delegation, workspace mutations and
unrelated MCP tools. Check same-named global/project overrides particularly
carefully. Configuration checks do not require a model completion or a Kodi
mutation; keep MCP disabled while checking offline setup.

Then perform only the applicable authorized smoke checks:

- Ask the developer to load `kodi-addon-validation` and validate an existing
  disposable fixture for the configured release. Retain exit status and warnings.
- With inspection configured, select `kodi-narrow` and request target health.
  Confirm actual discovery/status results and no runtime mutation.
- For visual questions verify receipt of actual image content, not just a capture
  ID. Logs/UI access depends on installed schemas and grants.
- Test development/runtime only against an explicitly authorized disposable
  workspace. Record source/target/workspace identity, generation, validation,
  preflight, deployment receipt and observed behavior. Do not call a blocked or
  unperformed stage a pass. The tester does not repair source or prepare a missing
  baseline; use the developer or operator's supported preparation path.

These templates are not a full workstation backup. An exact private migration
also needs the old effective agent settings, applicable project instructions,
installed skills, tool versions and the operator's separate connection setup.
Sessions, API logins and server grants are not embedded in an agent preset.

References: [OpenCode agents](https://opencode.ai/docs/agents/),
[configuration precedence and variables](https://opencode.ai/docs/config/),
[skills](https://opencode.ai/docs/skills/) and
[MCP servers](https://opencode.ai/docs/mcp-servers/).
