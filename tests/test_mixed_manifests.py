"""Structural mixed-manifest controls; no add-on import, Kodi or network calls."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from kodi_agent_toolkit.checker_runner import inspect_manifest_paths, SourceViolation
from kodi_agent_toolkit.paths import discover
from kodi_agent_toolkit.validate import validate


class MixedManifestTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="kodi-mixed-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / "script.mixed"
        self.root.mkdir()
        for filename in ("script.py", "plugin.py", "service.py"):
            (self.root / filename).write_text("raise AssertionError('never execute addon')\n")
        (self.root / "LICENSE.txt").write_text("MIT\n")

    def manifest(self, extensions):
        (self.root / "addon.xml").write_text(
            '<addon id="script.mixed" name="Inert mixed" version="1.0.0" provider-name="Toolkit">'
            '<requires><import addon="xbmc.python" version="3.0.0"/></requires>'
            + extensions + '</addon>')

    def checks(self):
        # The test targets structural validation, not unrelated type coverage.
        with patch("kodi_agent_toolkit.validate._types", return_value={"passed": True}):
            return validate(self.root, branch="matrix")["checks"]

    def test_supported_combinations_retain_all_library_entries_and_ignore_service_timing(self):
        entries = {
            "script": '<extension point="xbmc.python.script" library="script.py"/>',
            "plugin": '<extension point="xbmc.python.pluginsource" library="plugin.py"><provides>video</provides></extension>',
            "service": '<extension point="xbmc.service" library="service.py" start="login"/>',
        }
        for names in (("service",), ("script", "service"), ("plugin", "service"),
                      ("script", "plugin"), ("script", "plugin", "service"),
                      ("service", "script", "plugin")):
            with self.subTest(names=names):
                self.manifest("".join(entries[n] for n in names))
                checks = self.checks()
                for name in ("syntax", "manifest", "paths", "package"):
                    self.assertTrue(checks[name]["passed"], checks[name])
                inspect_manifest_paths(self.root)
                found = discover(self.root)["addons"][0]["entry_points"]
                self.assertEqual([x["path"] for x in found], [n + ".py" for n in names])
                self.assertTrue(all(x["exists"] for x in found))
                self.assertEqual([x["extension"] for x in found],
                                 ["xbmc.service" if n == "service" else "xbmc.python." +
                                  ("script" if n == "script" else "pluginsource") for n in names])

    def test_service_libraries_and_assets_still_require_safe_existing_paths(self):
        for attr in ("library", "asset"):
            for value in ("missing.py", "../outside.py", "/outside.py", "C:/outside.py"):
                with self.subTest(attr=attr, value=value):
                    library = value if attr == "library" else "service.py"
                    assets = ('<extension point="xbmc.addon.metadata"><assets><icon>' + value +
                              '</icon></assets></extension>') if attr == "asset" else ""
                    self.manifest('<extension point="xbmc.service" library="' + library +
                                  '" start="login"/>' + assets)
                    self.assertFalse(self.checks()["paths"]["passed"])
                    with self.assertRaises(SourceViolation):
                        inspect_manifest_paths(self.root)

    def test_nonservice_start_is_still_a_file_reference(self):
        for value, valid in (("script.py", True), ("missing.html", False), ("../outside", False)):
            with self.subTest(value=value):
                self.manifest('<extension point="xbmc.webinterface" start="' + value + '"/>')
                self.assertEqual(self.checks()["paths"]["passed"], valid)
                self.assertEqual(discover(self.root)["addons"][0]["entry_points"][0]["exists"], valid)
                if valid:
                    inspect_manifest_paths(self.root)
                else:
                    with self.assertRaises(SourceViolation):
                        inspect_manifest_paths(self.root)


if __name__ == "__main__":
    unittest.main()
