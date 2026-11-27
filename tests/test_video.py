import json
import os
import shutil
import subprocess
from hashlib import sha256
from pathlib import Path

import pytest

from kodi_agent_toolkit import video


def test_sidecar_preserves_explicit_monotonic_text(tmp_path):
    sidecar = tmp_path / "progress.jsonl"
    video.comment(sidecar, "Reproduced the navigation defect.", ms=100, started_at=None)
    video.comment(sidecar, "Static validation passed.", ms=1300, started_at=None)
    assert [cue["ms"] for cue in video.read_cues(sidecar)] == [100, 1300]
    for offset, text in [
        (1200, "Out of order"),
        (1400, "Markup {\\an5}"),
        (1400, "Two\nlines"),
    ]:
        with pytest.raises(ValueError):
            video.comment(sidecar, text, ms=offset, started_at=None)
    assert os.name == "nt" or sidecar.stat().st_mode & 0o077 == 0


@pytest.mark.skipif(
    shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None,
    reason="Native FFmpeg tools are unavailable",
)
def test_composition_preserves_originals_and_order(tmp_path):
    originals = [tmp_path / "one.mp4", tmp_path / "two.mp4"]
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
    sidecar = tmp_path / "progress.jsonl"
    video.comment(sidecar, "Verified the corrected behavior.", ms=500, started_at=None)
    manifest = tmp_path / "session.json"
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
        output = tmp_path / f"composed-{captions}.mp4"
        result = video.compose(manifest, output, captions=captions)
        assert result["timeline"][1]["output_ms"] == 2000
        assert result["duration"] == 4 and result["audio_streams"] == 0
        assert (result["width"], result["height"]) == (640, 440 if captions else 360)
        assert result["fps"] == "2/1"
        assert os.name == "nt" or output.stat().st_mode & 0o077 == 0
        with pytest.raises(ValueError, match="unused local output"):
            video.compose(manifest, output, captions=captions)
    assert [
        sha256(path.read_bytes()).hexdigest() for path in originals
    ] == original_digests


def test_download_refuses_untrusted_origin_and_id(tmp_path):
    with pytest.raises(ValueError, match="finalized recording ID"):
        video.download(
            "https://lab.example/mcp",
            Path("unopened"),
            "../secret",
            "b" * 64,
            tmp_path / "recording.mp4",
        )
    with pytest.raises(ValueError, match="authorized Kodi Lab HTTPS MCP"):
        video.download(
            "http://lab.example/mcp",
            Path("unopened"),
            "a" * 32,
            "b" * 64,
            tmp_path / "recording.mp4",
        )
