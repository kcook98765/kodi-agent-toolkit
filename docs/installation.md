# Installation and platform scope

The reference environment uses Python 3.12, Kodistubs 20.0.1, kodi-addon-checker 0.0.36 and mypy 2.4.0. Install the complete `requirements-dev.lock` with `--require-hashes --only-binary=:all:` as shown in the README, then install the original toolkit with `--no-build-isolation --no-deps -e .`. Do not import Kodi stubs as runtime modules. Core discovery/review need only Python's standard library; full static validation needs the pinned dependencies. The public beta qualifies Python 3.12 only; the package's >=3.10 metadata is a source compatibility floor, not a tested-version promise. Standalone use needs no OpenCode, model provider, running Kodi, Docker, WSL2, or Kodi Lab.

After installation, run `python -m pip check`, the unit suite and one actual CLI validation. Acquire official indexes explicitly with `python scripts/fetch-indexes.py --cache CACHE`; pass that same cache path to validation. A missing cache is an environment failure, not a diagnosed add-on defect. Avoid accidental use of another environment's `python`, `mypy` or stubs.

| Platform | Qualification |
|---|---|
| Ubuntu 24.04 WSL2 | Full dependency, regression, CLI and actual OpenCode reference environment. |
| Native Windows 11 / Python 3.12.3 | Fresh isolated hash-locked dependencies, full applicable regression suite, CLI discovery/review and actual static/checker/type validation. Symlink privileges and POSIX-only cases skipped; actual junctions tested. Native OpenCode execution/cleanup unqualified. |
| Independent Linux hosts | Source conventions apply; only the Ubuntu WSL2 environment was executed in this phase. |
| macOS | Suggested venv commands only; not executed. |

For WSL use the Linux filesystem and Linux virtualenv. Use a Windows path only in a native Windows session; when crossing into WSL translate it with `wslpath` and verify the result. Discovery deliberately refuses drive-letter/backslash inputs in POSIX sessions. It does not automatically translate usernames, home paths or network shares. Quote shell paths containing spaces. From a nested add-on directory `kodi-toolkit discover` scans the nearest containing add-on and retains an enclosing repository as the path origin. A global `.agents` directory alone is not a project marker. Explicit directory arguments bound the scan to that directory. An explicit nonexistent directory is rejected; an empty/wrong scan root yields no claimed artifact.

The lock lists compatible wheel hashes, but availability of a wheel on an untested architecture/platform remains to be qualified. Other Kodi branches need isolated, matching stubs and explicit tests; this lock targets Nexus. Do not overwrite the qualified environment with another stub release.

For an optional OpenCode trial, first install/configure OpenCode using its official documentation, discover actual provider/model IDs and verify tools. Keep credentials private. Ensure the separately installed `@opencode-ai/plugin` SDK version matches OpenCode (reference: 1.19.0). Its `node_modules` can be supplied to the runner through `OPENCODE_SDK_DIR`; the compatibility default uses the existing OpenCode user SDK directory. If OpenCode has prepared a local `.opencode/node_modules`, set `OPENCODE_SDK_DIR` to its verified absolute path. The runner installs no packages during trials. Use `OPENCODE_BIN` for a nonstandard executable and invoke the runner with the toolkit venv Python.

Skills can be copied without adapters, Python tools or Kodi Lab. Include the skill's references. For other agents use their supported Agent Skills location and bounded CLI invocation. Tool adapter and evaluation-runner qualification is separate from portable skill discovery.

Windows commands use the same arguments with `.venv\Scripts\python.exe`. The Linux virtualenv must never be reused as a Windows virtualenv. An observed Windows metadata download returned HTTP 429; it left no accepted manifest. Native validation then passed with an explicitly copied, hash-verified official snapshot from the fresh Ubuntu setup. Keep failed setup evidence and choose the cache explicitly; this is not automatic fallback. See [beta scope](public-beta.md).

OpenCode configuration layers merge. The standalone example contains no MCP/provider credential, but it does not erase your existing global MCP configuration. Its agents deny unrelated tools. For a clean standalone setup use a separate task-local configuration environment; inspect effective configuration privately before model execution. No model/server configuration change is required for the CLI.

Sources: [OpenCode skills](https://opencode.ai/docs/skills/), [custom tool directory/worktree context](https://opencode.ai/docs/custom-tools/). Installed 1.19.0 SDK definitions were checked locally; docs can evolve independently.


## Installation verification

Use the complete native Windows or Linux sequence in the README, always invoking the venv interpreter explicitly. Activation is optional; no PowerShell execution-policy change is required. Keep Linux and Windows virtual environments separate.

After initial acquisition, test the valid sample and expected failing API control, then run the offline suite, historical scorecard and harness help. Editor support means selecting this same venv interpreter; Pyright was not executed. Network index acquisition is an explicit setup step and can be rate limited. An existing cache must be independently trusted and supplied explicitly, not silently substituted.

Phase 6 counts and network limits are historical qualification evidence. See docs/phase7-results.md for the original release-snapshot coverage. Local Linux testing used Ubuntu 24.04 inside WSL2; macOS was not executed. [Hosted GitHub Actions](https://github.com/kcook98765/kodi-agent-toolkit/actions/runs/38495360537) subsequently passed the deterministic suite on Ubuntu 24.04 (171 passed, 1 skipped) and Windows 2025 (167 passed, 5 skipped). Hosted CI does not acquire official metadata or test agent/runtime workflows; local download failures and the documented qualification limits remain applicable.
