"""Bounded project/manifest discovery. Reads files; never guesses an entry point."""
from __future__ import annotations

import os
from pathlib import Path, PurePosixPath
import re
import stat
import xml.etree.ElementTree as ET

from .checker_runner import safe_path, SourceViolation

EXCLUDED = frozenset({".git", ".venv", "venv", "node_modules", "__pycache__",
                      ".local", ".mypy_cache", ".pytest_cache", ".ruff_cache"})
MAX_ENTRIES = 4096
MAX_MANIFEST_BYTES = 256 * 1024


def _project_root(directory: Path) -> Path:
    # Nearest actual repository/workspace marker wins; an add-on without a
    # containing workspace uses its own directory. Never search another home.
    for parent in (directory, *directory.parents):
        if any((parent / marker).exists() for marker in (".git", "pyproject.toml")):
            return parent
    for parent in (directory, *directory.parents):
        if (parent / "addon.xml").is_file():
            return parent
    return directory


def discover(directory: Path = Path(".")) -> dict:
    value = str(directory)
    if os.name != "nt" and (re.match(r"^[A-Za-z]:", value) or "\\" in value):
        raise SourceViolation("Windows path in a POSIX session; translate with wslpath in WSL and verify it, or use a native path")
    scan = safe_path(Path(directory))
    if not scan.is_dir():
        raise SourceViolation(f"Discovery directory does not exist: {scan}")
    project = _project_root(scan)
    if value == ".":
        # A nested add-on session should inspect its own manifest, not siblings
        # or a global skill directory. Keep the enclosing repo as path origin.
        scan = next((parent for parent in (scan, *scan.parents)
                     if parent.is_relative_to(project) and (parent / "addon.xml").is_file()), project)
    result = {"passed": False, "project_root": str(project), "scan_root": str(scan),
              "addons": [], "omitted": [], "errors": [], "complete": True,
              "guidance": "Use only returned existing paths. No manifest found: confirm the requested root; do not invent addon.xml or entry files."}
    found: list[Path] = []
    pending = [scan]
    count = 0
    while pending:
        current = pending.pop()
        try:
            safe_path(current)
            with os.scandir(current) as entries:
                batch = []
                for entry in entries:
                    count += 1
                    if count > MAX_ENTRIES:
                        result["omitted"].append({"path": current.relative_to(project).as_posix(), "reason": "scan-entry-limit"})
                        pending.clear()
                        break
                    batch.append(entry)
            for entry in sorted(batch, key=lambda e: e.name, reverse=True):
                path = Path(entry.path)
                relative = path.relative_to(project).as_posix()
                info = entry.stat(follow_symlinks=False)
                if entry.is_symlink() or getattr(info, "st_file_attributes", 0) & 0x400:
                    result["omitted"].append({"path": relative, "reason": "link-or-reparse-excluded"})
                elif entry.is_dir(follow_symlinks=False):
                    if entry.name not in EXCLUDED:
                        pending.append(path)
                elif entry.name == "addon.xml" and stat.S_ISREG(info.st_mode):
                    found.append(path)
        except (OSError, ValueError, RuntimeError) as exc:
            result["omitted"].append({"path": current.relative_to(project).as_posix(), "reason": str(exc)})
    for manifest in sorted(found):
        addon = manifest.parent
        record = {"addon_dir": addon.relative_to(project).as_posix(),
                  "manifest": manifest.relative_to(project).as_posix(),
                  "entry_points": [], "files": [], "directories": [], "manifest_error": None}
        # Enumerate only actual files; keep the same shared bound across all
        # add-ons. Links/omissions are explicit, not verified artifacts.
        for current, dirs, names in os.walk(addon, followlinks=False):
            record["directories"].append(Path(current).relative_to(addon).as_posix())
            dirs[:] = sorted(d for d in dirs if d not in EXCLUDED and
                             not (Path(current) / d).is_symlink() and
                             not getattr((Path(current) / d).lstat(), "st_file_attributes", 0) & 0x400)
            for name in sorted(names):
                path = Path(current) / name
                if path.is_symlink() or getattr(path.lstat(), "st_file_attributes", 0) & 0x400:
                    continue
                if count >= MAX_ENTRIES:
                    result["omitted"].append({"path": record["addon_dir"], "reason": "file-inventory-limit"})
                    break
                count += 1
                if path.is_file():
                    record["files"].append(path.relative_to(addon).as_posix())
            if count >= MAX_ENTRIES:
                break
        try:
            with manifest.open("rb") as stream:
                raw = stream.read(MAX_MANIFEST_BYTES + 1)
            if len(raw) > MAX_MANIFEST_BYTES or b"<!DOCTYPE" in raw.replace(b"\x00", b"").upper() or b"<!ENTITY" in raw.replace(b"\x00", b"").upper():
                raise ValueError("Unsafe or oversized manifest")
            xml = ET.fromstring(raw)
            if xml.tag != "addon":
                raise ValueError("Manifest root must be addon")
            record["addon_id"] = xml.get("id")
            record["python_requirement"] = [item.get("version") for item in xml.findall("requires/import") if item.get("addon") == "xbmc.python"]
            for extension in xml.findall("extension"):
                for key in ("library", "start"):
                    declared = extension.get(key)
                    if declared is None:
                        continue
                    raw_path = declared.replace("\\", "/")
                    parts = PurePosixPath(raw_path)
                    safe = bool(declared) and not parts.is_absolute() and ".." not in raw_path.split("/") and ":" not in declared and "\x00" not in declared
                    normalized = parts.as_posix()
                    exists = safe and (normalized in record["files"] or normalized in record["directories"])
                    record["entry_points"].append({"path": normalized, "exists": exists, "extension": extension.get("point")})
        except (OSError, ValueError, ET.ParseError) as exc:
            record["manifest_error"] = str(exc)
        result["addons"].append(record)
    result["complete"] = not result["omitted"]
    if not found:
        result["errors"].append("No existing addon.xml found in the bounded scan")
    result["passed"] = bool(found) and not result["errors"]
    return result
