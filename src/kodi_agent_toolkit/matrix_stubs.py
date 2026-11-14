"""One source-verified correction for the exact published Matrix stub artifact.

Generate a temporary mypy shadow; never edit installed packages or execute stubs.
Kodi 19.5 ListItem.h / ListItem.cpp support numeric and list info-label values.
See docs/matrix-stubs.md for pinned source, artifact hash and remaining limits.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

CAST_OLD = "def setCast(self, actors: List[Dict[str, str]]) -> None:"
CAST_NEW = "def setCast(self, actors: List[Mapping[str, Union[str, int]]]) -> None:"
GUI_SHA256 = "45c11ed1c23872eb5b56d6d1e75815bfad5c07047115b0cc1e968e80bd1225f2"
OLD = "def setInfo(self, type: str, infoLabels: Dict[str, str]) -> None:"
NEW = ("def setInfo(self, type: str, infoLabels: Mapping[str, "
       "Union[str, int, float, List[Union[str, Tuple[str, Union[str, int, float]]]]]]) -> None:")


def matrix_shadow(gui: Path, work: Path) -> tuple[Path, dict]:
    raw = gui.read_bytes()
    if hashlib.sha256(raw).hexdigest() != GUI_SHA256:
        raise ValueError("Matrix xbmcgui artifact hash differs from reviewed Kodistubs 19.0.3")
    text = raw.decode("utf-8")
    if text.count(OLD) != 1 or text.count(CAST_OLD) != 1:
        raise ValueError("Matrix setInfo signature differs from reviewed Kodistubs 19.0.3")
    shadow = work / "xbmcgui.py"
    shadow.write_text(text.replace("from typing import Union,", "from typing import Mapping, Union,", 1)
                      .replace(OLD, NEW, 1).replace(CAST_OLD, CAST_NEW, 1), encoding="utf-8")
    return shadow, {"id": "matrix-19.0.3-setinfo", "upstream_sha256": GUI_SHA256,
                    "shadow_sha256": hashlib.sha256(shadow.read_bytes()).hexdigest(),
                    "scope": "ListItem.setInfo/setCast value annotations only; installed packages unchanged"}
