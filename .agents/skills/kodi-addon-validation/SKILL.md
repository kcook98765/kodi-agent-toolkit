---
name: kodi-addon-validation
description: "Run static Kodi add-on validation and official addon-check; review contextual source issues with evidence when requested."
license: MIT
---

Verify the project/add-on root and target release. Enumerate files with `kodi_validate operation="discover"`, `kodi-toolkit discover`, or available file listing; use existing project-relative paths. Missing path: rediscover once, then report what is unavailable. Quote spaces; do not pass Windows paths to a WSL tool.

Run `kodi_validate` or `kodi-toolkit validate ADDON --branch VERIFIED_BRANCH` with the isolated checker/stub environment. Read references/validation.md for setup or stage details. Inspect every stage: completed tool calls and zero exits alone do not prove success. Missing cache, crash, timeout or skipped required stages remain incomplete validation. Do not download or alter configuration to hide failures. Read the reported manifest line before explaining an XML correction.

For contextual review read references/review.md. Use numbered `kodi_review context` sources once, trace related evidence and counterevidence, then compose a brief draft using `kodi_review compose` with its structured `report` argument. Do not rerun validation after successful composition. Use `finding_categories`; structurally accepted claims remain observations unless independently supported. Kodi requirements need an identifiable basis. Empty findings are valid.

Completion: report actual stages, locations, warnings and limits. Correct a rejected draft once; if still rejected, report PARTIAL or FAIL. Prefer recorded `report-build`/evaluation final reports; never restate rejected claims as verified. Summarize within 200 words unless detail is requested.
