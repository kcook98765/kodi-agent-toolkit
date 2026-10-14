"""Portable, read-only validation of a local review's evidence contract.

Reports require model_findings, coverage (scope, complete, reviewed_files), and
nonempty limitations. deterministic_findings is an optional, separate collection
of checker records; this module does not certify those records.

A model finding requires path, line, quote, title, category, reason, mechanism,
severity, and confidence. Categories are privacy, api, packaging, submission,
and correctness. Related evidence optionally has role support, counterevidence,
or context. Quotes are exact, case-sensitive substrings of a single stated line.

passed means the evidence/report contract passed, not that the add-on is safe or
that findings are true. Confidence is the author's claim. Mechanism is required
descriptive prose, not proof: no semantic, runtime, or API verification occurs.
"""

from __future__ import annotations

import copy
import os
import re
import stat
from pathlib import Path
from typing import Any

CATEGORIES = ("privacy", "api", "packaging", "submission", "correctness")
SEVERITIES = ("blocker", "material", "advisory")
CONFIDENCES = ("demonstrated", "source-supported", "unresolved")
ROLES = ("support", "counterevidence", "context")

MAX_FINDINGS = 100
MAX_CHECKER_FINDINGS = 1000
MAX_RELATED_EVIDENCE = 16
MAX_SOURCE_BYTES = 256 * 1024
MAX_EVIDENCE_FILES = 64
MAX_CONTEXT_FILES = 32
MAX_CONTEXT_BYTES = 128 * 1024
MAX_CONTEXT_LINES = 1200
MAX_FILE_LINES = 400
MAX_LINE_CHARS = 2000
MAX_SCAN_ENTRIES = 2048
EXCLUDED_DIRECTORIES = frozenset(
    {".git", ".venv", "venv", "__pycache__", "node_modules", ".mypy_cache",
     ".pytest_cache", ".ruff_cache"}
)
LIMITATIONS = [
    "Source anchoring checks locations and literal quotes; it does not verify "
    "a finding's mechanism, consequence, severity, or claimed confidence.",
    "No add-on imports, Kodi execution, network access, or compatibility tests "
    "are performed. Files may change after this read.",
    "Context includes addon.xml, Python, and settings XML within explicit "
    "budgets; excluded or omitted material requires further review.",
]


class EvidenceError(ValueError):
    """A path, source, or location cannot safely support an evidence record."""


def _root(addon: Path) -> Path:
    path = Path(addon)
    try:
        for component in (path.absolute(), *path.absolute().parents):
            if component.is_symlink() or (component.exists() and _reparse(component)):
                raise EvidenceError('add-on root/ancestors must not be a symlink or junction')
        root = path.resolve(strict=True)
    except (OSError, ValueError, RuntimeError) as exc:
        if isinstance(exc, EvidenceError):
            raise
        raise EvidenceError("add-on root is unavailable") from exc
    if not root.is_dir():
        raise EvidenceError("add-on root must be a directory")
    return root


def _reparse(path: Path) -> bool:
    return bool(getattr(path.lstat(), 'st_file_attributes', 0) & 0x400)


def _safe_path(root: Path, value: Any) -> Path:
    if not isinstance(value, str) or not value:
        raise EvidenceError("path must be a nonempty relative string")
    if "\\" in value or any(ord(char) < 32 for char in value):
        raise EvidenceError("path must use safe forward-slash components")
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise EvidenceError("absolute, empty, dot, and traversal components are forbidden")
    for part in parts:
        if any(char in '<>:"|?*' for char in part) or part.endswith((" ", ".")):
            raise EvidenceError("path is not portable")
        if re.fullmatch(r"(?i)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])", part.split(".")[0]):
            raise EvidenceError("reserved device names are forbidden")
    current = root
    try:
        for part in parts:
            current = current / part
            if stat.S_ISLNK(current.lstat().st_mode) or _reparse(current):
                raise EvidenceError("symlink/junction/reparse evidence is forbidden")
        current.resolve(strict=True).relative_to(root)
        if not stat.S_ISREG(current.lstat().st_mode):
            raise EvidenceError("evidence path must be an existing regular file")
    except (OSError, ValueError, RuntimeError) as exc:
        if isinstance(exc, EvidenceError):
            raise
        raise EvidenceError("evidence path is unavailable or outside the add-on") from exc
    return current


def _read_bytes(root: Path, value: str, limit: int) -> bytes:
    """Use descriptor-relative no-follow traversal where the OS supports it.

    Other platforms check every component and recheck after opening; concurrent
    ancestor replacement is outside that fallback's snapshot guarantee.
    """
    path = _safe_path(root, value)
    descriptor: int | None = None
    directories: list[int] = []
    try:
        flags = (os.O_RDONLY | getattr(os, "O_BINARY", 0)
                 | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
        if os.open in os.supports_dir_fd and hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_DIRECTORY"):
            dir_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
            directories.append(os.open(root, dir_flags))
            parts = value.split("/")
            for part in parts[:-1]:
                directories.append(os.open(part, dir_flags, dir_fd=directories[-1]))
            descriptor = os.open(parts[-1], flags, dir_fd=directories[-1])
        else:
            descriptor = os.open(path, flags)
            checked = _safe_path(root, value)
            opened_stat = os.fstat(descriptor)
            current_stat = checked.stat()
            if (opened_stat.st_dev, opened_stat.st_ino) != (current_stat.st_dev, current_stat.st_ino):
                raise EvidenceError("source changed while opening")
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise EvidenceError("evidence source is not a regular file")
        with os.fdopen(descriptor, "rb") as source:
            descriptor = None
            return source.read(limit + 1)
    except OSError as exc:
        raise EvidenceError("source could not be opened safely") from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)
        for directory in reversed(directories):
            os.close(directory)


def _lines(data: bytes) -> list[str]:
    if b"\x00" in data:
        raise EvidenceError("source contains binary NUL bytes")
    try:
        text = data.decode("utf-8-sig")
    except UnicodeError as exc:
        raise EvidenceError("source is not valid UTF-8 text") from exc
    lines = text.split("\n")
    if lines[-1] == "":
        lines.pop()
    return [line[:-1] if line.endswith("\r") else line for line in lines]


def _source_lines(root: Path, path: str, cache: dict[str, list[str]]) -> list[str]:
    if path not in cache:
        if len(cache) >= MAX_EVIDENCE_FILES:
            raise EvidenceError("too many distinct evidence files")
        data = _read_bytes(root, path, MAX_SOURCE_BYTES)
        if len(data) > MAX_SOURCE_BYTES:
            raise EvidenceError("source exceeds the evidence read budget")
        cache[path] = _lines(data)
    return cache[path]


def _text(value: Any, field: str, errors: list[str], maximum: int = 4000) -> bool:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        errors.append(f"{field}: requires nonempty text of at most {maximum} characters")
        return False
    return True


def _anchor(root: Path, record: Any, cache: dict[str, list[str]],
            reviewed: set[str], label: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return [f"{label}: evidence must be an object"]
    path, line, quote = record.get("path"), record.get("line"), record.get("quote")
    try:
        _safe_path(root, path)
        if path not in reviewed:
            errors.append(f"{label}.path: file is absent from coverage.reviewed_files")
        lines = _source_lines(root, path, cache)
    except EvidenceError as exc:
        return [f"{label}.path: {exc}"]
    if type(line) is not int or line < 1 or line > len(lines):
        errors.append(f"{label}.line: requires a 1-based line within the file")
    if not _text(quote, f"{label}.quote", errors, MAX_LINE_CHARS):
        return errors
    if "\n" in quote or "\r" in quote:
        errors.append(f"{label}.quote: must quote a single line")
    elif type(line) is int and 1 <= line <= len(lines) and quote not in lines[line - 1]:
        errors.append(f"{label}.quote: literal quote is absent from the stated line")
    return errors


def report_schema() -> dict[str, Any]:
    """Return a fresh original JSON Schema describing the input contract."""
    text = {"type": "string", "minLength": 1, "maxLength": 4000}
    anchor: dict[str, Any] = {
        "type": "object", "additionalProperties": False,
        "required": ["path", "line", "quote"],
        "properties": {
            "path": {"type": "string", "minLength": 1},
            "line": {"type": "integer", "minimum": 1},
            "quote": {"type": "string", "minLength": 1, "maxLength": MAX_LINE_CHARS},
            "role": {"enum": list(ROLES)},
        },
    }
    properties = copy.deepcopy(anchor["properties"])
    properties.pop("role")
    properties.update({
        "title": {"type": "string", "minLength": 1, "maxLength": 240},
        "category": {"enum": list(CATEGORIES)},
        "reason": copy.deepcopy(text), "mechanism": copy.deepcopy(text),
        "severity": {"enum": list(SEVERITIES)},
        "confidence": {"enum": list(CONFIDENCES)},
        "reproduction": {"type": "object", "additionalProperties": False,
                         "required": ["steps", "observed", "expected"],
                         "properties": {key: copy.deepcopy(text) for key in ("steps", "observed", "expected")}},
        "related_evidence": {"type": "array", "maxItems": MAX_RELATED_EVIDENCE,
                             "items": anchor},
        "requirement_basis": {"type": "string", "minLength": 1, "maxLength": 160},
    })
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object", "additionalProperties": False,
        "required": ["model_findings", "coverage", "limitations"],
        "properties": {
            "model_findings": {
                "type": "array", "maxItems": MAX_FINDINGS,
                "items": {"type": "object", "additionalProperties": False,
                          "required": ["path", "line", "quote", "title", "category",
                                       "reason", "mechanism", "severity", "confidence"],
                          "properties": properties,
                          "allOf": [
                              {"if": {"properties": {"confidence": {"const": "unresolved"}}, "required": ["confidence"]},
                               "then": {"properties": {"severity": {"const": "advisory"}}}},
                              {"if": {"properties": {"severity": {"const": "blocker"}}, "required": ["severity"]},
                               "then": {"properties": {"confidence": {"const": "demonstrated"}}}},
                              {"if": {"properties": {"confidence": {"const": "demonstrated"}}, "required": ["confidence"]},
                               "then": {"required": ["reproduction"]},
                               "else": {"not": {"required": ["reproduction"]}}},
                          ]},
            },
            "deterministic_findings": {"type": "array", "maxItems": MAX_CHECKER_FINDINGS,
                                       "items": {"type": "object"}},
            "limitations": {"type": "array", "minItems": 1, "maxItems": 64,
                            "items": copy.deepcopy(text)},
            "coverage": {
                "type": "object", "additionalProperties": False,
                "required": ["scope", "complete", "reviewed_files"],
                "properties": {
                    "scope": copy.deepcopy(text), "complete": {"type": "boolean"},
                    "reviewed_files": {"type": "array", "maxItems": MAX_SCAN_ENTRIES,
                                       "items": {"type": "string", "minLength": 1}},
                },
            },
        },
    }


def validate_review(addon: Path, report: dict[str, Any]) -> dict[str, Any]:
    """Check a report's static source anchors, never its semantic conclusions."""
    result: dict[str, Any] = {
        "passed": False, "accepted_findings": [], "rejected_findings": [],
        "deterministic_findings": [], "errors": [],
        "coverage": {
            "scope": None, "complete": False, "reviewed_files": [],
            "limitations": list(LIMITATIONS),
            "semantic_verification": "not-performed",
            "runtime_execution": "not-performed", "network_access": "not-performed",
            "scope_completion_is_claim": True,
            "deterministic_verification": "not-performed",
        },
    }
    errors: list[str] = result["errors"]
    try:
        root = _root(addon)
    except EvidenceError as exc:
        errors.append(f"addon: {exc}")
        return result
    if not isinstance(report, dict):
        errors.append("report: requires an object")
        return result
    unknown = set(report) - {"model_findings", "deterministic_findings", "coverage", "limitations"}
    if unknown:
        errors.append("report: unknown fields; use model_findings for contextual claims")
    coverage = report.get("coverage")
    reviewed: set[str] = set()
    if not isinstance(coverage, dict):
        errors.append("coverage: requires scope, complete, and reviewed_files")
    else:
        if set(coverage) - {"scope", "complete", "reviewed_files"}:
            errors.append("coverage: unknown fields")
        if _text(coverage.get("scope"), "coverage.scope", errors):
            result["coverage"]["scope"] = coverage["scope"]
        if type(coverage.get("complete")) is not bool:
            errors.append("coverage.complete: requires an explicit boolean")
        else:
            result["coverage"]["complete"] = coverage["complete"]
        paths = coverage.get("reviewed_files")
        if not isinstance(paths, list) or len(paths) > MAX_SCAN_ENTRIES:
            errors.append("coverage.reviewed_files: requires a bounded list")
        else:
            for path in paths:
                try:
                    _safe_path(root, path)
                    reviewed.add(path)
                except EvidenceError as exc:
                    errors.append(f"coverage.reviewed_files: {exc}")
            if coverage.get("complete") is True and not reviewed:
                errors.append("coverage.complete: cannot be complete with no reviewed files")
            result["coverage"]["reviewed_files"] = sorted(reviewed)
    limitations = report.get("limitations")
    if not isinstance(limitations, list) or not 1 <= len(limitations) <= 64:
        errors.append("limitations: requires an explicit nonempty bounded list")
    else:
        for limitation in limitations:
            _text(limitation, "limitations", errors)
        if all(isinstance(item, str) for item in limitations):
            result["coverage"]["limitations"] = copy.deepcopy(limitations) + list(LIMITATIONS)
    deterministic = report.get("deterministic_findings", [])
    if (not isinstance(deterministic, list) or len(deterministic) > MAX_CHECKER_FINDINGS
            or not all(isinstance(item, dict) for item in deterministic)):
        errors.append("deterministic_findings: requires a separate list of checker objects")
    else:
        result["deterministic_findings"] = copy.deepcopy(deterministic)
    findings = report.get("model_findings")
    if not isinstance(findings, list) or len(findings) > MAX_FINDINGS:
        errors.append("model_findings: requires a bounded list")
        return result
    cache: dict[str, list[str]] = {}
    required = {"path", "line", "quote", "title", "category", "reason",
                "mechanism", "severity", "confidence"}
    for index, finding in enumerate(findings):
        problems: list[str] = []
        if not isinstance(finding, dict):
            problems.append("finding: requires an object")
        else:
            if set(finding) - required - {"related_evidence", "reproduction", "requirement_basis"}:
                problems.append("finding: unknown fields")
            if "requirement_basis" in finding:
                _text(finding['requirement_basis'], 'requirement_basis', problems, 160)
            for field in ("title", "reason", "mechanism"):
                _text(finding.get(field), field, problems, 240 if field == "title" else 4000)
            mechanism = finding.get("mechanism")
            if isinstance(mechanism, str) and mechanism.strip().lower().strip(".!") in {
                "unsafe", "insecure", "always unsafe", "definitely unsafe",
                "a bug", "bad", "guaranteed", "unknown", "n/a", "none", "no evidence",
            }:
                problems.append("mechanism: a certainty label is not a described operation")
            for field, values in (("category", CATEGORIES), ("severity", SEVERITIES),
                                  ("confidence", CONFIDENCES)):
                if finding.get(field) not in values:
                    problems.append(f"{field}: must be one of {', '.join(values)}")
            confidence, severity = finding.get("confidence"), finding.get("severity")
            if confidence == "unresolved" and severity != "advisory":
                problems.append("severity: unresolved observations cannot be material or blocker")
            if severity == "blocker" and confidence != "demonstrated":
                problems.append("severity: blocker requires demonstrated impact and a reproduction")
            reproduction = finding.get("reproduction")
            if "reproduction" in finding and confidence != "demonstrated":
                problems.append("reproduction: observed outcomes are permitted only for demonstrated claims; static source-supported findings must omit reproduction")
            if confidence == "demonstrated" or reproduction is not None:
                if not isinstance(reproduction, dict) or set(reproduction) != {"steps", "observed", "expected"}:
                    problems.append("reproduction: requires steps, observed, expected for demonstrated claims")
                else:
                    for field in ("steps", "observed", "expected"):
                        _text(reproduction.get(field), f"reproduction.{field}", problems)
            problems.extend(_anchor(root, finding, cache, reviewed, "finding"))
            related = finding.get("related_evidence", [])
            if not isinstance(related, list) or len(related) > MAX_RELATED_EVIDENCE:
                problems.append("related_evidence: requires a bounded list")
            else:
                for position, evidence in enumerate(related):
                    label = f"related_evidence[{position}]"
                    if isinstance(evidence, dict):
                        if set(evidence) - {"path", "line", "quote", "role"}:
                            problems.append(f"{label}: unknown fields")
                        if evidence.get("role", "context") not in ROLES:
                            problems.append(f"{label}.role: invalid evidence role")
                    problems.extend(_anchor(root, evidence, cache, reviewed, label))
        if problems:
            result["rejected_findings"].append({
                "index": index, "finding": copy.deepcopy(finding), "errors": problems,
            })
        else:
            accepted = copy.deepcopy(finding)
            accepted.setdefault("related_evidence", [])
            accepted["disposition"] = "observation"
            accepted.update(source="model", evidence_status="source-anchored",
                            semantic_verification="not-performed", confidence_is_claim=True)
            result["accepted_findings"].append(accepted)
    result["passed"] = not errors and not result["rejected_findings"]
    return result


def _relevant(path: str) -> bool:
    candidate = Path(path)
    return (path == "addon.xml" or candidate.suffix.lower() == ".py"
            or (candidate.suffix.lower() == ".xml"
                and (candidate.stem.lower().startswith("settings")
                     or "settings" in [part.lower() for part in candidate.parts[:-1]])))


def _context_paths(root: Path) -> tuple[list[str], list[dict[str, Any]]]:
    paths: list[str] = []
    omitted: list[dict[str, Any]] = []
    pending = [root]
    visited = 0
    while pending:
        directory = pending.pop()
        try:
            # Do not follow a directory that changed to a symlink after discovery.
            if directory.is_symlink() or _reparse(directory) or directory.resolve(strict=True) != directory:
                raise EvidenceError("directory changed or became a symlink")
            with os.scandir(directory) as entries:
                batch = []
                for entry in entries:
                    visited += 1
                    if visited > MAX_SCAN_ENTRIES:
                        omitted.append({"path": directory.relative_to(root).as_posix(),
                                        "reason": "scan-entry-limit"})
                        return paths, omitted
                    batch.append(entry)
            for entry in sorted(batch, key=lambda item: item.name, reverse=True):
                path = Path(entry.path)
                relative = path.relative_to(root).as_posix()
                if entry.is_symlink():
                    omitted.append({"path": relative, "reason": "symlink-excluded"})
                elif entry.is_dir(follow_symlinks=False):
                    if entry.name not in EXCLUDED_DIRECTORIES:
                        pending.append(path)
                elif _relevant(relative):
                    paths.append(relative)
        except (OSError, ValueError, RuntimeError) as exc:
            omitted.append({"path": directory.relative_to(root).as_posix(),
                            "reason": "directory-unavailable", "detail": str(exc)})
    return paths, omitted


def review_context(addon: Path) -> dict[str, Any]:
    """Return bounded, numbered source context and the original report schema.

    Only filesystem reads are performed. Omitted and truncated source is explicit.
    This is a context inventory, not a review or a completeness certificate.
    """
    root = _root(addon)
    paths, omitted = _context_paths(root)
    if "addon.xml" not in paths:
        omitted.append({"path": "addon.xml", "reason": "required-manifest-unavailable"})
    files: list[dict[str, Any]] = []
    remaining_bytes, remaining_lines = MAX_CONTEXT_BYTES, MAX_CONTEXT_LINES
    for path in sorted(paths, key=lambda value: (value != "addon.xml", value)):
        if len(files) >= MAX_CONTEXT_FILES or remaining_bytes <= 0 or remaining_lines <= 0:
            omitted.append({"path": path, "reason": "context-budget"})
            continue
        limit = min(MAX_SOURCE_BYTES, remaining_bytes)
        try:
            data = _read_bytes(root, path, limit)
            remaining_bytes -= min(len(data), limit)
            truncated_bytes = len(data) > limit
            data = data[:limit]
            if truncated_bytes:
                # Keep only complete lines, avoiding a split UTF-8 sequence.
                newline = data.rfind(b"\n")
                data = data[:newline + 1] if newline >= 0 else b""
            lines = _lines(data)
        except EvidenceError as exc:
            omitted.append({"path": path, "reason": "source-unavailable", "detail": str(exc)})
            continue
        numbered = []
        line_limit = min(MAX_FILE_LINES, remaining_lines)
        for number, text in enumerate(lines[:line_limit], 1):
            if len(text) > MAX_LINE_CHARS:
                omitted.append({"path": path, "line": number, "reason": "line-length-limit"})
                continue
            numbered.append({"line": number, "text": text})
        truncated = (truncated_bytes or len(lines) > line_limit
                     or len(numbered) < min(len(lines), line_limit))
        if truncated:
            omitted.append({"path": path, "reason": "source-truncated",
                            "included_lines": len(numbered)})
        files.append({"path": path, "lines": numbered, "truncated": truncated})
        remaining_lines -= len(numbered)
    return {
        "schema_version": "1.3", "addon": str(root), "files": files,
        "report_schema": report_schema(),
        "coverage": {
            "scope": "addon.xml, Python files, and settings XML; static context only",
            "reviewed_files": [source["path"] for source in files],
            "complete": not omitted, "omitted_files": omitted,
            "limits": {
                "files": MAX_CONTEXT_FILES, "source_bytes_per_file": MAX_SOURCE_BYTES,
                "total_source_bytes": MAX_CONTEXT_BYTES, "total_lines": MAX_CONTEXT_LINES,
                "lines_per_file": MAX_FILE_LINES, "line_characters": MAX_LINE_CHARS,
                "scan_entries": MAX_SCAN_ENTRIES,
            },
            "excluded_directories": sorted(EXCLUDED_DIRECTORIES),
            "semantic_verification": "not-performed",
            "runtime_execution": "not-performed", "network_access": "not-performed",
        },
        "limitations": list(LIMITATIONS),
        "guidance": [
            "Source anchoring accepts structure only. Composition independently classifies support; unsupported claims remain unverified. Empty findings are valid.",
            "Kodi requirement claims need requirement_basis identifying a documented rule; known IDs identify sources only, never applicability or a defect.",
            "Separate model findings from deterministic checker diagnostics.",
            "Material: reachable incorrect behavior with a concrete conditional consequence. Advisory: nonbreaking recommendation. Unresolved: advisory observation only.",
            "Blocker needs demonstrated install/start failure or serious boundary impact, plus reproduction steps/observed/expected. Source anchoring alone cannot establish it.",
            "Static source-supported findings must omit reproduction and describe conditional risk, not invented observations. Demonstrated reproduction is still an author claim, not independently certified.",
            "Describe a concrete mechanism and preconditions; avoid unsupported certainty.",
            "Inspect related supporting context and counterevidence before making a claim.",
            "Use the input schema's coverage fields; context inventory is not proof of review.",
            "Evidence quotes must occur literally on the specified 1-based source line.",
        ],
    }
