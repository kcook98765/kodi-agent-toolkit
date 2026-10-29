# Kodi Agent Toolkit

Portable instructions for coding agents, plus Python tools that help Kodi add-on developers find source files, check Kodi API use, run the official add-on checker, and produce reports of what actually passed or failed.

You can use the command-line tools without an AI agent or [Kodi Lab](https://github.com/kcook98765/kodi-lab). Standalone validation needs Python and public dependency downloads; it does not require a running Kodi instance, Docker, WSL2, or a model server.

**Public beta scope:** static development and validation are supported in the tested Python 3.12 environments. AI contextual review, autonomous repair, smaller local-model workflows, Kodi Lab MCP integration, and runtime debugging are experimental. Autonomous add-on development is not consistently reliable. Runtime deployment and reproduction were **not validated end-to-end** in the historical beta evaluation. See [scope and limits](docs/public-beta.md).

## Quick start

Requirements: Git, Python **3.12** with venv support, and internet access for the initial dependency and official metadata downloads. The pinned setup targets **Kodi 20 / Nexus**. Python 3.12 runs the development tools; it is not a claim about Kodi's embedded interpreter.

Linux shell (tested on Ubuntu 24.04 under WSL2):

```sh
git clone https://github.com/kcook98765/kodi-agent-toolkit.git
cd kodi-agent-toolkit
python3.12 -m venv .venv
.venv/bin/python -m pip install --require-hashes --only-binary=:all: -r requirements-dev.lock
.venv/bin/python -m pip install --no-build-isolation --no-deps -e .
.venv/bin/python -m pip check
.venv/bin/python scripts/fetch-indexes.py --cache .local/index-cache
.venv/bin/python -m kodi_agent_toolkit.cli discover fixtures/valid
.venv/bin/python -m kodi_agent_toolkit.cli validate fixtures/valid/script.toolkit.sample --branch nexus --cache .local/index-cache > .local/validation.json
.venv/bin/python -m kodi_agent_toolkit.cli report-build fixtures/valid/script.toolkit.sample --validation .local/validation.json --markdown
```

Native Windows PowerShell (tested on Windows 11):

```powershell
git clone https://github.com/kcook98765/kodi-agent-toolkit.git
Set-Location kodi-agent-toolkit
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install --require-hashes --only-binary=:all: -r requirements-dev.lock
.venv\Scripts\python.exe -m pip install --no-build-isolation --no-deps -e .
.venv\Scripts\python.exe -m pip check
.venv\Scripts\python.exe scripts/fetch-indexes.py --cache .local/index-cache
.venv\Scripts\python.exe -m kodi_agent_toolkit.cli discover fixtures/valid
.venv\Scripts\python.exe -m kodi_agent_toolkit.cli validate fixtures/valid/script.toolkit.sample --branch nexus --cache .local/index-cache > .local/validation.json
.venv\Scripts\python.exe -m kodi_agent_toolkit.cli report-build fixtures/valid/script.toolkit.sample --validation .local/validation.json --markdown
```

The valid sample should pass all six static stages and produce a **PASS** report with two retained official warnings: its example source URL cannot be verified offline, and its Python API dependency has a Nexus version recommendation. Warnings do not disappear when a command succeeds. This does not test execution inside Kodi.

Metadata acquisition downloads ten official indexes, not add-ons or Kodi binaries. If it fails, stop setup and retain the error; retry later or explicitly supply a separately trusted complete cache. Partial downloads are not accepted. Once dependencies and that cache exist, validation runs offline. See [installation and platform coverage](docs/installation.md) and [checker behavior](docs/validation.md).

To check your own add-on, replace the sample path with the directory containing its `addon.xml`; quote paths containing spaces. Keep `--branch nexus` for this pinned environment. Other Kodi majors need isolated matching stubs and separate qualification.

## Kodi Python stubs and official addon-check

The lock installs **Kodistubs 20.0.1**, **mypy 2.4.0**, and **kodi-addon-checker 0.0.36**. Select `.venv` as your editor's Python interpreter for Kodi API completion. Stubs describe signatures; they do not implement Kodi and must not be used to run an add-on outside Kodi.

For a reproducible failing control, run this after the quick start:

```sh
.venv/bin/python -m kodi_agent_toolkit.cli validate fixtures/invalid-api/script.toolkit.sample --branch nexus --cache .local/index-cache
```

On Windows use `.venv\Scripts\python.exe` with the same arguments. Exit **1** is expected: `default.py:7` supplies a string logging level where the stub requires an integer. The valid control uses `xbmc.LOGINFO`. See [editor/stub setup](docs/stubs.md).

Validation checks Python syntax, the manifest, declared paths, packaging, types, and the installed official checker. The toolkit calls the original checker in a subprocess, replays the explicitly acquired indexes, and preserves its diagnostics and warnings. Missing cache, crashes, timeouts, and incomplete checks are never passes. Neither static success nor offline URL checks guarantee acceptance into Kodi's repository.

## Use the Agent Skills

Copy the relevant directory from `.agents/skills/`, **including its references**, into your add-on project's agent-supported skill location. No toolkit installation is needed to read the portable instructions; the validation steps need the Python setup above.

| Skill | Helps with |
|---|---|
| `kodi-addon-development` | Manifest/entry-point discovery and focused API repairs |
| `kodi-addon-validation` | Static checks, official diagnostics, and evidence-based review |
| `kodi-version-compatibility` | Target API and dependency interpretation |
| `kodi-addon-debugging` | Reproduction and diagnosis with available evidence |
| `kodi-mcp-testing` | Optional authorized Kodi Lab runtime inspection |

**OpenCode 1.19.0 is the initial reference agent.** In a project with these skills, run `opencode debug skill --pure` to verify discovery, then explicitly ask: “Load `kodi-addon-validation` and validate this add-on for Kodi 20/Nexus; report every stage, warning, and untested runtime step.” Discovery alone does not guarantee that an agent loads or follows a skill. Other agents with compatible Agent Skills support are expected to use the directories, but were not qualified in this release. See [copy/install instructions](docs/skills.md).

The Python CLI is agent independent. `.opencode` custom tools are optional **fixture-scoped evaluation adapters**; ordinary add-on projects can call the CLI directly. The [standalone OpenCode example](examples/opencode/standalone.json) has no MCP or credentials. Model-driven use still needs a separately configured provider/model; existing global OpenCode settings merge with examples. See [optional provider and MCP setup](docs/providers-and-mcp.md).

## Optional Kodi Lab MCP

[Kodi Lab](https://github.com/kcook98765/kodi-lab) is a separate project. A configured Lab instance can extend the workflow with target discovery, health/UI inspection, and authorized runtime diagnostics. It needs its own installation, disposable target, private credentials, and server-side grants. Client tool filtering cannot grant access.

The historical beta runtime deployment evaluation was blocked because registered development-source infrastructure was absent. No deployment, runtime reproduction, or autonomous runtime repair completed. Read-only inspection does not establish that an add-on runs correctly. The [everyday development guide](docs/development-workflow.md) describes the current optional loop and dated qualification boundaries.

## Evidence, evaluation, and limitations

Reports distinguish deterministic errors, independently supported conditional issues, recommendations, and unverified claims. Source anchors do not prove general semantics; `report-build` needs trusted tool records, and source hashes detect staleness rather than forged input.

Run the offline deterministic regression suite and historical scorecard check with:

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python evaluation/scorecard.py
.venv/bin/python evaluation/run.py --help
```

Use the Windows venv Python for native Windows. The [evaluation guide](docs/evaluation.md) explains optional model trials and independent judgments. Phase 6 recorded **2 PASS, 6 PARTIAL, 5 FAIL** across 13 agent trials; two bounded API repairs were verified. Passing deterministic tests does not make the model-driven workflows reliable. Raw transcripts remain private; [Phase 6 evidence](docs/phase6-results.md) retains failures and qualification limits. macOS, native Windows agent execution/cleanup, and other Kodi major environments are unqualified.

Original toolkit source, skills, and fixtures are **MIT**. Installed dependencies keep their own licenses; no Kodi binaries or proprietary KodiAI code/prompts are bundled. See [attribution](docs/licensing.md), [contributing](CONTRIBUTING.md), [security reporting](SECURITY.md), and [beta release notes](docs/release-notes-v0.1.0-beta.1.md).
