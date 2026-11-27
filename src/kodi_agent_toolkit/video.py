"""Private managed recording transfer, commentary, verification and composition."""

from __future__ import annotations

import hashlib
import http.client
import json
import math
import os
import re
import stat
import subprocess
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from textwrap import fill
from urllib.parse import urlsplit

MAX_RECORDING_BYTES = 64 * 1024**2
MAX_SEGMENTS = 12
MAX_DURATION = 7200
MAX_CUES = 240
MAX_CAPTION = 104
CAPTION_BAND = 80
ID_PATTERN = re.compile(r"[0-9a-f]{32}")
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")


@contextmanager
def private_output(destination: Path):
    """Publish a completed private file without replacing an existing path."""
    if destination.exists() or destination.is_symlink():
        raise ValueError("Choose an unused local output path")
    with NamedTemporaryFile(dir=destination.parent, delete=False) as file:
        temporary = Path(file.name)
        try:
            yield file, temporary
            if not file.closed:
                file.flush()
            os.link(temporary, destination)
        finally:
            temporary.unlink(missing_ok=True)


def download(
    endpoint: str, token_file: Path, recording: str, digest: str, destination: Path
) -> dict:
    if not ID_PATTERN.fullmatch(recording) or not SHA256_PATTERN.fullmatch(digest):
        raise ValueError("Use the finalized recording ID and SHA-256 from Kodi Lab")
    if destination.suffix.lower() != ".mp4":
        raise ValueError("Choose a private MP4 destination")
    url = urlsplit(endpoint)
    if (
        not url.hostname
        or url.username is not None
        or url.query
        or url.fragment
        or not url.path.endswith("/mcp")
        or not (
            url.scheme == "https"
            or url.scheme == "http"
            and url.hostname in {"localhost", "127.0.0.1", "::1"}
        )
    ):
        raise ValueError(
            "Use the authorized Kodi Lab HTTPS MCP URL or a loopback HTTP MCP URL"
        )
    with token_file.open(encoding="ascii") as file:
        token = file.read(45).strip()
    if not re.fullmatch(r"[A-Za-z0-9_-]{43}", token):
        raise ValueError("Expected a private Kodi Lab bearer token file")

    connection_type = (
        http.client.HTTPSConnection
        if url.scheme == "https"
        else http.client.HTTPConnection
    )
    connection = connection_type(url.hostname, url.port, timeout=20)
    try:
        connection.request(
            "POST",
            url.path,
            body=b"",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/vnd.kodi-lab.recording",
                "X-Kodi-Lab-Recording": recording,
                "Accept": "video/mp4",
            },
        )
        response = connection.getresponse()
        if response.status != 200:
            raise ValueError(
                f"Kodi Lab recording retrieval returned HTTP {response.status}"
            )
        length = response.getheader("Content-Length", "")
        if (
            response.getheader("Content-Type") != "video/mp4"
            or not length.isascii()
            or not length.isdecimal()
            or len(length) > 9
            or not 0 < int(length) <= MAX_RECORDING_BYTES
        ):
            raise ValueError("Kodi Lab returned invalid recording metadata")
        checksum = hashlib.sha256()
        remaining = int(length)
        with private_output(destination) as (file, temporary):
            while remaining:
                chunk = response.read(min(remaining, 65536))
                if not chunk:
                    raise ValueError("Recording transfer ended early")
                checksum.update(chunk)
                file.write(chunk)
                remaining -= len(chunk)
            if checksum.hexdigest() != digest:
                raise ValueError("Recording checksum differs from Kodi Lab")
            file.close()
            metadata = verify(temporary)
    finally:
        connection.close()
    return {
        "path": str(destination.resolve()),
        "recording": recording,
        "sha256": digest,
        **metadata,
    }


def verify(video: Path) -> dict:
    source = video.resolve(strict=True)
    if not source.is_file():
        raise ValueError("Select one local recording file")
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "stream=codec_type,codec_name,width,height,r_frame_rate:format=duration,format_name",
            "-of",
            "json",
            "-protocol_whitelist",
            "file",
            str(source),
        ],
        check=True,
        stdout=subprocess.PIPE,
        timeout=15,
    )
    data = json.loads(result.stdout)
    streams = data.get("streams", [])
    if (
        len(streams) != 1
        or streams[0].get("codec_type") != "video"
        or streams[0].get("codec_name") != "h264"
        or "mp4" not in data["format"]["format_name"].split(",")
    ):
        raise ValueError("Expected a silent MP4 with one H.264 video stream")
    stream = streams[0]
    width, height = (stream[key] for key in ("width", "height"))
    duration = float(data["format"]["duration"])
    if not (0 < duration <= MAX_DURATION and 0 < width <= 1920 and 0 < height <= 1160):
        raise ValueError("Recording duration or dimensions are out of bounds")
    return {
        "width": width,
        "height": height,
        "duration": duration,
        "fps": stream["r_frame_rate"],
        "codec": "h264",
        "audio_streams": 0,
        "bytes": source.stat().st_size,
    }


def read_cues(path: Path) -> list[dict]:
    with path.open("rb") as file:
        raw = file.read(128 * 1024 + 1)
    if len(raw) > 128 * 1024:
        raise ValueError("Commentary sidecar exceeds its size limit")
    cues = []
    for line in raw.splitlines():
        cue = json.loads(line)
        if not isinstance(cue, dict) or set(cue) != {"ms", "text"}:
            raise ValueError("Each commentary line must contain ms and text")
        check_cue(cue["ms"], cue["text"], cues)
        cues.append(cue)
    return cues


def check_cue(ms: int, text: str, cues: list[dict]) -> None:
    if (
        type(ms) is not int
        or not 0 <= ms < MAX_DURATION * 1000
        or (cues and ms <= cues[-1]["ms"])
    ):
        raise ValueError("Commentary offsets must increase in milliseconds")
    if (
        not isinstance(text, str)
        or text != text.strip()
        or not text
        or len(text) > MAX_CAPTION
        or not text.isprintable()
        or any(char in text for char in "{<>}\\")
        or len(fill("[00:00:00] " + text, width=56).splitlines()) > 2
        or len(cues) >= MAX_CUES
    ):
        raise ValueError("Use short public-facing plain text with no markup")


def comment(path: Path, text: str, *, ms: int | None, started_at: str | None) -> dict:
    if started_at is not None:
        anchor = datetime.fromisoformat(started_at)
        if anchor.tzinfo is None:
            raise ValueError("Use the recording's UTC started_at value")
        ms = round((datetime.now(timezone.utc) - anchor).total_seconds() * 1000)
    if ms is None:
        raise ValueError("Supply --at-ms or --started-at")
    cues = read_cues(path) if path.exists() else []
    check_cue(ms, text, cues)
    cue = {"ms": ms, "text": text}
    flags = os.O_WRONLY | os.O_APPEND | os.O_CREAT
    descriptor = os.open(path, flags | getattr(os, "O_NOFOLLOW", 0), 0o600)
    with os.fdopen(descriptor, "a", encoding="utf-8") as file:
        metadata = os.fstat(file.fileno())
        if not stat.S_ISREG(metadata.st_mode) or (
            os.name != "nt" and metadata.st_mode & 0o077
        ):
            raise ValueError("Choose a private local commentary file")
        file.write(json.dumps(cue, ensure_ascii=False) + "\n")
    return cue


def srt_time(ms: int) -> str:
    seconds, millis = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"


def compose(manifest: Path, destination: Path, *, captions: bool) -> dict:
    with manifest.open("rb") as file:
        raw = file.read(64 * 1024 + 1)
    if len(raw) > 64 * 1024:
        raise ValueError("Composition manifest exceeds its size limit")
    segments = json.loads(raw)["segments"]
    if not isinstance(segments, list) or not 1 <= len(segments) <= MAX_SEGMENTS:
        raise ValueError("Supply an ordered list of up to 12 original recordings")
    if destination.suffix.lower() != ".mp4":
        raise ValueError("Choose a private MP4 destination")

    dimensions = set()
    filters, subtitles, inputs, label = [], [], [], []
    elapsed = 0
    offset_map = []
    frame_rate = 2
    for index, segment in enumerate(segments):
        video = manifest.parent / segment["video"]
        original = verify(video)
        if original["fps"] not in {"2/1", "5/1"}:
            raise ValueError("Use original 2 or 5 FPS managed recordings")
        frame_rate = max(frame_rate, int(original["fps"][0]))
        dimensions.add((original["width"], original["height"]))
        duration = round(original["duration"] * 1000)
        if elapsed + duration > MAX_DURATION * 1000:
            raise ValueError("Composition exceeds the two-hour limit")
        offset_map.append(
            {
                "original": str(video.resolve()),
                "output_ms": elapsed,
                "duration_ms": duration,
            }
        )
        if captions and segment.get("comments"):
            cues = read_cues(manifest.parent / segment["comments"])
            for n, cue in enumerate(cues):
                end = cues[n + 1]["ms"] if n + 1 < len(cues) else duration
                if not cue["ms"] < end <= duration:
                    raise ValueError(
                        "Commentary offset is outside its original recording"
                    )
                stamp = srt_time(cue["ms"]).split(",")[0]
                caption = fill(f"[{stamp}] {cue['text']}", width=56)
                subtitles.append(
                    f"{len(subtitles) + 1}\n{srt_time(elapsed + cue['ms'])} --> "
                    f"{srt_time(elapsed + end)}\n{caption}\n"
                )
        elapsed += duration
        inputs += ["-protocol_whitelist", "file", "-i", str(video.resolve())]
        filters.append(f"[{index}:v]setpts=PTS-STARTPTS[v{index}]")
        label.append(f"[v{index}]")
    if len(dimensions) != 1:
        raise ValueError("All recording segments must have the same native dimensions")
    filters.append(f"{''.join(label)}concat=n={len(segments)}:v=1:a=0,fps={frame_rate}")
    if captions and not subtitles:
        raise ValueError(
            "Supply the explicitly authored commentary sidecar for a captioned video"
        )
    with TemporaryDirectory() as work:
        if captions:
            Path(work, "comments.srt").write_text(
                "\n".join(subtitles), encoding="utf-8"
            )
            filters[-1] += (
                f",pad=iw:ih+{CAPTION_BAND}:0:0:color=0x121212,"
                "subtitles=comments.srt:force_style='"
                "FontName=DejaVu Sans,FontSize=16,MarginV=10,Outline=1,Shadow=0'"
            )
        with private_output(destination) as (file, temporary):
            file.close()
            subprocess.run(
                [
                    "ffmpeg",
                    "-nostdin",
                    "-loglevel",
                    "error",
                    "-y",
                    *inputs,
                    "-filter_complex_threads",
                    "1",
                    "-filter_complex",
                    ";".join(filters),
                    "-an",
                    "-map_metadata",
                    "-1",
                    "-c:v",
                    "libx264",
                    "-threads",
                    "2",
                    "-preset",
                    "veryfast",
                    "-pix_fmt",
                    "yuv420p",
                    "-movflags",
                    "+faststart",
                    "-fs",
                    str(512 * 1024**2),
                    "-f",
                    "mp4",
                    str(temporary.resolve()),
                ],
                cwd=work,
                check=True,
                timeout=1200,
            )
            metadata = verify(temporary)
            if not math.isclose(
                metadata["duration"], elapsed / 1000, abs_tol=1 / frame_rate
            ):
                raise ValueError(
                    "Derived duration differs from the original segment timeline"
                )
    return {"path": str(destination.resolve()), "timeline": offset_map, **metadata}
