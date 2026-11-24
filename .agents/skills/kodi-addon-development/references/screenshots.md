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

Acquire a local capture through the authorized Kodi viewer or a real MCP PNG attachment. See the Toolkit's screenshot documentation for the session export and local-file requirements. For artwork, use a compatible local image copy when the runtime capture dimensions are smaller.

OpenCode 1.19.3 retains MCP PNG attachments in its supported session export:

```sh
umask 077
opencode export SESSION_ID > /private/session.json
kodi-toolkit screenshot-export ./script.example \
  resources/screenshots/screenshot-01.png \
  --opencode-export /private/session.json --call-id EXACT_CALL_ID --update-manifest
```

Select the exact completed `*_screenshot_capture` or `*_managed_screen` call with one PNG attachment.
`--sanitize` removes image data; text/metadata-only results cannot be exported.
Keep JSON/transcripts/pixels outside Git. No plugin, database access, URL download
or configuration change is needed. Export verifies the decoded file and its artwork eligibility. Observe runtime pixels separately.

Capture still requires existing authentication, exact-target grant, screenshot
permission/capability and permitted runtime state. Do not broaden grants, access
household targets or start Kodi to make this workflow pass.

Check returned path, dimensions, format, bytes, SHA-256 and manifest_changed.
Inspect the image; then run normal validation with the intended Kodi lane and
cache, and check that the distributed package contains the referenced file.
Capture, locally acquired bytes, export, declaration and package validation are
separate outcomes. Catchable write failures roll back new files; sudden process
termination can leave an undeclared image. Retry only after inspecting the tree.
