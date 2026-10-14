"""Portable static validation; never imports or executes add-on Python.

validate(Path, branch='nexus', cache=None) returns a JSON-serializable dict:
passed, returncode/exit_code, checks (syntax, manifest, paths, package, types,
official_checker), and coverage_limits. Official WARN records alone do not fail.
Cache is explicit: None does not trigger downloads or implicitly trust a cache.
.tests-config.json is rejected and its original hash recorded. Unsupported
stub-major/branch combinations fail type coverage rather than guessing.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.metadata as metadata
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
import tokenize
import xml.etree.ElementTree as ET

from .checker_runner import BRANCHES, SourceViolation, copy_source, inspect_source, run_checker

LIMITS = [
    "Static validation does not prove Kodi runtime behavior.",
    "Official repository findings use the supplied index snapshot, not live repository state.",
    "Online metadata URL checks are blocked, remain original official warnings, and are unverified.",
    "mypy uses installed Kodistubs; it does not execute add-on code or validate Kodi native behavior.",
    "Missing third-party typing dependencies and unsupported stub targets are real coverage failures.",
    "Replay is an application-level guard for the reviewed checker, not an OS sandbox.",
]


def _check(errors: list[str], **extra) -> dict:
    return {"status": "failed" if errors else "passed", "passed": not errors,
            "errors": errors, **extra}


def _reference(root: Path, text: str) -> Path:
    normalized = text.replace("\\", "/")
    path = PurePosixPath(normalized)
    if (not text or "\x00" in text or path.is_absolute() or ".." in path.parts
            or re.match(r"^[A-Za-z]:", normalized) or ":" in normalized):
        raise SourceViolation(f"Unsafe manifest path: {text!r}")
    resolved = root.joinpath(*path.parts)
    if not resolved.exists():
        raise SourceViolation(f"Missing manifest path: {text!r}")
    if resolved.is_symlink() or not resolved.resolve().is_relative_to(root.resolve()):
        raise SourceViolation(f"Manifest path escapes add-on: {text!r}")
    return resolved


def _types(root: Path, python_files: list[Path], branch: str) -> dict:
    if not python_files:
        return {"status": "not_applicable", "passed": True, "errors": [],
                "reason": "No Python source files", "stdout": "", "stderr": "", "output": ""}
    try:
        stub_version = metadata.version("Kodistubs")
        mypy_version = metadata.version("mypy")
        target = {"matrix": 19, "nexus": 20, "omega": 21, "piers": 22}.get(branch)
        if target is None or int(stub_version.split(".")[0]) != target:
            raise ValueError(f"Kodistubs {stub_version} does not match branch {branch}")
        distribution = metadata.distribution("Kodistubs")
        stub = next((distribution.locate_file(file) for file in distribution.files or []
                     if str(file) in ("xbmc.py", "xbmc/__init__.py")), None)
        if stub is None:
            raise ValueError("Installed Kodistubs xbmc module cannot be located")
        with tempfile.TemporaryDirectory(prefix="kodi-mypy-") as temporary:
            work = Path(temporary)
            config = work / "mypy.ini"
            config.write_text("[mypy]\npython_version = 3.10\n", encoding="utf-8")
            command = [sys.executable, "-I", "-B", "-m", "mypy",
                       "--config-file", str(config), "--no-incremental",
                       "--cache-dir", str(work / "cache"), "--show-error-codes",
                       "--check-untyped-defs", "--follow-imports=silent", "--follow-untyped-imports",
                       *[str(root / path) for path in python_files]]
            env = {key: value for key, value in os.environ.items()
                   if not key.startswith(("PYTHON", "MYPY"))}
            result = subprocess.run(command, cwd=work, env=env, capture_output=True,
                                    text=True, encoding="utf-8", errors="replace", timeout=120)
            return {"status": "passed" if result.returncode == 0 else "failed",
                    "passed": result.returncode == 0, "exit_code": result.returncode,
                    "returncode": result.returncode, "stdout": result.stdout,
                    "stderr": result.stderr, "output": result.stdout + result.stderr,
                    "errors": [] if result.returncode == 0 else [result.stdout + result.stderr],
                    "stub_version": stub_version, "mypy_version": mypy_version,
                    "command": command, "config": "explicit empty-plugin mypy config; Python target 3.10"}
    except (metadata.PackageNotFoundError, ValueError, OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "error", "passed": False, "errors": [str(exc)],
                "stdout": "", "stderr": "", "output": "", "exit_code": None}


def validate(addon: Path, branch: str = "nexus", cache: Path | None = None) -> dict:
    """Validate an isolated snapshot and preserve failures; warnings are not errors."""
    result: dict = {"addon": str(addon), "branch": branch, "passed": False,
                    "returncode": 1, "exit_code": 1, "checks": {},
                    "coverage_limits": list(LIMITS), "config_input": {"status": "not_inspected"},
                    "type_status": "skipped"}
    checks = result["checks"]
    for name in ("syntax", "manifest", "paths", "package", "types", "official_checker"):
        checks[name] = {"status": "skipped", "passed": False,
                        "reason": "Source/package safety preflight has not succeeded",
                        "output": "", "stdout": "", "stderr": "", "errors": [], "warnings": [],
                        "exit_code": None, "returncode": None, "completed": False}
    checks["official_checker"]["online_url_checks"] = "unverified"
    if branch not in BRANCHES:
        checks["paths"] = _check([f"Unsupported Kodi branch: {branch}"])
        return result
    try:
        source = Path(addon)
        files = inspect_source(source)
        result['source_snapshot'] = {path.as_posix(): hashlib.sha256((source / path).read_bytes()).hexdigest()
                                     for path in files}
        source = source.absolute()
        config_files = [path for path in files if path.name == ".tests-config.json"]
        result["config_input"] = {"status": "absent"}
        if config_files:
            result["config_input"] = {"status": "rejected", "files": [
                {"path": str(path), "sha256": hashlib.sha256((source / path).read_bytes()).hexdigest()}
                for path in config_files]}
            raise SourceViolation(".tests-config.json is rejected because it can disable checks")
        with tempfile.TemporaryDirectory(prefix="kodi-validate-") as temporary:
            root = copy_source(source, Path(temporary) / source.name)
            files = inspect_source(root)
            result['source_snapshot'] = {path.as_posix(): hashlib.sha256((root / path).read_bytes()).hexdigest()
                                         for path in files}
            python_files = [path for path in files if path.suffix == ".py"]
            syntax_errors = []
            for path in python_files:
                try:
                    with tokenize.open(root / path) as stream:
                        ast.parse(stream.read(), filename=str(path), feature_version=(3, 10))
                except (SyntaxError, UnicodeError, OSError) as exc:
                    syntax_errors.append(f"{path}: {exc}")
            checks["syntax"] = _check(syntax_errors, files=[str(path) for path in python_files],
                                       target_python="3.10")
            manifest_errors: list[str] = []
            path_errors: list[str] = []
            package_errors: list[str] = []
            manifest_path = root / "addon.xml"
            manifest = None
            if not manifest_path.is_file():
                manifest_errors.append("Missing root addon.xml")
            else:
                raw = manifest_path.read_bytes()
                try:
                    if b"<!DOCTYPE" in raw.replace(b"\x00", b"").upper() or b"<!ENTITY" in raw.replace(b"\x00", b"").upper():
                        raise ValueError("DOCTYPE/entity declarations are not accepted")
                    manifest = ET.fromstring(raw)
                    if manifest.tag != "addon":
                        manifest_errors.append("Manifest root must be addon")
                    for key in ("id", "name", "version", "provider-name"):
                        if not manifest.get(key):
                            manifest_errors.append(f"Missing manifest attribute: {key}")
                    identifier = manifest.get("id", "")
                    if not re.fullmatch(r"[A-Za-z0-9_]+(?:[.-][A-Za-z0-9_]+)*", identifier):
                        manifest_errors.append("Unsafe/invalid manifest add-on ID")
                    if identifier != root.name:
                        package_errors.append("Folder basename and manifest add-on ID differ")
                    if not manifest.findall("extension"):
                        manifest_errors.append("Manifest has no extension")
                    references = []
                    for extension in manifest.findall("extension"):
                        for name in ("library", "start", "folder"):
                            if extension.get(name) is not None:
                                references.append(extension.attrib[name])
                        for asset in extension.findall("assets/*"):
                            references.append(asset.text or "")
                    for reference in references:
                        try:
                            _reference(root, reference)
                        except SourceViolation as exc:
                            path_errors.append(str(exc))
                except (ET.ParseError, ValueError) as exc:
                    manifest_errors.append(f"addon.xml: {exc}")
            if not any(path.name.upper() in ("LICENSE", "LICENSE.TXT", "LICENSE.MD")
                       and len(path.parts) == 1 for path in files):
                package_errors.append("Missing root LICENSE / LICENSE.txt / LICENSE.md")
            checks["manifest"] = _check(manifest_errors)
            checks["paths"] = _check(path_errors, symlinks="rejected", traversal="rejected")
            checks["package"] = _check(package_errors, file_count=len(files),
                                       addon_id=manifest.get("id") if manifest is not None else None)
            checks["types"] = _types(root, python_files, branch) if not syntax_errors else {
                "status": "skipped", "passed": False, "errors": [],
                "reason": "Python syntax failed", "stdout": "", "stderr": "", "output": ""}
            # Unsafe references must never reach upstream file readers.
            if path_errors or not manifest_path.is_file() or any(
                    "DOCTYPE" in message or "root must" in message for message in manifest_errors):
                checks["official_checker"] = {
                    "status": "skipped", "passed": False, "completed": False,
                    "reason": "Unsafe/missing manifest input", "exit_code": None, "returncode": None,
                    "stdout": "", "stderr": "", "output": "", "errors": [], "warnings": [],
                    "online_url_checks": "unverified"}
            else:
                # Malformed ordinary XML still reaches upstream: preserve its real error/traceback.
                checks["official_checker"] = run_checker(root, branch, cache)
            result["passed"] = all(check.get("passed", False) for check in checks.values())
            official_code = checks["official_checker"].get("exit_code")
            result["returncode"] = 0 if result["passed"] else official_code if official_code else 1
            result["exit_code"] = result["returncode"]
    except (SourceViolation, OSError, ValueError) as exc:
        checks["paths"] = _check([str(exc)])
        for name in ("syntax", "manifest", "package", "types", "official_checker"):
            checks.setdefault(name, {"status": "skipped", "passed": False,
                                    "reason": "Source/package safety preflight failed",
                                    "output": "", "stdout": "", "stderr": ""})
    result["type_status"] = checks.get("types", {}).get("status", "skipped")
    return result
