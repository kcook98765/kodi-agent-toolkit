"""Read-only stub lanes: pin consistency, no implicit environment qualification."""
import importlib.metadata as metadata
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from kodi_agent_toolkit.stub_lanes import LANES, stub_lanes

ROOT = Path(__file__).resolve().parents[1]


class StubLaneTests(unittest.TestCase):
    def setUp(self):
        self.tools = {"Kodistubs": "20.0.1", "mypy": "2.4.0", "kodi-addon-checker": "0.0.36"}
        def version(package):
            if self.tools.get(package) is None:
                raise metadata.PackageNotFoundError(package)
            return self.tools[package]
        for target, kwargs in (
            ("metadata.version", {"side_effect": version}),
            ("platform.python_implementation", {"return_value": "CPython"}),
            ("sys.version_info", {"new": (3, 12, 3)}),
            ("sys.platform", {"new": "linux"}),
        ):
            patcher = patch("kodi_agent_toolkit.stub_lanes." + target, **kwargs)
            patcher.start()
            self.addCleanup(patcher.stop)

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
        self.tools["Kodistubs"] = "22.0.1rc1"
        piers = stub_lanes()["lanes"][3]
        self.assertTrue(piers["installed_in_this_interpreter"])
        self.assertFalse(piers["ready_for_qualified_static_checks"])
        self.assertEqual(piers["static_qualification"], "pending")

    def test_nexus_only_when_matching_exact_pin(self):
        result = stub_lanes()
        self.assertEqual(result["python_executable"], sys.executable)
        self.assertTrue(result["python_version"])
        ready = [x["branch"] for x in result["lanes"]
                 if x["ready_for_qualified_static_checks"]]
        self.assertEqual(ready, ["nexus"])
        self.tools["Kodistubs"] = "20.0.2"
        self.assertFalse(stub_lanes()["lanes"][1]["ready_for_qualified_static_checks"])

    def test_missing_or_mismatched_tools_cannot_report_ready(self):
        for package in ("mypy", "kodi-addon-checker"):
            for value in (None, "0.0.0"):
                with self.subTest(package=package, value=value):
                    old = self.tools[package]
                    self.tools[package] = value
                    lane = stub_lanes()["lanes"][1]
                    self.assertFalse(lane["ready_for_qualified_static_checks"])
                    self.assertTrue(any(package in x for x in lane["readiness_limits"]))
                    self.tools[package] = old

    def test_unqualified_interpreter_or_platform_cannot_report_ready(self):
        with patch("kodi_agent_toolkit.stub_lanes.sys.version_info", (3, 11, 0)):
            self.assertFalse(stub_lanes()["lanes"][1]["ready_for_qualified_static_checks"])
        with patch("kodi_agent_toolkit.stub_lanes.sys.platform", "darwin"):
            self.assertFalse(stub_lanes()["lanes"][1]["ready_for_qualified_static_checks"])
        self.tools["Kodistubs"] = "21.0.0"
        with patch("kodi_agent_toolkit.stub_lanes.sys.platform", "win32"):
            self.assertFalse(stub_lanes()["lanes"][2]["ready_for_qualified_static_checks"])

    def test_no_mutation_in_lane_module(self):
        source = (ROOT / "src/kodi_agent_toolkit/stub_lanes.py").read_text()
        self.assertNotIn("subprocess.run(", source)
        self.assertNotIn("subprocess", source)


if __name__ == "__main__":
    unittest.main()
