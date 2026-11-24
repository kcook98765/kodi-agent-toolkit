"""Offline synthetic screenshot imports; no Kodi, credentials or network."""
import base64
import binascii
import hashlib
from io import BytesIO
import json
import os
from pathlib import Path
import subprocess
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from PIL import Image

from kodi_agent_toolkit import screenshots as shot

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = b'''<?xml version="1.0" encoding="UTF-8"?>
<!-- preserve this comment -->
<addon id="script.toolkit.sample" name="Sample" version="1.0.0" provider-name="Toolkit">
  <extension point="xbmc.python.script" library="default.py"/>
  <extension point='xbmc.addon.metadata'>
    <summary lang="en_GB">A &amp; B</summary>
    <description lang="en_GB">Keep this metadata.</description>
    <platform>all</platform><license>MIT</license>
    <assets>
      <icon>resources/icon.png</icon>
      <fanart>resources/fanart.jpg</fanart>
    </assets>
    <news>Keep news</news>
  </extension>
</addon>
'''
DESTINATION = "resources/screenshots/screenshot-01.png"


def image_bytes(image_format="PNG", mode="RGB", size=(1280, 720), **save_options):
    output = BytesIO()
    Image.new(mode, size).save(output, format=image_format, **save_options)
    return output.getvalue()


def session_export(data, tool="kodi_lab_screenshot_capture"):
    return {"info": {"id": "ses_fixture"}, "messages": [{"info": {"role": "assistant"}, "parts": [{
        "type": "tool", "tool": tool, "callID": "call_fixture",
        "state": {"status": "completed", "attachments": [{
            "type": "file", "mime": "image/png",
            "url": "data:image/png;base64," + base64.b64encode(data).decode("ascii")}]}}]}]}


@unittest.skipUnless(os.name == "posix", "Export writes require Linux/WSL no-follow operations")
class ScreenshotExportTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="toolkit screenshot ")
        self.addCleanup(temporary.cleanup)
        self.work = Path(temporary.name)
        self.addon = self.work / "script.toolkit.sample"
        self.addon.mkdir()
        self.manifest = self.addon / "addon.xml"
        self.manifest.write_bytes(MANIFEST)
        self.input = self.work / "input.png"
        self.input.write_bytes(image_bytes())

    def export(self, destination=DESTINATION, **kwargs):
        return shot.export_screenshot(self.addon, destination, source=self.input, **kwargs)

    def inventory(self):
        return {str(p.relative_to(self.addon)): p.read_bytes() if p.is_file() else None
                for p in self.addon.rglob("*")}

    def reject_unchanged(self, operation, message=None):
        before = self.inventory()
        with self.assertRaisesRegex(shot.ScreenshotError, message or "."):
            operation()
        self.assertEqual(before, self.inventory())

    def test_png_export_only_and_exact_file_metadata(self):
        result = self.export()
        saved = (self.addon / DESTINATION).read_bytes()
        self.assertEqual(saved, self.input.read_bytes())
        self.assertEqual(self.manifest.read_bytes(), MANIFEST)
        for key, value in {"passed": True, "format": "PNG", "width": 1280, "height": 720,
                           "bytes": len(saved), "sha256": hashlib.sha256(saved).hexdigest(),
                           "manifest_changed": False, "path": DESTINATION,
                           "capture_verified": False, "package_validated": False}.items():
            self.assertEqual(result[key], value)
        self.assertEqual(result["manifest_entry"], f"<screenshot>{DESTINATION}</screenshot>")

    def test_jpeg_full_hd_import_preserves_quality(self):
        self.input.write_bytes(image_bytes("JPEG", size=(1920, 1080)))
        result = self.export("resources/screenshots/screen.JPG", update_manifest=True)
        self.assertEqual(result["format"], "JPEG")
        self.assertEqual(result["width"], 1920)
        self.assertEqual((self.addon / result["path"]).read_bytes(), self.input.read_bytes())
        self.assertTrue(result["manifest_changed"])

    def test_real_bytes_required_and_truncated_pixels_rejected(self):
        for data in (b"", b"not a PNG", b"\x89PNG\r\n\x1a\n", image_bytes()[:200],
                     image_bytes("JPEG")[:-100], image_bytes("GIF")):
            with self.subTest(size=len(data)):
                self.input.write_bytes(data)
                self.reject_unchanged(lambda: self.export(update_manifest=True))

    def test_png_crc_corruption_rejected(self):
        data = bytearray(image_bytes())
        data[-5] ^= 1
        self.input.write_bytes(data)
        self.reject_unchanged(self.export)

    def test_dimensions_and_size_fail_before_writes(self):
        self.input.write_bytes(image_bytes(size=(1366, 768)))
        self.reject_unchanged(self.export, "1280x720")
        self.input.write_bytes(image_bytes() + b"x" * shot.MAX_IMAGE_BYTES)
        self.reject_unchanged(self.export, "750,000")

    def test_size_boundary(self):
        data = image_bytes()
        # Trailing bytes do not alter this valid PNG's pixels; size is conservative.
        self.input.write_bytes(data + b"\0" * (shot.MAX_IMAGE_BYTES - len(data)))
        self.assertEqual(self.export()["bytes"], shot.MAX_IMAGE_BYTES)

    def test_alpha_and_palette_transparency_rejected(self):
        for mode, options in (("RGBA", {}), ("LA", {}), ("P", {"transparency": 0})):
            with self.subTest(mode=mode):
                self.input.write_bytes(image_bytes(mode=mode, **options))
                self.reject_unchanged(self.export, "transparency")

    def test_transparency_in_trailing_png_chunk_rejected_after_decode(self):
        data = image_bytes()
        payload = struct.pack(">HHH", 0, 0, 0)
        chunk_type = b"tRNS"
        chunk = (struct.pack(">I", len(payload)) + chunk_type + payload
                 + struct.pack(">I", binascii.crc32(chunk_type + payload)))
        self.input.write_bytes(data[:-12] + chunk + data[-12:])
        self.reject_unchanged(lambda: self.export(update_manifest=True), "transparency")

    def test_opaque_palette_and_grayscale(self):
        for index, mode in enumerate(("P", "L")):
            self.input.write_bytes(image_bytes(mode=mode))
            self.assertTrue(self.export(f"screen-{index}.png")["passed"])

    def test_opaque_16bit_png_and_cmyk_jpeg(self):
        for image_format, mode, path in (("PNG", "I;16", "gray.png"), ("JPEG", "CMYK", "color.jpg")):
            self.input.write_bytes(image_bytes(image_format, mode=mode))
            self.assertTrue(self.export(path)["passed"])

    def test_animated_png_rejected(self):
        output = BytesIO()
        Image.new("RGB", (1280, 720)).save(output, format="PNG", save_all=True,
            append_images=[Image.new("RGB", (1280, 720), "white")], duration=100)
        self.input.write_bytes(output.getvalue())
        self.reject_unchanged(self.export, "single-frame")

    def test_destination_suffix_matches_content(self):
        self.reject_unchanged(lambda: self.export("screen.jpg"), "extension")

    def test_unsafe_destinations(self):
        for path in ("../screen.png", "/tmp/screen.png", "resources/../../screen.png",
                     "resources//screen.png", "resources/./screen.png", "", "C:/screen.png",
                     "resources\\screen.png", ".git/screen.png", "screen&evil.png",
                     'screen<evil.png', "screen\n.png", "CON.png", "dir./screen.png"):
            with self.subTest(path=path):
                self.reject_unchanged(lambda: self.export(path))

    def test_symlink_root_parent_input_and_manifest_rejected(self):
        link = self.work / "root-link"
        link.symlink_to(self.addon, target_is_directory=True)
        self.reject_unchanged(lambda: shot.export_screenshot(link, DESTINATION, source=self.input))
        source = self.work / "linked.png"
        source.symlink_to(self.input)
        self.reject_unchanged(lambda: shot.export_screenshot(self.addon, DESTINATION, source=source))
        self.manifest.unlink()
        actual = self.work / "original.xml"
        actual.write_bytes(MANIFEST)
        self.manifest.symlink_to(actual)
        self.reject_unchanged(self.export)
        self.assertEqual(actual.read_bytes(), MANIFEST)

    def test_symlink_escape_and_dangling_collision(self):
        outside = self.work / "outside"
        outside.mkdir()
        (self.addon / "resources").symlink_to(outside, target_is_directory=True)
        self.reject_unchanged(self.export)
        self.assertEqual(list(outside.iterdir()), [])
        (self.addon / "resources").unlink()
        (self.addon / "screen.png").symlink_to(outside / "missing")
        self.reject_unchanged(lambda: self.export("screen.png"), "already exists")

    def test_collision_never_overwrites(self):
        self.export()
        self.reject_unchanged(lambda: self.export(update_manifest=True), "already exists")

    def test_special_file_input_rejected_without_blocking(self):
        self.input.unlink()
        os.mkfifo(self.input)
        self.reject_unchanged(self.export, "regular files")

    def test_manifest_update_preserves_every_unrelated_byte_and_mode(self):
        self.manifest.chmod(0o640)
        self.export(update_manifest=True)
        inserted = f"      <screenshot>{DESTINATION}</screenshot>\n".encode()
        self.assertEqual(self.manifest.read_bytes().replace(inserted, b""), MANIFEST)
        self.assertEqual(self.manifest.stat().st_mode & 0o777, 0o640)
        root = ET.parse(self.manifest).getroot()
        self.assertEqual(root.findtext("extension/assets/screenshot"), DESTINATION)
        self.assertEqual(root.findtext("extension/assets/icon"), "resources/icon.png")
        self.assertEqual(root.findtext("extension/assets/fanart"), "resources/fanart.jpg")

    def test_existing_screenshots_and_crlf_preserved(self):
        raw = MANIFEST.replace(b"    </assets>", b"      <screenshot>old.png</screenshot>\n    </assets>").replace(b"\n", b"\r\n")
        self.manifest.write_bytes(raw)
        self.export(update_manifest=True)
        inserted = f"      <screenshot>{DESTINATION}</screenshot>\r\n".encode()
        self.assertEqual(self.manifest.read_bytes().replace(inserted, b""), raw)

    def test_existing_declaration_not_duplicated(self):
        self.manifest.write_bytes(MANIFEST.replace(b"    </assets>", f"      <screenshot>{DESTINATION}</screenshot>\n    </assets>".encode()))
        before = self.manifest.read_bytes()
        result = self.export(update_manifest=True)
        self.assertFalse(result["manifest_changed"])
        self.assertEqual(self.manifest.read_bytes(), before)
        self.assertTrue((self.addon / DESTINATION).is_file())

    def test_ten_limit_duplicate_metadata_and_unsafe_existing_paths(self):
        ten = b"".join(f"<screenshot>screen-{i}.png</screenshot>".encode() for i in range(10))
        raw = MANIFEST.replace(b"    </assets>", ten + b"    </assets>")
        self.manifest.write_bytes(raw)
        self.reject_unchanged(lambda: self.export(update_manifest=True), "Ten screenshots")
        # Export-only does not add a declaration and remains useful at the limit.
        self.assertTrue(self.export()["passed"])
        for invalid in (ten + b"<screenshot>eleven.png</screenshot>",
                        b"<screenshot>same.png</screenshot>" * 2,
                        b"<screenshot>../outside.png</screenshot>",
                        b"<screenshot><injected/></screenshot>"):
            self.manifest.write_bytes(MANIFEST.replace(b"    </assets>", invalid + b"    </assets>"))
            self.reject_unchanged(lambda: self.export("another.png", update_manifest=True))

    def test_missing_inline_and_self_closing_assets(self):
        for index, assets in enumerate((b"", b"<assets/>", b"<assets />", b"<assets><icon /></assets>",
                                        b'<assets test="a>b"/>')):
            raw = MANIFEST[:MANIFEST.index(b"    <assets>")] + b"    " + assets + b"\n  </extension>\n</addon>\n"
            self.manifest.write_bytes(raw)
            self.export(f"screen-{index}.png", update_manifest=True)
            self.assertEqual(ET.parse(self.manifest).findtext("extension/assets/screenshot"), f"screen-{index}.png")
        self.manifest.write_bytes(b'<addon id="a" name="n" version="1" provider-name="p"><extension point="xbmc.addon.metadata"/></addon>')
        self.export("selfclosing.png", update_manifest=True)
        self.assertEqual(ET.parse(self.manifest).findtext("extension/assets/screenshot"), "selfclosing.png")

    def test_invalid_or_ambiguous_manifest(self):
        for data in (b"not XML", MANIFEST[:-20], b"<!DOCTYPE addon><addon/>",
                     MANIFEST.replace(b'name="Sample"', b""),
                     MANIFEST.replace(b"    </assets>", b"    </assets><assets/>"),
                     MANIFEST.replace(b"</addon>", b'<extension point="xbmc.addon.metadata"/></addon>'),
                     MANIFEST.replace(b"xbmc.addon.metadata", b"wrong.metadata"),
                     MANIFEST.replace(b'encoding="UTF-8"', b'encoding="ISO-8859-1"'),
                     MANIFEST.replace(b'id="script.toolkit.sample"', b'id="../unsafe"')):
            with self.subTest(data=data[:50]):
                self.manifest.write_bytes(data)
                self.reject_unchanged(lambda: self.export(update_manifest=True))

    def test_utf16_entities_and_non_utf8_declarations_rejected_before_parse(self):
        xml = ('<?xml version="1.0" encoding="UTF-16LE"?>'
               '<!DOCTYPE addon [<!ENTITY title "Injected">]>'
               '<addon id="a" name="&title;" version="1" provider-name="p">'
               '<extension point="xbmc.addon.metadata"><assets/></extension></addon>')
        for data in (xml.encode("utf-16-le"), xml.replace("UTF-16LE", "UTF-16BE").encode("utf-16-be"),
                     xml.encode("utf-16"), MANIFEST.replace(b'encoding="UTF-8"', b'encoding = "ISO-8859-1"')):
            for update in (False, True):
                with self.subTest(update=update, prefix=data[:20]):
                    self.manifest.write_bytes(data)
                    self.reject_unchanged(lambda: self.export(update_manifest=update))

    def test_failure_staging_image_and_manifest_leaves_no_partial_export(self):
        original = shot._stage
        for stage_number in (1, 2):
            calls = 0
            def failing_stage(*args):
                nonlocal calls
                calls += 1
                if calls == stage_number:
                    raise OSError(28, "Synthetic disk full")
                return original(*args)
            with patch.object(shot, "_stage", side_effect=failing_stage):
                self.reject_unchanged(lambda: self.export(update_manifest=True))

    def test_failure_fsync_link_and_manifest_replace_roll_back(self):
        for operation in ("fsync", "link", "replace"):
            with self.subTest(operation=operation), patch.object(shot.os, operation, side_effect=OSError(5, "Synthetic write failure")):
                self.reject_unchanged(lambda: self.export(update_manifest=True))

    def test_collision_at_publication_does_not_clobber(self):
        original = os.link
        def competing_link(*args, **kwargs):
            (self.addon / "screen.png").write_bytes(b"competing writer")
            return original(*args, **kwargs)
        with patch.object(shot.os, "link", side_effect=competing_link):
            with self.assertRaises(shot.ScreenshotError):
                self.export("screen.png", update_manifest=True)
        self.assertEqual((self.addon / "screen.png").read_bytes(), b"competing writer")
        self.assertEqual(self.manifest.read_bytes(), MANIFEST)
        self.assertEqual(len(list(self.addon.iterdir())), 2)

    def test_changed_manifest_is_not_replaced(self):
        original = shot._stage
        changed = MANIFEST.replace(b"Keep news", b"Another editor")
        def editing_stage(*args):
            name = original(*args)
            self.manifest.write_bytes(changed)
            return name
        with patch.object(shot, "_stage", side_effect=editing_stage):
            with self.assertRaisesRegex(shot.ScreenshotError, "changed during"):
                self.export(update_manifest=True)
        self.assertEqual(self.inventory(), {"addon.xml": changed})

    def test_opencode_export_selected_call_extracts_exact_bytes(self):
        exported = self.work / "session.json"
        exported.write_text(json.dumps(session_export(self.input.read_bytes())))
        result = shot.export_screenshot(self.addon, DESTINATION, opencode_export=exported,
            call_id="call_fixture", update_manifest=True)
        self.assertEqual(result["source"], "opencode_export")
        self.assertEqual((self.addon / DESTINATION).read_bytes(), self.input.read_bytes())

    def test_opencode_export_supports_managed_v2_capture(self):
        exported = self.work / "session.json"
        data = self.input.read_bytes()
        exported.write_text(json.dumps(session_export(data, "kodi_lab_dev_managed_screen")))
        shot.export_screenshot(self.addon, DESTINATION, opencode_export=exported,
                               call_id="call_fixture")
        self.assertEqual((self.addon / DESTINATION).read_bytes(), data)

    def test_opencode_export_rejects_missing_ambiguous_redacted_or_remote_bytes(self):
        exported = self.work / "session.json"
        base = session_export(self.input.read_bytes())
        cases = [b"not JSON", b"[]", json.dumps({"messages": []}).encode()]
        for key, value in (("tool", "kodi_lab_other"), ("callID", "wrong")):
            record = json.loads(json.dumps(base)); record["messages"][0]["parts"][0][key] = value
            cases.append(json.dumps(record).encode())
        for url in ("https://example.org/screen.png", "file:///tmp/screen.png", "[redacted:file-url:x]",
                    "data:image/png;base64,not-base64!", "data:image/png;base64," + "A" * 1_000_004):
            record = json.loads(json.dumps(base)); record["messages"][0]["parts"][0]["state"]["attachments"][0]["url"] = url
            cases.append(json.dumps(record).encode())
        for change in ("duplicate_call", "two_images", "missing_image", "running"):
            record = json.loads(json.dumps(base)); part = record["messages"][0]["parts"][0]
            if change == "duplicate_call": record["messages"][0]["parts"].append(part)
            elif change == "two_images": part["state"]["attachments"] *= 2
            elif change == "missing_image": part["state"]["attachments"] = []
            else: part["state"]["status"] = "running"
            cases.append(json.dumps(record).encode())
        for data in cases:
            with self.subTest(size=len(data)):
                exported.write_bytes(data)
                self.reject_unchanged(lambda: shot.export_screenshot(self.addon, DESTINATION,
                    opencode_export=exported, call_id="call_fixture", update_manifest=True))

    def test_source_selection_requires_explicit_inputs(self):
        for kwargs in ({}, {"source": self.input, "call_id": "x"},
                       {"source": self.input, "opencode_export": self.input},
                       {"opencode_export": self.input}):
            self.reject_unchanged(lambda: shot.export_screenshot(self.addon, DESTINATION, **kwargs))

    def test_cli_success_and_failure_contain_no_absolute_host_paths(self):
        command = [sys.executable, "-m", "kodi_agent_toolkit.cli", "screenshot-export",
                   str(self.addon), DESTINATION, "--input", str(self.input), "--update-manifest"]
        result = subprocess.run(command, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["manifest_changed"])
        self.assertNotIn(str(self.work), result.stdout)
        result = subprocess.run(command, text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn(str(self.work), result.stderr)


class UnsupportedPlatformTests(unittest.TestCase):
    def test_missing_no_follow_support_fails_closed(self):
        with patch.object(shot.os, "name", "nt"):
            with self.assertRaisesRegex(shot.ScreenshotError, "Linux/WSL"):
                shot._supported()


if __name__ == "__main__":
    unittest.main()
