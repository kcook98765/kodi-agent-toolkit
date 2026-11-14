"""Read-only stub lanes: pin consistency, no implicit environment qualification."""
import importlib.metadata as metadata
from pathlib import Path
import re
import unittest
from unittest.mock import patch

from kodi_agent_toolkit.stub_lanes import LANES, stub_lanes

ROOT = Path(__file__).resolve().parents[1]


class StubLaneTests(unittest.TestCase):
    def test_four_distinct_branches_and_pinned_requirements(self):
        self.assertEqual([x[0] for x in LANES], ["matrix", "nexus", "omega", "piers"])
        for branch, version, expected, filename, qualified in LANES:
            with self.subTest(branch=branch):
                contents = (ROOT / filename).read_text(encoding="utf-8")
                self.assertIn(f"Kodistubs=={expected}", contents)
                self.assertIn("kodi-addon-checker==0.0.36", contents)
                self.assertIn("mypy==2.4.0", contents)
                self.assertIsNotNone(version)
                self.assertEqual(qualified == "qualified", filename.endswith(".lock"))

    def test_no_installed_stubs_means_none_ready(self):
        with patch("kodi_agent_toolkit.stub_lanes.metadata.version",
                   side_effect=metadata.PackageNotFoundError("Kodistubs")):
            result = stub_lanes()
        self.assertIsNone(result["installed_kodistubs"])
        self.assertEqual(len(result["lanes"]), 4)
        self.assertTrue(all(not x["ready_for_qualified_static_checks"]
                            for x in result["lanes"]))

    def test_correct_major_without_qualification_remains_pending(self):
        with patch("kodi_agent_toolkit.stub_lanes.metadata.version", return_value="22.0.1rc1"):
            result = stub_lanes()
        piers = next(x for x in result["lanes"] if x["branch"] == "piers")
        self.assertTrue(piers["installed_in_this_interpreter"])
        self.assertFalse(piers["ready_for_qualified_static_checks"])
        self.assertEqual(piers["static_qualification"], "pending")

    def test_nexus_only_when_matching_exact_pin(self):
        with patch("kodi_agent_toolkit.stub_lanes.metadata.version", return_value="20.0.1"):
            result = stub_lanes()
        ready = [x["branch"] for x in result["lanes"]
                 if x["ready_for_qualified_static_checks"]]
        self.assertEqual(ready, ["nexus"])

    def test_no_mutation_in_lane_module(self):
        source = (ROOT / "src/kodi_agent_toolkit/stub_lanes.py").read_text()
        self.assertNotIn("pip install", source)
        self.assertNotIn("subprocess", source)


if __name__ == "__main__":
    unittest.main()
