# Static Kodi API support
The tested environment uses Kodistubs==20.0.1 for the Kodi 20/Nexus target, installed from PyPI inside .venv. Mypy 2.4.0 with --follow-untyped-imports passes the representative fixture and reports that xbmc.log's second argument must be int when the invalid fixture supplies a string.
```sh
.venv/bin/python -m mypy --no-incremental --follow-untyped-imports fixtures/valid/script.toolkit.sample/default.py
.venv/bin/python -m mypy --no-incremental --follow-untyped-imports fixtures/invalid-api/script.toolkit.sample/default.py
```
These commands analyze files; they never import/execute the add-on. Never use stubs as runtime replacements. Their placeholder bodies do not implement Kodi or prove GUI/player behavior.

The toolkit qualifies only the pinned 20.0.1 distribution. Other major versions require a separate matching environment and explicit tests; do not overwrite the qualified Nexus environment. No claim is made about the latest available stub releases or full coverage of any Kodi major.

In editors select the actual .venv interpreter (use a WSL remote interpreter only if your checkout is inside WSL). The installed xbmc/xbmcaddon/xbmcgui/xbmcplugin/xbmcvfs/xbmcdrm modules then supply completion. pyproject.toml includes basic Pyright settings; Pyright itself was not installed/run. Do not enable downloading language servers automatically for agent trials.
Sources: https://github.com/romanvm/Kodistubs/blob/5a7c9c13e8a1cc368a2e91cbbe91d4d8fd211090/docs/using.rst ; https://pypi.org/project/Kodistubs/ ; https://github.com/romanvm/Kodistubs/blob/201cdebab97200761d1ef1ced24738e8aa207c80/setup.cfg
