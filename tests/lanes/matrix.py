"""Explicit Matrix qualification job: requires real locked packages; never skipped."""
import hashlib
import json
import importlib.metadata as metadata
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests"))
from test_validation import fixture_cache
from kodi_agent_toolkit.validate import validate
from kodi_agent_toolkit.matrix_stubs import matrix_shadow
from unittest.mock import patch


class MatrixStaticTests(unittest.TestCase):
    def setUp(self):
        self.assertEqual(metadata.version("Kodistubs"), "19.0.3")
        self.assertEqual(metadata.version("mypy"), "2.4.0")
        self.assertEqual(metadata.version("kodi-addon-checker"), "0.0.36")
        self.temporary = tempfile.TemporaryDirectory(prefix="toolkit-matrix-")
        self.addCleanup(self.temporary.cleanup)
        self.work = Path(self.temporary.name)
        self.cache = fixture_cache(self.work / "indexes")
        self.addon = self.work / "script.toolkit.sample"
        shutil.copytree(ROOT / "fixtures/valid/script.toolkit.sample", self.addon)

    def check(self, code=None, branch="matrix"):
        if code is not None:
            (self.addon / "default.py").write_text(code, encoding="utf-8")
        result = validate(self.addon, branch=branch, cache=self.cache)
        evidence = ROOT / ".local/qualification/matrix"
        evidence.mkdir(parents=True, exist_ok=True)
        (evidence / f"{self._testMethodName}-{branch}.json").write_text(
            json.dumps(result, indent=2) + "\n", encoding="utf-8")
        return result

    def test_valid_retains_all_stages_and_official_warnings(self):
        result = self.check()
        self.assertTrue(result["passed"], result)
        self.assertEqual(len(result["checks"]), 6)
        self.assertEqual(result["checks"]["types"]["stub_version"], "19.0.3")
        official = result["checks"]["official_checker"]
        self.assertTrue(official["completed"])
        self.assertGreater(official["warning_count"], 0)
        self.assertEqual(official["online_url_checks"], "unverified")

    def test_matrix_metadata_and_vfs_apis(self):
        result = self.check((ROOT / "fixtures/matrix-api.py").read_text())
        self.assertTrue(result["passed"], result)
        self.assertEqual(result["checks"]["types"]["compatibility_overlay"]["id"],
                         "matrix-19.0.3-setinfo")

    def test_string_log_severity_fails(self):
        result = self.check('import xbmc\nxbmc.log("bad", "INFO")\n')
        self.assertFalse(result["passed"])
        self.assertIn("arg-type", result["checks"]["types"]["output"])
        self.assertTrue(result["checks"]["official_checker"]["completed"])

    def test_nexus_infotag_setter_is_not_a_matrix_api(self):
        result = self.check('import xbmcgui\nxbmcgui.ListItem().getVideoInfoTag().setTitle("new API")\n')
        self.assertFalse(result["passed"])
        self.assertIn("attr-defined", result["checks"]["types"]["output"])

    def test_corrected_setinfo_still_rejects_invalid_values(self):
        result = self.check('import xbmcgui\nxbmcgui.ListItem().setInfo("video", {"year": object()})\n')
        self.assertFalse(result["passed"])
        self.assertIn("dict-item", result["checks"]["types"]["output"])

    def test_matrix_cannot_qualify_other_majors(self):
        for branch in ("nexus", "omega", "piers"):
            with self.subTest(branch=branch):
                result = self.check(branch=branch)
                self.assertFalse(result["passed"])
                self.assertEqual(result["checks"]["types"]["status"], "error")
                self.assertIn("does not match", result["checks"]["types"]["errors"][0])

    def test_overlay_preserves_installed_artifact_and_rejects_tamper(self):
        gui = metadata.distribution("Kodistubs").locate_file("xbmcgui.py")
        original = gui.read_bytes()
        shadow, evidence = matrix_shadow(gui, self.work)
        self.assertEqual(gui.read_bytes(), original)
        self.assertEqual(evidence["upstream_sha256"], hashlib.sha256(original).hexdigest())
        self.assertNotEqual(shadow.read_bytes(), original)
        shadow.write_bytes(original + b"\n")
        with self.assertRaisesRegex(ValueError, "artifact hash"):
            matrix_shadow(shadow, self.work)

    def test_same_major_unreviewed_patch_is_rejected(self):
        version = metadata.version
        with patch("kodi_agent_toolkit.validate.metadata.version",
                   side_effect=lambda name: "19.0.4" if name == "Kodistubs" else version(name)):
            result = self.check()
        self.assertFalse(result["passed"])
        self.assertIn("requires Kodistubs==19.0.3", result["checks"]["types"]["errors"][0])

    def test_corrected_cast_still_rejects_invalid_values(self):
        result = self.check('import xbmcgui\nxbmcgui.ListItem().setCast([{"name": object()}])\n')
        self.assertFalse(result["passed"])
        self.assertIn("dict-item", result["checks"]["types"]["output"])

    def test_actual_cli(self):
        run = subprocess.run([sys.executable, "-m", "kodi_agent_toolkit.cli", "validate",
                              str(self.addon), "--branch", "matrix", "--cache", str(self.cache)],
                             capture_output=True, text=True, timeout=60)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


if __name__ == "__main__":
    unittest.main()
