"""Independent artifact checks; human judgment remains separate from these gates."""
from pathlib import Path, PurePosixPath
import argparse
import ast
import json
import os
import re
import stat
from kodi_agent_toolkit.validate import validate
from kodi_agent_toolkit.review import validate_review

ROOT = Path(__file__).resolve().parents[1]
TASKS=json.loads((ROOT/"evaluation/tasks.json").read_text())
PRIVATE = Path(os.environ.get("KODI_EVAL_PRIVATE", str(Path.home()/".local/share/kodi-agent-toolkit/evaluation")))

def final_object(text):
    if not isinstance(text, str):
        return None
    text = text.strip()
    blocks = re.findall(r"```(?:json)?\s*(.*?)\s*```", text, re.S)
    if len(blocks) == 1:
        text = blocks[0].strip()
    try:
        value=json.loads(text)
        return value if isinstance(value,dict) else None
    except ValueError:
        return None

def tool_payload(state):
    """Decode adapter envelopes without mistaking completed events for checks."""
    try:
        envelope = state.get("output", "")
        if isinstance(envelope, str):
            envelope = json.loads(envelope)
        if not isinstance(envelope, dict):
            return None, None, "Tool envelope must be an object"
        result = envelope.get("output")
        if isinstance(result, str):
            result = json.loads(result)
        if not isinstance(result, dict):
            return envelope, None, "Tool result must be an object"
        return envelope, result, None
    except (ValueError, TypeError):
        return None, None, "Malformed tool JSON"


def submitted_report(inputs):
    """Accept exactly one report interface, matching the adapter contract."""
    if not isinstance(inputs, dict):
        return None, "Review tool inputs must be an object"
    if "report" in inputs and "report_json" in inputs:
        return None, "Supply exactly one of report or report_json"
    if "report" in inputs:
        value = inputs["report"]
        return (value, None) if isinstance(value, dict) else (None, "report must be an object")
    value = inputs.get("report_json")
    if not isinstance(value, str):
        return None, "report_json must be a JSON object string when report is absent"
    try:
        report = json.loads(value)
    except (ValueError, TypeError):
        return None, "Malformed report_json"
    return (report, None) if isinstance(report, dict) else (None, "report_json must decode to an object")


def validation_record(event):
    if event["part"].get("tool") != "kodi_validate" or event["part"]["state"].get("status") != "completed":
        return None
    envelope, result, error = tool_payload(event["part"]["state"])
    if error or envelope.get("timed_out") or envelope.get("process_exit") not in (0, 1):
        return None
    if result.get("passed") is True and envelope.get("process_exit") != 0:
        return None
    return result


def type_defect_reproduced(result):
    if not result or result.get("passed") is not False or not isinstance(result.get("checks"), dict):
        return False
    check = result["checks"].get("types")
    if not isinstance(check, dict) or check.get("status") != "failed" or check.get("passed") is not False:
        return False
    diagnostics = str(check.get("stdout", "")) + str(check.get("errors", ""))
    return bool(re.search(r'default\.py:\d+.*Argument 2 to "log" has incompatible type "str"; expected "int"', diagnostics))


def validation_passed(result):
    """A post-check needs actual stage coverage, including checker completion."""
    if not result or result.get("passed") is not True:
        return False
    checks = result.get("checks")
    if not isinstance(checks, dict):
        return False
    stages = ("syntax", "manifest", "paths", "package", "types", "official_checker")
    if not all(isinstance(checks.get(name), dict) and
               checks[name].get("passed") is True and checks[name].get("status") == "passed"
               for name in stages):
        return False
    official = checks["official_checker"]
    return official.get("completed") is True and not official.get("infrastructure_errors")


def trial_metrics(calls, events, final_text):
    """Counters are observations; repeated calls can be needed after an edit."""
    signatures = []
    missing = []
    schema_errors = 0
    for i, event in enumerate(calls):
        part = event["part"]
        state = part["state"]
        signature = json.dumps([part.get("tool"), state.get("input", {})], sort_keys=True)
        signatures.append(signature)
        error = str(state.get("error", ""))
        if state.get("status") == "error":
            if re.search(r"file not found|no such file|does not exist|enoent", error, re.I):
                missing.append((i, signature))
            if re.search(r"invalid arguments|invalid input|expected.*received|schemaerror|zod", error, re.I):
                schema_errors += 1
    missing_signatures = [signature for _, signature in missing]
    finishes = [event.get("part", {}).get("reason") for event in events if event.get("type") == "step_finish"]
    return {
        "missing_path_errors": len(missing),
        "repeated_missing_path_errors": len(missing_signatures) - len(set(missing_signatures)),
        "schema_argument_errors": schema_errors,
        "identical_input_repeats": len(signatures) - len(set(signatures)),
        "failed_tool_events": sum(event["part"]["state"].get("status") != "completed" for event in calls),
        "path_error_followed_by_completed_call": sum(any(
            call["part"]["state"].get("status") == "completed" for call in calls[i + 1:]) for i, _ in missing),
        "step_finish_reasons": finishes,
        "last_step_finish_reason": finishes[-1] if finishes else None,
        "step_cap_response": "MAXIMUM STEPS REACHED" in final_text.upper(),
        "final_words": len(final_text.split()),
        "tool_output_characters": sum(len(str(event["part"]["state"].get("output", ""))) for event in calls),
        "limits": ["Identical calls are not automatically unnecessary.",
                   "A completed call after a path error is not proof the failed operation was recovered.",
                   "Counters use emitted OpenCode events; hidden or missing events are unmeasured."],
    }


def final_fixture_paths(text, project):
    """Observe inline, project-relative fixture citations without semantic grading.

    Missing paths explicitly described as missing/stale, or as examples, are
    recorded separately. These local prose cues are conservative exclusions,
    not proof of task completion or correctness of arbitrary prose.
    """
    mentions = []
    for match in re.finditer(r"(?<!`)`([^`\r\n]+)`(?!`)", text):
        value = match.group(1).strip()
        if not value.startswith("fixtures/"):
            continue
        normalized = value.rstrip(".,;:!?")
        normalized = re.sub(r"(?:#L\d+(?:-L?\d+)?|:\d+(?:[-?]\d+)?(?::\d+)?)$", "", normalized)
        normalized = normalized.rstrip(".,;:!?").rstrip("/")
        start = max(text.rfind("\n", 0, match.start()), text.rfind(";", 0, match.start())) + 1
        endings = [position for separator in ("\n", ";")
                   if (position := text.find(separator, match.end())) >= 0]
        end = min(endings) if endings else len(text)
        clause = text[start:end]
        negative = bool(re.search(r"\b(?:stale|nonexistent|non-existent|missing|not found|does not exist|doesn't exist|old path|incorrect path|rejected path|invalid path|absent)\b", clause, re.I))
        example = bool(re.search(r"\b(?:example|hypothetical|illustrative)\b", clause, re.I))
        role = "reported_missing_or_stale" if negative else "example" if example else "artifact_citation"
        verified = False
        reason = None
        parts = PurePosixPath(normalized)
        if "\\" in normalized or ".." in parts.parts or ":" in normalized or any(ord(char) < 32 for char in normalized):
            reason = "unsafe fixture path"
        else:
            current = project
            try:
                # Never follow citation links or inspect a path outside project.
                for component in parts.parts:
                    current = current / component
                    info = current.lstat()
                    if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                        raise ValueError("linked citation path")
                verified = stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)
                if not verified:
                    reason = "citation is not a regular file or directory"
            except (OSError, ValueError, RuntimeError):
                reason = "citation unavailable or linked"
        mentions.append({"path": normalized, "quoted": value, "verified": verified,
                         "role": role, "reason": reason})
    return mentions


def assess(label, private=None, output_directory=None):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,119}", label):
        raise ValueError("Label must be one safe filename component")
    directory = (PRIVATE if private is None else private)/"runs"/label
    output_directory = directory if output_directory is None else Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)
    summary=json.loads((directory/"summary.json").read_text())
    events=json.loads((directory/"events.json").read_text())
    calls=[x for x in events if x.get("type")=="tool_use"]
    texts=[x["part"].get("text","") for x in events if x.get("type")=="text"]
    artifact={"summary":summary,"final_text":texts[-1] if texts else "",
              "automatic_gates":{},"human_verdict":"not-reviewed",
              "assessment_source_hashes":{str(f.relative_to(ROOT)):__import__("hashlib").sha256(f.read_bytes()).hexdigest() for f in [*(ROOT/"src/kodi_agent_toolkit").glob("*.py"), ROOT/"evaluation/assess.py"]},
              "limits":["Source-contract validation does not prove a finding is true.",
                        "Completed tool events may contain operational failures.",
                        "Token counts are cumulative SDK reports, not server billing or unique prompt size."]}
    metrics = trial_metrics(calls, events, artifact["final_text"])
    artifact["metrics"] = metrics
    submissions = []
    for index, event in enumerate(calls):
        state = event["part"]["state"]
        inputs = state.get("input", {})
        if event["part"].get("tool") != "kodi_review" or inputs.get("operation") not in {"verify", "compose"}:
            continue
        submitted, error = submitted_report(inputs)
        submissions.append({"call_index": index, "operation": inputs["operation"],
                            "interface": "report" if "report" in inputs else "report_json",
                            "valid_report_object": error is None, "error": error,
                            "tool_status": state.get("status")})
    artifact["review_submissions"] = submissions
    artifact["legacy_gates"] = ["typed_log_level", "agent_validation_before_and_after", "composition_passed"]
    artifact["automatic_gates"]["execution_completed"] = (summary.get("exit_code") == 0 and
        not summary.get("termination", {}).get("timed_out") and
        not summary.get("termination", {}).get("reason"))
    artifact["automatic_gates"]["final_response_complete"] = bool(artifact["final_text"].strip() and
        metrics["last_step_finish_reason"] == "stop" and not metrics["step_cap_response"])
    artifact["review_semantics"] = {"verdict": "not-reviewed", "criteria": [
        "Does the quoted source support the claimed mechanism and consequence?",
        "Is severity proportional to observed impact, with uncertainty retained?",
        "Are external Kodi requirements backed by an authoritative source?",
        "Are static results kept separate from runtime behavior?"]}
    operational=[]
    stage_failures=[]
    for event in calls:
        state=event["part"]["state"]
        try:
            value=json.loads(state.get("output",""))
        except (ValueError,TypeError):
            value = None
        if isinstance(value,dict) and value.get("process_exit",0) not in (0,1):
            operational.append({"tool":event["part"]["tool"],"process_exit":value["process_exit"]})
        envelope, payload, parse_error = tool_payload(state)
        if event["part"]["tool"] in {"kodi_validate", "kodi_review"}:
            if parse_error:
                stage_failures.append({"tool": event["part"]["tool"], "error": parse_error})
            elif isinstance(payload.get("checks"), dict):
                for name, check in payload["checks"].items():
                    if isinstance(check, dict) and (check.get("status") == "error" or
                            (name == "official_checker" and check.get("completed") is False)):
                        stage_failures.append({"tool": event["part"]["tool"], "stage": name,
                                               "status": check.get("status"), "errors": check.get("errors", [])})
    artifact["operational_failures"]=operational
    artifact["stage_operational_failures"]=stage_failures
    artifact["first_domain_action_seconds"]=next((x["elapsed_seconds"] for x in calls
           if x["part"]["state"].get("status")=="completed" and x["part"]["tool"] in {"kodi_validate","kodi_review","edit","apply_patch",
               "kodi_lab_target_list","kodi_lab_target_status","kodi_lab_inspect_ui_state"}),None)
    project = directory / "project"
    trial_cwd = project / TASKS.get(summary["task"], {}).get("start_directory", ".")
    outside_paths = []
    for event in calls:
        part = event["part"]
        if part.get("tool") not in {"read", "edit", "write"}:
            continue
        value = part["state"].get("input", {}).get("filePath")
        if not isinstance(value, str):
            continue
        candidate = Path(value)
        candidate = candidate if candidate.is_absolute() else trial_cwd / candidate
        try:
            candidate.resolve().relative_to(project.resolve())
        except (OSError, ValueError, RuntimeError):
            outside_paths.append({"tool": part["tool"], "path": value,
                                  "status": part["state"].get("status")})
    final_paths = final_fixture_paths(artifact["final_text"], project)
    unverified_citations = [record for record in final_paths
                            if record["role"] == "artifact_citation" and not record["verified"]]
    artifact["final_fixture_path_mentions"] = final_paths
    artifact["metrics"]["final_fixture_path_mentions"] = len(final_paths)
    artifact["metrics"]["unverified_final_fixture_citations"] = len(unverified_citations)
    artifact["automatic_gates"]["explicit_final_fixture_paths_verified"] = not unverified_citations
    artifact["limits"].append("Final-path observations cover inline backtick strings beginning fixtures/ only. Missing/stale/example prose cues are excluded conservatively; generic prose and absolute artifact paths are ungraded. This gate is not an overall semantic verdict.")
    artifact["native_paths_outside_trial_project"] = outside_paths
    artifact["automatic_gates"]["native_file_paths_within_trial_project"] = not outside_paths
    artifact["limits"].append("Native file-path isolation observes explicit read/edit/write filePath arguments; it does not prove all tools or processes stayed within the project.")
    addon=project/"fixtures/script.toolkit.sample"
    if summary["task"] in {"api-fix","api-fix-contract","api-fix-nexus"}:
        actual=(addon/"default.py").read_text()
        original=(ROOT/"fixtures/invalid-api/script.toolkit.sample/default.py").read_text()
        expected=original.replace('"info"', 'xbmc.LOGINFO')
        try:
            artifact["automatic_gates"]["typed_log_level"] = ast.dump(ast.parse(actual)) == ast.dump(ast.parse(expected))
        except SyntaxError:
            artifact["automatic_gates"]["typed_log_level"] = False
        edit_positions=[i for i,x in enumerate(calls) if x["part"]["tool"] in {"edit","write","apply_patch"} and x["part"]["state"]["status"]=="completed"]
        validation_positions=[i for i,x in enumerate(calls) if x["part"]["tool"]=="kodi_validate" and x["part"]["state"]["status"]=="completed"]
        artifact["automatic_gates"]["agent_validation_before_and_after"] = bool(edit_positions and any(i<min(edit_positions) for i in validation_positions) and any(i>max(edit_positions) for i in validation_positions))
        pre = [(i, validation_record(event)) for i, event in enumerate(calls)
               if edit_positions and i < min(edit_positions)]
        post = [(i, validation_record(event)) for i, event in enumerate(calls)
                if edit_positions and i > max(edit_positions)]
        reproduced = [result for _, result in pre if type_defect_reproduced(result)]
        verified = [result for _, result in post if validation_passed(result)]
        artifact["automatic_gates"]["agent_reproduced_type_defect_before_edit"] = bool(reproduced)
        artifact["automatic_gates"]["agent_post_edit_validation_passed"] = bool(verified)
        artifact["automatic_gates"]["agent_validation_target_consistent"] = any(
            before.get("branch") and before.get("branch") == after.get("branch") and
            (summary["task"] != "api-fix-nexus" or after.get("branch") == "nexus")
            for before in reproduced for after in verified)
        result=validate(addon,cache=ROOT/".local/index-cache")
        (output_directory/"independent-validation.json").write_text(json.dumps(result,indent=2))
        artifact["automatic_gates"]["independent_static_pass"]=result["passed"]
    if summary["task"] in {"review","review-bounded"}:
        report=final_object(artifact["final_text"])
        artifact["automatic_gates"]["complete_json_report"]=report is not None
        try:
            artifact["automatic_gates"]["strict_final_json_only"]=isinstance(json.loads(artifact["final_text"]),dict)
        except ValueError:
            artifact["automatic_gates"]["strict_final_json_only"]=False
        if report:
            checked=validate_review(addon,report)
            (output_directory/"review-contract.json").write_text(json.dumps(checked,indent=2))
            (output_directory/"agent-review.json").write_text(json.dumps(report,indent=2))
            artifact["automatic_gates"]["evidence_contract"]=checked["passed"]
            artifact["automatic_gates"]["anchored_privacy_candidate"]=any(
                f.get("category")=="privacy" and ((f.get("path")=="default.py" and f.get("line")==9) or any(e.get("path")=="default.py" and e.get("line")==9 for e in f.get("related_evidence",[])))
                for f in checked.get("accepted_findings",[]))
            final_verified = False
            for event in calls:
                state = event["part"]["state"]
                if event["part"]["tool"] != "kodi_review" or state.get("status") != "completed" or state.get("input", {}).get("operation") != "verify":
                    continue
                envelope, verification, error = tool_payload(state)
                draft, submission_error = submitted_report(state.get("input", {}))
                if not error and not submission_error and envelope.get("process_exit") == 0 and verification.get("passed") is True and draft == report:
                    final_verified = True
            artifact["automatic_gates"]["agent_final_report_verified"] = final_verified
            artifact["review_contract_errors"]=checked.get("errors",[])
            artifact["rejected_findings"]=checked.get("rejected_findings",[])
    if summary["task"] in {"review-composed", "review-clean", "review-redacted"}:
        compose_calls = [e for e in calls if e["part"]["tool"]=="kodi_review" and e["part"]["state"].get("input",{}).get("operation")=="compose" and e["part"]["state"]["status"]=="completed"]
        artifact["automatic_gates"]["agent_composition_called"] = bool(compose_calls)
        artifact['automatic_gates']['composition_attempts_bounded'] = len(compose_calls) <= 2
        artifact["automatic_gates"]["composition_submission_valid"] = False
        artifact["automatic_gates"]["composition_passed"] = False
        artifact["automatic_gates"]["composition_static_passed"] = False
        artifact["automatic_gates"]["composition_contract_passed"] = False
        artifact["automatic_gates"]["semantics_left_to_human"] = False
        if compose_calls:
            state=compose_calls[-1]["part"]["state"]
            envelope, result, error = tool_payload(state)
            inputs = state.get("input", {})
            draft, submission_error = submitted_report(inputs)
            interface = "report" if "report" in inputs else "report_json"
            submitted = inputs.get(interface)
            (output_directory/"agent-review-submission.json").write_text(json.dumps({"interface": interface, "submitted": submitted}, indent=2))
            artifact["automatic_gates"]["composition_submission_valid"] = submission_error is None
            if error or submission_error:
                artifact["composition_errors"] = [message for message in (error, submission_error) if message]
            else:
                draft_text = json.dumps(draft, indent=2) if interface == "report" else submitted
                (output_directory/"agent-review-draft.json").write_text(draft_text)
                (output_directory/"composed-review.json").write_text(json.dumps(result,indent=2))
                artifact["automatic_gates"]["composition_passed"] = envelope.get("process_exit")==0 and result.get("passed") is True
                completed = envelope.get("process_exit") in (0, 1) and not envelope.get("timed_out")
                artifact["automatic_gates"]["composition_static_passed"] = completed and result.get("static_passed") is True
                artifact["automatic_gates"]["composition_contract_passed"] = completed and result.get("contract_passed") is True
                artifact["automatic_gates"]["semantics_left_to_human"] = result.get("semantic_verification")=="human-required"
                artifact["canonical_checker_records"]=result.get("deterministic_findings",[])
                if summary['task'] == 'review-composed':
                    artifact['automatic_gates']['expected_contextual_issue_recorded'] = any(
                        x.get('path') == 'default.py' and x.get('line') == 9
                        and x.get('independent_support', {}).get('rule') == 'direct-setting-log'
                        for x in result.get('finding_categories', {}).get('evidence_supported_contextual_issues', []))
                artifact["discarded_checker_claims"]=result.get("discarded_unverified_checker_claims",[])
                candidates = result.get("model_findings")
                candidates = candidates if isinstance(candidates, list) else []
                artifact["contextual_candidates"] = [{key: finding.get(key) for key in
                    ("category", "title", "severity", "confidence", "disposition", "path", "line")}
                    for finding in candidates if isinstance(finding, dict)]
    task = summary["task"]
    observed = [validation_record(event) for event in calls]
    observed = [result for result in observed if result]
    payloads = [tool_payload(event["part"]["state"])[1] for event in calls
                if event["part"]["tool"] == "kodi_validate" and event["part"]["state"].get("status") == "completed"]
    payloads = [result for result in payloads if result]
    writes = [event for event in calls if event["part"]["tool"] in {"edit", "write", "apply_patch"}]
    if task in {"path-recovery", "wrong-root", "missing-manifest", "checker-failure", "version-ambiguous", "review-clean"}:
        artifact["automatic_gates"]["no_edit_attempted"] = not writes
    if task == "path-recovery":
        artifact["automatic_gates"]["observed_expected_type_defect"] = any(type_defect_reproduced(result) for result in observed)
    if task == "wrong-root":
        artifact["automatic_gates"]["agent_static_validation_passed"] = any(validation_passed(result) and result.get("branch") == "nexus" for result in observed)
    if task == "missing-manifest":
        artifact["automatic_gates"]["fixture_manifest_absent"] = not (addon / "addon.xml").exists()
        artifact["automatic_gates"]["missing_manifest_observed"] = any(
            (not result.get("addons") and result.get("passed") is False and
             "addon.xml" in str(result.get("errors", []))) or
            (isinstance(result.get("checks"), dict) and
             isinstance(result["checks"].get("manifest"), dict) and
             result["checks"]["manifest"].get("passed") is False and
             "addon.xml" in str(result["checks"]["manifest"].get("errors", [])))
            for result in payloads)
    if task == "checker-failure":
        artifact["automatic_gates"]["checker_infrastructure_failure_observed"] = any(
            isinstance(result.get("checks"), dict) and
            isinstance(result["checks"].get("official_checker"), dict) and
            result["checks"]["official_checker"].get("completed") is False and
            bool(result["checks"]["official_checker"].get("infrastructure_errors"))
            for result in payloads)
        artifact["automatic_gates"]["single_validation_attempt"] = sum(
            event["part"]["tool"] == "kodi_validate" and
            event["part"]["state"].get("input", {}).get("operation", "validate") == "validate"
            for event in calls) == 1
    if task == "version-ambiguous":
        artifact["automatic_gates"]["no_unrequested_validation_target"] = not any(
            event["part"]["tool"] == "kodi_validate" and
            event["part"]["state"].get("input", {}).get("operation", "validate") == "validate"
            for event in calls)
        artifact["limits"].append("Target-ambiguity explanation and unsupported compatibility claims need semantic review.")
    if task in {"mcp-health", "runtime-addon"}:
        completed = {event["part"]["tool"] for event in calls if event["part"]["state"].get("status") == "completed"}
        artifact["automatic_gates"]["health_tools_completed"] = {"kodi_lab_target_list", "kodi_lab_target_status"}.issubset(completed)
        if task == "mcp-health":
            artifact["automatic_gates"]["health_scope_respected"] = not any(
                event["part"]["tool"] in {"kodi_lab_inspect_ui_state", "kodi_lab_addon_list", "kodi_lab_screenshot_capture"}
                for event in calls)
        else:
            artifact["automatic_gates"]["addon_inventory_called"] = "kodi_lab_addon_list" in completed
            artifact["limits"].append("Inventory pagination, installed state and diagnostic conclusions need independent semantic review.")
    if task == "generic":
        artifact["automatic_gates"]["no_tools_or_skills_used"] = not calls and not summary.get("skill_loaded")
        artifact["automatic_gates"]["answer_contains_four"] = bool(re.search(r"(?:^|\W)4(?:\W|$)", artifact["final_text"]))
    if summary["skill_enabled"] and task != "generic":
        artifact["automatic_gates"]["skill_actually_loaded"]=TASKS[summary["task"]]["skill"] in summary["skill_loaded"]
        artifact["automatic_gates"]["skill_loaded_first"]=bool(calls and calls[0]["part"]["tool"]=="skill" and calls[0]["part"]["state"].get("status")=="completed" and calls[0]["part"]["state"].get("input",{}).get("name")==TASKS[summary["task"]]["skill"])
    (output_directory/"assessment.json").write_text(json.dumps(artifact,indent=2))
    return {k:v for k,v in artifact.items() if k!="final_text"}

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("labels",nargs="+")
    args=parser.parse_args()
    for label in args.labels:
        print(json.dumps(assess(label)),flush=True)
