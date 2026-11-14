# Matrix static environment

Use this isolated lane for Kodi **19.5 / Matrix**, with CPython **3.12** as the
host development interpreter. The add-on syntax/mypy target remains Python 3.10;
this does not identify the interpreter embedded in another Kodi installation.
Nexus and Omega environments must keep their existing packages.

From the toolkit repository, choose a **new, unused** directory:

```sh
python3.12 -m venv .local/matrix
.local/matrix/bin/python -m pip install --require-hashes --only-binary=:all: -r requirements-matrix.lock
.local/matrix/bin/python -m pip install --no-build-isolation --no-deps -e .
.local/matrix/bin/python -m pip check
.local/matrix/bin/python -m kodi_agent_toolkit.cli stub-lanes
.local/matrix/bin/python tests/lanes/matrix.py -v
.local/matrix/bin/python scripts/fetch-indexes.py --cache .local/index-cache
.local/matrix/bin/python -m kodi_agent_toolkit.cli validate /path/to/addon --branch matrix --cache .local/index-cache
```

On Windows use `py -3.12 -m venv .local/matrix`, then
`.local/matrix/Scripts/python.exe` for every subsequent command. Quote paths with
spaces. Select that interpreter in the editor. No Kodi Lab, OpenCode, model or
running Kodi is required. Downloading repository metadata is an explicit step;
the tests instead use a labeled synthetic index, never a claim about live dependencies.

## Artifact and dependency evidence (2026-11-14)

[Kodistubs 19.0.3 on PyPI](https://pypi.org/project/Kodistubs/19.0.3/) provides
`Kodistubs-19.0.3-py3-none-any.whl`, SHA-256
`aef7fb14ea2349d2ecf673a240e72e87aff0a34966e0ac9ec15ce90d2b7b84e3`,
Requires-Python >=3.6, no distribution dependencies, GPLv3. The wheel was fetched
and its bytes hashed against PyPI JSON metadata. It has no PyPI provenance
attestation. All six API modules match upstream tag `19.0.3`, commit
[`e64b240933b0547db96694904cce27599fab411e`](https://github.com/romanvm/Kodistubs/tree/e64b240933b0547db96694904cce27599fab411e), byte for byte. No upstream stub source or wheel is vendored here.

`requirements-matrix.lock` retains all 23 other Nexus dependency pins and their
hashes, including official `kodi-addon-checker==0.0.36` and `mypy==2.4.0`. All 519
hashes in the inherited 24-package lock were checked against their exact PyPI
release JSON records before replacing only Kodistubs with the verified Matrix
wheel hash. Fresh `--require-hashes --only-binary=:all:` installation and
`pip check` passed on Ubuntu 24.04 / CPython 3.12.3. CI separately tests Linux and
Windows; its artifacts record the actual patch version, packages, fixture reports
and retained checker diagnostics. Rebuild by starting from `requirements-dev.lock`,
replacing only its Kodistubs block with the wheel pin/hash above, and rechecking
the exact metadata at `https://pypi.org/pypi/Kodistubs/19.0.3/json`.

The [Kodi Lab 19.5 catalog at reviewed source 574eeee](https://github.com/kcook98765/kodi-lab/blob/574eeee5b3dd444ab651cab3b73071714bd95ff6/src/kodi_lab/runtime/catalog/kodi-19.5.json)
pins Team Kodi's Jammy package `6:19.5+git20221224.1006-f8fdeb6b1b-0~jammy`.
That source abbreviation resolves to
[`f8fdeb6b1b1a7b753e1559d34a98cea62b4920d9`](https://github.com/xbmc/xbmc/commit/f8fdeb6b1b1a7b753e1559d34a98cea62b4920d9).
Kodi Lab also retains separate 19.4 recipes; this 19.5 comparison does not claim
those runtimes were tested or selected.

## Narrow compatibility correction

The published 19.0.3 annotations reject genuine Matrix metadata calls:
`ListItem.setInfo("video", {"year": 2024, "rating": 8.5, "genre": ["Comedy"]})`
expects only `Dict[str, str]`; `setCast` similarly rejects integer `order`.
The exact 19.5 [ListItem.h](https://github.com/xbmc/xbmc/blob/f8fdeb6b1b1a7b753e1559d34a98cea62b4920d9/xbmc/interfaces/legacy/ListItem.h)
and [ListItem.cpp](https://github.com/xbmc/xbmc/blob/f8fdeb6b1b1a7b753e1559d34a98cea62b4920d9/xbmc/interfaces/legacy/ListItem.cpp)
document/implement numeric, list and cast tuple info labels and integer cast order.
The original false-positive mypy failure was reproduced before correction.

For Matrix validation only, the toolkit generates a temporary mypy `--shadow-file`
with two corrected value annotations. It checks the exact upstream `xbmcgui.py`
SHA-256 `45c11ed1c23872eb5b56d6d1e75815bfad5c07047115b0cc1e968e80bd1225f2`
and original signatures before applying the correction. Unexpected bytes fail
closed. Installed files are never modified; other APIs and Nexus/Omega checks
are unchanged. Results name the overlay and record upstream/shadow hashes.

This corrects value types, not label-specific semantics: an unknown label or
inappropriate metadata value can still need native testing. Direct editor/mypy
runs against the unmodified wheel retain its original annotations; use the
toolkit validator for the reviewed correction. No `Any`, ignored diagnostics,
package execution, project-supplied mypy plugins or skipped qualification tests
are introduced.

## Measured coverage and limits

The explicit Matrix test job requires the actual 19.0.3 package and matching
checker/mypy, and fails if any is absent or wrong. It exercises all six static
stages, a metadata/VFS positive fixture, invalid severity/metadata/cast values,
rejection of a Nexus-only InfoTag setter, three wrong branches, an unreviewed
same-major version, artifact tampering and the actual CLI. A Nexus job also
rejects Matrix validation with its real 20.0.1 package. Checker warnings and
unverified online URL checks remain in results.

This is representative static qualification, not complete API fidelity,
verification of live repository metadata, playback, UI or native Kodi execution.
