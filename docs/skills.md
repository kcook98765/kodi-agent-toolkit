# Installing portable skills

Choose a project-local location supported by your agent and copy each chosen skill directory with its references. The portable format is one `SKILL.md` with name/description frontmatter plus optional supporting files. OpenCode supports `.agents/skills/NAME/SKILL.md`; other compatible agents may use a different location.

From the toolkit root, with an existing add-on project directory:

```sh
mkdir -p /path/to/addon-project/.agents/skills
cp -R .agents/skills/kodi-addon-validation /path/to/addon-project/.agents/skills/
cd /path/to/addon-project
opencode debug skill --pure
```

PowerShell equivalent (replace the placeholder with your project):

```powershell
$addonProject = 'C:\path\to\addon-project'
New-Item -ItemType Directory -Force -Path (Join-Path $addonProject '.agents\skills')
Copy-Item -Recurse -LiteralPath '.agents\skills\kodi-addon-validation' -Destination (Join-Path $addonProject '.agents\skills')
Set-Location $addonProject
opencode debug skill --pure
```

Inspect existing skill directories before copying to avoid overwriting your changes. Ask the agent to load the chosen skill explicitly. Provide the add-on directory, Kodi target, trusted toolkit Python/CLI path, and an existing metadata cache for validation. If the agent cannot call the toolkit, run the CLI yourself and provide its actual results.

The optional OpenCode adapters use `.opencode/tools` and `.opencode/lib`; they restrict file operations to the receiving project's `fixtures`. They need a separately installed matching `@opencode-ai/plugin` SDK and `KODI_TOOLKIT_PYTHON`, `KODI_TOOLKIT_CLI`, `KODI_TOOLKIT_INDEX_CACHE` pointing to trusted absolute paths. Copying skills alone does not require this SDK. No agent/provider installation is part of standalone quick start.

Qualified discovery/loading: OpenCode 1.19.0 on Ubuntu. Compatible agents can use the format and independent CLI, but compatibility is an expectation rather than an executed qualification. Native Windows OpenCode execution is not qualified.

Reference: [OpenCode Agent Skills](https://opencode.ai/docs/skills/).
