"""Discovery regressions in isolated temporary projects, without Kodi."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from kodi_agent_toolkit.paths import discover
from kodi_agent_toolkit.checker_runner import SourceViolation


class PathTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="kodi path test ")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        (self.root / ".git").mkdir()
        self.addon = self.root / "addons with spaces" / "script.example"
        self.addon.mkdir(parents=True)
        (self.addon / "source with spaces.py").write_text("raise RuntimeError('never import')\n")
        (self.addon / "addon.xml").write_text('<addon id="script.example"><requires><import addon="xbmc.python" version="3.0.1"/></requires><extension point="xbmc.python.script" library="source with spaces.py"/></addon>')

    def test_enumerates_actual_entry_point_and_spaces(self):
        report = discover(self.root)
        self.assertTrue(report["passed"])
        record = report["addons"][0]
        self.assertEqual(record["addon_dir"], "addons with spaces/script.example")
        self.assertEqual(record["files"], ["addon.xml", "source with spaces.py"])
        self.assertTrue(record["entry_points"][0]["exists"])
        self.assertNotIn("main.py", record["files"])

    def test_nested_working_directory_finds_workspace(self):
        nested = self.addon / "resources"
        nested.mkdir()
        report = discover(self.addon)
        self.assertEqual(report["project_root"], str(self.root))
        # CLI uses the explicitly supplied path even from an unrelated cwd.
        result = subprocess.run([sys.executable, "-m", "kodi_agent_toolkit.cli", "discover", str(self.root)], cwd=nested, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["project_root"], str(self.root))

    def test_nonexistent_root_and_file_are_rejected(self):
        for path in (self.root / "missing", self.addon / "addon.xml"):
            with self.subTest(path=path), self.assertRaises((SourceViolation, OSError)):
                discover(path)

    def test_empty_wrong_root_reports_no_artifact(self):
        empty = self.root / "wrong root"
        empty.mkdir()
        report = discover(empty)
        self.assertFalse(report["passed"])
        self.assertEqual(report["addons"], [])
        self.assertTrue(report["errors"])

    def test_missing_entry_is_marked_unverified_and_unsafe_reference_is_false(self):
        for path in ("invented.py", "../outside.py", "C:/outside.py"):
            with self.subTest(path=path):
                (self.addon / "addon.xml").write_text(f'<addon><extension library="{path}"/></addon>')
                entry = discover(self.root)["addons"][0]["entry_points"][0]
                self.assertFalse(entry["exists"])

    def test_xml_parse_error_does_not_guess_entry_points(self):
        (self.addon / "addon.xml").write_text('<addon><extension library="invented.py"></addon>')
        record = discover(self.root)["addons"][0]
        self.assertTrue(record["manifest_error"])
        self.assertEqual(record["entry_points"], [])

    def test_symlink_and_venv_do_not_become_addons(self):
        excluded = self.root / ".venv"
        excluded.mkdir()
        (excluded / "addon.xml").write_text("<addon/>")
        try:
            (self.root / "link").symlink_to(self.addon, target_is_directory=True)
        except OSError:
            self.skipTest("Links unavailable")
        report = discover(self.root)
        self.assertEqual(len(report["addons"]), 1)
        self.assertFalse(report["complete"])

    @unittest.skipIf(os.name == "nt", "POSIX boundary")
    def test_windows_path_is_not_guessed_in_wsl(self):
        with self.assertRaisesRegex(SourceViolation, "wslpath"):
            discover(Path("C:/unknown/addon"))

    def test_scan_budget_is_explicit(self):
        with patch("kodi_agent_toolkit.paths.MAX_ENTRIES", 1):
            report = discover(self.root)
        self.assertFalse(report["complete"])

    def test_global_skill_directory_is_not_project_root(self):
        home = self.root / "simulated home"
        (home / ".agents").mkdir(parents=True)
        addon = home / "standalone" / "script.example"
        addon.mkdir(parents=True)
        (addon / "addon.xml").write_text("<addon/>")
        # Remove repo marker so this models a standalone user project.
        (self.root / ".git").rmdir()
        self.assertEqual(discover(addon)["project_root"], str(addon))

    def test_default_nested_scan_stays_in_containing_addon(self):
        nested = self.addon / "nested"
        nested.mkdir()
        with patch("kodi_agent_toolkit.paths.safe_path", wraps=__import__("kodi_agent_toolkit.checker_runner", fromlist=["safe_path"]).safe_path):
            original = Path.cwd()
            try:
                os.chdir(nested)
                result = discover()
            finally:
                os.chdir(original)
        self.assertEqual(result["project_root"], str(self.root))
        self.assertEqual(result["scan_root"], str(self.addon))
        self.assertEqual(len(result["addons"]), 1)

    def test_dot_prefix_duplicate_separator_and_module_directory(self):
        module = self.addon / "lib"
        module.mkdir()
        (module / "entry.py").write_text("# no execution")
        for declared, expected in (("./source with spaces.py", "source with spaces.py"), ("lib//entry.py", "lib/entry.py"), ("./lib", "lib")):
            with self.subTest(path=declared):
                (self.addon / "addon.xml").write_text(f'<addon><extension library="{declared}"/></addon>')
                entry = discover(self.root)["addons"][0]["entry_points"][0]
                self.assertEqual(entry["path"], expected)
                self.assertTrue(entry["exists"])

    def test_default_manifest_search_does_not_escape_nearer_repository(self):
        # A repository nested beneath an unrelated ancestor manifest must not
        # scan outside its verified repository boundary.
        nested_repo = self.addon / "independent project"
        (nested_repo / ".git").mkdir(parents=True)
        original = Path.cwd()
        try:
            os.chdir(nested_repo)
            result = discover()
        finally:
            os.chdir(original)
        self.assertEqual(result["project_root"], str(nested_repo))
        self.assertEqual(result["scan_root"], str(nested_repo))
        self.assertFalse(result["passed"])
        self.assertEqual(result["addons"], [])
