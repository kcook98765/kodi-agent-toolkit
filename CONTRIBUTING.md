# Contributing

Keep changes focused on existing development, validation, review and testing workflows. Work on a local branch and use disposable add-on fixtures. Do not change production Kodi, grant new MCP permissions, or change provider/server settings as part of a toolkit test.

Follow the README's Python 3.12 isolated, hash-locked setup. Ubuntu WSL2 is the OpenCode reference environment; native Windows static tooling is tested, while macOS, other hosts and native Windows agents need qualification. Run Linux dependency commands inside the Linux checkout. Copy one skill directory, including references, into the receiving agent's supported location; OpenCode is optional for the CLI.

For a source change, run relevant deterministic tests and then the full applicable suite:

```sh
.venv/bin/python -m unittest discover -s tests -v
python3 scripts/secret-scan.py
git diff --cached --name-only
python3 scripts/secret-scan.py --staged
python3 scripts/secret-scan.py --history
```

CLI official checks need the explicitly acquired metadata cache described in docs/validation.md; regressions generate synthetic offline caches. A failed or skipped checker, unavailable model, or untested runtime is not a pass. Preserve original evaluation artifacts; use new labels for trials. Keep subjective review judgments separate from deterministic acceptance.

Keep private providers, tokens, endpoints, Kodi profiles, logs, screenshots and model transcripts outside Git. For known credentials, add `--secret-file PRIVATE_TOKEN_PATH` to each scan; the file must stay outside the repository. The scanner is heuristic and reports only file names and rule names. Review the complete candidate diff and history before sharing.

Original contributions are offered under the repository's MIT license. Do not copy proprietary KodiAI code or prompts, third-party stubs, checker source, or Kodi binaries into this repository. Dependencies retain their own licenses; update the lock and dependency inventory deliberately and document verified license sources. See docs/licensing.md.

A proposed change should explain the demonstrated problem, resulting behavior, commands actually run, and remaining limits. Report model/agent versions and trial conditions when evaluating skill changes. Avoid claiming cross-platform or runtime support from static checks alone.

## Beta feedback

Use the issue forms for a minimal sanitized reproduction or documentation feedback. Follow CODE_OF_CONDUCT.md. Pull requests should explain the reproduced problem, resulting behavior, actual validation, and remaining limits. The small CI matrix runs offline regressions and scans with publicly downloaded locked dependencies; it never contacts Kodi Lab or model providers. Public history starts at the reviewed beta snapshot, so historical phase commit hashes are provenance references rather than fetchable public commits.
