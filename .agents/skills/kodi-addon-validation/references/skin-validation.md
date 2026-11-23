# Optional skin validation with kdk 3.4.0

Use this workflow when the user requests additional skin semantics. It supplements
Toolkit validation and the official Kodi add-on checker; it adds no default gate,
Toolkit dependency, MCP tool or OpenCode configuration. Includes, variables,
conditions/InfoLabels, fonts, image references and control/window scope are useful
additional checks. Findings need contextual review, not automatic source edits.

Verify an existing `addon.xml` with extension `xbmc.gui.skin` and the intended
target. **kdk skin validation supports Omega (21) and Piers (22) only.
Matrix/Nexus are not supported kdk validation targets in this workflow.** Do not
substitute Omega for an older target. Piers reference data does not certify exact
22 RC2 behavior. The separate `kdk addon validate` command is outside this recipe.
Keep the existing Toolkit release lanes and official checker authoritative for
their own checks, including dependency and packaging validation.

## Isolated setup, when installation is authorized

An OpenCode agent may perform this setup itself with ordinary shell/network
permissions and explicit authorization to install optional tooling. Loading the
skill does not authorize installation. Reuse a verified matching isolated
environment if available, substituting its path for `$KDK_WORK/venv` below while
keeping a fresh evidence directory. No operator provisioning or configuration
change is required. Never install into Toolkit's environment or system Python.

Linux/Bash example, using CPython 3.12 as evaluated. Run the snippets in the same
shell, or restore their task-local paths in subsequent shell calls. The temporary
directory must be outside the skin checkout. These dependency versions reproduce
the evaluated runtime set; this is not a new Toolkit lockfile. Retain upstream
license notices with the separate installation; do not vendor its code/data.

```bash
set -eu
KDK_WORK=$(mktemp -d /tmp/kdk-skin-XXXXXX)
python3.12 -m venv "$KDK_WORK/venv"
PIP_CACHE_DIR="$KDK_WORK/pip-cache" \
  "$KDK_WORK/venv/bin/python" -m pip install --report "$KDK_WORK/install.json" \
  'kdk @ git+https://github.com/MikeSiLVO/kdk.git@bea0c7d6095e3b0eb4ef24e90bc8df27e9828f33' \
  'lxml==6.1.3' 'rich==15.0.0' 'markdown-it-py==4.3.0' \
  'mdurl==0.1.2' 'Pygments==2.21.0' \
  >"$KDK_WORK/install.stdout" 2>"$KDK_WORK/install.stderr"
"$KDK_WORK/venv/bin/python" -c \
  'import importlib.metadata as m; v = m.version("kdk"); assert v == "3.4.0", v; print(v)' \
  >"$KDK_WORK/kdk-version.txt"
"$KDK_WORK/venv/bin/python" --version >"$KDK_WORK/python-version.txt"
"$KDK_WORK/venv/bin/python" -m pip freeze --all >"$KDK_WORK/packages.txt"
```

The source SHA pins release `v3.4.0` and its bundled rule data. Pip may acquire
build tools; preserve `install.json` and logs rather than claiming a fully
hash-locked build. Missing tools, denied installation or a setup failure mean
optional coverage is unavailable/incomplete; do not alter an existing environment
or install GUI/texture extras to work around it. An already authorized installation
needs no second operator confirmation beyond ordinary permission enforcement.

## Validate and retain JSON

Replace the example skin path with the verified absolute project path, and choose
`omega` or `piers` deliberately. Use authorized local source; check that symlinks
or referenced paths do not escape its boundary. `--isolated` ignores configuration
files, not filesystem access or XML suppression comments; it is not a sandbox.
Use a fresh result directory for each run and preserve earlier evidence.

```bash
KDK_ADDON=/absolute/path/to/skin.example
KDK_RELEASE=omega
KDK_VALIDATE_RC=0
XDG_CACHE_HOME="$KDK_WORK/cache" KDK_NO_UPDATE_CHECK=1 \
  timeout --kill-after=5s 120s "$KDK_WORK/venv/bin/kdk" validate "$KDK_ADDON" \
  --release "$KDK_RELEASE" --isolated --show-include-warnings --json \
  -o "$KDK_WORK/skin.json" \
  >"$KDK_WORK/validate.stdout" 2>"$KDK_WORK/validate.stderr" || KDK_VALIDATE_RC=$?
printf '%s\n' "$KDK_VALIDATE_RC" >"$KDK_WORK/validate.exit"
```

The outer timeout bounds a run; the evaluated Aura run took about 20 seconds.
`--show-include-warnings` preserves warnings hidden by default. Do not narrow by
category/severity or use `--exit-zero` for the retained report. JSON failures may
be on stdout even with `-o`; retain both streams and check the expected file.
Read fresh `validate` output, not the unversioned last-run `issues` cache.

| Result | Meaning and required handling |
| --- | --- |
| Validate exit 0 | Finished without counted errors; warnings can include repository blockers. Inspect JSON before reporting coverage. |
| Validate exit 1 | Findings, or an internal check failure. Triage rows; do not call it an infrastructure success from this code alone. |
| Exit 2 | Invalid invocation or unfinished run. Preserve the error and report incomplete coverage. |
| Timeout (usually 124, possibly 137), missing executable, signal or other failure | Incomplete coverage, never a clean result. Preserve partial output; do not retry indefinitely. |

Check `format_version: 1`, `kdk_version: 3.4.0`, the intended `kodi_release`,
`categories`, counts, `info_source`, `notices` and muted findings. Missing,
malformed or error JSON is incomplete. So is a `kdk.check-failed` row, even when
the process exits 1. Skin JSON has no general `partial` flag: investigate notices
for skipped/failed checks or weakened data coverage before stating completeness.
`--strict` fails on all warnings; it is not the default policy for this workflow.

## Triage and optional baseline comparison

Separate verified source defects, possible defects requiring runtime confirmation,
advice, false positives and duplicates of existing checks. Error severity can
represent unused definitions or repository policy, not observed runtime breakage.
Generated controls, conditional includes, external add-on windows and constrained
identifier values can defeat static inference. Source-tree build tools may be
excluded from the packaged add-on; inspect the actual payload before a packaging
claim. Do not suppress or fix a finding without supporting context.

Known 3.4.0 false positives: `xml.invalid-tag` can reject `pulseonselect` in
spincontrol/slider defaults, although Kodi 21.3 applies it to every constructed
control. Aura also showed uncertain ID-scope and URL-encoding reports, and missing
references inside unused legacy PVR includes. Those do not establish current GUI
failures. See the [evaluated findings](https://github.com/kcook98765/kodi-agent-toolkit/issues/35#issuecomment-7091596386)
and [Kodi control factory](https://github.com/xbmc/xbmc/blob/21.3-Omega/xbmc/guilib/GUIControlFactory.cpp#L1754).

Optionally compare saved, complete reports for the same project, kdk version,
release, dependency/rule data, language and filtering/suppression policy. Record
each source tree separately. Do not replace an accepted baseline automatically;
keep its original report and triage decisions. A saved baseline does not itself
waive known findings. After inspecting the fresh head report:

```bash
KDK_BASELINE=/absolute/path/to/accepted-baseline/skin.json
KDK_COMPARE_RC=0
timeout --kill-after=5s 120s "$KDK_WORK/venv/bin/kdk" compare \
  "$KDK_BASELINE" "$KDK_WORK/skin.json" --json -o "$KDK_WORK/delta.json" \
  >"$KDK_WORK/compare.stdout" 2>"$KDK_WORK/compare.stderr" || KDK_COMPARE_RC=$?
printf '%s\n' "$KDK_COMPARE_RC" >"$KDK_WORK/compare.exit"
```

Compare exits 1 for new findings (warnings included), 0 for no new findings, and
2 when comparison cannot finish, including tool/release mismatch. Timeout and
invalid/incomplete inputs remain incomplete comparison. Matching uses rule, file
and subject, so moving lines is stable, but **comparison may miss severity-only
or message-only changes**. Inspect head severities, totals and notices separately;
compare does not verify project identity or complete provenance. It compares full
reports, not just changed files, and a zero delta is not a clean validation.

## Agent report and runtime boundary

Retain full JSON, streams, exit codes, exact commands, times, Python/platform and
package versions, source commit plus dirty state/tree hashes, and baseline
identity when used. kdk JSON does not contain source commit/tree hashes. Keep
artifacts outside source and preserve them at a durable task evidence location
before temporary-directory cleanup. Give the model counts and a bounded set of
rule/file/line/subject findings or deltas, with paths to full evidence; do not
silently truncate the saved reports. State incomplete/skipped coverage explicitly.

Runtime correctness, rendering, navigation and playback still require separately
authorized verification through **Kodi Lab**, with its existing permissions. This
static workflow grants no managed/external Kodi access and does not authorize
source edits, deployment, GUI/texture operations or changes to validation gates.

Basis: [issue #35 evaluation](https://github.com/kcook98765/kodi-agent-toolkit/issues/35),
[pinned upstream usage and license information](https://github.com/MikeSiLVO/kdk/blob/bea0c7d6095e3b0eb4ef24e90bc8df27e9828f33/README.md).
