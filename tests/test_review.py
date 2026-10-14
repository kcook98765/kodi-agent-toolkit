"""Evidence validation tests; fixture add-ons are never imported or executed."""

from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from kodi_agent_toolkit import review

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
REVIEW_ADDON = FIXTURES / "review" / "script.toolkit.sample"
VALID_ADDON = FIXTURES / "valid" / "script.toolkit.sample"

# An original fixed candidate for the existing hidden-setting-to-logging fixture.
PRIVACY_CANDIDATE = {
    "path": "default.py",
    "line": 9,
    "quote": "xbmc.log(supplied_secret, xbmc.LOGINFO)",
    "title": "A private setting value reaches the log",
    "category": "privacy",
    "severity": "material",
    "confidence": "source-supported",
    "reason": "If a user supplies a private value, reaching this call can put "
              "that value in the Kodi log.",
    "mechanism": "main reads private_value into supplied_secret and passes "
                 "that variable unchanged to xbmc.log; a hidden edit control "
                 "only conceals its UI display.",
    "related_evidence": [
        {"path": "default.py", "line": 8,
         "quote": 'supplied_secret = addon.getSetting("private_value")',
         "role": "support"},
        {"path": "resources/settings.xml", "line": 3,
         "quote": '<setting id="private_value" type="string" label="Private value">',
         "role": "support"},
        {"path": "resources/settings.xml", "line": 5,
         "quote": "<hidden>true</hidden>", "role": "context"},
    ],
}


def report(candidate: dict | None = None) -> dict:
    return {
        "model_findings": [copy.deepcopy(candidate or PRIVACY_CANDIDATE)],
        "coverage": {
            "scope": "The supplied script and its private-setting declaration",
            "complete": True,
            "reviewed_files": ["default.py", "resources/settings.xml"],
        },
        "limitations": ["Static source only; the fixture was not run in Kodi."],
    }


class ValidateReviewTests(unittest.TestCase):
    def rejected(self, candidate: dict, addon: Path = REVIEW_ADDON) -> dict:
        result = review.validate_review(addon, report(candidate))
        self.assertFalse(result["passed"])
        self.assertEqual(result["accepted_findings"], [])
        self.assertEqual(len(result["rejected_findings"]), 1)
        self.assertTrue(result["rejected_findings"][0]["errors"])
        return result

    def test_fixed_dataflow_candidate_has_exact_primary_and_related_anchors(self):
        result = review.validate_review(REVIEW_ADDON, report())
        self.assertTrue(result["passed"], result)
        accepted = result["accepted_findings"][0]
        self.assertEqual(accepted["source"], "model")
        self.assertEqual(accepted["evidence_status"], "source-anchored")
        self.assertEqual(accepted["semantic_verification"], "not-performed")
        self.assertTrue(accepted["confidence_is_claim"])
        self.assertEqual(result["coverage"]["runtime_execution"], "not-performed")

    def test_empty_findings_on_valid_fixture_do_not_certify_runtime_safety(self):
        data = report()
        data["model_findings"] = []
        data["coverage"]["reviewed_files"] = ["addon.xml", "default.py"]
        result = review.validate_review(VALID_ADDON, data)
        self.assertTrue(result["passed"], result)
        self.assertEqual(result["accepted_findings"], [])
        self.assertEqual(result["coverage"]["semantic_verification"], "not-performed")
        self.assertTrue(result["coverage"]["limitations"])

    def test_quote_on_a_different_existing_line_is_rejected(self):
        candidate = copy.deepcopy(PRIVACY_CANDIDATE)
        candidate["line"] = 8
        self.rejected(candidate)

    def test_invented_quote_is_rejected_even_at_real_location(self):
        candidate = copy.deepcopy(PRIVACY_CANDIDATE)
        candidate["quote"] = "send_secret_to_remote_server(supplied_secret)"
        self.rejected(candidate)

    def test_line_must_be_an_integer_within_the_file(self):
        for line in (0, -1, 999, True, 9.0, "9"):
            with self.subTest(line=line):
                candidate = copy.deepcopy(PRIVACY_CANDIDATE)
                candidate["line"] = line
                self.rejected(candidate)

    def test_unsafe_paths_do_not_become_source_evidence(self):
        paths = [
            "../default.py", "resources/../../default.py", "/etc/passwd",
            "C:/Windows/win.ini", "C:\\Windows\\win.ini", "\\\\server\\share",
            "./default.py", "resources//settings.xml", "default.py/",
            "default.py\x00", "default.py\n", "CON", "aux.txt", "file:stream",
        ]
        for path in paths:
            with self.subTest(path=path):
                candidate = copy.deepcopy(PRIVACY_CANDIDATE)
                candidate["path"] = path
                self.rejected(candidate)

    def test_missing_file_or_directory_is_rejected(self):
        for path in ("invented.py", "resources"):
            with self.subTest(path=path):
                candidate = copy.deepcopy(PRIVACY_CANDIDATE)
                candidate["path"] = path
                self.rejected(candidate)

    def test_related_evidence_is_not_a_location_bypass(self):
        for changes in (
            {"path": "../default.py"}, {"line": 900},
            {"quote": "the value has already been redacted"},
        ):
            with self.subTest(changes=changes):
                candidate = copy.deepcopy(PRIVACY_CANDIDATE)
                candidate["related_evidence"][0].update(changes)
                self.rejected(candidate)

    def test_related_evidence_must_have_a_valid_shape_and_role(self):
        for related in ({}, [None], [{"path": "default.py", "line": 8,
                                    "quote": "supplied_secret", "role": "proven"}]):
            with self.subTest(related=related):
                candidate = copy.deepcopy(PRIVACY_CANDIDATE)
                candidate["related_evidence"] = related
                self.rejected(candidate)

    def test_primary_and_related_sources_must_be_declared_in_coverage(self):
        data = report()
        data["coverage"]["reviewed_files"] = ["default.py"]
        result = review.validate_review(REVIEW_ADDON, data)
        self.assertFalse(result["passed"])
        self.assertIn("coverage.reviewed_files",
                      " ".join(result["rejected_findings"][0]["errors"]))

    def test_enum_typos_and_unknown_category_are_rejected(self):
        for field, value in (
            ("severity", "critical"), ("confidence", "certain"),
            ("category", "style"), ("category", None),
        ):
            with self.subTest(field=field, value=value):
                candidate = copy.deepcopy(PRIVACY_CANDIDATE)
                candidate[field] = value
                self.rejected(candidate)

    def test_broad_certainty_without_a_mechanism_is_rejected(self):
        for mechanism in (None, "", "   ", "definitely unsafe"):
            with self.subTest(mechanism=mechanism):
                candidate = copy.deepcopy(PRIVACY_CANDIDATE)
                candidate["title"] = "All executions definitely expose every secret"
                candidate["reason"] = "This is guaranteed."
                if mechanism is None:
                    candidate.pop("mechanism")
                else:
                    candidate["mechanism"] = mechanism
                self.rejected(candidate)

    def test_whitespace_or_multiline_quotes_are_rejected(self):
        for quote in (" ", "\n", "supplied_secret\nxbmc.log"):
            with self.subTest(quote=quote):
                candidate = copy.deepcopy(PRIVACY_CANDIDATE)
                candidate["quote"] = quote
                self.rejected(candidate)

    def test_coverage_and_limitations_are_required(self):
        variants = []
        for field in ("coverage", "limitations"):
            data = report()
            data.pop(field)
            variants.append(data)
        data = report()
        data["limitations"] = []
        variants.append(data)
        data = report()
        data["coverage"]["complete"] = "yes"
        variants.append(data)
        data = report()
        data["coverage"]["scope"] = ""
        variants.append(data)
        for data in variants:
            with self.subTest(data=data):
                result = review.validate_review(REVIEW_ADDON, data)
                self.assertFalse(result["passed"])
                self.assertTrue(result["errors"])

    def test_partial_coverage_is_explicit_and_can_pass_the_contract(self):
        data = report()
        data["coverage"]["complete"] = False
        data["limitations"].append("Other helpers were not reviewed.")
        result = review.validate_review(REVIEW_ADDON, data)
        self.assertTrue(result["passed"], result)
        self.assertFalse(result["coverage"]["complete"])
        self.assertTrue(result["coverage"]["scope_completion_is_claim"])

    def test_checker_records_are_separate_unverified_and_never_model_acceptances(self):
        data = report()
        deterministic = {"tool": "a-checker", "message": "opaque diagnostic",
                         "path": "../not-model-evidence"}
        data["deterministic_findings"] = [deterministic]
        result = review.validate_review(REVIEW_ADDON, data)
        self.assertTrue(result["passed"], result)
        self.assertEqual(len(result["accepted_findings"]), 1)
        self.assertEqual(result["deterministic_findings"], [deterministic])
        self.assertEqual(result["coverage"]["deterministic_verification"], "not-performed")

    def test_valid_findings_survive_an_invalid_candidate_without_mutating_input(self):
        data = report()
        bad = copy.deepcopy(PRIVACY_CANDIDATE)
        bad["line"] = 1000
        data["model_findings"].append(bad)
        before = copy.deepcopy(data)
        result = review.validate_review(REVIEW_ADDON, data)
        self.assertFalse(result["passed"])
        self.assertEqual(len(result["accepted_findings"]), 1)
        self.assertEqual(len(result["rejected_findings"]), 1)
        self.assertEqual(data, before)
        result["accepted_findings"][0]["related_evidence"].clear()
        self.assertEqual(data, before)

    def test_collection_and_distinct_source_budgets_are_enforced(self):
        data = report()
        data["model_findings"] = [copy.deepcopy(PRIVACY_CANDIDATE)] * 2
        with patch.object(review, "MAX_FINDINGS", 1):
            self.assertFalse(review.validate_review(REVIEW_ADDON, data)["passed"])
        data = report()
        data["deterministic_findings"] = [{"message": "one"}, {"message": "two"}]
        with patch.object(review, "MAX_CHECKER_FINDINGS", 1):
            self.assertFalse(review.validate_review(REVIEW_ADDON, data)["passed"])
        with patch.object(review, "MAX_EVIDENCE_FILES", 1):
            result = review.validate_review(REVIEW_ADDON, report())
        self.assertFalse(result["passed"])
        self.assertIn("too many distinct evidence files",
                      " ".join(result["rejected_findings"][0]["errors"]))

    def test_malformed_collections_fail_as_report_errors(self):
        for field, value in (("model_findings", {}), ("deterministic_findings", [1]),
                             ("coverage", [])):
            with self.subTest(field=field):
                data = report()
                data[field] = value
                result = review.validate_review(REVIEW_ADDON, data)
                self.assertFalse(result["passed"])
                self.assertTrue(result["errors"])

    def test_unrecognized_top_level_or_model_fields_are_not_silently_ignored(self):
        data = report()
        data["findings"] = [PRIVACY_CANDIDATE]
        self.assertFalse(review.validate_review(REVIEW_ADDON, data)["passed"])
        candidate = copy.deepcopy(PRIVACY_CANDIDATE)
        candidate["source"] = "deterministic"
        self.rejected(candidate)

    def test_symlink_file_directory_and_root_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            addon = parent / "addon"
            addon.mkdir()
            outside = parent / "outside"
            outside.mkdir()
            (outside / "source.py").write_text("print('external')\n", encoding="utf-8")
            try:
                (addon / "file.py").symlink_to(outside / "source.py")
                (addon / "linked").symlink_to(outside, target_is_directory=True)
                (parent / "linked-addon").symlink_to(addon, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable on this platform")
            for path in ("file.py", "linked/source.py"):
                candidate = copy.deepcopy(PRIVACY_CANDIDATE)
                candidate.update(path=path, line=1, quote="print", related_evidence=[])
                data = report(candidate)
                data["coverage"]["reviewed_files"] = [path]
                result = review.validate_review(addon, data)
                self.assertFalse(result["passed"])
                self.assertEqual(result["accepted_findings"], [])
                self.assertIn("symlink", " ".join(result["rejected_findings"][0]["errors"]))
            result = review.validate_review(parent / "linked-addon", report())
            self.assertFalse(result["passed"])
            self.assertTrue(result["errors"])

    def test_counterevidence_can_be_supplied_but_truth_is_not_verified(self):
        with tempfile.TemporaryDirectory() as temporary:
            addon = Path(temporary)
            (addon / "default.py").write_text(
                "value = 'private'\nvalue = '[redacted]'\nprint(value)\n", encoding="utf-8"
            )
            candidate = copy.deepcopy(PRIVACY_CANDIDATE)
            candidate.update(path="default.py", line=3, quote="print(value)",
                             related_evidence=[
                                 {"path": "default.py", "line": 2,
                                  "quote": "value = '[redacted]'", "role": "counterevidence"},
                             ])
            data = report(candidate)
            data["coverage"]["reviewed_files"] = ["default.py"]
            result = review.validate_review(addon, data)
            self.assertTrue(result["passed"], result)
            self.assertEqual(result["accepted_findings"][0]["semantic_verification"],
                             "not-performed")
            self.assertEqual(result["accepted_findings"][0]["related_evidence"][0]["role"],
                             "counterevidence")

    def test_crlf_and_substring_quotes_preserve_actual_line_coordinates(self):
        with tempfile.TemporaryDirectory() as temporary:
            addon = Path(temporary)
            (addon / "default.py").write_bytes(b"first\r\n    print('private')\r\n")
            candidate = copy.deepcopy(PRIVACY_CANDIDATE)
            candidate.update(line=2, quote="print('private')", related_evidence=[])
            data = report(candidate)
            data["coverage"]["reviewed_files"] = ["default.py"]
            self.assertTrue(review.validate_review(addon, data)["passed"])

    def test_empty_non_utf8_binary_and_oversized_sources_cannot_anchor_findings(self):
        with tempfile.TemporaryDirectory() as temporary:
            addon = Path(temporary)
            for content in (b"", b"x\xff", b"x\x00", b"x" * 65):
                with self.subTest(content=content[:8]):
                    (addon / "default.py").write_bytes(content)
                    candidate = copy.deepcopy(PRIVACY_CANDIDATE)
                    candidate.update(line=1, quote="x", related_evidence=[])
                    data = report(candidate)
                    data["coverage"]["reviewed_files"] = ["default.py"]
                    with patch.object(review, "MAX_SOURCE_BYTES", 64):
                        result = review.validate_review(addon, data)
                    self.assertFalse(result["passed"])
                    self.assertEqual(result["accepted_findings"], [])


class ReviewContextTests(unittest.TestCase):
    def test_fixture_context_numbers_python_manifest_and_settings_without_running(self):
        before = {path: path.read_bytes() for path in REVIEW_ADDON.rglob("*") if path.is_file()}
        context = review.review_context(REVIEW_ADDON)
        files = {source["path"]: source for source in context["files"]}
        self.assertEqual(set(files), {"addon.xml", "default.py", "resources/settings.xml"})
        self.assertEqual(files["default.py"]["lines"][8]["line"], 9)
        self.assertIn("xbmc.log(supplied_secret", files["default.py"]["lines"][8]["text"])
        self.assertTrue(context["coverage"]["complete"])
        self.assertEqual(context["coverage"]["network_access"], "not-performed")
        self.assertEqual(context["report_schema"]["properties"]["model_findings"]["items"]
                         ["properties"]["category"]["enum"], list(review.CATEGORIES))
        self.assertEqual(before, {path: path.read_bytes() for path in before})

    def test_context_budgets_and_omitted_material_are_visible(self):
        with tempfile.TemporaryDirectory() as temporary:
            addon = Path(temporary)
            (addon / "addon.xml").write_text("<addon/>\n", encoding="utf-8")
            (addon / "default.py").write_text("one\ntwo\nthree\nfour\n", encoding="utf-8")
            (addon / "other.py").write_text("raise RuntimeError('do not import')\n",
                                           encoding="utf-8")
            with patch.object(review, "MAX_CONTEXT_FILES", 2), \
                 patch.object(review, "MAX_FILE_LINES", 2):
                context = review.review_context(addon)
            self.assertFalse(context["coverage"]["complete"])
            self.assertEqual([source["path"] for source in context["files"]],
                             ["addon.xml", "default.py"])
            self.assertEqual(context["files"][1]["lines"],
                             [{"line": 1, "text": "one"}, {"line": 2, "text": "two"}])
            self.assertEqual({item["reason"] for item in context["coverage"]["omitted_files"]},
                             {"source-truncated", "context-budget"})

    def test_context_skips_symlinks_and_excluded_trees_and_lists_settings_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            addon = Path(temporary)
            (addon / ".venv").mkdir()
            (addon / ".venv" / "secret.py").write_text("outside scope\n", encoding="utf-8")
            (addon / "resources" / "settings").mkdir(parents=True)
            (addon / "resources" / "settings" / "general.xml").write_text(
                "<settings/>\n", encoding="utf-8"
            )
            (addon / "unsafe.py").write_text("raise RuntimeError('not executed')\n",
                                            encoding="utf-8")
            try:
                (addon / "linked.py").symlink_to(addon / "unsafe.py")
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable on this platform")
            context = review.review_context(addon)
            self.assertEqual({source["path"] for source in context["files"]},
                             {"unsafe.py", "resources/settings/general.xml"})
            self.assertIn(".venv", context["coverage"]["excluded_directories"])
            self.assertFalse(context["coverage"]["complete"])
            self.assertIn("symlink-excluded",
                          [item["reason"] for item in context["coverage"]["omitted_files"]])

    def test_total_bytes_scan_and_long_line_limits_are_reported(self):
        with tempfile.TemporaryDirectory() as temporary:
            addon = Path(temporary)
            (addon / "default.py").write_text("a" * 25 + "\nsecond\n", encoding="utf-8")
            with patch.object(review, "MAX_LINE_CHARS", 20):
                context = review.review_context(addon)
            self.assertEqual(context["files"][0]["lines"], [{"line": 2, "text": "second"}])
            self.assertFalse(context["coverage"]["complete"])
            with patch.object(review, "MAX_CONTEXT_BYTES", 4):
                context = review.review_context(addon)
            self.assertFalse(context["coverage"]["complete"])
            self.assertEqual(context["files"][0]["lines"], [])
            (addon / "other.py").write_text("text\n", encoding="utf-8")
            with patch.object(review, "MAX_SCAN_ENTRIES", 1):
                context = review.review_context(addon)
            self.assertFalse(context["coverage"]["complete"])
            self.assertIn("scan-entry-limit",
                          [item["reason"] for item in context["coverage"]["omitted_files"]])

    def test_missing_manifest_prevents_a_complete_context_claim(self):
        with tempfile.TemporaryDirectory() as temporary:
            context = review.review_context(Path(temporary))
            self.assertEqual(context["files"], [])
            self.assertFalse(context["coverage"]["complete"])
            self.assertEqual(context["coverage"]["omitted_files"],
                             [{"path": "addon.xml", "reason": "required-manifest-unavailable"}])

    def test_schema_is_fresh_and_context_requires_a_real_directory(self):
        schema = review.report_schema()
        schema["properties"]["model_findings"]["items"]["properties"]["category"]["enum"].clear()
        self.assertTrue(review.report_schema()["properties"]["model_findings"]["items"]
                        ["properties"]["category"]["enum"])
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "missing"
            with self.assertRaises(review.EvidenceError):
                review.review_context(path)


if __name__ == "__main__":
    unittest.main()
