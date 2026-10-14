"""Run installed addon-check 0.0.36 without changing or copying its source.

Replay requires all ten HTTPS-fetched indexes and manifest.json (schema_version=1).
Only exact official index GETs are served. HEAD URL checks raise the original
requests ConnectionError and therefore remain official WARN findings. Other
network/child-process attempts abort, even if upstream catches Exception.
This is an application-level replay guard, not an OS security sandbox.
"""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import importlib.metadata as metadata
import io
import json
import os
from pathlib import Path
import re
import shutil
import socket
import stat
import subprocess
import sys
import tempfile
import traceback
import xml.etree.ElementTree as ET

BRANCHES = ("gotham", "helix", "isengard", "jarvis", "krypton", "leia",
            "matrix", "nexus", "omega", "piers")
INDEX_BASE = "https://mirrors.kodi.tv/addons"
MAX_GZIP = 32 * 1024 * 1024
MAX_XML = 256 * 1024 * 1024
ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


class SourceViolation(ValueError):
    """Unsafe or unsupported source input."""


class ReplayViolation(BaseException):
    """Must not be swallowed by upstream exception handlers."""


def _is_reparse_point(path: Path, info: os.stat_result | None = None) -> bool:
    """Reject Windows junctions and other reparse points, including on Python 3.10."""
    is_junction = getattr(path, "is_junction", None)
    if is_junction is not None and is_junction():
        return True
    try:
        info = path.lstat() if info is None else info
    except FileNotFoundError:
        return False
    return bool(getattr(info, "st_file_attributes", 0)
                & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def safe_path(path: Path) -> Path:
    path = Path(path)
    if ".." in path.parts:
        raise SourceViolation(f"Traversal is not allowed: {path}")
    absolute = path.absolute()
    for part in reversed((absolute, *absolute.parents)):
        if part.is_symlink():
            raise SourceViolation(f"Symlink is not allowed: {part}")
        if _is_reparse_point(part):
            raise SourceViolation(f"Junction/reparse point is not allowed: {part}")
    return absolute


def inspect_source(addon: Path) -> list[Path]:
    root = safe_path(addon)
    if not root.is_dir():
        raise SourceViolation(f"Add-on directory does not exist: {root}")
    resolved_root = root.resolve(strict=True)
    files: list[Path] = []
    size = 0
    for directory, folders, names in os.walk(root, followlinks=False):
        current = Path(directory)
        if current.is_symlink() or _is_reparse_point(current):
            raise SourceViolation(f"Symlink/junction/reparse directory is not allowed: {current}")
        if not current.resolve(strict=True).is_relative_to(resolved_root):
            raise SourceViolation(f"Source directory escapes add-on: {current}")
        for name in folders + names:
            path = Path(directory) / name
            info = path.lstat()
            mode = info.st_mode
            if stat.S_ISLNK(mode) or not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
                raise SourceViolation(f"Symlink/special file is not allowed: {path}")
            if _is_reparse_point(path, info):
                raise SourceViolation(f"Junction/reparse point is not allowed: {path}")
            if not path.resolve(strict=True).is_relative_to(resolved_root):
                raise SourceViolation(f"Source entry escapes add-on: {path}")
            if "\\" in name:
                raise SourceViolation(f"Ambiguous package filename: {path}")
            if stat.S_ISREG(mode):
                files.append(path.relative_to(root))
                size += info.st_size
                if len(files) > 10000 or size > 64 * 1024 * 1024:
                    raise SourceViolation("Add-on exceeds 10,000 files or 64 MiB")
    return sorted(files)


def copy_source(addon: Path, destination: Path) -> Path:
    inspect_source(addon)
    shutil.copytree(addon, destination, symlinks=True)
    inspect_source(destination)
    return destination


def inspect_manifest_paths(root: Path) -> None:
    """Protect standalone replay as well as callers from manifest file escapes."""
    path = root / "addon.xml"
    if not path.is_file():
        raise SourceViolation("Standalone replay requires root addon.xml")
    raw = path.read_bytes()
    if b"<!DOCTYPE" in raw.replace(b"\x00", b"").upper() or b"<!ENTITY" in raw.replace(b"\x00", b"").upper():
        raise SourceViolation("DOCTYPE/entity declarations are not accepted")
    try:
        manifest = ET.fromstring(raw)
    except ET.ParseError:
        return  # Let official checker produce its original malformed-XML failure.
    if manifest.tag != "addon":
        raise SourceViolation("Manifest root must be addon")
    references = []
    for extension in manifest.findall("extension"):
        references.extend(extension.attrib[key] for key in ("library", "start", "folder")
                          if key in extension.attrib)
        references.extend(asset.text or "" for asset in extension.findall("assets/*"))
    for text in references:
        normalized = text.replace("\\", "/")
        parts = normalized.split("/")
        if (not text or "\x00" in text or normalized.startswith("/")
                or ".." in parts or ":" in normalized):
            raise SourceViolation(f"Unsafe manifest path: {text!r}")
        target = root.joinpath(*parts)
        if not target.exists() or not target.resolve().is_relative_to(root.resolve()):
            raise SourceViolation(f"Missing/escaping manifest path: {text!r}")


def load_indexes(cache: Path) -> tuple[dict[str, bytes], dict]:
    root = safe_path(cache)
    manifest_path = safe_path(root / "manifest.json")
    if not manifest_path.is_file() or manifest_path.stat().st_size > 1024 * 1024:
        raise ValueError("Cache manifest.json missing or oversized")
    manifest_raw = manifest_path.read_bytes()
    manifest = json.loads(manifest_raw.decode("utf-8"))
    if manifest.get("schema_version") != 1:
        raise ValueError("Unsupported cache manifest schema")
    timestamp = dt.datetime.fromisoformat(manifest["fetched_at"].replace("Z", "+00:00"))
    if timestamp.tzinfo is None:
        raise ValueError("Cache timestamp requires a timezone")
    entries = manifest["indexes"]
    if set(entries) != set(BRANCHES):
        raise ValueError("Cache must contain exactly all ten checker branches")
    bodies = {}
    for branch in BRANCHES:
        entry = entries[branch]
        expected = f"{INDEX_BASE}/{branch}/addons.xml.gz"
        if entry["url"] != expected or entry["filename"] != f"{branch}.xml.gz":
            raise ValueError(f"Unexpected index identity for {branch}")
        path = safe_path(root / entry["filename"])
        if not path.is_file() or path.stat().st_size > MAX_GZIP:
            raise ValueError(f"Missing or oversized index: {branch}")
        raw = path.read_bytes()
        if len(raw) != entry["size"] or hashlib.sha256(raw).hexdigest() != entry["sha256"]:
            raise ValueError(f"Index hash/size mismatch: {branch}")
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as zipped:
            xml = zipped.read(MAX_XML + 1)
        if len(xml) > MAX_XML or b"<!DOCTYPE" in xml.replace(b"\x00", b"").upper() or b"<!ENTITY" in xml.replace(b"\x00", b"").upper():
            raise ValueError(f"Unsafe or oversized index XML: {branch}")
        if ET.fromstring(xml).tag != "addons":
            raise ValueError(f"Invalid repository XML root: {branch}")
        bodies[expected] = raw
        bodies[expected.replace("https://", "http://", 1)] = raw
    evidence = {"fetched_at": manifest["fetched_at"],
                "manifest_sha256": hashlib.sha256(manifest_raw).hexdigest(),
                "indexes": entries, "fixture": manifest.get("fixture", False)}
    return bodies, evidence


def _worker(args: argparse.Namespace) -> int:
    evidence: dict = {"requested_indexes": [], "blocked_url_checks": [],
                      "network_violations": [], "online_url_checks": "unverified"}
    result_path = Path(args.result)
    code = 2
    try:
        if metadata.version("kodi-addon-checker") != "0.0.36":
            raise ValueError("Replay is reviewed only for kodi-addon-checker==0.0.36")
        bodies, cache_evidence = load_indexes(Path(args.cache))
        evidence["cache"] = cache_evidence
        evidence["checker_version"] = metadata.version("kodi-addon-checker")
        source = Path(args.addon)
        paths = inspect_source(source)
        if any(p.name == ".tests-config.json" for p in paths):
            raise SourceViolation(".tests-config.json is rejected; it can disable validation")

        def forbidden(*unused, **kwargs):
            event = "Unexpected network or child-process operation"
            evidence["network_violations"].append(event)
            raise ReplayViolation(event)

        for name in ("connect", "connect_ex", "send", "sendall", "sendto", "sendmsg"):
            if hasattr(socket.socket, name):
                setattr(socket.socket, name, forbidden)
        socket.create_connection = forbidden
        socket.getaddrinfo = forbidden
        socket.gethostbyname = forbidden
        socket.gethostbyname_ex = forbidden
        socket.gethostbyaddr = forbidden
        subprocess.Popen = forbidden
        os.system = forbidden
        os.popen = forbidden

        import requests

        def replay(session, request, **kwargs):
            if request.method == "GET" and request.url in bodies:
                response = requests.Response()
                response.status_code = 200
                response.url = request.url
                response.request = request
                response._content = bodies[request.url]
                response.headers["Content-Type"] = "application/gzip"
                evidence["requested_indexes"].append(request.url)
                return response
            if request.method == "HEAD":
                evidence["blocked_url_checks"].append(request.url)
                raise requests.exceptions.ConnectionError(
                    f"Offline replay: online URL check unverified: {request.url}")
            event = f"Unexpected network request: {request.method} {request.url}"
            evidence["network_violations"].append(event)
            raise ReplayViolation(event)

        requests.sessions.Session.send = replay
        from kodi_addon_checker import ValidKodiVersions
        if tuple(ValidKodiVersions) != BRANCHES:
            raise ValueError("Installed checker branch protocol changed")
        from kodi_addon_checker.__main__ import main
        with tempfile.TemporaryDirectory(prefix="kodi-checker-") as temporary:
            work = Path(temporary)
            copied = copy_source(source, work / source.name)
            inspect_manifest_paths(copied)
            previous = Path.cwd()
            os.chdir(work)
            sys.argv = ["kodi-addon-checker", "--branch", args.branch,
                        "--reporter", "console", str(copied)]
            try:
                try:
                    main()
                    code = 0
                except SystemExit as exc:
                    code = exc.code if isinstance(exc.code, int) else 1
            finally:
                os.chdir(previous)
        if evidence["network_violations"]:
            raise ReplayViolation("Unexpected network attempt occurred")
        if len(evidence["requested_indexes"]) != len(BRANCHES):
            raise ReplayViolation("Checker did not request exactly all ten indexes")
        evidence["worker_status"] = "finished"
    except BaseException as exc:
        evidence["worker_status"] = "error"
        evidence["failure"] = f"{type(exc).__name__}: {exc}"
        traceback.print_exc()
        code = 2 if isinstance(exc, (ValueError, SourceViolation, metadata.PackageNotFoundError)) else 1
    finally:
        result_path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    return code


def _report(stdout: str, stderr: str, code: int | None, evidence: dict) -> dict:
    lines = ANSI.sub("", stdout).splitlines()
    summary = next((line for line in reversed(lines)
                    if re.match(r"^(ERROR|WARN|INFO): We found ", line)), None)
    findings = [line for line in lines if re.match(r"^(ERROR|WARN|INFO): ", line)
                and line != summary]
    errors = [line[7:] for line in findings if line.startswith("ERROR: ")]
    warnings = [line[6:] for line in findings if line.startswith("WARN: ")]
    completed = summary is not None and evidence.get("worker_status") == "finished"
    if completed:
        match = re.search(r"We found (\d+) problems and (\d+) warnings", summary)
        warn_match = re.search(r"We found no problems and (\d+) warnings", summary)
        counts = (int(match[1]), int(match[2])) if match else (0, int(warn_match[1]) if warn_match else 0)
    else:
        counts = (len(errors), len(warnings))
    passed = completed and code == 0 and counts[0] == 0
    return {"status": "passed" if passed else "failed" if completed else "error",
            "passed": passed, "completed": completed, "exit_code": code,
            "returncode": code, "stdout": stdout, "stderr": stderr,
            "output": stdout + stderr, "errors": errors, "warnings": warnings,
            "error_count": counts[0], "problem_count": counts[0],
            "warning_count": counts[1], "summary": summary,
            "online_url_checks": "unverified", "replay": evidence,
            "infrastructure_errors": [evidence["failure"]] if evidence.get("failure") else []}


def run_checker(addon: Path, branch: str = "nexus", cache: Path | None = None,
                timeout: float = 180) -> dict:
    """Return untouched subprocess streams plus parsed official records/counts.

    No cache means an explicit error (no network fallback). Exceptions/timeouts
    remain infrastructure failures; they never become a fabricated pass.
    """
    if cache is None:
        return _report("", "", None, {"worker_status": "error",
                       "failure": "An explicit complete index cache is required",
                       "online_url_checks": "unverified"})
    with tempfile.TemporaryDirectory(prefix="kodi-replay-result-") as temporary:
        result_path = Path(temporary) / "worker.json"
        command = [sys.executable, "-I", "-B", str(Path(__file__).absolute()),
                   "--addon", str(Path(addon).absolute()), "--branch", branch,
                   "--cache", str(Path(cache).absolute()), "--result", str(result_path)]
        try:
            result = subprocess.run(command, capture_output=True,
                                    cwd=temporary, timeout=timeout)
            evidence = json.loads(result_path.read_text()) if result_path.exists() else {
                "worker_status": "error", "failure": "Missing replay worker evidence"}
            report = _report(result.stdout.decode("utf-8", "replace"),
                             result.stderr.decode("utf-8", "replace"), result.returncode, evidence)
        except subprocess.TimeoutExpired as exc:
            def decoded(value):
                return value.decode("utf-8", "replace") if isinstance(value, bytes) else value or ""
            report = _report(decoded(exc.stdout), decoded(exc.stderr), None,
                             {"worker_status": "error", "failure": "Checker timeout",
                              "online_url_checks": "unverified"})
        except (OSError, ValueError) as exc:
            report = _report("", "", None, {"worker_status": "error", "failure": str(exc)})
        report["command"] = command
        return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--addon", required=True)
    parser.add_argument("--branch", default="nexus", choices=BRANCHES)
    parser.add_argument("--cache", required=True)
    parser.add_argument("--result", required=True, help="Replay evidence JSON, separate from official streams")
    raise SystemExit(_worker(parser.parse_args()))
