# GitHub publication plan — approval required

Nothing in this plan has been executed remotely. Repository creation, push, visibility changes, tag publication and a GitHub release require the owner's explicit approval of the final reviewed commit and operations.

## Proposed metadata

| Field | Value |
|---|---|
| Owner/repository | `kcook98765/kodi-agent-toolkit` |
| Description | Portable agent skills and standalone Kodi add-on validation with official checker integration and evidence-based reports. |
| Topics | `kodi`, `kodi-addon`, `python`, `agent-skills`, `opencode`, `mcp`, `developer-tools`, `static-analysis` |
| Homepage/related project | https://github.com/kcook98765/kodi-lab |
| Default branch | `main` |
| License | Existing MIT for original source; independently installed dependencies retain separate licenses |
| Version | GitHub prerelease `v0.1.0-beta.1`; Python package metadata `0.1.0b1` |
| Funding | `github: [kcook98765]`; authenticated Sponsors listing and public page verified |
| Issues | Enabled; bug and documentation forms; blank issues disabled |
| Private vulnerability reporting | Enable before pushing; SECURITY.md links to the proposed private channel |
| Wiki/projects/discussions | Disabled initially |

Authenticated GitHub account matched the intended owner. The repository API returned 404 and the authenticated owner's listing had no repository with the proposed name. This is an availability check, not a reservation; repeat it immediately before creation. Kodi Lab is a separate related project, not a toolkit prerequisite. No Kodi Lab settings or source are changed.

## History decision

Publish **only the independent reviewed initial snapshot**, preserving the original development repository and Phase 6 branch/commit locally. The original history audit found no known credentials, personal home paths or removed-file disclosures, but historical evaluation code includes workstation provider aliases, observer routing and implicit token-file discovery. Those assumptions are removed from the public harness. Sanitized Phase 4–6 results, source/skill/cache hashes and failures remain public evidence; old development commit IDs are provenance references and are not public Git objects. No raw transcripts or workstation journal is included.

## Approval-gated operations

The full approved SHA and exact local path are recorded in the external Phase 7 workstation report, avoiding personal paths in this public document. Use GitHub CLI and Git in an authenticated shell; replace the two placeholders, verify the candidate is clean, and stop on any command error. These commands are a proposal, not an executable release script.

```sh
cd REVIEWED_SNAPSHOT
approved_commit=APPROVED_FULL_SHA
test "$(git rev-parse HEAD)" = "$approved_commit"
test -z "$(git status --porcelain)"
test "$(git rev-list --count HEAD)" = 1
python3 scripts/secret-scan.py
python3 scripts/secret-scan.py --staged
python3 scripts/secret-scan.py --history
gh api user --jq .login
gh api repos/kcook98765/kodi-agent-toolkit
# Expect authenticated 404; distinguish it from network/authentication errors.
# After explicit owner approval, create empty source-only repository:
gh repo create kcook98765/kodi-agent-toolkit --public --description 'Portable agent skills and standalone Kodi add-on validation with official checker integration and evidence-based reports.' --homepage https://github.com/kcook98765/kodi-lab --disable-wiki
gh api --method PUT repos/kcook98765/kodi-agent-toolkit/private-vulnerability-reporting
gh repo edit kcook98765/kodi-agent-toolkit --enable-issues --enable-wiki=false --enable-projects=false --enable-discussions=false --add-topic kodi --add-topic kodi-addon --add-topic python --add-topic agent-skills --add-topic opencode --add-topic mcp --add-topic developer-tools --add-topic static-analysis
git remote add origin https://github.com/kcook98765/kodi-agent-toolkit.git
git push origin main:main
gh repo edit kcook98765/kodi-agent-toolkit --default-branch main
```

Push only `main` from the snapshot. Do not use `--mirror`, `--all`, or copy the original `.git` directory. Do not initialize a remote README/license/ignore file. GitHub creation starts public as approved; no separate visibility conversion is needed. The original local repository receives no remote.

Before tag/release publication, require the initial Actions run to finish successfully, check private reporting, and test a new public clone/README installation. If network acquisition fails, retain evidence and state it explicitly; a separately trusted complete cache is an explicit alternative, never an automatic fallback. Stop if the approved source needs modification and review the new commit before publishing a tag.

After approval includes these operations and the above checks pass:

```sh
git tag -a v0.1.0-beta.1 "$approved_commit" -m 'First standalone public beta'
git push origin refs/tags/v0.1.0-beta.1
gh release create v0.1.0-beta.1 --repo kcook98765/kodi-agent-toolkit --verify-tag --prerelease --title 'Kodi Agent Toolkit v0.1.0-beta.1' --notes-file docs/release-notes-v0.1.0-beta.1.md
```

Attach no extra binary/dependency/cache assets. GitHub generates source archives. No PyPI or container publication is proposed. Release notes explicitly retain model failures and unvalidated runtime scope.

## Suggested settings

Use read-only Actions token permissions and require approval for workflows from outside collaborators. The included Ubuntu/Windows jobs install public hash-locked dependencies, run offline deterministic tests/harness checks and scan public contents/history; they need no secret, private service, paid API, model server, Docker or running Kodi. Actions are pinned to verified official commit SHAs. Local equivalents are tested; GitHub-hosted runner execution is pending publication.

After the first successful run, protect `main` against force pushes/deletion and require the two standalone CI checks for pull requests. Use one approval when a second maintainer is available; avoid a sole-maintainer deadlock. Enable GitHub secret scanning/push protection and dependency alerts where available; do not add complex scheduled release/model automation for this beta. The lock/inventory must be updated deliberately with regression and license review.

References: [GitHub private reporting](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/configure-for-a-repository), [repository REST API](https://docs.github.com/en/rest/repos/repos#enable-private-vulnerability-reporting-for-a-repository), [hosted runners](https://docs.github.com/en/actions/reference/runners/github-hosted-runners), [Sponsors](https://github.com/sponsors/kcook98765).
