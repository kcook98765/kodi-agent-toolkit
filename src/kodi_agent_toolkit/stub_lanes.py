"""Read-only source qualification and active static-toolchain discovery.

A checker branch does not select a virtualenv. Never download packages or infer
Kodi runtime compatibility from an installed stub distribution.
"""
from __future__ import annotations

from importlib import metadata
import platform
import sys

LANES = (
    ("matrix", "19.5", "19.0.3", "requirements-matrix.lock", "qualified"),
    ("nexus", "20.5", "20.0.1", "requirements-dev.lock", "qualified"),
    ("omega", "21.3", "21.0.0", "requirements-omega.lock", "qualified"),
    ("piers", "22.0 RC2", "22.0.1rc1", "requirements-piers.lock", "qualified"),
)
TOOL_PINS = {"mypy": "2.4.0", "kodi-addon-checker": "0.0.36"}
# Platforms with recorded static fixtures, not native Kodi qualification.
QUALIFIED_PLATFORMS = {"matrix": ("linux", "win32"), "nexus": ("linux", "win32"), "omega": ("linux",), "piers": ("linux", "win32")}


def stub_lanes() -> dict:
    """Describe source pins and observed tools; cache/add-on checks remain required."""
    tools = {}
    for package in ("Kodistubs", *TOOL_PINS):
        try:
            tools[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            tools[package] = None
    installed = tools["Kodistubs"]
    interpreter_matches = (platform.python_implementation() == "CPython"
                           and sys.version_info[:2] == (3, 12))
    lanes = []
    for branch, kodi_version, expected, requirements, qualification in LANES:
        match = installed == expected
        reasons = []
        if not qualification:
            reasons.append("Source lane qualification is pending")
        if not match:
            reasons.append(f"Requires Kodistubs=={expected}; observed {installed!r}")
        if not interpreter_matches:
            reasons.append("Recorded qualification requires CPython 3.12")
        if sys.platform not in QUALIFIED_PLATFORMS.get(branch, ()):
            reasons.append(f"No recorded static qualification on {sys.platform}")
        for package, pin in TOOL_PINS.items():
            if tools[package] != pin:
                reasons.append(f"Requires {package}=={pin}; observed {tools[package]!r}")
        lanes.append({
            "branch": branch,
            "managed_kodi_version": kodi_version,
            "expected_kodistubs": expected,
            "prerelease": branch == "piers",
            "requirements": requirements,
            "lock_available": bool(qualification),
            "static_qualification": qualification or "pending",
            "qualified_python": "CPython 3.12" if qualification else None,
            "qualified_platforms": list(QUALIFIED_PLATFORMS.get(branch, ())),
            "installed_in_this_interpreter": match,
            "ready_for_qualified_static_checks": not reasons,
            "readiness_limits": reasons,
        })
    return {
        "python_executable": sys.executable,
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform": sys.platform,
        "installed_kodistubs": installed,
        "installed_tools": tools,
        "lanes": lanes,
        "notes": [
            "A --branch argument does not install or select Kodistubs or change Python interpreters.",
            "Use a separate interpreter and the lane's complete hash-locked dependencies.",
            "Piers is a bounded prerelease lane compared to exact Kodi RC2 source; see docs/piers-stubs.md for limits.",
            "Readiness reports observed tool versions, not verification of the full lock, cache or add-on.",
            "A static pass is not native Kodi qualification, even when the stub major matches.",
        ],
    }
