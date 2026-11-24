"""Opt-in local screenshot assets. Never contacts Kodi, OpenCode or a URL.

Writes use POSIX directory descriptors. Ordinary failures roll back publication;
two files cannot form a crash-atomic transaction (see docs/screenshots.md).
"""
from __future__ import annotations

from contextlib import ExitStack
from dataclasses import dataclass, field
import base64
import binascii
import hashlib
from io import BytesIO
import json
import os
from pathlib import Path
import re
import secrets
import stat
import warnings
import xml.etree.ElementTree as ET
from xml.parsers import expat

MAX_IMAGE_BYTES = 750_000
MAX_EXPORT_BYTES = 32 * 1024 * 1024
MAX_MANIFEST_BYTES = 256 * 1024
DIR_FD_SUPPORTED = {os.open, os.mkdir, os.unlink, os.link, os.rename}.issubset(os.supports_dir_fd)


class ScreenshotError(ValueError):
    """An actionable local export rejection; contains no source image data."""


def _relative(value: str) -> list[str]:
    parts = value.split("/")
    if (len(value) > 1024 or any(
            not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", part)
            or part.endswith(".") or part in {".", ".."}
            or part.split(".")[0].upper() in {
                "CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(10)),
                *(f"LPT{i}" for i in range(10))} for part in parts)):
        raise ScreenshotError("Use a relative asset path with simple names and / separators; no traversal or XML characters")
    return parts


def _supported() -> None:
    if (os.name != "posix" or not hasattr(os, "O_NOFOLLOW")
            or not DIR_FD_SUPPORTED):
        raise ScreenshotError("Screenshot export requires Linux/WSL POSIX no-follow filesystem operations")


def _directory(stack: ExitStack, parent: int, name: str) -> int:
    descriptor = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
    stack.callback(os.close, descriptor)
    return descriptor


def _absolute_directory(stack: ExitStack, path: Path) -> int:
    if ".." in path.parts:
        raise ScreenshotError("Parent traversal is not allowed in local paths")
    absolute = path.absolute()
    descriptor = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
    stack.callback(os.close, descriptor)
    for component in absolute.parts[1:]:
        descriptor = _directory(stack, descriptor, component)
    return descriptor


def _read_at(parent: int, name: str, limit: int) -> tuple[bytes, os.stat_result]:
    descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
    with os.fdopen(descriptor, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode):
            raise ScreenshotError("Input and addon.xml must be regular files")
        if info.st_size > limit:
            raise ScreenshotError(f"Input exceeds {limit:,} bytes; screenshots must be at most 750,000 bytes")
        data = stream.read(limit + 1)
        if len(data) > limit:
            raise ScreenshotError("Input grew beyond its size limit")
        return data, info


def _read(path: Path, limit: int) -> bytes:
    with ExitStack() as stack:
        parent = _absolute_directory(stack, path.parent)
        return _read_at(parent, path.name, limit)[0]


def _opencode_image(path: Path, call_id: str) -> bytes:
    try:
        exported = json.loads(_read(path, MAX_EXPORT_BYTES))
        calls = [part for message in exported["messages"] for part in message["parts"]
                 if part.get("type") == "tool" and part.get("callID") == call_id]
        if len(calls) != 1:
            raise ScreenshotError("Select exactly one screenshot tool call with --call-id")
        call = calls[0]
        if (not call["tool"].endswith(("_screenshot_capture", "_managed_screen"))
                or call["state"]["status"] != "completed"):
            raise ScreenshotError("Selected call must be a completed MCP screenshot_capture or managed_screen")
        attachments = call["state"].get("attachments", [])
        if len(attachments) != 1:
            raise ScreenshotError("Selected call needs exactly one image attachment; use a local PNG instead")
        attachment = attachments[0]
        prefix = "data:image/png;base64,"
        url = attachment["url"]
        if attachment["type"] != "file" or attachment["mime"] != "image/png" or not url.startswith(prefix):
            raise ScreenshotError("Missing PNG bytes; use an unsanitized private OpenCode export or browser-saved PNG")
        encoded = url[len(prefix):]
        if len(encoded) > 4 * ((MAX_IMAGE_BYTES + 2) // 3):
            raise ScreenshotError("Screenshot exceeds 750,000 bytes; save and optimize it locally first")
        return base64.b64decode(encoded, validate=True)
    except (KeyError, TypeError, AttributeError, UnicodeError, json.JSONDecodeError, binascii.Error, RecursionError) as exc:
        raise ScreenshotError("Invalid OpenCode export or PNG attachment; use a local PNG file") from exc


def _image(data: bytes, destination: str) -> dict[str, object]:
    try:
        from PIL import Image
    except ImportError as exc:
        raise ScreenshotError("Pillow is required; use the documented hash-locked Toolkit environment") from exc
    if len(data) > MAX_IMAGE_BYTES:
        raise ScreenshotError("Screenshot exceeds 750,000 bytes; optimize locally and retry")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(data), formats=["PNG", "JPEG"]) as image:
                image_format, size = image.format, image.size
                if size not in {(1280, 720), (1920, 1080)}:
                    raise ScreenshotError("Use a 1280x720 or 1920x1080 screenshot; resize locally and retry")
                if "A" in image.getbands() or "transparency" in image.info:
                    raise ScreenshotError("Screenshot must have no transparency; flatten to opaque RGB and retry")
                if getattr(image, "n_frames", 1) != 1:
                    raise ScreenshotError("Use a single-frame PNG or JPEG")
                image.verify()
            with Image.open(BytesIO(data), formats=["PNG", "JPEG"]) as image:
                image.load()  # verify() alone does not decode all pixel data.
                # PNG metadata can arrive in trailing chunks during load_end.
                if "A" in image.getbands() or "transparency" in image.info:
                    raise ScreenshotError("Screenshot must have no transparency; flatten to opaque RGB and retry")
    except ScreenshotError:
        raise
    except (OSError, ValueError, SyntaxError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise ScreenshotError("Invalid or truncated PNG/JPEG; save a complete image and retry") from exc
    suffixes = {"PNG": {".png"}, "JPEG": {".jpg", ".jpeg"}}
    if image_format not in suffixes or Path(destination).suffix.lower() not in suffixes[image_format]:
        raise ScreenshotError("Destination extension must match the actual PNG/JPEG format")
    return {"format": image_format, "width": size[0], "height": size[1],
            "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


@dataclass
class _Element:
    name: str
    attributes: dict[str, str]
    start: int
    close: int = 0
    self_closing: bool = False
    children: list[_Element] = field(default_factory=list)


def _elements(raw: bytes) -> _Element:
    """Parser byte offsets allow one insertion without reserializing metadata."""
    parser = expat.ParserCreate()
    stack: list[_Element] = []
    roots: list[_Element] = []

    def start(name: str, attributes: dict[str, str]) -> None:
        element = _Element(name, attributes, parser.CurrentByteIndex)
        opening = re.match(br'''<(?:[^<>"']|"[^"]*"|'[^']*')*>''', raw[element.start:])
        element.self_closing = opening is not None and opening[0].endswith(b"/>")
        (stack[-1].children if stack else roots).append(element)
        stack.append(element)

    def end(name: str) -> None:
        element = stack.pop()
        element.close = parser.CurrentByteIndex

    parser.StartElementHandler, parser.EndElementHandler = start, end
    parser.Parse(raw, True)
    return roots[0]


def _append(raw: bytes, parent: _Element, child: bytes) -> bytes:
    # Self-closing elements have the end event immediately after their />.
    if parent.self_closing:
        return raw[:parent.close - 2] + b">" + child + b"</" + parent.name.encode() + b">" + raw[parent.close:]
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    line = raw.rfind(b"\n", 0, parent.close) + 1
    indent = raw[line:parent.close]
    if indent.strip():  # Existing inline XML stays inline.
        return raw[:parent.close] + child + raw[parent.close:]
    child_indent = indent + b"  "
    if parent.children:
        first = parent.children[0].start
        candidate = raw[raw.rfind(b"\n", 0, first) + 1:first]
        if not candidate.strip():
            child_indent = candidate
    return raw[:line] + child_indent + child + newline + raw[line:]


def _manifest(raw: bytes, destination: str, update: bool) -> tuple[bytes, bool]:
    try:
        text = raw.decode("utf-8-sig")
        if "\x00" in text:
            raise ScreenshotError("addon.xml must use UTF-8 without NUL bytes")
        declaration = re.match(r"<\?xml\s[^?]*encoding\s*=\s*['\"]([^'\"]+)", text)
        if declaration and declaration[1].lower() not in {"utf-8", "utf8", "us-ascii"}:
            raise ScreenshotError("addon.xml must use UTF-8 for screenshot export")
        if "<!DOCTYPE" in text.upper() or "<!ENTITY" in text.upper():
            raise ScreenshotError("DOCTYPE/entity declarations are not accepted")
        root = ET.fromstring(raw)
        if root.tag != "addon" or any(not root.get(key, "").strip() for key in ("id", "name", "version", "provider-name")):
            raise ScreenshotError("addon.xml needs an addon root and id, name, version and provider-name")
        if not re.fullmatch(r"[A-Za-z0-9_]+(?:[.-][A-Za-z0-9_]+)*", root.get("id", "")):
            raise ScreenshotError("Invalid add-on ID in addon.xml")
        metadata = root.findall("extension[@point='xbmc.addon.metadata']")
        if len(metadata) != 1 or len(metadata[0].findall("assets")) > 1:
            raise ScreenshotError("addon.xml needs one xbmc.addon.metadata extension and at most one assets element")
        screenshots = metadata[0].findall("assets/screenshot")
        paths = []
        for item in screenshots:
            if list(item) or item.attrib:
                raise ScreenshotError("Existing screenshot declarations must be plain relative paths")
            value = (item.text or "").strip()
            _relative(value)
            paths.append(value)
        if len(paths) > 10 or len(paths) != len(set(paths)):
            raise ScreenshotError("addon.xml must have at most ten screenshots with no duplicate declarations")
        if not update or destination in paths:
            return raw, False
        if len(paths) == 10:
            raise ScreenshotError("Ten screenshots are already declared; remove a declaration before adding another")
        tree = _elements(raw)
        extension = next(item for item in tree.children if item.name == "extension" and item.attributes.get("point") == "xbmc.addon.metadata")
        assets = next((item for item in extension.children if item.name == "assets"), None)
        child = b"<screenshot>" + destination.encode("ascii") + b"</screenshot>"
        changed = _append(raw, assets, child) if assets else _append(raw, extension, b"<assets>" + child + b"</assets>")
        ET.fromstring(changed)
        return changed, True
    except (UnicodeError, ET.ParseError, expat.ExpatError, RecursionError) as exc:
        raise ScreenshotError("Invalid addon.xml; repair the existing manifest before exporting") from exc


def _stage(parent: int, data: bytes, mode: int) -> str:
    name = ".toolkit-screenshot-" + secrets.token_hex(16)
    descriptor = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fchmod(stream.fileno(), mode)
            os.fsync(stream.fileno())
    except BaseException:
        os.unlink(name, dir_fd=parent)
        raise
    return name


def export_screenshot(addon: Path, destination: str, *, source: Path | None = None,
                      opencode_export: Path | None = None, call_id: str | None = None,
                      update_manifest: bool = False) -> dict[str, object]:
    """Publish an image without clobbering, optionally declare it in addon.xml."""
    _supported()
    parts = _relative(destination)
    if (source is None) == (opencode_export is None) or (opencode_export is not None) != bool(call_id):
        raise ScreenshotError("Select --input FILE or --opencode-export JSON with --call-id ID")
    try:
        if source is not None:
            data = _read(source, MAX_IMAGE_BYTES)
        else:
            assert opencode_export is not None and call_id is not None
            data = _opencode_image(opencode_export, call_id)
        image = _image(data, destination)
        with ExitStack() as stack:
            root = _absolute_directory(stack, addon)
            manifest, manifest_info = _read_at(root, "addon.xml", MAX_MANIFEST_BYTES)
            updated, changed = _manifest(manifest, destination, update_manifest)
            created: list[tuple[int, str]] = []
            staged: list[tuple[int, str]] = []
            published = False
            parent = root
            try:
                for part in parts[:-1]:
                    try:
                        os.mkdir(part, dir_fd=parent)
                        created.append((parent, part))
                    except FileExistsError:
                        pass
                    parent = _directory(stack, parent, part)
                # lstat catches files, directories and dangling symlinks alike.
                try:
                    os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
                except FileNotFoundError:
                    pass
                else:
                    raise ScreenshotError("Destination already exists; select a new filename (no overwrite)")
                image_temp = _stage(parent, data, 0o644)
                staged.append((parent, image_temp))
                manifest_temp = None
                if changed:
                    manifest_temp = _stage(root, updated, stat.S_IMODE(manifest_info.st_mode))
                    staged.append((root, manifest_temp))
                # Catch manifest changes during preparation before any publication.
                current, info = _read_at(root, "addon.xml", MAX_MANIFEST_BYTES)
                if current != manifest or (info.st_dev, info.st_ino) != (manifest_info.st_dev, manifest_info.st_ino):
                    raise ScreenshotError("addon.xml changed during export; retry on a quiet checkout")
                os.link(image_temp, parts[-1], src_dir_fd=parent, dst_dir_fd=parent, follow_symlinks=False)
                published = True
                os.unlink(image_temp, dir_fd=parent)
                staged.remove((parent, image_temp))
                if manifest_temp is not None:
                    os.replace(manifest_temp, "addon.xml", src_dir_fd=root, dst_dir_fd=root)
                    staged.remove((root, manifest_temp))
            except BaseException:
                if published:
                    os.unlink(parts[-1], dir_fd=parent)
                for descriptor, name in reversed(staged):
                    os.unlink(name, dir_fd=descriptor)
                for descriptor, name in reversed(created):
                    os.rmdir(name, dir_fd=descriptor)
                raise
        return {"passed": True, "path": destination, **image,
                "manifest_changed": changed,
                "manifest_entry": f"<screenshot>{destination}</screenshot>",
                "source": "local_file" if source is not None else "opencode_export",
                "capture_verified": False, "package_validated": False}
    except OSError as exc:
        raise ScreenshotError(f"Local file operation failed ({exc.strerror}); check links, collisions and write permissions") from exc
