# Save screenshot artwork

Use `kodi-toolkit screenshot-export` in the [locked Python environment](../README.md#quick-start).
Pillow is already included in all four validation locks; no new package is needed.
Export writes currently require **Linux or WSL**. Other platforms fail before
writing; native Windows users can run the helper from their WSL checkout.

Select your local add-on source directory containing a valid `addon.xml` and one
`xbmc.addon.metadata` extension. Use an opaque, single-frame **PNG or JPEG** at
**1280×720 or 1920×1080**, at most **750,000 bytes** (a conservative 750 KB).
These follow [Kodi artwork recommendations](https://kodi.wiki/view/Add-on_structure#Screenshots).
The destination suffix must match the actual image format. Compliant bytes are
copied unchanged. Resize, flatten transparency or compress in your image editor
first if necessary; the helper does not change image quality.

## Manual route: Kodi Lab Web → local image → add-on

1. Sign in to your existing Kodi Lab Web interface. Use an already authorized,
   running **managed development** instance displaying the intended add-on UI.
   This workflow grants no new target access or lifecycle permission.
2. On the instance detail page, expand **Alternative viewers, screenshots and
   browser remote**, then find **Saved screenshot**. Use **Refresh screenshot**
   only within your existing authorization. Open/save the displayed image using
   your browser's image menu, keeping the PNG extension. The authenticated
   same-origin image URL is `/api/instances/INSTANCE_ID/screenshots/latest`.
   It serves the latest retained PNG inline; there is no dedicated export API.
   A new capture replaces the prior image. External targets do not provide this
   managed Web cache. Do not copy server cache paths or browser credentials.
3. Save/transfer the file to the machine and filesystem running the Toolkit.
   A browser download on a laptop is not automatically a file on a remote
   OpenCode host. Inspect the downloaded image before selecting it.
4. Export and explicitly request a manifest update:

```sh
kodi-toolkit screenshot-export ./script.example \
  resources/screenshots/screenshot-01.png \
  --input ./downloaded-screenshot.png --update-manifest
```

The image now lives at
`script.example/resources/screenshots/screenshot-01.png`. Its existing
`addon.xml` metadata receives:

```xml
<extension point="xbmc.addon.metadata">
  <!-- existing summary, description, license and other metadata stay here -->
  <assets>
    <icon>resources/icon.png</icon>
    <screenshot>resources/screenshots/screenshot-01.png</screenshot>
  </assets>
</extension>
```

Omit `--update-manifest` to **export only**, leaving `addon.xml` byte-for-byte
unchanged. The command prints the exact entry you can add later. When updating,
missing `<assets>` is added, existing icon/fanart/screenshots remain, an already
declared path is not duplicated, and at most ten screenshots may be declared.
An existing destination file is always rejected, even if its bytes match.

## OpenCode 1.19.3: authorized capture → private export → add-on

An MCP image visible to the model is not a local image file. OpenCode 1.19.3
retains native MCP images as base64 file attachments, and its supported
`export` command includes completed tool attachments in session JSON. Sources:
[MCP result adapter](https://github.com/anomalyco/opencode/blob/v1.19.3/packages/opencode/src/session/tools.ts)
and [session export](https://github.com/anomalyco/opencode/blob/v1.19.3/packages/opencode/src/cli/cmd/export.ts).
No plugin or OpenCode settings change is required.

With an existing authenticated Kodi Lab MCP connection, exact target grant,
screenshot permission/capability and permitted runtime state, request an
authorized `screenshot_capture`. Do not start a stopped target or broaden grants
to obtain artwork. Select that session and its **exact tool call ID**:

```sh
# Session JSON contains private transcript and image data. Keep it outside Git.
umask 077
opencode export SESSION_ID > /private/session.json

# List screenshot call IDs without printing their images or transcripts.
python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print("\n".join(p["callID"] for m in d["messages"] for p in m["parts"] if p.get("type")=="tool" and p.get("tool", "").endswith("_screenshot_capture")))' /private/session.json

kodi-toolkit screenshot-export ./script.example \
  resources/screenshots/screenshot-01.png \
  --opencode-export /private/session.json --call-id EXACT_CALL_ID \
  --update-manifest
```

The helper reads only the supplied local JSON (maximum 32 MiB), requires exactly
one completed `*_screenshot_capture` call with that ID and exactly one PNG data
attachment, then validates the decoded image. It never contacts OpenCode, reads
its database, downloads URLs or calls Kodi. This is explicit extraction from a
session export, not automatic saving on capture. The export's claims do not
authenticate its origin or prove what UI the image depicts.

Qualification used synthetic image fixtures and an isolated installed OpenCode
1.19.3 import/export roundtrip. **Live Kodi capture → OpenCode → add-on was not
tested.** The local image workflow and attachment extraction are separate from
live capture acceptance. Other OpenCode versions need their export shape checked.

## Verify and troubleshoot

Successful JSON reports the relative path, format, dimensions, byte count,
SHA-256, exact manifest entry and `manifest_changed`. `capture_verified` and
`package_validated` remain false: export alone proves neither. Inspect the image
and run your normal [add-on validation](validation.md), using the intended Kodi
lane and metadata cache. Include the asset in the package you actually distribute
and check that package separately. Export never packages, commits or publishes.

- **Missing PNG bytes:** model text or capture metadata cannot reconstruct an
  image. `opencode export --sanitize` redacts attachment URLs, so it cannot supply
  pixels. Use a private unsanitized export, or the browser/local-file route.
- **Unsupported image:** use a complete PNG/JPEG at the required dimensions,
  flatten to opaque RGB and reduce to 750,000 bytes or less in an editor.
- **Collision:** select a new filename or manage the existing file yourself.
  There is no overwrite flag.
- **Invalid manifest:** repair its existing XML, metadata extension, unsafe or
  duplicate screenshot paths, or count before retrying. UTF-8 is required.
- **Symlink or file-operation error:** select a real local source tree and input
  file without symlink ancestors. Source and manifest must be regular files.
- **Large session:** use a smaller dedicated capture session or browser-saved
  image. Do not publish session exports or screenshots as troubleshooting logs.

Writes stage and fsync both files, publish the image without clobbering, then
atomically replace the manifest. Catchable write failures roll back the new image
and created directories. No two-file operation is atomic across sudden process
termination or power loss: interruption between publication steps can leave an
undeclared image. Inspect the destination before retrying. Use a quiet checkout;
this helper is not a transaction system for concurrent editors. Permissions,
ownership and filesystem support for no-follow operations and hard links still
apply. No Kodi profiles, grants, configuration or temporary caches are modified.
