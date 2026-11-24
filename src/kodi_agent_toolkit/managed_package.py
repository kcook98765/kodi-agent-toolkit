"""Admit a ZIP through Kodi Lab's authenticated managed package transfer."""
from __future__ import annotations

import hashlib
import http.client
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
MAX_ZIP = 32 * 1024**2
MAX_REPLY = 64 * 1024


def admit_package(package: Path, endpoint: str, token_file: Path) -> dict[str, str]:
    if package.suffix.lower() != ".zip" or not package.is_file():
        raise ValueError("Select a local add-on ZIP file")
    target = urlsplit(endpoint)
    if (not target.hostname or target.username is not None or target.query or target.fragment
            or not target.path.endswith("/mcp")
            or not (target.scheme == "https" or target.scheme == "http"
                    and target.hostname in {"localhost", "127.0.0.1", "::1"})):
        raise ValueError("Use the authorized Kodi Lab HTTPS MCP URL or a loopback HTTP MCP URL")

    with package.open("rb") as file:
        raw = file.read(MAX_ZIP + 1)
    if not raw or len(raw) > MAX_ZIP:
        raise ValueError("ZIP exceeds the 32 MiB managed package limit or is empty")
    digest = hashlib.sha256(raw).hexdigest()

    with token_file.open(encoding="ascii") as file:
        token = file.read(513).strip()
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,512}", token):
        raise ValueError("Expected a private Kodi Lab bearer token file")
    connection_type = (http.client.HTTPSConnection
                       if target.scheme == "https" else http.client.HTTPConnection)
    connection = connection_type(target.hostname, target.port, timeout=40)
    try:
        connection.request("POST", target.path, body=raw, headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/zip",
            "X-Kodi-Lab-Package-SHA256": digest,
        })
        response = connection.getresponse()
        payload = response.read(MAX_REPLY + 1)
        if len(payload) > MAX_REPLY:
            raise ValueError("Kodi Lab admission response exceeded its expected size")
    finally:
        connection.close()

    if response.status != 200:
        code = ""
        try:
            error_reply = json.loads(payload)
            code = error_reply.get("code") or error_reply.get("error")
        except (ValueError, AttributeError):
            pass
        suffix = f" ({code})" if isinstance(code, str) and re.fullmatch(r"[a-z_]{1,96}", code) else ""
        raise ValueError(f"Kodi Lab admission returned HTTP {response.status}{suffix}")
    try:
        identity = json.loads(payload)["result"]
        addon, version = identity["addon"], identity["version"]
        if (identity["digest"] != digest or not re.fullmatch(r"[a-z][a-z0-9_.-]{1,95}", addon)
                or not re.fullmatch(r"[0-9][a-zA-Z0-9.+~-]{0,39}", version)):
            raise ValueError
    except (KeyError, TypeError, AttributeError, IndexError, ValueError) as error:
        raise ValueError("Unexpected Kodi Lab admission result; verify the package before retrying") from error
    return {"addon": addon, "version": version, "digest": digest}
