"""Offline evaluation regressions using synthetic artifacts and owned dummy processes.

No private trials/configuration, model calls, or Kodi execution are used. Unix
process coverage is exercised in Linux/WSL; it does not qualify native Windows.
"""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def load_module(name):
    spec = importlib.util.spec_from_file_location(
        f"toolkit_evaluation_test_{name}", ROOT / "evaluation" / f"{name}.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EvaluationTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        temporary = tempfile.TemporaryDirectory(prefix="kodi-evaluation-import-test-")
        cls.addClassCleanup(temporary.cleanup)
        workspace = Path(temporary.name)
        # run.py loads token files at import. Its home and private root must be
        # synthetic before importing it, not merely patched before calling run.
        with patch.object(Path, "home", return_value=workspace / "home"), \
                patch.dict(os.environ, {"KODI_EVAL_PRIVATE": str(workspace / "private")}):
            cls.processes = load_module("processes")
            cls.assessor = load_module("assess")
            with patch.dict(sys.modules, {"processes": cls.processes}):
                cls.runner = load_module("run")
        if cls.runner.TOKENS:
            raise AssertionError("Synthetic import must not discover token files")

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="kodi-evaluation-test-")
        self.addCleanup(temporary.cleanup)
        self.work = Path(temporary.name)
        self.private = self.work / "private"

    def make_run(self, source="pass\n", task="explain", events=None,
                 skill_enabled=False, skill_loaded=None, label="synthetic-run"):
        directory = self.private / "runs" / label
        addon = directory / "project/fixtures/script.toolkit.sample"
        addon.mkdir(parents=True)
        (addon / "default.py").write_text(source, encoding="utf-8")
        summary = {"label": label, "task": task, "model": "dummy/offline",
                   "skill_enabled": skill_enabled, "skill_loaded": skill_loaded or [],
                   "exit_code": 0, "termination": {"timed_out": False, "reason": None}}
        (directory / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
        (directory / "events.json").write_text(json.dumps(events or []), encoding="utf-8")
        return directory, addon

    def assess_run(self, label="synthetic-run"):
        with patch.object(self.assessor, "PRIVATE", self.private), \
                patch.object(self.assessor, "validate", return_value={"passed": True}) as validate:
            result = self.assessor.assess(label)
        return result, validate

    @staticmethod
    def tool_event(tool, status="completed", inputs=None, process_exit=0):
        return {"type": "tool_use", "elapsed_seconds": 0.1,
                "part": {"tool": tool, "state": {
                    "status": status, "input": inputs or {},
                    "output": json.dumps({"process_exit": process_exit,
                                          "output": json.dumps({"passed": process_exit == 0})}),
                }}}


class AssessmentTests(EvaluationTestCase):
    def original_source(self):
        return (ROOT / "fixtures/invalid-api/script.toolkit.sample/default.py").read_text()

    def repair_events(self):
        return [self.tool_event("kodi_validate", process_exit=1),
                self.tool_event("edit", inputs={"filePath": "fixtures/script.toolkit.sample/default.py"}),
                self.tool_event("kodi_validate")]

    def check_repair(self, source, expected):
        directory, addon = self.make_run(source, task="api-fix-contract", events=self.repair_events())
        result, validation = self.assess_run()
        self.assertIs(result["automatic_gates"]["typed_log_level"], expected)
        self.assertTrue(result["automatic_gates"]["independent_static_pass"])
        self.assertTrue(result["automatic_gates"]["agent_validation_before_and_after"])
        validation.assert_called_once_with(addon, cache=self.assessor.ROOT / ".local/index-cache")
        persisted = json.loads((directory / "assessment.json").read_text())
        self.assertEqual(persisted["automatic_gates"], result["automatic_gates"])
        self.assertEqual(result["human_verdict"], "not-reviewed")

    def test_exact_logging_repair_passes(self):
        self.check_repair(self.original_source().replace('"info"', "xbmc.LOGINFO"), True)

    def test_comment_only_changes_do_not_break_exact_logging_repair(self):
        self.check_repair("# Synthetic formatting change\n" +
                          self.original_source().replace('"info"', "xbmc.LOGINFO"), True)

    def test_dead_code_loginfo_does_not_replace_the_intended_log(self):
        source = self.original_source().replace(
            'xbmc.log("Toolkit sample ready", "info")',
            'pass\n    if False:\n        xbmc.log("Toolkit sample ready", xbmc.LOGINFO)',
        )
        self.check_repair(source, False)

    def test_deleting_the_intended_logging_call_fails(self):
        source = self.original_source().replace('xbmc.log("Toolkit sample ready", "info")', "pass")
        self.check_repair(source, False)

    def test_unrelated_loginfo_call_does_not_repair_the_original_level(self):
        self.check_repair(self.original_source() +
                          '\nif False:\n    xbmc.log("unrelated", xbmc.LOGINFO)\n', False)

    def test_independent_validation_does_not_substitute_for_agent_before_and_after(self):
        source = self.original_source().replace('"info"', "xbmc.LOGINFO")
        self.make_run(source, task="api-fix-contract", events=self.repair_events()[1:])
        result, _ = self.assess_run()
        self.assertTrue(result["automatic_gates"]["typed_log_level"])
        self.assertTrue(result["automatic_gates"]["independent_static_pass"])
        self.assertFalse(result["automatic_gates"]["agent_validation_before_and_after"])

    def test_failed_initial_skill_then_success_is_not_loaded_first(self):
        skill = self.assessor.TASKS["explain"]["skill"]
        self.make_run(events=[self.tool_event("skill", "error", {"name": skill}),
                              self.tool_event("read"),
                              self.tool_event("skill", inputs={"name": skill})],
                      skill_enabled=True, skill_loaded=[skill])
        result, validation = self.assess_run()
        self.assertTrue(result["automatic_gates"]["skill_actually_loaded"])
        self.assertFalse(result["automatic_gates"]["skill_loaded_first"])
        validation.assert_not_called()

    def test_completed_expected_skill_first_passes(self):
        skill = self.assessor.TASKS["explain"]["skill"]
        self.make_run(events=[self.tool_event("skill", inputs={"name": skill}),
                              self.tool_event("read")],
                      skill_enabled=True, skill_loaded=[skill])
        result, _ = self.assess_run()
        self.assertTrue(result["automatic_gates"]["skill_actually_loaded"])
        self.assertTrue(result["automatic_gates"]["skill_loaded_first"])

    def test_wrong_skill_first_then_expected_skill_does_not_pass_order_gate(self):
        skill = self.assessor.TASKS["explain"]["skill"]
        self.make_run(events=[self.tool_event("skill", inputs={"name": "unrelated-skill"}),
                              self.tool_event("skill", inputs={"name": skill})],
                      skill_enabled=True, skill_loaded=["unrelated-skill", skill])
        result, _ = self.assess_run()
        self.assertTrue(result["automatic_gates"]["skill_actually_loaded"])
        self.assertFalse(result["automatic_gates"]["skill_loaded_first"])

    @staticmethod
    def review_report():
        return {"model_findings": [], "deterministic_findings": [],
                "coverage": {"scope": "Synthetic source only", "complete": False,
                             "reviewed_files": ["default.py"]},
                "limitations": ["Offline test; no semantic or runtime verification."]}

    def test_raw_final_json_passes_extraction_and_strict_format(self):
        report = self.review_report()
        text = json.dumps(report)
        self.assertEqual(self.assessor.final_object(text), report)
        self.make_run(task="review", events=[{"type": "text", "part": {"text": text}}])
        result, validation = self.assess_run()
        self.assertTrue(result["automatic_gates"]["complete_json_report"])
        self.assertTrue(result["automatic_gates"]["strict_final_json_only"])
        self.assertTrue(result["automatic_gates"]["evidence_contract"])
        self.assertEqual(result["human_verdict"], "not-reviewed")
        validation.assert_not_called()

    def test_one_fenced_json_is_extracted_but_is_not_strict_final_json(self):
        report = self.review_report()
        text = "Synthetic preamble\n```json\n" + json.dumps(report) + "\n```\nSynthetic suffix"
        self.assertEqual(self.assessor.final_object(text), report)
        self.make_run(task="review", events=[{"type": "text", "part": {"text": text}}])
        result, _ = self.assess_run()
        self.assertTrue(result["automatic_gates"]["complete_json_report"])
        self.assertFalse(result["automatic_gates"]["strict_final_json_only"])
        self.assertTrue(result["automatic_gates"]["evidence_contract"])

    def test_truncated_or_ambiguous_json_is_not_recovered_as_a_complete_report(self):
        text = json.dumps(self.review_report())
        candidates = [text[:-1], "```json\n" + text, "```json\n" + text[:-1] + "\n```",
                      "```", "[]", "```json\n" + text + "\n```\n```json\n" + text + "\n```"]
        for candidate in candidates:
            with self.subTest(text=candidate):
                self.assertIsNone(self.assessor.final_object(candidate))

    def test_truncated_final_json_is_recorded_as_failed_extraction(self):
        text = json.dumps(self.review_report())[:-1]
        directory, _ = self.make_run(task="review", events=[{"type": "text", "part": {"text": text}}])
        result, _ = self.assess_run()
        self.assertFalse(result["automatic_gates"]["complete_json_report"])
        self.assertFalse(result["automatic_gates"]["strict_final_json_only"])
        self.assertFalse((directory / "agent-review.json").exists())
        self.assertEqual(json.loads((directory / "assessment.json").read_text())["final_text"], text)


class OutputAwareAssessmentTests(EvaluationTestCase):
    @staticmethod
    def validation_report(passed=True, branch="nexus"):
        checks = {name: {"status": "passed", "passed": True, "errors": []}
                  for name in ("syntax", "manifest", "paths", "package", "types", "official_checker")}
        checks["official_checker"].update(completed=True, infrastructure_errors=[])
        if not passed:
            checks["types"] = {"status": "failed", "passed": False,
                "errors": ['default.py:7: error: Argument 2 to "log" has incompatible type "str"; expected "int"  [arg-type]']}
        return {"passed": passed, "returncode": 0 if passed else 1, "branch": branch, "checks": checks}

    def domain_event(self, tool, result, process_exit=0, inputs=None):
        event = self.tool_event(tool, process_exit=process_exit, inputs=inputs)
        event["part"]["state"]["output"] = json.dumps({"process_exit": process_exit, "output": json.dumps(result)})
        return event

    def repair_assessment(self, before=None, after=None, task="api-fix-contract"):
        before = before or self.domain_event("kodi_validate", self.validation_report(False), 1)
        after = after or self.domain_event("kodi_validate", self.validation_report())
        source = (ROOT / "fixtures/invalid-api/script.toolkit.sample/default.py").read_text().replace('"info"', "xbmc.LOGINFO")
        events = [before, self.tool_event("edit"), after,
                  {"type": "text", "part": {"text": "Repaired; observed static stages pass. Runtime not tested."}},
                  {"type": "step_finish", "part": {"reason": "stop"}}]
        self.make_run(source, task=task, events=events)
        result, _ = self.assess_run()
        return result

    def test_real_pre_failure_and_complete_post_check_pass_new_gates(self):
        result = self.repair_assessment()
        for gate in ("agent_validation_before_and_after", "agent_reproduced_type_defect_before_edit",
                     "agent_post_edit_validation_passed", "agent_validation_target_consistent", "final_response_complete"):
            self.assertTrue(result["automatic_gates"][gate], gate)
        self.assertEqual(result["human_verdict"], "not-reviewed")

    def test_completed_tool_failures_do_not_pass_output_aware_checks(self):
        failed = self.domain_event("kodi_validate", {"passed": False}, 2)
        result = self.repair_assessment(failed, failed)
        self.assertTrue(result["automatic_gates"]["agent_validation_before_and_after"], "Legacy event-order gate is preserved")
        self.assertFalse(result["automatic_gates"]["agent_reproduced_type_defect_before_edit"])
        self.assertFalse(result["automatic_gates"]["agent_post_edit_validation_passed"])
        self.assertEqual(len(result["operational_failures"]), 2)

    def test_stub_branch_error_is_not_reproduced_source_defect(self):
        before = self.validation_report(False, "omega")
        before["checks"]["types"] = {"status": "error", "passed": False,
                                      "errors": ["Kodistubs 20.0.1 does not match branch omega"]}
        result = self.repair_assessment(self.domain_event("kodi_validate", before, 1))
        self.assertTrue(result["automatic_gates"]["agent_validation_before_and_after"])
        self.assertFalse(result["automatic_gates"]["agent_reproduced_type_defect_before_edit"])
        self.assertFalse(result["automatic_gates"]["agent_validation_target_consistent"])
        self.assertEqual(result["stage_operational_failures"][0]["stage"], "types")

    def test_unrelated_type_error_is_not_the_expected_defect(self):
        before = self.validation_report(False)
        before["checks"]["types"]["errors"] = ["unrelated.py:1: undefined name"]
        result = self.repair_assessment(self.domain_event("kodi_validate", before, 1))
        self.assertFalse(result["automatic_gates"]["agent_reproduced_type_defect_before_edit"])

    def test_post_pass_requires_every_stage_and_official_completion(self):
        for field in ("types", "official_checker", "missing"):
            with self.subTest(field=field):
                label = "post-" + field
                after = self.validation_report()
                if field == "types":
                    after["checks"][field]["status"] = "skipped"
                elif field == "official_checker":
                    after["checks"][field]["completed"] = False
                else:
                    del after["checks"]["package"]
                source = (ROOT / "fixtures/invalid-api/script.toolkit.sample/default.py").read_text().replace('"info"', "xbmc.LOGINFO")
                self.make_run(source, task="api-fix-contract", events=[
                    self.domain_event("kodi_validate", self.validation_report(False), 1), self.tool_event("edit"),
                    self.domain_event("kodi_validate", after)], label=label)
                with patch.object(self.assessor, "PRIVATE", self.private), patch.object(self.assessor, "validate", return_value={"passed": True}):
                    result = self.assessor.assess(label)
                self.assertFalse(result["automatic_gates"]["agent_post_edit_validation_passed"])

    def test_post_report_pass_with_nonzero_process_exit_is_not_success(self):
        result = self.repair_assessment(after=self.domain_event("kodi_validate", self.validation_report(), 1))
        self.assertFalse(result["automatic_gates"]["agent_post_edit_validation_passed"])

    def test_explicit_nexus_target_cannot_be_validated_on_another_branch(self):
        result = self.repair_assessment(
            self.domain_event("kodi_validate", self.validation_report(False, "omega"), 1),
            self.domain_event("kodi_validate", self.validation_report(True, "omega")), task="api-fix-nexus")
        self.assertTrue(result["automatic_gates"]["agent_post_edit_validation_passed"])
        self.assertFalse(result["automatic_gates"]["agent_validation_target_consistent"])

    def test_missing_or_length_limited_final_response_fails_completion(self):
        for index, events in enumerate(([],
            [{"type": "text", "part": {"text": "Partial response"}}, {"type": "step_finish", "part": {"reason": "length"}}],
            [{"type": "text", "part": {"text": "CRITICAL - MAXIMUM STEPS REACHED"}}, {"type": "step_finish", "part": {"reason": "stop"}}],
            [{"type": "text", "part": {"text": "No finish event"}}])):
            label = "incomplete-" + str(index)
            self.make_run(events=events, label=label)
            result, _ = self.assess_run(label)
            self.assertFalse(result["automatic_gates"]["final_response_complete"])

    def test_complete_final_response_does_not_hide_execution_timeout(self):
        directory, _ = self.make_run(events=[{"type": "text", "part": {"text": "Observed blocker."}},
                                           {"type": "step_finish", "part": {"reason": "stop"}}])
        summary = json.loads((directory / "summary.json").read_text())
        summary["termination"] = {"timed_out": True, "reason": "trial timeout"}
        (directory / "summary.json").write_text(json.dumps(summary))
        result, _ = self.assess_run()
        self.assertFalse(result["automatic_gates"]["execution_completed"])
        self.assertTrue(result["automatic_gates"]["final_response_complete"])

    def test_malformed_composition_envelopes_are_recorded_without_crashing(self):
        for index, output in enumerate(("truncated{", "[]", "{}", json.dumps({"process_exit": 0, "output": "{broken"}),
                                        json.dumps({"process_exit": 0, "output": []}))):
            label = "malformed-" + str(index)
            event = self.tool_event("kodi_review", inputs={"operation": "compose", "report_json": json.dumps(AssessmentTests.review_report())})
            event["part"]["state"]["output"] = output
            directory, _ = self.make_run(task="review-composed", events=[event], label=label)
            result, _ = self.assess_run(label)
            self.assertTrue(result["automatic_gates"]["agent_composition_called"])
            self.assertFalse(result["automatic_gates"]["composition_passed"])
            self.assertTrue(result["composition_errors"])
            self.assertTrue((directory / "assessment.json").exists())
            self.assertFalse((directory / "composed-review.json").exists())

    def test_composed_static_and_contract_results_remain_separate_and_unreviewed(self):
        result = {"passed": False, "static_passed": True, "contract_passed": False,
                  "semantic_verification": "human-required", "deterministic_findings": [],
                  "model_findings": [{"title": "Unsupported candidate", "severity": "blocker"}]}
        self.make_run(task="review-composed", events=[self.domain_event("kodi_review", result, 1, {"operation": "compose", "report_json": json.dumps(AssessmentTests.review_report())})])
        assessed, _ = self.assess_run()
        self.assertFalse(assessed["automatic_gates"]["composition_passed"])
        self.assertTrue(assessed["automatic_gates"]["composition_static_passed"])
        self.assertFalse(assessed["automatic_gates"]["composition_contract_passed"])
        self.assertEqual(assessed["review_semantics"]["verdict"], "not-reviewed")
        self.assertEqual(assessed["contextual_candidates"][0]["severity"], "blocker")

    def test_missing_path_repeats_and_schema_errors_are_observations(self):
        missing = self.tool_event("read", "error", {"filePath": "missing.py"})
        missing["part"]["state"]["error"] = "File not found: missing.py"
        schema = self.tool_event("skill", "error", {"skill": "bad argument"})
        schema["part"]["state"]["error"] = "Invalid arguments: name is required"
        self.make_run(events=[missing, missing, schema, self.tool_event("read", inputs={"filePath": "real.py"})])
        result, _ = self.assess_run()
        metrics = result["metrics"]
        self.assertEqual(metrics["missing_path_errors"], 2)
        self.assertEqual(metrics["repeated_missing_path_errors"], 1)
        self.assertEqual(metrics["schema_argument_errors"], 1)
        self.assertEqual(metrics["identical_input_repeats"], 1)
        self.assertEqual(metrics["path_error_followed_by_completed_call"], 2)
        self.assertEqual(result["human_verdict"], "not-reviewed")

    def test_final_report_must_match_the_report_actually_verified(self):
        report = AssessmentTests.review_report()
        verified = self.domain_event("kodi_review", {"passed": True}, inputs={"operation": "verify", "report_json": json.dumps(report)})
        changed = dict(report, limitations=["Changed after verification"])
        self.make_run(task="review", events=[verified, {"type": "text", "part": {"text": json.dumps(changed)}}])
        result, _ = self.assess_run()
        self.assertTrue(result["automatic_gates"]["evidence_contract"])
        self.assertFalse(result["automatic_gates"]["agent_final_report_verified"])


    def test_unrelated_task_does_not_require_loading_a_kodi_skill(self):
        self.make_run(task="generic", skill_enabled=True, events=[
            {"type": "text", "part": {"text": "2+2 equals 4."}},
            {"type": "step_finish", "part": {"reason": "stop"}}])
        result, _ = self.assess_run()
        self.assertTrue(result["automatic_gates"]["no_tools_or_skills_used"])
        self.assertTrue(result["automatic_gates"]["answer_contains_four"])
        self.assertNotIn("skill_actually_loaded", result["automatic_gates"])

    def test_missing_manifest_discovery_is_observed_without_fabricated_success(self):
        event = self.domain_event("kodi_validate", {"passed": False, "addons": [],
            "errors": ["No existing addon.xml found in the bounded scan"]}, 1, {"operation": "discover"})
        self.make_run(task="missing-manifest", events=[event])
        result, _ = self.assess_run()
        self.assertTrue(result["automatic_gates"]["fixture_manifest_absent"])
        self.assertTrue(result["automatic_gates"]["missing_manifest_observed"])
        self.assertTrue(result["automatic_gates"]["no_edit_attempted"])

    def test_checker_failure_is_measured_without_claiming_a_clean_validation(self):
        validation = self.validation_report()
        validation["passed"] = False
        validation["checks"]["official_checker"].update(status="error", passed=False, completed=False,
            infrastructure_errors=["Explicit complete index cache required"])
        self.make_run(task="checker-failure", events=[self.domain_event("kodi_validate", validation, 2)])
        result, _ = self.assess_run()
        self.assertTrue(result["automatic_gates"]["checker_infrastructure_failure_observed"])
        self.assertTrue(result["automatic_gates"]["single_validation_attempt"])
        self.assertTrue(result["stage_operational_failures"])
        self.assertEqual(result["operational_failures"][0]["process_exit"], 2)
        self.assertFalse(self.assessor.validation_passed(validation))

    def test_clean_review_uses_separate_composition_gates(self):
        self.make_run(task="review-clean", events=[self.domain_event("kodi_review", {
            "passed": True, "static_passed": True, "contract_passed": True,
            "semantic_verification": "human-required", "model_findings": []}, inputs={"operation": "compose", "report_json": json.dumps(AssessmentTests.review_report())})])
        result, _ = self.assess_run()
        self.assertTrue(result["automatic_gates"]["composition_static_passed"])
        self.assertTrue(result["automatic_gates"]["composition_contract_passed"])
        self.assertEqual(result["human_verdict"], "not-reviewed")


    def test_real_file_outside_disposable_project_is_an_isolation_failure(self):
        source_file = ROOT / "fixtures/valid/script.toolkit.sample/default.py"
        self.assertTrue(source_file.is_file())
        self.make_run(events=[self.tool_event("read", inputs={"filePath": str(source_file)})])
        result, _ = self.assess_run()
        self.assertFalse(result["automatic_gates"]["native_file_paths_within_trial_project"])
        self.assertEqual(result["native_paths_outside_trial_project"][0]["path"], str(source_file))
        self.assertEqual(result["metrics"]["missing_path_errors"], 0,
                         "An actual external file can be read successfully despite invalid trial isolation")

    def test_native_paths_and_copied_skill_references_inside_project_pass_isolation(self):
        project = self.private / "runs/synthetic-run/project"
        self.make_run(task="wrong-root", events=[
            self.tool_event("read", inputs={"filePath": str(project / ".agents/skills/kodi-addon-validation/SKILL.md")}),
            self.tool_event("read", inputs={"filePath": "../fixtures/script.toolkit.sample/default.py"})])
        result, _ = self.assess_run()
        self.assertTrue(result["automatic_gates"]["native_file_paths_within_trial_project"])
        self.assertEqual(result["native_paths_outside_trial_project"], [])

    def test_relative_parent_traversal_outside_trial_is_recorded(self):
        self.make_run(events=[self.tool_event("read", inputs={"filePath": "../outside.txt"})])
        result, _ = self.assess_run()
        self.assertFalse(result["automatic_gates"]["native_file_paths_within_trial_project"])


    def test_final_fixture_path_fabrication_is_observed_despite_correct_tool_paths(self):
        directory, addon = self.make_run(events=[
            self.tool_event("read", inputs={"filePath": "fixtures/script.toolkit.sample/default.py"}),
            {"type": "text", "part": {"text": "Validated `fixtures/script.toolkit-sample/default.py:7`."}}])
        result, _ = self.assess_run()
        self.assertTrue(result["automatic_gates"]["native_file_paths_within_trial_project"])
        self.assertFalse(result["automatic_gates"]["explicit_final_fixture_paths_verified"])
        self.assertEqual(result["metrics"]["unverified_final_fixture_citations"], 1)
        self.assertEqual(result["final_fixture_path_mentions"][0]["path"], "fixtures/script.toolkit-sample/default.py")
        self.assertTrue((addon / "default.py").is_file())

    def test_existing_final_paths_allow_spaces_punctuation_and_line_references(self):
        directory, addon = self.make_run()
        (addon / "source file.py").write_text("pass\n")
        text = "Files: `fixtures/script.toolkit.sample/default.py:7,`, `fixtures/script.toolkit.sample/source file.py#L1-L2`."
        mentions = self.assessor.final_fixture_paths(text, directory / "project")
        self.assertEqual(len(mentions), 2)
        self.assertTrue(all(record["verified"] for record in mentions), mentions)

    def test_stale_path_and_example_mentions_are_excluded_from_artifact_claims(self):
        self.make_run(events=[{"type": "text", "part": {"text":
            "Stale `fixtures/script.toolkit-sample` was not found; actual source is `fixtures/script.toolkit.sample/default.py:1`.\n"
            "Example: `fixtures/hypothetical-addon`."}}])
        result, _ = self.assess_run()
        self.assertTrue(result["automatic_gates"]["explicit_final_fixture_paths_verified"])
        self.assertEqual([record["role"] for record in result["final_fixture_path_mentions"]],
                         ["reported_missing_or_stale", "artifact_citation", "example"])
        self.assertFalse(result["final_fixture_path_mentions"][0]["verified"])

    def test_final_citation_cannot_escape_project_or_follow_external_link(self):
        directory, addon = self.make_run()
        outside = directory / "outside.py"
        outside.write_text("pass\n")
        cases = ["`fixtures/../../outside.py`"]
        if os.name == "posix":
            (addon / "linked.py").symlink_to(outside)
            cases.append("`fixtures/script.toolkit.sample/linked.py`")
        for text in cases:
            with self.subTest(text=text):
                mentions = self.assessor.final_fixture_paths(text, directory / "project")
                self.assertEqual(len(mentions), 1)
                self.assertFalse(mentions[0]["verified"])

    def test_final_path_observation_does_not_claim_absolute_or_unquoted_coverage(self):
        directory, _ = self.make_run()
        mentions = self.assessor.final_fixture_paths(
            "`/tmp/nonexistent.py` and fixtures/nonexistent.py are outside this observation's scope.", directory / "project")
        self.assertEqual(mentions, [])


    @staticmethod
    def composed_result():
        return {"passed": True, "static_passed": True, "contract_passed": True,
                "semantic_verification": "human-required", "model_findings": []}

    def test_composition_accepts_structured_report_and_preserves_submitted_draft(self):
        draft = AssessmentTests.review_report()
        directory, _ = self.make_run(task="review-composed", events=[self.domain_event(
            "kodi_review", self.composed_result(), inputs={"operation": "compose", "report": draft})])
        result, _ = self.assess_run()
        self.assertTrue(result["automatic_gates"]["composition_submission_valid"])
        self.assertTrue(result["automatic_gates"]["composition_passed"])
        self.assertEqual(json.loads((directory / "agent-review-draft.json").read_text()), draft)
        self.assertEqual(json.loads((directory / "agent-review-submission.json").read_text()),
                         {"interface": "report", "submitted": draft})
        self.assertEqual(result["review_submissions"][0]["interface"], "report")

    def test_composition_legacy_json_remains_supported_without_rewriting_draft(self):
        original = json.dumps(AssessmentTests.review_report(), indent=3)
        directory, _ = self.make_run(task="review-composed", events=[self.domain_event(
            "kodi_review", self.composed_result(), inputs={"operation": "compose", "report_json": original})])
        result, _ = self.assess_run()
        self.assertTrue(result["automatic_gates"]["composition_submission_valid"])
        self.assertEqual((directory / "agent-review-draft.json").read_text(), original)
        self.assertEqual(result["review_submissions"][0]["interface"], "report_json")

    def test_malformed_structured_report_is_rejected_without_legacy_fallback(self):
        for index, malformed in enumerate((None, [], "{}", 7)):
            label = "bad-report-type-" + str(index)
            directory, _ = self.make_run(task="review-composed", label=label, events=[self.domain_event(
                "kodi_review", self.composed_result(), inputs={"operation": "compose", "report": malformed})])
            result, _ = self.assess_run(label)
            self.assertFalse(result["automatic_gates"]["composition_submission_valid"])
            self.assertFalse(result["automatic_gates"]["composition_passed"])
            self.assertIn("report must be an object", result["composition_errors"])
            self.assertFalse((directory / "agent-review-draft.json").exists())
            self.assertEqual(json.loads((directory / "agent-review-submission.json").read_text())["submitted"], malformed)

    def test_verification_rejects_dual_report_arguments(self):
        report = AssessmentTests.review_report()
        other = dict(report, limitations=["Other draft"])
        self.make_run(task="review", events=[self.domain_event("kodi_review", {"passed": True}, inputs={
            "operation": "verify", "report": report, "report_json": json.dumps(other)}),
            {"type": "text", "part": {"text": json.dumps(report)}}])
        result, _ = self.assess_run()
        self.assertFalse(result["automatic_gates"]["agent_final_report_verified"])
        self.assertEqual(result["review_submissions"][0]["error"], "Supply exactly one of report or report_json")

    def test_verification_rejects_present_malformed_structured_report(self):
        report = AssessmentTests.review_report()
        self.make_run(task="review", events=[self.domain_event("kodi_review", {"passed": True}, inputs={
            "operation": "verify", "report": []}),
            {"type": "text", "part": {"text": json.dumps(report)}}])
        result, _ = self.assess_run()
        self.assertFalse(result["automatic_gates"]["agent_final_report_verified"])
        self.assertEqual(result["review_submissions"][0]["error"], "report must be an object")

    def test_legacy_review_submission_must_decode_to_object(self):
        for value in ("[]", "null", "truncated{", None):
            report, error = self.assessor.submitted_report({"report_json": value})
            self.assertIsNone(report)
            self.assertTrue(error)


    def test_composition_rejects_dual_arguments_even_when_reports_are_identical(self):
        draft = AssessmentTests.review_report()
        directory, _ = self.make_run(task="review-composed", events=[self.domain_event(
            "kodi_review", self.composed_result(), inputs={"operation": "compose", "report": draft,
                                                         "report_json": json.dumps(draft)})])
        result, _ = self.assess_run()
        self.assertFalse(result["automatic_gates"]["composition_submission_valid"])
        self.assertFalse(result["automatic_gates"]["composition_passed"])
        self.assertIn("Supply exactly one of report or report_json", result["composition_errors"])
        self.assertFalse((directory / "agent-review-draft.json").exists())


class LabelTests(EvaluationTestCase):
    def test_unsafe_labels_fail_before_creating_output_or_starting_processes(self):
        labels = ["", ".", "..", "../escape", "a/../escape", "a/b", "..\\escape",
                  "a\\b", "/tmp/escape", "C:\\tmp\\escape", "C:/tmp/escape",
                  "a\n", "a\x00", "a" * 121]
        with patch.object(self.runner, "PRIVATE", self.private), \
                patch.object(self.assessor, "PRIVATE", self.private), \
                patch.object(Path, "mkdir", side_effect=AssertionError("Output directory creation")) as mkdir, \
                patch.object(Path, "read_text", side_effect=AssertionError("Unexpected artifact read")) as read, \
                patch.object(Path, "write_text", side_effect=AssertionError("Unexpected artifact write")) as write, \
                patch.object(self.runner.subprocess, "Popen", side_effect=AssertionError("Process launch")) as popen, \
                patch.object(self.runner.subprocess, "run", side_effect=AssertionError("Host command")) as command:
            for label in labels:
                with self.subTest(api="run", label=label), self.assertRaises(ValueError):
                    self.runner.run("coder", "validate", False, label)
                with self.subTest(api="assess", label=label), self.assertRaises(ValueError):
                    self.assessor.assess(label)
            for operation in (mkdir, read, write, popen, command):
                operation.assert_not_called()
        self.assertFalse(self.private.exists())
        self.assertEqual(list(self.work.iterdir()), [])


@unittest.skipUnless(os.name == "posix" and sys.platform.startswith("linux"),
                     "Linux/WSL /proc is required to distinguish running children from zombies")
class ProcessDeadlineTests(EvaluationTestCase):
    @staticmethod
    def child_is_running(pid):
        try:
            state = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0]
        except FileNotFoundError:
            return False
        # An orphan may await init's reap. A zombie has already stopped running.
        return state not in {"Z", "X"}

    def test_runner_deadline_kills_owned_group_after_parent_exits_and_records_timeout(self):
        toolkit = self.work / "toolkit"
        fixture = toolkit / "fixtures/valid/script.toolkit.sample"
        fixture.mkdir(parents=True)
        (fixture / "default.py").write_text("pass\n")
        (toolkit / "AGENTS.md").write_text("Offline dummy task only.\n")
        for name in (".opencode/tools/kodi_validate.ts", ".opencode/lib/dummy.ts"):
            target = toolkit / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("export {};\n")
        (toolkit / "evaluation").mkdir()
        for name in ("evaluation/run.py", "evaluation/tasks.json", "evaluation/processes.py",
                     "requirements-dev.lock"):
            (toolkit / name).write_text("{}\n")
        child_record = self.work / "dummy-child.json"
        child_source = (
            "import json, os, signal, sys, time\n"
            "from pathlib import Path\n"
            "signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
            "Path(sys.argv[1]).write_text(json.dumps({'pid': os.getpid(), 'pgid': os.getpgrp()}))\n"
            "print(json.dumps({'type': 'text', 'part': {'text': 'dummy child ready'}}), flush=True)\n"
            "while True: time.sleep(1)\n"
        )
        dummy = self.work / "dummy-opencode"
        dummy.write_text(
            f"#!{sys.executable}\n"
            "import os, subprocess, sys\n"
            f"child = subprocess.Popen([sys.executable, '-I', '-B', '-c', {child_source!r}, "
            "os.environ['KODI_EVALUATION_TEST_CHILD']])\n"
            "child.wait()\n"
        )
        dummy.chmod(0o700)
        launched = []
        outcomes = {}
        real_popen = subprocess.Popen

        def launch(*args, **kwargs):
            self.assertTrue(kwargs.get("start_new_session"), "Dummy must own a separate group")
            self.assertEqual(args[0][0], str(dummy), "Only the dummy executable may run")
            trial_project = self.private / "runs/dummy-deadline/project"
            expected_cwd = trial_project / "nested working directory"
            self.assertEqual(Path(kwargs["cwd"]), expected_cwd)
            self.assertEqual(kwargs["env"]["PWD"], str(expected_cwd), "Inherited PWD must not select the toolkit source instance")
            directory_option = args[0].index("--dir")
            self.assertEqual(args[0][directory_option + 1], str(expected_cwd), "OpenCode run must receive the explicit disposable directory")
            self.assertEqual(kwargs["env"].get("KODI_EVAL_PROJECT_ROOT"), str(trial_project), "Adapters must fail closed outside the disposable project")
            process = real_popen(*args, **kwargs)
            launched.append(process)
            return process

        def fake_git(command, **kwargs):
            self.assertEqual(command[:3], ["git", "init", "-q"])
            return subprocess.CompletedProcess(command, 0)

        def invoke():
            try:
                outcomes["result"] = self.runner.run("dummy/offline", "validate", False, "dummy-deadline", timeout=2)
            except BaseException as exc:
                outcomes["error"] = exc

        real_stop_tree = self.processes.stop_tree
        started = time.monotonic()
        worker = threading.Thread(target=invoke, daemon=True)
        with patch.object(self.runner, "ROOT", toolkit), \
                patch.object(self.runner, "PRIVATE", self.private), \
                patch.object(self.runner, "TASKS", {"validate": {"fixture": "valid", "prompt": "Offline dummy", "start_directory": "nested working directory"}}), \
                patch.object(Path, "home", return_value=self.work / "home"), \
                patch.dict(os.environ, {"OPENCODE_BIN": str(dummy),
                                        "KODI_EVALUATION_TEST_CHILD": str(child_record),
                                        "KODI_EVAL_SKILL_CATALOG": "relevant-only",
                                        "KODI_EVAL_TOOL_SCOPE": "standard"}), \
                patch.object(self.runner.subprocess, "Popen", side_effect=launch), \
                patch.object(self.runner.subprocess, "run", side_effect=fake_git), \
                patch.object(self.runner, "stop_tree", side_effect=lambda p: real_stop_tree(p, grace=0.15)), \
                patch.object(self.runner, "print", create=True):
            try:
                worker.start()
                worker.join(timeout=8)
                self.assertFalse(worker.is_alive(), "Deadline failed to close inherited child pipes")
                if "error" in outcomes:
                    raise outcomes["error"]
                self.assertLess(time.monotonic() - started, 8)
                self.assertEqual(len(launched), 1)
                child = json.loads(child_record.read_text())
                self.assertEqual(child["pgid"], launched[0].pid)
                self.assertNotEqual(child["pgid"], os.getpgrp())
                self.assertEqual(launched[0].returncode, -signal.SIGTERM,
                                 "Parent should exit before the ignoring child needs SIGKILL")
                until = time.monotonic() + 3
                while self.child_is_running(child["pid"]) and time.monotonic() < until:
                    time.sleep(0.02)
                self.assertFalse(self.child_is_running(child["pid"]), "Dummy child remains running")
                expected = {"timed_out": True, "reason": "trial timeout"}
                self.assertEqual(outcomes["result"]["termination"], expected)
                directory = self.private / "runs/dummy-deadline"
                self.assertEqual(json.loads((directory / "summary.json").read_text())["termination"], expected)
                events = json.loads((directory / "events.json").read_text())
                self.assertTrue(any(e.get("part", {}).get("text") == "dummy child ready" for e in events),
                                "Child must install its SIGTERM handler before the deadline")
            finally:
                # Clean only groups launched above, even when a regression makes
                # the assertion fail. No production or pre-existing PID is used.
                for process in launched:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    process.wait(timeout=3)
                worker.join(timeout=3)
                for process in launched:
                    for stream in (process.stdout, process.stderr):
                        if stream is not None:
                            stream.close()


if __name__ == "__main__":
    unittest.main()
