# Python add-on development
Read the whole addon.xml plus each declared library. Requires/import records are add-on API dependencies, not PyPI requirements. For Kodi 19+ Python add-ons declare xbmc.python >=3.0.0 as appropriate; distinguish its API version from the interpreter.
Script: xbmc.python.script library is executed by Kodi. Plugin: xbmc.python.pluginsource receives argv URL/handle/query; end the directory or resolve playback using the appropriate xbmcplugin function. Service: xbmc.service should bound its work with xbmc.Monitor abortRequested/waitForAbort and exit promptly.
Use addon profile paths for private persistent data, xbmcvfs.translatePath for special paths, and Kodi logging constants, not arbitrary strings. Use xbmcaddon settings APIs only where documented for the target. Never edit another add-on or Kodi databases directly.
Keep reusable logic separate from Kodi imports so ordinary tests can use explicit mocks. Stubs provide static signatures, not working GUI/player objects. Packaging must match addon ID/folder and declared files. Validation is local; deployment requires separate scope.
Sources: https://kodi.wiki/view/Addon.xml ; https://xbmc.github.io/docs.kodi.tv/master/kodi-dev-kit/group__python.html ; https://github.com/romanvm/Kodistubs

Observed Nexus logging boundary: installed Kodistubs 20.0.1 defines LOGINFO=1 and LOGWARNING=2; LOGNOTICE is absent; Kodi removed LOGNOTICE in version 19 and directs callers to LOGINFO. To preserve an INFO-level message use xbmc.LOGINFO, not the guessed literal 2. A numeric value can type-check while changing severity. Verify missing names against the target API rather than inventing a mapping. Official Nexus evidence: https://github.com/xbmc/xbmc/blob/4b95737efaddf7c869736e539318f18433413ff1/xbmc/interfaces/legacy/ModuleXbmc.h and ModuleXbmc.cpp .

## Longer development sessions

Keep full validation/test output and synchronization inventories in task-appropriate evidence files. Return the exit status, pass/fail/skip counts, warnings, relevant changed paths and evidence locations to the agent. Read detailed failures when needed instead of repeatedly loading complete successful reports or every file hash. Preserve failure output and command exit codes; reducing transcript size must not hide warnings or turn a failed check into a pass.

Use a compact checkpoint at phase boundaries or before supported context compaction: actual project/skill/toolchain paths, current source revision, unfinished checks, failures, next action and evidence locations. For runtime work retain the selected version, exact package or edited source, and fresh native observations. Reuse valid checks for unchanged source; rerun the checks affected by an edit.

## Managed-v2 iteration

Start with the [managed workflow](../../kodi-mcp-testing/references/managed-agent-workflow.md). Use Kodi's native installer for a clean package or dependency change. For regular source edits, use the private workspace, matched static validation and direct deployment. Preserve the existing package version and settings for a source-only edit.

Reproduce the result from the intended add-on with fresh UI, logs or a unique marker. Deployment verifies file application. Launch reports dispatch. Record what actually ran. The Kodi runtime owns services and other extension lifecycles. Review the [mixed Python manifest guidance](../../kodi-mcp-testing/references/mixed-python-addons.md) before changing an add-on with multiple entry types.
