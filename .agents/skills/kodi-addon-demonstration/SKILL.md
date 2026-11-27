---
name: kodi-addon-demonstration
description: >-
  Record a short silent video of an existing add-on on authorized managed Kodi.
  Use for deliberate Kodi navigation, feature demonstrations and a private
  MP4 for later owner review or publication.
license: MIT
---

# Kodi add-on demonstration

1. Identify the authorized managed generation and the exact add-on. Agree on the behavior to demonstrate and where to save private output. Use a disposable profile when existing settings, data or activity should be preserved.
2. Discover the managed recording and navigation tools. Inspect status, acquire ordinary agent input if needed and navigate to a safe starting screen. Leave the add-on source and published packages alone.
3. Call `managed_recording_start` on that generation. Use the default 2 FPS and choose a bound long enough to hold each important screen. Check `managed_recording_status` until it reports recording and provides `started_at`.
4. Use normal managed navigation. Observe focus, dialogs or results through the appropriate native tools. Hold key screens for three to five seconds so a viewer can read them. Stop capture before opening settings or fields that could show sensitive values.
5. Call `managed_recording_stop` with the returned recording ID. Poll status for finalization and export with `kodi-toolkit video download`, using its ID and SHA-256 with the issuing credential. Verify the file and watch the significant portions locally. Keep the original Kodi-only MP4 as the default deliverable.
6. Return the private local path, verified behavior and a short forum-ready description of what the clip depicts. Leave publication to the owner.

See the Toolkit recording guide for the private export command and optional captions. An expired credential, terminal recording error or changed runtime requires a fresh status check before starting another segment.
