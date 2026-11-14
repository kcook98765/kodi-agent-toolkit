"""Real Piers prerelease packages, exact RC2 representative API signatures; no skips."""
import hashlib
import importlib.metadata as metadata
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests"))
from test_validation import fixture_cache
from kodi_agent_toolkit.validate import validate


class PiersStaticTests(unittest.TestCase):
    def setUp(self):
        self.assertEqual(metadata.version("Kodistubs"), "22.0.1rc1")
        self.assertEqual(metadata.version("mypy"), "2.4.0")
        self.assertEqual(metadata.version("kodi-addon-checker"), "0.0.36")
        self.temporary = tempfile.TemporaryDirectory(prefix="toolkit-piers-")
        self.addCleanup(self.temporary.cleanup)
        self.work = Path(self.temporary.name)
        self.cache = fixture_cache(self.work / "indexes")
        self.addon = self.work / "script.toolkit.sample"
        shutil.copytree(ROOT / "fixtures/valid/script.toolkit.sample", self.addon)

    def check(self, code=None, branch="piers"):
        if code is not None:
            (self.addon / "default.py").write_text(code, encoding="utf-8")
        result = validate(self.addon, branch=branch, cache=self.cache)
        evidence = ROOT / ".local/qualification/piers"
        evidence.mkdir(parents=True, exist_ok=True)
        (evidence / f"{self._testMethodName}-{branch}.json").write_text(
            json.dumps(result, indent=2) + "\n", encoding="utf-8")
        return result

    def test_valid_retains_all_six_stages_and_warnings(self):
        result = self.check()
        self.assertTrue(result["passed"], result)
        self.assertEqual(len(result["checks"]), 6)
        types = result["checks"]["types"]
        self.assertEqual(types["stub_version"], "22.0.1rc1")
        self.assertIsNone(types["compatibility_overlay"])
        official = result["checks"]["official_checker"]
        self.assertTrue(official["completed"])
        self.assertGreater(official["warning_count"], 0)
        self.assertEqual(official["online_url_checks"], "unverified")

    def test_piers_and_rc2_game_metadata_apis(self):
        manifest = self.addon / "addon.xml"
        manifest.write_text(manifest.read_text().replace('version="3.0.0"', 'version="3.1.1"'), encoding="utf-8")
        result = self.check((ROOT / "fixtures/piers-api.py").read_text())
        self.assertTrue(result["passed"], result)
        self.assertIn("advised to set xbmc.python version to 3.0.1",
                      result["checks"]["official_checker"]["stdout"])
        self.assertTrue(any("predating RC2" in x for x in result["coverage_limits"]))

    def test_string_log_severity_fails(self):
        result = self.check('import xbmc\nxbmc.log("bad", "INFO")\n')
        self.assertFalse(result["passed"])
        self.assertIn("arg-type", result["checks"]["types"]["output"])
        self.assertTrue(result["checks"]["official_checker"]["completed"])

    def test_piers_setter_rejects_invalid_type(self):
        result = self.check('import xbmcgui\nxbmcgui.ListItem().setCount("two")\n')
        self.assertFalse(result["passed"])
        self.assertIn("arg-type", result["checks"]["types"]["output"])

    def test_rc2_game_setters_reject_invalid_type(self):
        result = self.check('import xbmcgui\ngame = xbmcgui.ListItem().getGameInfoTag()\n'
                            'game.setPlayers("two")\ngame.setTags([3])\n')
        self.assertFalse(result["passed"])
        self.assertIn("arg-type", result["checks"]["types"]["output"])
        self.assertIn("list-item", result["checks"]["types"]["output"])

    def test_rc2_game_getter_return_types(self):
        result = self.check('import xbmcgui\ngame = xbmcgui.ListItem().getGameInfoTag()\n'
                            'wrong: str = game.getPlayers()\nwrong_tags: list[int] = game.getTags()\n')
        self.assertFalse(result["passed"])
        self.assertIn("assignment", result["checks"]["types"]["output"])

    def test_removed_matrix_api_is_rejected(self):
        result = self.check('import xbmc\nxbmc.translatePath("special://profile/")\n')
        self.assertFalse(result["passed"])
        self.assertIn("attr-defined", result["checks"]["types"]["output"])

    def test_wrong_major_cannot_qualify_other_lanes(self):
        for branch in ("matrix", "nexus", "omega"):
            with self.subTest(branch=branch):
                result = self.check(branch=branch)
                self.assertFalse(result["passed"])
                self.assertEqual(result["checks"]["types"]["status"], "error")
                self.assertIn("does not match", result["checks"]["types"]["errors"][0])

    def test_unreviewed_prerelease_is_rejected(self):
        version = metadata.version
        with patch("kodi_agent_toolkit.validate.metadata.version",
                   side_effect=lambda name: "22.0.0rc1" if name == "Kodistubs" else version(name)):
            result = self.check()
        self.assertFalse(result["passed"])
        self.assertIn("requires Kodistubs==22.0.1rc1", result["checks"]["types"]["errors"][0])

    def test_actual_cli_and_unchanged_installed_packages(self):
        distribution = metadata.distribution("Kodistubs")
        files = [distribution.locate_file(f) for f in distribution.files
                 if str(f).endswith(".py")]
        before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
        run = subprocess.run([sys.executable, "-m", "kodi_agent_toolkit.cli", "validate",
                              str(self.addon), "--branch", "piers", "--cache", str(self.cache)],
                             capture_output=True, text=True, timeout=60)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(before, {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files})


if __name__ == "__main__":
    unittest.main()
