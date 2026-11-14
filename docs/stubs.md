# Static Kodi API support

## Four Kodi Lab target lanes (2026-11-14)

Use `kodi-toolkit stub-lanes` to inspect **this interpreter's** installed Kodistubs version, the four supported Kodi Lab branch names, the expected package pins and the current qualification state. It also reports the actual Python version, platform, mypy and official checker versions. Readiness requires the recorded CPython 3.12/platform scope and pinned tools; it does not verify the full dependency lock, index cache or an add-on. It performs no downloads, mutations or version switching. `--branch` selects the official checker branch; it **does not** change Python environments or install matching type stubs. Use an isolated Python interpreter for each lane and execute validation with that interpreter. A wrong-major installation is a type-coverage failure.

| Managed Kodi | Candidate Kodistubs | Toolkit environment | Qualification |
| --- | --- | --- | --- |
| Matrix 19.5 | 19.0.3 | `requirements-matrix.lock` | [Bounded static qualification with two reviewed annotation corrections](matrix-stubs.md) |
| Nexus 20.5 | 20.0.1 | `requirements-dev.lock` | Existing validated default |
| Omega 21.3 | 21.0.0 | `requirements-omega.lock` | Existing separately validated static lane |
| Piers 22 RC2 | 22.0.1rc1 (prerelease candidate) | `requirements-piers.in` | Pending artifact verification, exact RC2 signature comparison and tests (#14) |

**Create a new environment for each lock; never replace a qualified environment's stubs.** The Piers `.in` file remains a candidate pin only, pending its own hash-locked qualification. Matrix installation, source comparison and the narrow validator-only annotation corrections are documented in [the Matrix guide](matrix-stubs.md). No version is automatically selected by the toolkit or OpenCode. Preserve checker warnings and distinguish static validation from actual native Kodi behavior.

The tested environment uses Kodistubs==20.0.1 for the Kodi 20/Nexus target, installed from PyPI inside .venv. Mypy 2.4.0 with --follow-untyped-imports passes the representative fixture and reports that xbmc.log's second argument must be int when the invalid fixture supplies a string.
```sh
.venv/bin/python -m mypy --no-incremental --follow-untyped-imports fixtures/valid/script.toolkit.sample/default.py
.venv/bin/python -m mypy --no-incremental --follow-untyped-imports fixtures/invalid-api/script.toolkit.sample/default.py
```
These commands analyze files; they never import/execute the add-on. Never use stubs as runtime replacements. Their placeholder bodies do not implement Kodi or prove GUI/player behavior.

The original lane qualifies the pinned 20.0.1 distribution. Other majors need a
separate matching environment and explicit tests; do not overwrite the qualified
Nexus environment. No full API coverage or native compatibility is claimed.

## Isolated Omega option

`requirements-omega.in` / `requirements-omega.lock` preserve every Nexus dependency
pin except `Kodistubs==21.0.0`. The stable wheel is published by the upstream
Kodistubs maintainer on [PyPI](https://pypi.org/project/Kodistubs/21.0.0/), declares
Python >=3.6, no additional distribution dependencies, and GPL-3.0-only. Its
PyPI SHA-256 is `b82cf094648ad5c75cf532bc377e1255c71730011d23d664b7df8ac96aedd3e0`.
No stub/checker source or wheel is bundled. The lock keeps official
`kodi-addon-checker==0.0.36` (including its Omega branch), `mypy==2.4.0` and the
same hash-locked transitive dependencies. Use CPython **3.12** to run these tools;
the validator's syntax/mypy target remains Python 3.10. Neither value establishes
the target Kodi runtime's embedded interpreter.

Create a **new** environment outside any qualified Nexus environment:

```sh
python3.12 -m venv /absolute/private/omega-venv
/absolute/private/omega-venv/bin/python -m pip install --require-hashes --only-binary=:all: -r requirements-omega.lock
/absolute/private/omega-venv/bin/python -m pip install --no-build-isolation --no-deps -e .
/absolute/private/omega-venv/bin/python -m pip check
/absolute/private/omega-venv/bin/python -B -m unittest discover -s tests -p test_omega_lane.py -v
/absolute/private/omega-venv/bin/python -B -m kodi_agent_toolkit.cli validate fixtures/valid/script.toolkit.sample --branch omega --cache /absolute/private/index-cache
```

Acquire the explicit metadata cache separately through the existing documented
workflow; validation never downloads it implicitly. A real-project run must use
the actual nested add-on root, not necessarily its Git root. Retain all output,
warnings, cache/source/toolchain identities and unverified URL checks. Never use
stubs as an executable Kodi replacement.

The measured option covers CPython 3.12 on Linux, dependency consistency, a valid
static fixture, an invalid API-type fixture and rejection of a mismatched stub
major. It is not full Omega API coverage, add-on feature acceptance, native
Windows/macOS qualification, or Matrix/Piers support. Existing Nexus artifacts
remain evidence for Nexus only. A failed/skipped stage cannot become PASS by
choosing a different checker branch or ignoring type failure.

In editors select the actual .venv interpreter (use a WSL remote interpreter only if your checkout is inside WSL). The installed xbmc/xbmcaddon/xbmcgui/xbmcplugin/xbmcvfs/xbmcdrm modules then supply completion. pyproject.toml includes basic Pyright settings; Pyright itself was not installed/run. Do not enable downloading language servers automatically for agent trials.
Sources: https://github.com/romanvm/Kodistubs/blob/5a7c9c13e8a1cc368a2e91cbbe91d4d8fd211090/docs/using.rst ; https://pypi.org/project/Kodistubs/ ; https://github.com/romanvm/Kodistubs/blob/201cdebab97200761d1ef1ced24738e8aa207c80/setup.cfg
