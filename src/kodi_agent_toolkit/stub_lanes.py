"""Read-only Kodi version / Kodistubs lane discovery.

A checker branch does not select a virtualenv. Never download packages or infer
Kodi runtime compatibility from an installed stub distribution.
"""
from __future__ import annotations

from importlib import metadata
import sys

LANES = (
    ("matrix", "19.5", "19.0.3", "requirements-matrix.in", None),
    ("nexus", "20.5", "20.0.1", "requirements-dev.lock", "qualified"),
    ("omega", "21.3", "21.0.0", "requirements-omega.lock", "qualified"),
    ("piers", "22.0 RC2", "22.0.1rc1", "requirements-piers.in", None),
)


def stub_lanes() -> dict:
    """Describe source pins and the active interpreter, not live server state."""
    try:
        installed = metadata.version("Kodistubs")
    except metadata.PackageNotFoundError:
        installed = None
    lanes = []
    for branch, kodi_version, expected, requirements, qualification in LANES:
        match = installed == expected
        # An unqualified lane cannot become qualified merely by pip installing it.
        lanes.append({
            "branch": branch,
            "managed_kodi_version": kodi_version,
            "expected_kodistubs": expected,
            "requirements": requirements,
            "lock_available": bool(qualification),
            "static_qualification": qualification or "pending",
            "installed_in_this_interpreter": match,
            "ready_for_qualified_static_checks": match and qualification == "qualified",
        })
    return {
        "python_executable": sys.executable,
        "installed_kodistubs": installed,
        "lanes": lanes,
        "notes": [
            "A --branch argument does not install or select Kodistubs or change Python interpreters.",
            "Run validation using a separate interpreter with matching major-version stubs.",
            "Matrix and Piers have candidate version pins only; hash-locked setup and real checks remain pending.",
            "A static pass is not native Kodi qualification, even when the stub major matches.",
        ],
    }
