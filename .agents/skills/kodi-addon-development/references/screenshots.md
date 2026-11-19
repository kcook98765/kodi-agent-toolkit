# Screenshot artwork

Use the existing Toolkit Linux/WSL CLI in its hash-locked environment. Acquire a
real local PNG/JPEG before importing; do not reconstruct pixels from metadata.

```sh
kodi-toolkit screenshot-export ./script.example \
  resources/screenshots/screenshot-01.png --input ./saved.png --update-manifest
```

Omit `--update-manifest` to export without XML changes. With it, the existing
`xbmc.addon.metadata/assets` receives
`<screenshot>resources/screenshots/screenshot-01.png</screenshot>` without losing
other metadata. Missing assets is added, duplicate paths are not added, ten
declarations is the maximum. Existing files are never overwritten.

Use 1280x720 or 1920x1080 opaque, single-frame PNG/JPEG, <=750,000 bytes.
Compliant bytes are preserved. Fix dimensions, transparency or size in an image
editor first. Source paths and add-on tree must not traverse symlinks.

Manual: sign in to Kodi Lab Web, select the already authorized running managed
development instance, expand **Alternative viewers, screenshots and browser
remote** → **Saved screenshot**, refresh only if authorized, then use the
browser's image menu to save its PNG. This uses authenticated
`/api/instances/INSTANCE_ID/screenshots/latest`; it is latest-only, managed-only
storage. Transfer a laptop download to the Toolkit host if necessary. Never use
Lab cache paths, credentials in commands, or `workspace_edit` for image bytes.

OpenCode 1.19.3 retains MCP PNG attachments in its supported session export:

```sh
umask 077
opencode export SESSION_ID > /private/session.json
kodi-toolkit screenshot-export ./script.example \
  resources/screenshots/screenshot-01.png \
  --opencode-export /private/session.json --call-id EXACT_CALL_ID --update-manifest
```

Select the exact completed `*_screenshot_capture` call with one PNG attachment.
`--sanitize` removes image data; text/metadata-only results cannot be exported.
Keep JSON/transcripts/pixels outside Git. No plugin, database access, URL download
or configuration change is needed. Extraction from a supplied export is supported;
live Kodi-to-OpenCode-to-add-on capture has not been qualified by this feature.

Capture still requires existing authentication, exact-target grant, screenshot
permission/capability and permitted runtime state. Do not broaden grants, access
household targets or start Kodi to make this workflow pass.

Check returned path, dimensions, format, bytes, SHA-256 and manifest_changed.
Inspect the image; then run normal validation with the intended Kodi lane and
cache, and check that the distributed package contains the referenced file.
Capture, locally acquired bytes, export, declaration and package validation are
separate outcomes. Catchable write failures roll back new files; sudden process
termination can leave an undeclared image. Retry only after inspecting the tree.
