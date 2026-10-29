---
name: kodi-addon-development
description: "Create or repair Kodi Python add-ons using their actual manifest, entry points and target APIs. Use validation for audits and review."
license: MIT
---

Find the actual project and add-on root before reading or editing. Use `kodi-toolkit discover` or, when its exposed schema matches the optional fixture adapter, `kodi_validate` with `operation="discover"` (omit `addon_dir`) to enumerate existing files and manifest entry points; otherwise use the agent's file listing. Use returned project-relative paths. After a missing path, rediscover once; do not guess another filename. Quote paths containing spaces and use paths native to the current Windows/WSL session.

For a named project, check applicable instruction files at its known ancestor paths directly; keep recursive searches inside the relevant project instead of scanning an entire drive or home directory. Resolve installed skill references from the loaded skill's location, which can differ from the add-on and agent working directories.

Read `addon.xml` and its verified declared entry files. Confirm the requested Kodi release: `xbmc.python` alone does not uniquely select it. For manifest/lifecycle/API details or longer test/fix loops read references/development.md; use version-compatibility when release differences matter.

Reproduce a repair with static validation before editing. Preserve behavior, dependencies and intended logging severity; use a verified target symbolic constant, never a guessed number or deleted level. Kodi modules/stubs must not be executed outside Kodi.

Make one focused correction, then rerun relevant checks and official validation. For an authorized Kodi Lab loop, read references/development.md and use `kodi-mcp-testing` when installed for the detailed MCP contracts: prepare the owned workspace, validate its current generation, read deployment prerequisites, deploy through the admitted workflow, then launch only a qualified entry point and observe the changed behavior. Reuse valid receipts for unchanged bytes; do not reset Kodi to force progress.

Completion means the original defect was detected, corrected and rechecked. Distinguish failed, passed, skipped and untested stages; retain warnings. File application, launch dispatch and functional runtime acceptance are separate results. Stop after completion. Unless requested otherwise, summarize change, evidence and limits within 150 words. Standalone development needs no Kodi Lab; deployment requires an authorized disposable target.
