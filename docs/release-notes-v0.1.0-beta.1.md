# Kodi Agent Toolkit v0.1.0-beta.1

First public beta for standalone Kodi add-on development assistance. The [repository](https://github.com/kcook98765/kodi-agent-toolkit) is public. Package metadata uses the corresponding Python prerelease version `0.1.0b1`; no PyPI publication is planned.

## Supported standalone functionality

- Five portable skills and supporting references; OpenCode 1.19.0 is the initial reference agent.
- Kodi 20/Nexus Python stubs configuration and mypy API checks.
- Integration with the separately installed official addon-check, retaining original warnings and failures.
- Read-only source discovery and six-stage static add-on validation.
- Independent evidence categories and factual reports from trusted tool records.
- Original sample add-ons, validation fixtures, deterministic tests, and an optional evaluation harness.

Follow the [README quick start](../README.md) with Python 3.12, the hash-locked development dependencies, and an explicit official metadata cache. No agent, model server, running Kodi, Docker, WSL2, or Kodi Lab is required for standalone validation. Network is needed for initial downloads; later validation and deterministic tests can run offline.

## Experimental components and limits

AI contextual review, autonomous repair, smaller-model workflows, Kodi Lab MCP integration, and runtime debugging remain experimental. Phase 6's 13 agent trials received 2 PASS, 6 PARTIAL, 5 FAIL by independent task/answer judgment. Two bounded API repairs were verified; this does not establish dependable autonomous development.

Runtime deployment and reproduction were not validated end-to-end: required registered development-source infrastructure was absent. No autonomous runtime repair completed. General semantic correctness, spontaneous skill routing, macOS execution, native Windows agent cleanup, and other Kodi major environments remain unqualified.

Original source is MIT. The lock separately installs Kodistubs 20.0.1 and kodi-addon-checker 0.0.36 under their own GPL-3.0-only notices, plus mypy 2.4.0 and the inventoried transitive dependencies. No third-party dependency wheels, Kodi binaries, proprietary KodiAI code/prompts, private configuration, or raw transcripts are included. See [attribution](licensing.md).

Phase 7 published a reviewed initial source snapshot while preserving the private development history separately. Sanitized Phase 4–6 scorecards and qualification limitations remain intact. Historical installation/regression results are recorded in [release preparation evidence](phase7-results.md). [Hosted GitHub Actions](https://github.com/kcook98765/kodi-agent-toolkit/actions/runs/38495360537) subsequently passed on Ubuntu 24.04 (171 passed, 1 skipped) and Windows 2025 (167 passed, 5 skipped). These deterministic checks do not validate model reliability or runtime deployment.
