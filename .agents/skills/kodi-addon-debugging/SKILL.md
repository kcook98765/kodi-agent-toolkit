---
name: kodi-addon-debugging
description: "Investigate Kodi add-on symptoms with reproducible tests and available logs/UI diagnostics; distinguish observations from hypotheses."
license: MIT
---

Identify the add-on, target version, symptom and reproduction. For local source, enumerate existing files and read the manifest's verified entry point before diagnosing. Never cite a guessed path; after a missing path rediscover once.

For a static reproduction, find the target release's documented isolated interpreter. Run it with `-m kodi_agent_toolkit.cli stub-lanes` to record actual Python/platform, installed tools and qualification/readiness limits, then use that same interpreter and intended branch for validation. Use version-compatibility for lane locks and Matrix/Piers limits. Preserve every error and warning; unavailable setup or a failed type check remains incomplete. Never replace another environment or treat static success as native reproduction.

For managed Kodi use the explicit generation and the acquired lease. Use `managed_status` for release and authenticated Bridge readiness, `managed_gui` for the current window and focus, `managed_logs` for the bounded tail, and `managed_screen` for actual pixels. Record the expected revision or run marker. For external Kodi, discover the separately authorized target UUID and inspect the available capabilities. The [debugging reference](references/debugging.md) describes external native diagnostics and large-log scanning. Read-only grants do not allow navigation or lifecycle changes.

Separate observations, hypotheses, next test and verified outcome. Use only available authorized logs; screenshots require actual image input to an image-capable model. A proposed correction is untested until the original reproduction passes afterward. Report blocked deployment/launch steps accurately. Finish with source/tool evidence and limits in at most 150 words unless more detail is requested.
