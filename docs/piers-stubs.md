# Piers RC2 prerelease static environment

This opt-in lane uses published **Kodistubs 22.0.1rc1**, compared to the exact
Kodi Lab **22.0 RC2** source. Its version string alone is not the compatibility
basis. The measured APIs pass with the unmodified wheel; no Piers overlay is used.
Full API fidelity and native execution remain unverified.

Use a **new, unused** CPython 3.12 environment, keeping Matrix/Nexus/Omega intact:

```sh
python3.12 -m venv .local/piers
.local/piers/bin/python -m pip install --require-hashes --only-binary=:all: -r requirements-piers.lock
.local/piers/bin/python -m pip install --no-build-isolation --no-deps -e .
.local/piers/bin/python -m pip check
.local/piers/bin/python -m kodi_agent_toolkit.cli stub-lanes
.local/piers/bin/python tests/lanes/piers.py -v
.local/piers/bin/python scripts/fetch-indexes.py --cache .local/index-cache
.local/piers/bin/python -m kodi_agent_toolkit.cli validate /path/to/addon --branch piers --cache .local/index-cache
```

On Windows create the environment with `py -3.12 -m venv .local/piers` and use
`.local/piers/Scripts/python.exe` afterward. Quote paths with spaces. The host
interpreter version and validator Python 3.10 syntax target do not establish a
native Kodi runtime's embedded Python. No Kodi Lab, OpenCode, model or running
Kodi is needed. Index acquisition is explicit; test indexes are labeled synthetic.

## Artifact provenance and reproducibility (2026-11-14)

The [PyPI prerelease](https://pypi.org/project/Kodistubs/22.0.1rc1/) was uploaded
2026-10-25. Its wheel `kodistubs-22.0.1rc1-py3-none-any.whl` has SHA-256
`a211fcb3215f2c8891f4f1efb4f1aaf562d85172efbe439ef68f95af0152ea6d`.
The downloaded bytes match PyPI release JSON. METADATA declares Python >=3.10,
GPL-3.0-only and no distribution dependencies. Its six API modules are typed
packages with `py.typed`, rather than the flat modules in earlier releases.
All six match upstream tag `22.0.1rc1`, commit
[`0cef502d791481f85e89909704a446bd43c8eed7`](https://github.com/romanvm/Kodistubs/tree/0cef502d791481f85e89909704a446bd43c8eed7),
byte for byte. The later `22.0.1rc1-2` tag has the same API module bytes. Neither
a package hash nor a source-tag comparison proves publisher identity beyond
those channels: PyPI supplies no provenance attestation for this wheel. No wheel
or upstream stub implementation is vendored.

`requirements-piers.lock` preserves all 23 other Nexus pins and hashes,
including mypy 2.4.0 and official kodi-addon-checker 0.0.36. The inherited 519
hashes were verified against exact PyPI JSON releases; only the Kodistubs block
was replaced with the verified prerelease wheel hash. Reproduce from
`requirements-dev.lock` using that one replacement and the exact metadata at
`https://pypi.org/pypi/Kodistubs/22.0.1rc1/json`. Fresh binary-only hash-required
installation, `pip check` and actual tests passed on Ubuntu 24.04 / CPython
3.12.3. CI separately records Linux and Windows interpreter patch versions,
installed packages, fixture reports and full test output as artifacts.

## Exact RC2 comparison

The [Kodi Lab qualification](https://github.com/kcook98765/kodi-lab/blob/574eeee5b3dd444ab651cab3b73071714bd95ff6/docs/PIERS-RC2-QUALIFICATION.md)
and [reviewed installation recipe](https://github.com/kcook98765/kodi-lab/blob/574eeee5b3dd444ab651cab3b73071714bd95ff6/src/kodi_lab/runtime/recipes/piers-22.0-rc2-installation-r4.json)
bind `piers-22.0-rc2-r4`, official Kodi source
`d686683a55d50e576dd282f53fb2bf9914931b38`, and signed Flathub app commit
`83b803ab50c19471377943f35bed0d96247a425834580a420d5842912ce7cbdd`.
The downloaded acquisition/installation JSON hashes equal the qualification's
`4f5dd5942456563175f2f6bca1c0bfb192172792376d4c6c62d5ec633b7532bd` and
`16b275718524e6dafef27691677d07ac4bffb7af97e5960d227c0ae54bfa8527`.
This work reads that evidence; it does not requalify or alter Kodi Lab.

Complete Git trees, rather than a truncated 300-file GitHub compare response,
were compared between the official RC1 tag and exact RC2. The Python API/binding
trees differ. Changes include twelve `InfoTagGame` metadata methods, runtime
callback/lifetime fixes, and the API version bump to **3.1.1** in
[kodi_common.i](https://github.com/xbmc/xbmc/blob/d686683a55d50e576dd282f53fb2bf9914931b38/xbmc/interfaces/swig/kodi_common.i).

| Exact RC2 source | Representative installed-stub checks |
| --- | --- |
| [ListItem.h](https://github.com/xbmc/xbmc/blob/d686683a55d50e576dd282f53fb2bf9914931b38/xbmc/interfaces/legacy/ListItem.h) | New file title, count, size and overlay setters accept their string/integer values; wrong count type fails |
| [InfoTagVideo.h](https://github.com/xbmc/xbmc/blob/d686683a55d50e576dd282f53fb2bf9914931b38/xbmc/interfaces/legacy/InfoTagVideo.h) | HDR detail constructor/getter/setter, original language with boolean result, season plot and three-field season tuples, available fanart |
| [InfoTagGame.h](https://github.com/xbmc/xbmc/blob/d686683a55d50e576dd282f53fb2bf9914931b38/xbmc/interfaces/legacy/InfoTagGame.h) | All twelve added getter/setter signatures: original title, rating, players, age rating, trailer and tags; invalid player/tag values and getter assignments fail |
| [ModuleXbmc.h](https://github.com/xbmc/xbmc/blob/d686683a55d50e576dd282f53fb2bf9914931b38/xbmc/interfaces/legacy/ModuleXbmc.h) | Integer log severity; removed Matrix `xbmc.translatePath` is rejected |

Those new RC2 game methods are already present with matching types in the
published prerelease wheel despite its `rc1` label. No missing or incorrect
signature was found in this bounded comparison. The evidence snapshot records
source/header/module hashes in [piers-rc2-stubs.json](evidence/piers-rc2-stubs.json).

## Retained limitations

Official checker 0.0.36 accepts branch `piers`, but its dependency advice still
recommends `xbmc.python` **3.0.1**. An RC2-specific fixture declaring **3.1.1**
passes while retaining that original warning. The validator also reports the
outdated advice as a coverage limitation. **Do not lower a required dependency
to silence it.** Refreshing upstream checker advice remains pending; its presence
must remain visible. Online URL checks remain unverified, and synthetic indexes
do not establish current repository dependency availability.

Ten explicit real-package tests require the exact stub/checker/mypy, exercise
all six validation stages and the CLI, verify the installed sources stay intact,
and reject wrong majors and unreviewed prereleases. The RC2-specific positive
fixture includes the manifest API 3.1.1 case. Nexus validation also rejects this
target with actual 20.x stubs. There are no optional skips or ignored diagnostics
in the Piers qualification job.

Static types do not prove valid ranges, metadata keys, collection instance types,
threading, lifetime behavior, UI, playback or binary/runtime compatibility. For
example native vectors require lists/tuples even where stubs annotate Iterable;
unsigned/ranged values such as player count still require sensible native input.
Full API fidelity, native acceptance and macOS qualification are **pending** and
must not be inferred from these tests or from Kodi Lab's separate native evidence.
