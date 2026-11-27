from __future__ import annotations

import json
import os
import shutil
import subprocess
import unittest
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

from kodi_agent_toolkit import video


class VideoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scratch = TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)

    def test_sidecar_preserves_explicit_monotonic_text(self) -> None:
        sidecar = self.root / "progress.jsonl"
        video.comment(
            sidecar, "Reproduced the navigation defect.", ms=100, started_at=None
        )
        video.comment(sidecar, "Static validation passed.", ms=1300, started_at=None)
        self.assertEqual([cue["ms"] for cue in video.read_cues(sidecar)], [100, 1300])
        for offset, text in [
            (1200, "Out of order"),
            (1400, "Markup {\\an5}"),
            (1400, "Two\nlines"),
        ]:
            with self.assertRaises(ValueError):
                video.comment(sidecar, text, ms=offset, started_at=None)
        if os.name != "nt":
            self.assertEqual(sidecar.stat().st_mode & 0o077, 0)

    @unittest.skipUnless(
        shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg tools unavailable"
    )
    def test_composition_preserves_originals_order_and_caption_timing(self) -> None:
        capabilities = {}
        for flag in ("-filters", "-encoders"):
            capabilities[flag] = subprocess.check_output(
                ["ffmpeg", "-hide_banner", flag],
                stderr=subprocess.STDOUT,
                timeout=15,
            )
        if (
            b" subtitles " not in capabilities["-filters"]
            or b" libx264 " not in capabilities["-encoders"]
        ):
            self.skipTest("FFmpeg subtitles filter or libx264 unavailable")
        originals = [self.root / "one.mp4", self.root / "two.mp4"]
        for color, path in zip(("red", "blue"), originals):
            subprocess.run(
                [
                    "ffmpeg",
                    "-loglevel",
                    "error",
                    "-f",
                    "lavfi",
                    "-i",
                    f"color=c={color}:s=640x360:r=2:d=2",
                    "-c:v",
                    "libx264",
                    "-threads",
                    "1",
                    "-pix_fmt",
                    "yuv420p",
                    str(path),
                ],
                check=True,
                timeout=15,
            )
        original_digests = [sha256(path.read_bytes()).hexdigest() for path in originals]
        sidecar = self.root / "progress.jsonl"
        video.comment(
            sidecar, "Verified the corrected behavior.", ms=500, started_at=None
        )
        manifest = self.root / "session.json"
        manifest.write_text(
            json.dumps(
                {
                    "segments": [
                        {"video": "one.mp4"},
                        {"video": "two.mp4", "comments": "progress.jsonl"},
                    ]
                }
            )
        )
        for captions in (False, True):
            output = self.root / f"composed-{captions}.mp4"
            result = video.compose(manifest, output, captions=captions)
            self.assertEqual(result["timeline"][1]["output_ms"], 2000)
            self.assertEqual((result["duration"], result["audio_streams"]), (4, 0))
            self.assertEqual(
                (result["width"], result["height"]), (640, 440 if captions else 360)
            )
            self.assertEqual(result["fps"], "2/1")
            if os.name != "nt":
                self.assertEqual(output.stat().st_mode & 0o077, 0)
            with self.assertRaisesRegex(ValueError, "unused local output"):
                video.compose(manifest, output, captions=captions)
            if captions:
                before, after = (
                    self.read_band(output, stamp) for stamp in ("1.0", "3.0")
                )
                self.assertLess(max(before), 64)
                self.assertGreater(max(after), 200)
        self.assertEqual(
            [sha256(path.read_bytes()).hexdigest() for path in originals],
            original_digests,
        )

    @staticmethod
    def read_band(path: Path, seconds: str) -> bytes:
        data = subprocess.check_output(
            [
                "ffmpeg",
                "-loglevel",
                "error",
                "-ss",
                seconds,
                "-i",
                str(path),
                "-vf",
                "crop=640:80:0:360,format=gray",
                "-frames:v",
                "1",
                "-threads",
                "1",
                "-f",
                "rawvideo",
                "pipe:1",
            ],
            timeout=15,
        )
        if len(data) != 640 * 80:
            raise ValueError("Caption sample differs from the expected band")
        return data

    def test_download_refuses_untrusted_origin_and_id(self) -> None:
        with self.assertRaisesRegex(ValueError, "finalized recording ID"):
            video.download(
                "https://lab.example/mcp",
                Path("unopened"),
                "../secret",
                "b" * 64,
                self.root / "recording.mp4",
            )
        with self.assertRaisesRegex(ValueError, "authorized Kodi Lab HTTPS MCP"):
            video.download(
                "http://lab.example/mcp",
                Path("unopened"),
                "a" * 32,
                "b" * 64,
                self.root / "recording.mp4",
            )
