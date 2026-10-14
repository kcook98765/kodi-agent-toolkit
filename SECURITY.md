# Security

## Reporting a vulnerability

Report suspected toolkit vulnerabilities privately through GitHub's [Report a vulnerability](https://github.com/kcook98765/kodi-agent-toolkit/security/advisories/new) channel. This candidate awaits publication; the channel must be enabled when the repository is created. If the private channel is unavailable, ask the maintainer for a private contact route without posting vulnerability details publicly.

Include the toolkit revision, platform, a minimal sanitized fixture, observed behavior, expected boundary, and reproduction steps. Do not include credentials, private endpoints, Kodi profiles, library metadata, logs, screenshots, or sensitive transcripts. The current beta line is the maintained security scope; there is no support commitment for historical evaluation revisions.

## Boundaries

Static checks do not execute add-on Python code. The pinned official-checker replay guard is an application-level restriction, not a sandbox for hostile programs. Use an isolated environment and disposable fixtures for untrusted add-ons. Do not import stubs as runtime replacements.

Kodi Lab is optional and requires server-side target authorization. Skill instructions and client permissions do not grant authority. Keep MCP/provider credentials and actual configuration outside Git. Never expand state-changing access merely to complete an evaluation.

Before sharing, inspect the complete candidate and run:

```sh
python3 scripts/secret-scan.py
python3 scripts/secret-scan.py --staged
python3 scripts/secret-scan.py --history
```

For exact known-credential matching, add `--secret-file PRIVATE_TOKEN_PATH`; that file must remain outside Git. Values are not printed. Working-tree scans omit ignored files; staged/history scans inspect actual blob bytes. History scanning covers reachable refs, not unreachable objects, reflogs, or external artifacts. Review commit metadata, images, URLs, and private paths separately. Heuristics cannot guarantee that every credential form is detected.

If a credential was committed, revoke or rotate it at the issuer. Deleting a current file does not erase history. Preserve the original local history and coordinate any publication-history decision with the owner. See [licensing](docs/licensing.md) before redistributing dependencies or combined distributions.
