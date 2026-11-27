# Managed Kodi video recording

Use the Toolkit with a Kodi Lab application release that advertises the managed recording tools. FFmpeg and ffprobe must be on the Toolkit host's PATH. Caption composition also needs FFmpeg's subtitles filter and a readable sans-serif font such as DejaVu Sans. The managed Linux broker supplies its own encoder and uses the approved runtime’s existing display. Check the Lab release notes for the exact qualified runtime versions and Windows/WSL2 status.

The Trusted Managed Lab credential that starts a recording must also inspect, stop, retrieve or delete it. Direct Toolkit download accepts the authorized HTTPS MCP endpoint or a loopback HTTP MCP endpoint. Point it at an existing private bearer-token file. No administrator Web session is needed.

## Download and review

Call `managed_recording_start` on the intended live managed generation. The default is 2 FPS. Poll `managed_recording_status` with its ID until it reports `recording`. After navigation or development, call `managed_recording_stop` and wait for `ready`. Use the ID and SHA-256 from the final status.

```sh
umask 077
mkdir -p "$HOME/kodi-private-recordings"
kodi-toolkit video download RECORDING_ID "$HOME/kodi-private-recordings/demo.mp4" \
  --sha256 RECORDING_SHA256 --url http://127.0.0.1:18100/mcp \
  --token-file /path/to/private/managed-agent.token
kodi-toolkit video verify "$HOME/kodi-private-recordings/demo.mp4"
```

The client checks the SHA-256, stream count, codec and local container before publishing the file at the requested path. Check visually that Kodi behavior and text are readable. Store originals outside source control. After verifying a download you can retire its server copy with `managed_recording_delete`. The server limits one active recording, 30 minutes and 64 MiB per segment, and four retained recordings for up to 24 hours.

## Development captions and segments

Write explicit public-facing progress messages while doing the actual authorized work. `--started-at` uses the segment's first-frame UTC anchor and the Toolkit host's current clock. Use synchronized clocks or supply the known segment-relative offset with `--at-ms`.

```sh
kodi-toolkit video comment before.jsonl "Reproduced the navigation defect." --at-ms 0
kodi-toolkit video comment before.jsonl "Applying a focused correction." --started-at FIRST_FRAME_UTC
kodi-toolkit video comment after.jsonl "Verified corrected native navigation after deploy." --at-ms 0
```

Keep a private manifest with original paths, ordered recording IDs, start times and hashes. The composer uses `video` and optional `comments` relative to the manifest. Additional identity fields can be kept alongside them. For example:

```json
{
  "segments": [
    {"video": "before.mp4", "comments": "before.jsonl", "recording": "BEFORE_ID"},
    {"video": "after.mp4", "comments": "after.jsonl", "recording": "AFTER_ID"}
  ]
}
```

```sh
kodi-toolkit video compose session.json development.mp4 --captions
```

The caption band sits below the Kodi pixels. The output receipt maps original segments to their positions in the derived MP4. Omitting `--captions` produces a Kodi-only composition. Capture duration, wall-clock gaps and incarnation changes remain in the original metadata and manifest. Composition joins the videos in manifest order. It omits the time between segments. It supports up to twelve originals of matching dimensions and a two-hour total.

Stop capture before displaying credentials, private configuration, personal media details or other sensitive information. Retain the original recordings separately. Review everything locally before the owner decides whether to share. Supply commentary deliberately. The utilities have no access to agent transcripts or publication accounts.

## Skill prompts

- “Load `kodi-addon-demonstration`. Record a silent 2 FPS Kodi-only walkthrough of [add-on] on [authorized managed version]. Show [features], hold important screens and return the private MP4 with a forum-ready description.”
- “Load `kodi-development-recording` while fixing [defect] in [disposable add-on]. Reproduce it, make a focused correction and verify it on managed Kodi. Add timestamped captions at meaningful milestones, keep originals and return a private captioned MP4.”

If recording tools are absent, confirm the Lab release and assigned role. If retrieval returns an authorization error, confirm the issuing credential and its current permission. If finalization fails after a stop or quota error, confirm the runtime and source status before starting a new segment. For caption errors, check that offsets increase, fit the original duration and contain short plain text.
