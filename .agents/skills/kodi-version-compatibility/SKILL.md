---
name: kodi-version-compatibility
description: "Assess Kodi add-on compatibility for specified releases using version-specific API, dependency and stub evidence; identify ambiguous targets."
license: MIT
---

Verify the actual add-on root/files and read its manifest and relevant source. A Python API dependency version is not the runtime CPython version and does not uniquely select a Kodi release. If the target is missing, state the ambiguity and required information; do not guess a checker branch or advertise broad compatibility.
An import version is a minimum dependency, not an exact release or upper bound. A higher provided API version can satisfy it; do not exclude later Kodi releases from this field alone.

Read references/versions.md for dated, pinned evidence. Match each API/signature and installed stub major to the requested release; verify removals rather than infer them from release names. Moving master docs and prerelease evidence do not prove stable support. Missing/mismatched stubs are a coverage failure.

For a multi-version target prefer the oldest verified common API or a documented guard. Run branch-matched syntax/types/checker tests where available. Do not install a different stub version into an existing validated environment without isolating it.

Completion: identify supported/unsupported or uncertain API use with verified file/line evidence, documentation snapshot, static target and actual runtime-tested versions. Static acceptance does not prove runtime/binary compatibility. Do not claim an untested platform/version passed. Keep the final summary within 150 words unless a matrix or detailed report is requested.
