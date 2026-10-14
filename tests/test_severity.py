"""Severity contract regressions, separate from semantic judgment."""
import copy
from unittest.mock import patch
import unittest
from kodi_agent_toolkit.review import validate_review
from kodi_agent_toolkit.compose import compose_review
from test_review import report, REVIEW_ADDON, VALID_ADDON
# These tests mock the checker deliberately; importing another full suite's
# cache helper pulled in optional installed metadata before skip evaluation.
def static_report():
    return {"passed": True, "returncode": 0, "checks": {
        "official_checker": {"errors": [], "warnings": ["Synthetic checker warning"]}
    }}

class SeverityTests(unittest.TestCase):
    def test_source_anchor_cannot_justify_blocker(self):
        draft = report()
        draft["model_findings"][0].update(severity="blocker", confidence="source-supported")
        result = validate_review(REVIEW_ADDON, draft)
        self.assertFalse(result["passed"])
        self.assertIn("blocker requires", str(result["rejected_findings"]))

    def test_uncertain_claim_is_observation_and_cannot_be_material(self):
        draft = report()
        finding = draft["model_findings"][0]
        finding.update(confidence="unresolved", severity="material")
        self.assertFalse(validate_review(REVIEW_ADDON, draft)["passed"])
        finding["severity"] = "advisory"
        result = validate_review(REVIEW_ADDON, draft)
        self.assertTrue(result["passed"])
        self.assertEqual(result["accepted_findings"][0]["disposition"], "observation")

    def test_demonstrated_requires_reproduction_but_is_still_author_claim(self):
        draft = report()
        draft["model_findings"][0].update(confidence="demonstrated", severity="blocker")
        self.assertFalse(validate_review(REVIEW_ADDON, draft)["passed"])
        draft["model_findings"][0]["reproduction"] = {"steps":"Synthetic described test", "observed":"Synthetic actual behavior", "expected":"Synthetic expected behavior"}
        result = validate_review(REVIEW_ADDON, draft)
        self.assertTrue(result["passed"])
        self.assertEqual(result["accepted_findings"][0]["semantic_verification"], "not-performed")

    def test_invalid_model_severity_does_not_change_checker_pass(self):
        draft = report()
        draft["model_findings"][0].update(severity="blocker", confidence="source-supported")
        with patch("kodi_agent_toolkit.compose.validate", return_value=static_report()):
            result = compose_review(REVIEW_ADDON, draft)
        self.assertTrue(result["static_passed"])
        self.assertFalse(result["contract_passed"])
        self.assertEqual(result["status"], "contract-rejected")
        self.assertTrue(all(f["severity"] == "warning" for f in result["deterministic_findings"]))

    def test_valid_addon_with_no_model_findings_retains_checker_success(self):
        draft = report()
        draft["model_findings"] = []
        draft["coverage"]["reviewed_files"] = ["addon.xml", "default.py"]
        with patch("kodi_agent_toolkit.compose.validate", return_value=static_report()):
            result = compose_review(VALID_ADDON, draft)
        self.assertTrue(result["passed"])
        self.assertEqual(result["status"], "semantic-review-required")

    def test_static_findings_cannot_claim_observed_reproduction(self):
        draft = report()
        draft["model_findings"][0].update(confidence="source-supported", reproduction={"steps":"Not executed", "observed":"Invented runtime output", "expected":"No output"})
        self.assertFalse(validate_review(REVIEW_ADDON, draft)["passed"])
        del draft["model_findings"][0]["reproduction"]
        self.assertTrue(validate_review(REVIEW_ADDON, draft)["passed"])

    def test_exposed_schema_encodes_classification_constraints(self):
        from kodi_agent_toolkit.review import report_schema
        rules = report_schema()["properties"]["model_findings"]["items"]["allOf"]
        self.assertEqual(rules[0]["then"]["properties"]["severity"]["const"], "advisory")
        self.assertEqual(rules[1]["then"]["properties"]["confidence"]["const"], "demonstrated")
        self.assertEqual(rules[2]["then"]["required"], ["reproduction"])
        self.assertEqual(rules[2]["else"], {"not": {"required": ["reproduction"]}})
