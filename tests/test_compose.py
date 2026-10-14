"""Composition regression tests; no models, add-on execution, or network fetches."""
from __future__ import annotations

import copy
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from kodi_agent_toolkit.compose import compose_review
from kodi_agent_toolkit.review import validate_review
from test_review import REVIEW_ADDON, VALID_ADDON, report
from test_validation import fixture_cache

INVENTED_RULE = {
    "source": "official_checker", "severity": "error",
    "message": "Invented rule: all Kodi scripts must provide an imaginary.json file",
}


def static_report(passed=True, returncode=0):
    return {
        "passed": passed, "returncode": returncode,
        "coverage_limits": ["Static checks only"],
        "checks": {
            "official_checker": {
                "errors": [] if passed else ["Literal official error"],
                "warnings": ["Literal warning: punctuation & whitespace  "],
                "stdout": "original stdout\n", "stderr": "original stderr\n",
                "exit_code": returncode, "replay": {"cache": {"fixture": True}},
            },
        },
    }


class ComposeTests(unittest.TestCase):
    def test_draft_checker_claims_are_removed_before_contract_validation(self):
        # Even malformed draft claims cannot contaminate the evidence contract.
        for claims in ([INVENTED_RULE], {"invented": "malformed checker collection"}):
            with self.subTest(claims=claims):
                draft = report()
                draft["deterministic_findings"] = copy.deepcopy(claims)
                before = copy.deepcopy(draft)
                validation = static_report()
                cache = Path("explicit-cache")
                with patch("kodi_agent_toolkit.compose.validate", return_value=validation) as checked, \
                        patch("kodi_agent_toolkit.compose.validate_review", wraps=validate_review) as anchored:
                    result = compose_review(REVIEW_ADDON, draft, branch="omega", cache=cache)
                checked.assert_called_once_with(REVIEW_ADDON, branch="omega", cache=cache)
                sanitized = copy.deepcopy(before)
                sanitized.pop("deterministic_findings")
                anchored.assert_called_once_with(REVIEW_ADDON, sanitized)
                self.assertEqual(draft, before)
                self.assertEqual(result["discarded_unverified_checker_claims"], claims)
                self.assertEqual(result["contract_report"]["deterministic_findings"], [])
                self.assertTrue(result["passed"], result)
                self.assertEqual(result["returncode"], 0)
                self.assertEqual(result["deterministic_findings"], [{
                    "source": "official_checker", "severity": "warning",
                    "message": validation["checks"]["official_checker"]["warnings"][0],
                }])
                self.assertEqual(result["validation_report"], validation)
                self.assertEqual(result["semantic_verification"], "human-required")
                self.assertEqual(result["model_findings"], result["contract_report"]["accepted_findings"])
                self.assertEqual(result["model_findings"][0]["evidence_status"], "source-anchored")
                self.assertEqual(result["model_findings"][0]["semantic_verification"], "not-performed")
                result["discarded_unverified_checker_claims"].clear()
                result["model_findings"][0]["title"] = "changed"
                self.assertEqual(draft, before)
                self.assertNotEqual(result["contract_report"]["accepted_findings"][0]["title"], "changed")

    def test_bad_quote_fails_contract_and_retains_only_accepted_candidates(self):
        draft = report()
        invalid = copy.deepcopy(draft["model_findings"][0])
        invalid["quote"] = "send_to_imaginary_server(supplied_secret)"
        draft["model_findings"].append(invalid)
        with patch("kodi_agent_toolkit.compose.validate", return_value=static_report()):
            result = compose_review(REVIEW_ADDON, draft)
        self.assertTrue(result["static_passed"])
        self.assertFalse(result["contract_passed"])
        self.assertFalse(result["passed"])
        self.assertEqual(result["returncode"], 1)
        self.assertEqual(len(result["model_findings"]), 1)
        self.assertEqual(len(result["contract_report"]["rejected_findings"]), 1)
        self.assertNotIn(invalid, result["model_findings"])

    def test_pass_requires_both_checks_and_preserves_static_failure_code(self):
        for static_passed, code in ((True, 0), (False, 2), (False, 0)):
            for contract_passed in (True, False):
                with self.subTest(static=static_passed, contract=contract_passed, code=code):
                    draft = report()
                    if not contract_passed:
                        draft["model_findings"][0]["quote"] = "invented quote"
                    validation = static_report(static_passed, code)
                    with patch("kodi_agent_toolkit.compose.validate", return_value=validation):
                        result = compose_review(REVIEW_ADDON, draft)
                    self.assertEqual(result["passed"], static_passed and contract_passed)
                    expected_code = code or 1 if not static_passed else (0 if contract_passed else 1)
                    self.assertEqual(result["returncode"], expected_code)
                    self.assertEqual(result["exit_code"], expected_code)
                    self.assertEqual(result["validation_report"], validation)
                    self.assertEqual([finding["message"] for finding in result["deterministic_findings"]],
                                     validation["checks"]["official_checker"]["errors"] +
                                     validation["checks"]["official_checker"]["warnings"])

    def test_missing_cache_fails_without_using_existing_local_cache(self):
        draft = report()
        draft["model_findings"] = []
        draft["coverage"]["reviewed_files"] = ["addon.xml", "default.py"]
        result = compose_review(VALID_ADDON, draft)
        self.assertTrue(result["contract_passed"], result)
        self.assertFalse(result["static_passed"])
        self.assertFalse(result["passed"])
        self.assertNotEqual(result["returncode"], 0)
        official = result["validation_report"]["checks"]["official_checker"]
        self.assertFalse(official["completed"])
        self.assertIn("explicit complete index cache", " ".join(official["infrastructure_errors"]))
        self.assertEqual(result["deterministic_findings"], [])


class OriginalCheckerComposeTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="kodi-compose-test-")
        self.addCleanup(temporary.cleanup)
        public_cache = ROOT / ".local" / "index-cache"
        self.cache = (public_cache if public_cache.is_dir() else
                      fixture_cache(Path(temporary.name) / "indexes"))

    def test_real_checker_warnings_are_canonical_and_invented_rule_is_excluded(self):
        draft = report()
        draft["model_findings"] = []
        draft["coverage"]["reviewed_files"] = ["addon.xml", "default.py"]
        draft["deterministic_findings"] = [copy.deepcopy(INVENTED_RULE)]
        result = compose_review(VALID_ADDON, draft, cache=self.cache)
        self.assertTrue(result["passed"], result)
        self.assertEqual(result["returncode"], 0)
        official = result["validation_report"]["checks"]["official_checker"]
        self.assertTrue(official["completed"])
        self.assertEqual(official["replay"]["checker_version"], "0.0.36")
        self.assertEqual(len(official["replay"]["requested_indexes"]), 10)
        self.assertEqual(official["replay"]["network_violations"], [])
        self.assertTrue(official["warnings"])
        self.assertIn("online URL check unverified", official["stdout"])
        self.assertEqual(result["deterministic_findings"], [
            {"source": "official_checker", "severity": severity, "message": message}
            for field, severity in (("errors", "error"), ("warnings", "warning"))
            for message in official[field]
        ])
        self.assertNotIn(INVENTED_RULE, result["deterministic_findings"])
        self.assertEqual(result["discarded_unverified_checker_claims"], [INVENTED_RULE])
        self.assertEqual(official["output"], official["stdout"] + official["stderr"])
        self.assertEqual(result["semantic_verification"], "human-required")

    def test_real_checker_failure_preserves_error_records_and_original_traceback(self):
        addon = ROOT / "fixtures" / "invalid-xml" / "script.toolkit.sample"
        draft = report()
        draft["model_findings"] = []
        draft["coverage"]["reviewed_files"] = ["addon.xml", "default.py"]
        result = compose_review(addon, draft, cache=self.cache)
        self.assertTrue(result["contract_passed"], result)
        self.assertFalse(result["passed"])
        self.assertEqual(result["returncode"], 1)
        official = result["validation_report"]["checks"]["official_checker"]
        self.assertIn("Invalid XML data in addon.xml", official["stdout"])
        self.assertIn("UnboundLocalError", official["stderr"])
        self.assertEqual(result["deterministic_findings"], [
            {"source": "official_checker", "severity": severity, "message": message}
            for field, severity in (("errors", "error"), ("warnings", "warning"))
            for message in official[field]
        ])
        self.assertTrue(any(item["severity"] == "error" for item in result["deterministic_findings"]))


if __name__ == "__main__":
    unittest.main()
