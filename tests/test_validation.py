"""Real installed mypy/checker tests using explicitly synthetic metadata snapshots.

Run: .venv/bin/python -B -m unittest discover -s tests -p test_validation.py -v
No network, add-on execution, repo config edits, or installed-package edits.
"""
from __future__ import annotations

import datetime as dt
import gzip
import hashlib
import importlib.metadata as metadata
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from kodi_agent_toolkit.checker_runner import (
    BRANCHES, SourceViolation, copy_source, inspect_source, run_checker, safe_path,
)
from kodi_agent_toolkit.validate import validate


def fixture_cache(path: Path) -> Path:
    path.mkdir()
    entries = {}
    for branch in BRANCHES:
        # Original test metadata, clearly labeled synthetic in replay evidence.
        raw = gzip.compress(b'<addons><addon id="script.module.unrelated" version="1.0.0">'
                            b'<requires><import addon="xbmc.python" version="3.0.0"/></requires>'
                            b'<extension point="xbmc.python.module" library="lib"/></addon></addons>',
                            mtime=0)
        filename = f"{branch}.xml.gz"
        (path / filename).write_bytes(raw)
        entries[branch] = {"url": f"https://mirrors.kodi.tv/addons/{branch}/addons.xml.gz",
                          "filename": filename, "size": len(raw),
                          "sha256": hashlib.sha256(raw).hexdigest()}
    (path / "manifest.json").write_text(json.dumps({
        "schema_version": 1, "fixture": True,
        "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(), "indexes": entries}))
    return path


class SourceSafetyTests(unittest.TestCase):
    """Mock Windows metadata in WSL; these tests do not qualify native Windows."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="kodi-source-safety-test-")
        self.addCleanup(self.temporary.cleanup)
        self.work = Path(self.temporary.name)
        self.addon = self.work / "script.toolkit.sample"
        self.addon.mkdir()
        (self.addon / "resources").mkdir()
        (self.addon / "default.py").write_text("pass\n")

    def reparse_lstat(self, target):
        original = Path.lstat

        def flagged(path, *args, **kwargs):
            info = original(path, *args, **kwargs)
            if path == target:
                return SimpleNamespace(st_mode=info.st_mode, st_size=info.st_size,
                                       st_file_attributes=0x400)
            return info

        return flagged

    def escaping_resolve(self, target):
        original = Path.resolve

        def escaped(path, *args, **kwargs):
            if path == target:
                return self.work / "outside" / target.name
            return original(path, *args, **kwargs)

        return escaped

    def test_safe_path_rejects_reparse_root_and_parent_without_junction_api(self):
        for target in (self.addon, self.work):
            with self.subTest(target=target), \
                    patch.object(Path, "is_junction", None, create=True), \
                    patch.object(Path, "lstat", self.reparse_lstat(target)):
                with self.assertRaisesRegex(SourceViolation, "Junction/reparse"):
                    safe_path(self.addon)

    def test_safe_path_rejects_root_and_parent_with_junction_api(self):
        for target in (self.addon, self.work):
            with self.subTest(target=target), \
                    patch.object(Path, "is_junction", lambda path: path == target, create=True):
                with self.assertRaisesRegex(SourceViolation, "Junction/reparse"):
                    safe_path(self.addon)

    def test_reparse_file_and_directory_are_rejected_before_copy(self):
        for target in (self.addon / "default.py", self.addon / "resources"):
            with self.subTest(target=target), \
                    patch.object(Path, "is_junction", None, create=True), \
                    patch.object(Path, "lstat", self.reparse_lstat(target)), \
                    patch("kodi_agent_toolkit.checker_runner.shutil.copytree") as copied:
                with self.assertRaisesRegex(SourceViolation, "Junction/reparse"):
                    copy_source(self.addon, self.work / "copy")
                copied.assert_not_called()

    def test_junction_directory_is_rejected_before_copy(self):
        target = self.addon / "resources"
        with patch.object(Path, "is_junction", lambda path: path == target, create=True), \
                patch("kodi_agent_toolkit.checker_runner.shutil.copytree") as copied:
            with self.assertRaisesRegex(SourceViolation, "Junction/reparse"):
                copy_source(self.addon, self.work / "copy")
            copied.assert_not_called()

    def test_resolved_file_and_directory_escapes_are_rejected_before_copy(self):
        for target in (self.addon / "default.py", self.addon / "resources"):
            with self.subTest(target=target), \
                    patch.object(Path, "resolve", self.escaping_resolve(target)), \
                    patch("kodi_agent_toolkit.checker_runner.shutil.copytree") as copied:
                with self.assertRaisesRegex(SourceViolation, "Source entry escapes add-on"):
                    copy_source(self.addon, self.work / "copy")
                copied.assert_not_called()

    def test_empty_walk_directory_must_still_resolve_inside_addon(self):
        target = self.addon / "resources"
        with patch.object(Path, "resolve", self.escaping_resolve(target)), \
                patch("kodi_agent_toolkit.checker_runner.os.walk",
                      return_value=iter([(str(target), [], [])])):
            with self.assertRaisesRegex(SourceViolation, "Source directory escapes add-on"):
                inspect_source(self.addon)

    def test_regular_tree_and_missing_safe_path_remain_supported(self):
        self.assertEqual(inspect_source(self.addon), [Path("default.py")])
        missing = self.work / "missing" / "addon"
        self.assertEqual(safe_path(missing), missing.absolute())
        with self.assertRaisesRegex(SourceViolation, "does not exist"):
            inspect_source(missing)


@unittest.skipUnless(all(metadata.version(name) for name in
                         ("Kodistubs", "kodi-addon-checker", "mypy")), "Installed tools required")
class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="kodi-validation-test-")
        self.addCleanup(self.temporary.cleanup)
        self.work = Path(self.temporary.name)
        self.cache = fixture_cache(self.work / "indexes")

    def addon(self, fixture="valid"):
        destination = self.work / "script.toolkit.sample"
        shutil.copytree(ROOT / "fixtures" / fixture / "script.toolkit.sample", destination)
        return destination

    def test_valid_with_original_url_warnings_and_counts(self):
        addon = self.addon()
        before = {str(p.relative_to(addon)): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in addon.rglob("*") if p.is_file()}
        result = validate(addon, cache=self.cache)
        self.assertTrue(result["passed"], result)
        self.assertEqual(result["returncode"], 0)
        official = result["checks"]["official_checker"]
        self.assertTrue(official["completed"])
        self.assertEqual(official["exit_code"], 0)
        self.assertEqual(official["error_count"], 0)
        self.assertGreaterEqual(official["warning_count"], 1)
        self.assertIn("online URL check unverified", official["stdout"])
        self.assertEqual(len(official["replay"]["requested_indexes"]), 10)
        self.assertTrue(official["replay"]["cache"]["fixture"])
        self.assertEqual(official["online_url_checks"], "unverified")
        self.assertEqual(official["warning_count"], len(official["warnings"]))
        self.assertEqual(before, {str(p.relative_to(addon)): hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in addon.rglob("*") if p.is_file()})

    def test_api_string_log_level_fails_mypy(self):
        result = validate(self.addon("invalid-api"), cache=self.cache)
        self.assertFalse(result["passed"])
        self.assertEqual(result["checks"]["types"]["status"], "failed")
        self.assertIn("arg-type", result["checks"]["types"]["output"])
        self.assertTrue(result["checks"]["official_checker"]["completed"])

    def test_malformed_xml_preserves_actual_checker_failure(self):
        result = validate(self.addon("invalid-xml"), cache=self.cache)
        self.assertFalse(result["passed"])
        self.assertEqual(result["checks"]["manifest"]["status"], "failed")
        official = result["checks"]["official_checker"]
        self.assertIn("Invalid XML data in addon.xml", official["stdout"])
        self.assertIn("UnboundLocalError", official["stderr"])
        self.assertEqual(official["exit_code"], 1)
        self.assertFalse(official["completed"])

    def test_no_runtime_import_or_mypy_plugin_loading(self):
        addon = self.addon()
        with (addon / "default.py").open("a") as stream:
            stream.write('\nraise RuntimeError("THIS ADDON MUST NEVER BE IMPORTED")\n')
        (addon / "mypy.ini").write_text("[mypy]\nplugins = nonexistent_dangerous_plugin\n")
        result = validate(addon, cache=self.cache)
        self.assertEqual(result["checks"]["types"]["status"], "passed", result)
        self.assertNotIn("THIS ADDON MUST NEVER BE IMPORTED", result["checks"]["official_checker"]["stderr"])

    def test_syntax_failure_is_distinct(self):
        addon = self.addon()
        (addon / "default.py").write_text("if :\n    pass\n")
        result = validate(addon, cache=self.cache)
        self.assertFalse(result["passed"])
        self.assertEqual(result["checks"]["syntax"]["status"], "failed")
        self.assertEqual(result["checks"]["types"]["status"], "skipped")

    def test_manifest_traversal_is_rejected_before_checker(self):
        addon = self.addon()
        text = (addon / "addon.xml").read_text().replace('library="default.py"', 'library="../outside.py"')
        (addon / "addon.xml").write_text(text)
        result = validate(addon, cache=self.cache)
        self.assertFalse(result["passed"])
        self.assertIn("Unsafe manifest path", result["checks"]["paths"]["errors"][0])
        self.assertEqual(result["checks"]["official_checker"]["status"], "skipped")

    def test_symlink_and_symlink_parent_are_rejected(self):
        addon = self.addon()
        try:
            (addon / "link.py").symlink_to(addon / "default.py")
        except (OSError, NotImplementedError):
            self.skipTest('Symlink creation unavailable; separate junction checks cover Windows reparse boundaries')
        result = validate(addon, cache=self.cache)
        self.assertFalse(result["passed"])
        self.assertIn("Symlink", result["checks"]["paths"]["errors"][0])
        (addon / "link.py").unlink()
        alias = self.work / "alias"
        alias.symlink_to(self.work, target_is_directory=True)
        self.assertFalse(validate(alias / addon.name, cache=self.cache)["passed"])

    def test_tests_config_rejected_and_hashed(self):
        addon = self.addon()
        config = addon / ".tests-config.json"
        config.write_text('{"reporter":[],"check_license_file_exists":false}')
        result = validate(addon, cache=self.cache)
        self.assertFalse(result["passed"])
        self.assertEqual(result["config_input"]["status"], "rejected")
        self.assertEqual(result["config_input"]["files"][0]["sha256"],
                         hashlib.sha256(config.read_bytes()).hexdigest())

    def test_folder_mismatch_and_missing_license(self):
        addon = self.addon()
        (addon / "LICENSE.txt").unlink()
        text = (addon / "addon.xml").read_text().replace('id="script.toolkit.sample"', 'id="script.other"')
        (addon / "addon.xml").write_text(text)
        result = validate(addon, cache=self.cache)
        self.assertFalse(result["passed"])
        self.assertEqual(len(result["checks"]["package"]["errors"]), 2)
        official = result["checks"]["official_checker"]
        self.assertEqual(official["exit_code"], 1)
        self.assertTrue(official["completed"])
        self.assertGreater(official["error_count"], 0)

    def test_cache_absent_incomplete_or_corrupt_fails_closed(self):
        addon = self.addon()
        absent = run_checker(addon)
        self.assertFalse(absent["passed"])
        self.assertIn("required", absent["replay"]["failure"])
        corrupt_path = self.cache / "nexus.xml.gz"
        raw = corrupt_path.read_bytes()
        corrupt_path.write_bytes(raw + b"tamper")
        corrupt = run_checker(addon, cache=self.cache)
        self.assertIn("mismatch", corrupt["replay"]["failure"])
        self.assertEqual(corrupt["replay"]["requested_indexes"], [])
        corrupt_path.write_bytes(raw)
        manifest = json.loads((self.cache / "manifest.json").read_text())
        del manifest["indexes"]["gotham"]
        (self.cache / "manifest.json").write_text(json.dumps(manifest))
        incomplete = run_checker(addon, cache=self.cache)
        self.assertIn("all ten", incomplete["replay"]["failure"])

    def test_symlink_cache_fails_closed(self):
        addon = self.addon()
        alias = self.work / "cache-link"
        try:
            alias.symlink_to(self.cache, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest('Symlink creation unavailable')
        self.assertFalse(run_checker(addon, cache=alias)["passed"])

    def test_stub_target_mismatch_cannot_pass(self):
        result = validate(self.addon(), branch="omega", cache=self.cache)
        self.assertFalse(result["passed"])
        self.assertIn("does not match", result["checks"]["types"]["errors"][0])

    def test_deterministic_missing_dependency_finding_preserved(self):
        addon = self.addon()
        xml = ET.parse(addon / "addon.xml")
        ET.SubElement(xml.getroot().find("requires"), "import",
                      {"addon": "script.module.missing.fixture", "version": "1.0.0"})
        xml.write(addon / "addon.xml", encoding="utf-8", xml_declaration=True)
        official = validate(addon, cache=self.cache)["checks"]["official_checker"]
        self.assertTrue(official["completed"], official)
        self.assertIn("Required dependency script.module.missing.fixture is not available",
                      official["stdout"])
        self.assertGreaterEqual(official["warning_count"], 2)

    def test_unexpected_network_attempt_aborts_worker(self):
        addon = self.addon()
        evidence = self.work / "unexpected.json"
        script = (
            "import argparse, importlib.util\n"
            f"spec=importlib.util.spec_from_file_location('runner', {str(ROOT / 'src/kodi_agent_toolkit/checker_runner.py')!r})\n"
            "runner=importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)\n"
            "import kodi_addon_checker.__main__ as official\n"
            "def surprise():\n"
            "    import requests\n"
            "    requests.get('https://example.org/unexpected')\n"
            "official.main=surprise\n"
            f"args=argparse.Namespace(addon={str(addon)!r}, cache={str(self.cache)!r}, result={str(evidence)!r}, branch='nexus')\n"
            "raise SystemExit(runner._worker(args))\n")
        completed = subprocess.run([sys.executable, "-I", "-B", "-c", script],
                                   capture_output=True, text=True, timeout=30)
        self.assertNotEqual(completed.returncode, 0)
        observed = json.loads(evidence.read_text())
        self.assertIn("Unexpected network request", observed["failure"])
        self.assertEqual(observed["worker_status"], "error")
        self.assertEqual(len(observed["network_violations"]), 1)

    def test_standalone_replay_rejects_manifest_escape(self):
        addon = self.addon()
        (addon / "addon.xml").write_text((addon / "addon.xml").read_text().replace(
            'library="default.py"', 'library="../outside.py"'))
        official = run_checker(addon, cache=self.cache)
        self.assertFalse(official["passed"])
        self.assertIn("Unsafe manifest path", official["replay"]["failure"])
        self.assertEqual(official["replay"]["requested_indexes"], [])

    def test_doctype_in_utf16_manifest_is_rejected(self):
        addon = self.addon()
        xml = '<!DOCTYPE addon [<!ENTITY lib "default.py">]>' + (addon / "addon.xml").read_text().split("?>", 1)[1]
        (addon / "addon.xml").write_bytes(xml.encode("utf-16"))
        result = validate(addon, cache=self.cache)
        self.assertFalse(result["passed"])
        self.assertIn("DOCTYPE", result["checks"]["manifest"]["errors"][0])
        self.assertEqual(result["checks"]["official_checker"]["status"], "skipped")

    def test_https_metadata_redirects_only(self):
        import importlib.util
        import urllib.request
        spec = importlib.util.spec_from_file_location("index_fetch", ROOT / "scripts/fetch-indexes.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        handler = module.MetadataRedirect()
        request = urllib.request.Request("https://mirrors.kodi.tv/addons/nexus/addons.xml.gz")
        accepted = handler.redirect_request(request, None, 302, "Found", {},
                    "https://mirror.example/xbmc/addons/nexus/addons.xml.gz")
        self.assertEqual(accepted.full_url, "https://mirror.example/xbmc/addons/nexus/addons.xml.gz")
        for url in ("http://mirror.example/addons/nexus/addons.xml.gz",
                    "https://mirror.example/addons/nexus/dependency.zip",
                    "https://mirror.example/addons/omega/addons.xml.gz"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                handler.redirect_request(request, None, 302, "Found", {}, url)


    def test_invalid_inputs_keep_complete_result_shape(self):
        expected = {"syntax", "manifest", "paths", "package", "types", "official_checker"}
        for addon, branch in [(self.work / "missing", "nexus"),
                              (self.work / "missing", "not-a-branch")]:
            with self.subTest(branch=branch):
                result = validate(addon, branch=branch, cache=self.cache)
                self.assertFalse(result["passed"])
                self.assertEqual(set(result["checks"]), expected)
                self.assertEqual(result["type_status"], "skipped")
                for key in ("output", "stdout", "stderr", "exit_code", "warnings", "errors"):
                    self.assertIn(key, result["checks"]["official_checker"])



if __name__ == "__main__":
    unittest.main()
