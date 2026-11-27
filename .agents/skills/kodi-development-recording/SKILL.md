---
name: kodi-development-recording
description: >-
  Record an actual authorized Kodi add-on development task on managed Kodi.
  Use when the owner wants source, deploy, native testing and defect correction
  milestones explained in timestamped captions over a silent Kodi video.
license: MIT
---

# Kodi development recording

Follow the normal authorized development workflow and use this skill alongside it.

1. Identify the add-on, defect or change, worktree, disposable managed profile and acceptance check. Agree on a private destination. Keep pre-existing source and runtime state protected.
2. Confirm the exact running managed generation. Call `managed_recording_start` at 2 FPS by default. Poll `managed_recording_status` for the recording ID, `started_at` and recording state. Keep a private manifest in the order segments were captured.
3. Reproduce and observe the behavior on Kodi. At meaningful milestones use `kodi-toolkit video comment SIDECAR TEXT --started-at ANCHOR` for explicit public-facing text. Use approved text only, such as "Reproduced the missing focus restore after opening Details." Use an explicit offset for a title at the start of a segment.
4. Inspect and correct the real source. Perform the normal static and deployment checks. Add a concise caption describing the action and its observed result, without including credentials, private source or transcripts. Keep the Kodi display on a safe screen during source work. Stop capture before a sensitive native screen.
5. Stop and finalize the old recording before a Kodi Stop/deploy/Start cycle when possible. Confirm the new incarnation before starting its next authorized segment. Preserve each ID, time anchor, original checksum and caption sidecar. Add a caption at the new segment's start identifying the deploy or intentional pause. Use an independently observed native result to verify the fix.
6. Download and verify every original. Compose ordered segments with `kodi-toolkit video compose MANIFEST OUTPUT --captions`. Retain originals, commentary and manifest in private storage. The derivative omits gaps between segments. Review screen contents, text and timing locally before providing its path to the owner.

Use the Toolkit recording guide for export and manifest examples. Report failed validation and missing segments accurately and leave publication to the owner.
