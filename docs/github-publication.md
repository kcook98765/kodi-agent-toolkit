# GitHub publication record and release procedure

The [public repository](https://github.com/kcook98765/kodi-agent-toolkit) contains the reviewed initial snapshot; its initial public clones and [hosted CI](https://github.com/kcook98765/kodi-agent-toolkit/actions/runs/38495360537) were verified. The owner has approved the final documentation correction and `v0.1.0-beta.1` prerelease after protected-branch publication and successful CI on the corrected main commit. The original development history remains private and unchanged.

## Repository metadata

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
| Private vulnerability reporting | Enabled; SECURITY.md links to the private reporting channel |
| Wiki/projects/discussions | Disabled initially |

The repository was created publicly under the verified owner `kcook98765` after an authenticated availability check. Metadata and private vulnerability reporting were applied and verified. Kodi Lab is a separate related project, not a toolkit prerequisite. No Kodi Lab settings or source are changed.

## History decision

Published **only the independent reviewed initial snapshot**, preserving the original development repository and Phase 6 branch/commit locally. Subsequent release documentation corrections retain that snapshot as their ancestor. The original history audit found no known credentials, personal home paths or removed-file disclosures, but historical evaluation code includes workstation provider aliases, observer routing and implicit token-file discovery. Those assumptions are removed from the public harness. Sanitized Phase 4–6 results, source/skill/cache hashes and failures remain public evidence; old development commit IDs are provenance references and are not public Git objects. No raw transcripts or workstation journal is included.

## Initial publication commands (historical record)

The following commands record the completed initial publication procedure, with placeholders for the originally approved snapshot and local path. Do not rerun repository creation or the one-commit initial-snapshot checks against the now-public repository. Exact original source and publication details are retained in the external Phase 7 workstation report.

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

Initial publication pushed only snapshot `main`. Do not use `--mirror`, `--all`, or copy the original development `.git` directory. The repository was created public with no generated README/license/ignore commit. The original local development repository still has no remote.

Initial hosted CI, private reporting and fresh public-clone checks passed. Windows public-clone metadata acquisition succeeded; the Linux attempt failed with network unreachable and checker tests explicitly used a trusted complete Phase 6 cache. Earlier HTTP 429/download failures remain documented. Before tagging, publish only the approved documentation correction through normal branch protection, verify its exact remote main commit and require successful hosted CI on that commit. Stop on failed checks, unrelated changes or an existing remote version tag; do not bypass protection.

After the corrected main commit passes those checks, confirm `v0.1.0-beta.1` is absent remotely. Replace the earlier unpublished local annotated tag so it targets that verified commit, then publish only that tag and the approved prerelease notes:

```sh
# approved_commit is the corrected, CI-verified main SHA.
# Delete only the unpublished local tag after confirming no remote version tag exists.
git tag -d v0.1.0-beta.1
git tag -a v0.1.0-beta.1 "$approved_commit" -m 'First standalone public beta'
git push origin refs/tags/v0.1.0-beta.1
gh release create v0.1.0-beta.1 --repo kcook98765/kodi-agent-toolkit --verify-tag --prerelease --title 'Kodi Agent Toolkit v0.1.0-beta.1' --notes-file docs/release-notes-v0.1.0-beta.1.md
```

Attach no extra binary/dependency/cache assets. GitHub generates source archives. No PyPI or container publication is proposed. Release notes explicitly retain model failures and unvalidated runtime scope.

## Verified settings

Use read-only Actions token permissions and require approval for workflows from outside collaborators. The included Ubuntu/Windows jobs install public hash-locked dependencies, run offline deterministic tests/harness checks and scan public contents/history; they need no secret, private service, paid API, model server, Docker or running Kodi. Actions are pinned to verified official commit SHAs. Local equivalents and [GitHub-hosted Ubuntu/Windows jobs](https://github.com/kcook98765/kodi-agent-toolkit/actions/runs/38495360537) passed.

`main` is protected against force pushes/deletion, including admins, and requires both standalone CI checks. No mandatory human review count is configured for the sole maintainer. Secret scanning, push protection and dependency alerts are enabled. No settings are changed by the documentation correction. Future lock/inventory changes require deliberate regression and license review; no complex scheduled release/model automation is needed for this beta.

References: [GitHub private reporting](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/configure-for-a-repository), [repository REST API](https://docs.github.com/en/rest/repos/repos#enable-private-vulnerability-reporting-for-a-repository), [hosted runners](https://docs.github.com/en/actions/reference/runners/github-hosted-runners), [Sponsors](https://github.com/sponsors/kcook98765).
