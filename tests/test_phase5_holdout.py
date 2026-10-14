"""Independent Phase 5 holdouts, authored after APIs and guidance were fixed.

No model, Kodi runtime, credentials, downloads or existing profiles are used.
These scenarios were reserved by the harness reviewer and were not supplied to
skill/helper implementation before their first test run. They test boundaries,
not semantic truth of arbitrary model prose.
"""
from __future__ import annotations

import copy
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from kodi_agent_toolkit.paths import discover
from kodi_agent_toolkit.checker_runner import SourceViolation
from kodi_agent_toolkit.review import validate_review
from kodi_agent_toolkit.compose import compose_review
from test_validation import fixture_cache


class IndependentPhase5Holdouts(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="kodi independent holdout ")
        self.addCleanup(self.temporary.cleanup)
        self.workspace = Path(self.temporary.name) / "developer workspace"
        self.workspace.mkdir()
        (self.workspace / ".git").mkdir()
        self.addon = self.workspace / "addons with spaces" / "script.toolkit.sample"
        shutil.copytree(ROOT / "fixtures/valid/script.toolkit.sample", self.addon)
        self.entry = "lib spaces/entry point.py"
        (self.addon / "lib spaces").mkdir()
        (self.addon / "default.py").rename(self.addon / self.entry)
        manifest = self.addon / "addon.xml"
        manifest.write_text(manifest.read_text().replace('library="default.py"', 'library="' + self.entry + '"'))

    def draft(self):
        return {"model_findings": [], "deterministic_findings": [],
                "coverage": {"scope": "Manifest and declared entry only", "complete": False,
                             "reviewed_files": ["addon.xml", self.entry]},
                "limitations": ["Static source evidence; no runtime or semantic test."]}

    def speculative_finding(self):
        return {"path": self.entry, "line": 7,
                "quote": 'xbmc.log("Toolkit sample ready", xbmc.LOGINFO)',
                "title": "Hypothetical private data in diagnostic",
                "category": "privacy", "reason": "Impact has not been established.",
                "mechanism": "The fixed diagnostic is passed to xbmc.log; unknown private input is speculative.",
                "severity": "advisory", "confidence": "unresolved", "related_evidence": []}

    def test_wrong_cwd_reconstructs_actual_project_with_space_entrypoint(self):
        nested = self.workspace / "nested working directory" / "deeper"
        nested.mkdir(parents=True)
        previous = Path.cwd()
        try:
            os.chdir(nested)
            result = discover(Path("."))
        finally:
            os.chdir(previous)
        self.assertTrue(result["passed"], result)
        self.assertEqual(result["project_root"], str(self.workspace))
        self.assertEqual(result["scan_root"], str(self.workspace))
        record = result["addons"][0]
        self.assertEqual(record["addon_dir"], "addons with spaces/script.toolkit.sample")
        self.assertEqual(record["entry_points"][0]["path"], self.entry)
        self.assertTrue(record["entry_points"][0]["exists"])
        self.assertNotIn("default.py", record["files"])

    def test_stale_absolute_directory_is_rejected_without_guessing(self):
        with self.assertRaises(SourceViolation):
            discover(self.workspace / "addons with spaces" / "script.toolkit-sample")
        self.assertTrue((self.addon / "addon.xml").is_file())

    def test_missing_manifest_cannot_be_inferred_from_python_entry(self):
        (self.addon / "addon.xml").unlink()
        result = discover(self.workspace)
        self.assertFalse(result["passed"], result)
        self.assertEqual(result["addons"], [])
        self.assertTrue(result["errors"])
        self.assertTrue((self.addon / self.entry).is_file())

    @unittest.skipUnless(os.name == "posix", "POSIX path translation boundary")
    def test_windows_drive_path_is_not_reinterpreted_as_relative_posix_input(self):
        with self.assertRaises(SourceViolation):
            discover(Path("D:/developer workspace/addons"))

    @unittest.skipUnless(os.name == "posix", "POSIX symlink holdout")
    def test_manifest_entry_link_is_never_presented_as_verified_file(self):
        actual = self.addon / self.entry
        outside = self.workspace / "outside source.py"
        actual.rename(outside)
        actual.symlink_to(outside)
        result = discover(self.workspace)
        record = result["addons"][0]
        self.assertFalse(record["entry_points"][0]["exists"])
        self.assertNotIn(self.entry, record["files"])
        self.assertTrue(any(item["reason"] == "link-or-reparse-excluded" for item in result["omitted"]))

    def test_unresolved_material_claim_is_rejected_despite_exact_source_quote(self):
        draft = self.draft()
        finding = self.speculative_finding()
        finding["severity"] = "material"
        draft["model_findings"] = [finding]
        result = validate_review(self.addon, draft)
        self.assertFalse(result["passed"], result)
        self.assertEqual(result["accepted_findings"], [])
        self.assertIn("unresolved", str(result["rejected_findings"]))

    def test_observation_is_anchored_without_becoming_confirmed_privacy_defect(self):
        draft = self.draft()
        draft["model_findings"] = [self.speculative_finding()]
        result = validate_review(self.addon, draft)
        self.assertTrue(result["passed"], result)
        accepted = result["accepted_findings"][0]
        self.assertEqual(accepted["disposition"], "observation")
        self.assertEqual(accepted["semantic_verification"], "not-performed")
        self.assertTrue(accepted["confidence_is_claim"])

    def test_source_supported_blocker_does_not_poison_static_pass(self):
        draft = self.draft()
        finding = self.speculative_finding()
        finding.update(severity="blocker", confidence="source-supported")
        draft["model_findings"] = [finding]
        draft["deterministic_findings"] = [{"source": "official_checker", "severity": "error",
            "message": "Hypothetical rule: ordinary diagnostics require encrypted output"}]
        before = copy.deepcopy(draft)
        cache = fixture_cache(self.workspace / "checker indexes")
        result = compose_review(self.addon, draft, cache=cache)
        self.assertTrue(result["static_passed"], result)
        self.assertFalse(result["contract_passed"])
        self.assertFalse(result["passed"])
        self.assertEqual(result["validation_report"]["checks"]["official_checker"]["error_count"], 0)
        self.assertEqual(result["discarded_unverified_checker_claims"], before["deterministic_findings"])
        self.assertNotIn("encrypted output", str(result["deterministic_findings"]))
        self.assertEqual(draft, before)

    def test_missing_checker_environment_is_failure_with_clean_source_contract(self):
        result = compose_review(self.addon, self.draft(), cache=self.workspace / "unavailable checker indexes")
        self.assertTrue(result["contract_passed"], result)
        self.assertFalse(result["static_passed"])
        self.assertFalse(result["passed"])
        official = result["validation_report"]["checks"]["official_checker"]
        self.assertFalse(official["completed"])
        self.assertTrue(official["infrastructure_errors"])
        self.assertEqual(result["deterministic_findings"], [])
        self.assertEqual(result["semantic_verification"], "human-required")


if __name__ == "__main__":
    unittest.main()
