"""Focused optional Omega coverage; synthetic cache, no Kodi/model/network use."""
import importlib.metadata as metadata
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from kodi_agent_toolkit.validate import validate
from test_validation import fixture_cache


class OmegaLockTests(unittest.TestCase):
    def test_optional_lane_preserves_all_other_nexus_pins(self):
        def pins(name):
            return dict(re.findall(r"^([\w.-]+)==([^\s\\]+)",
                                   (ROOT / name).read_text(), re.M))
        nexus = pins("requirements-dev.lock")
        omega = pins("requirements-omega.lock")
        self.assertEqual(nexus["Kodistubs"], "20.0.1")
        self.assertEqual(omega.pop("Kodistubs"), "21.0.0")
        nexus.pop("Kodistubs")
        self.assertEqual(omega, nexus)
        self.assertEqual(pins("requirements-omega.in")["Kodistubs"], "21.0.0")


@unittest.skipUnless(metadata.version("Kodistubs").split(".")[0] == "21",
                     "Run in the separate requirements-omega.lock environment")
class OmegaStaticTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="toolkit-omega-")
        self.addCleanup(self.temporary.cleanup)
        self.work = Path(self.temporary.name)
        self.cache = fixture_cache(self.work / "indexes")

    def addon(self, name):
        destination = self.work / "script.toolkit.sample"
        shutil.copytree(ROOT / "fixtures" / name / "script.toolkit.sample", destination)
        return destination

    def test_omega_valid_retains_official_warnings(self):
        result = validate(self.addon("valid"), branch="omega", cache=self.cache)
        self.assertTrue(result["passed"], result)
        self.assertEqual(result["checks"]["types"]["stub_version"], "21.0.0")
        official = result["checks"]["official_checker"]
        self.assertTrue(official["completed"])
        self.assertGreater(official["warning_count"], 0)
        self.assertEqual(official["online_url_checks"], "unverified")

    def test_omega_invalid_api_still_fails(self):
        result = validate(self.addon("invalid-api"), branch="omega", cache=self.cache)
        self.assertFalse(result["passed"])
        self.assertEqual(result["checks"]["types"]["status"], "failed")
        self.assertIn("arg-type", result["checks"]["types"]["output"])
        self.assertTrue(result["checks"]["official_checker"]["completed"])

    def test_omega_stubs_cannot_qualify_nexus(self):
        result = validate(self.addon("valid"), branch="nexus", cache=self.cache)
        self.assertFalse(result["passed"])
        self.assertEqual(result["checks"]["types"]["status"], "error")
        self.assertIn("does not match branch nexus",
                      result["checks"]["types"]["errors"][0])


if __name__ == "__main__":
    unittest.main()
