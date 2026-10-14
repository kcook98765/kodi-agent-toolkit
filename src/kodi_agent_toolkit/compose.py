"""Compose independent static checks and source anchors; semantics need a human."""
from __future__ import annotations

import copy
from pathlib import Path

from .review import validate_review
from .validate import validate
from .evidence import classify


def compose_review(addon: Path, report: dict, branch: str = "nexus",
                   cache: Path | None = None) -> dict:
    """Use only official checker diagnostics as canonical deterministic findings.

    Draft checker claims are retained for inspection but removed before checking
    the model report's evidence contract. Neither a contract pass nor a static
    pass verifies model conclusions or Kodi runtime behavior. Cache is explicit.
    """
    model_report = copy.deepcopy(report)
    discarded = model_report.pop("deterministic_findings", [])
    validation_report = validate(addon, branch=branch, cache=cache)
    contract_report = validate_review(addon, model_report)
    official = validation_report["checks"]["official_checker"]
    deterministic = [
        {"source": "official_checker", "severity": severity, "message": message}
        for field, severity in (("errors", "error"), ("warnings", "warning"))
        for message in official.get(field, [])
    ]
    static_passed = validation_report["passed"]
    contract_passed = contract_report["passed"]
    categories = classify(addon, contract_report, deterministic)
    passed = static_passed and contract_passed
    returncode = 0 if passed else 1
    if not static_passed:
        returncode = validation_report["returncode"] or 1
    return {
        "addon": str(addon), "branch": branch,
        "passed": passed, "static_passed": static_passed,
        "contract_passed": contract_passed,
        "status": "static-failed" if not static_passed else "contract-rejected" if not contract_passed else "semantic-review-required",
        "passed_scope": "static-checks-and-report-contract-only",
        "returncode": returncode, "exit_code": returncode,
        "semantic_verification": "human-required",
        "deterministic_findings": deterministic,
        "discarded_unverified_checker_claims": discarded,
        "model_findings": copy.deepcopy(contract_report["accepted_findings"]),
        "finding_categories": categories,
        "validation_report": validation_report,
        "contract_report": contract_report,
    }
