"""Admit exact bytes to Kodi Lab's fixed authenticated managed MCP operation."""
from __future__ import annotations

import base64
import hashlib
import http.client
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
from uuid import uuid4

MAX_MCP_BODY = 64 * 1024


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
        raw = file.read(MAX_MCP_BODY * 3 // 4 + 1)
    if not raw or len(raw) > MAX_MCP_BODY * 3 // 4:
        raise ValueError("ZIP exceeds the Kodi Lab MCP request limit or is empty")
    digest = hashlib.sha256(raw).hexdigest()
    request_id = uuid4().hex
    body = json.dumps({
        "jsonrpc": "2.0", "id": request_id, "method": "tools/call",
        "params": {"name": "managed_package_import", "arguments": {
            "encoded": base64.b64encode(raw).decode("ascii"), "digest": digest,
        }},
    }, separators=(",", ":")).encode()
    if len(body) > MAX_MCP_BODY:
        raise ValueError("ZIP exceeds the Kodi Lab MCP request limit")

    with token_file.open(encoding="ascii") as file:
        token = file.read(513).strip()
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,512}", token):
        raise ValueError("Expected a private Kodi Lab bearer token file")
    connection_type = (http.client.HTTPSConnection
                       if target.scheme == "https" else http.client.HTTPConnection)
    connection = connection_type(target.hostname, target.port, timeout=25)
    try:
        connection.request("POST", target.path, body=body, headers={
            "Authorization": f"Bearer {token}",
            "MCP-Protocol-Version": "2025-11-25",
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
        })
        response = connection.getresponse()
        if response.status != 200:
            raise ValueError(f"Kodi Lab admission returned HTTP {response.status}")
        payload = response.read(MAX_MCP_BODY + 1)
        if len(payload) > MAX_MCP_BODY:
            raise ValueError("Kodi Lab admission response exceeded its expected size")
    finally:
        connection.close()

    try:
        reply = json.loads(payload)
        if reply["id"] != request_id or reply["jsonrpc"] != "2.0":
            raise ValueError
        result = reply["result"]
        content = result["content"]
        if len(content) != 1 or content[0]["type"] != "text":
            raise ValueError
        value = content[0]["text"]
        refused = result.get("isError", False)
        if not isinstance(value, str) or not isinstance(refused, bool):
            raise ValueError
        if not refused:
            identity = json.loads(value)["result"]
            addon, version = identity["addon"], identity["version"]
            if (identity["digest"] != digest or not re.fullmatch(r"[a-z][a-z0-9_.-]{1,95}", addon)
                    or not re.fullmatch(r"[0-9][a-zA-Z0-9.+~-]{0,39}", version)):
                raise ValueError
    except (KeyError, TypeError, AttributeError, IndexError, ValueError) as error:
        raise ValueError("Unexpected Kodi Lab admission result; verify the package before retrying") from error
    if refused:
        code = value if re.fullmatch(r"[a-z_]{1,96}", value) else "unconfirmed"
        raise ValueError(f"Kodi Lab package admission: {code}")
    return {"addon": addon, "version": version, "digest": digest}
