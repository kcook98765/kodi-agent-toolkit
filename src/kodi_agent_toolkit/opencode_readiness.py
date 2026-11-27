"""Check the effective OpenCode 1.19.x project and role before native work."""

from __future__ import annotations

import base64
import http.client
import json
import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlencode, urlsplit

REFERENCE = re.compile(r"(?<![\w/])references/[\w./-]+\.md\b")


def matches(value: str, pattern: str) -> bool:
    value = value.replace("\\", "/")
    pattern = pattern.replace("\\", "/")
    regex = re.escape(pattern).replace(r"\*", ".*").replace(r"\?", ".")
    if regex.endswith(r"\ .*"):
        regex = regex[:-4] + r"( .*)?"
    flags = re.DOTALL | (re.IGNORECASE if os.name == "nt" else 0)
    return re.fullmatch(regex, value, flags) is not None


def action(rules: list[dict[str, str]], permission: str, pattern: str = "*") -> str:
    return next(
        (rule["action"] for rule in reversed(rules)
         if matches(permission, rule["permission"]) and matches(pattern, rule["pattern"])),
        "ask",
    )


def assess(
    project: Path,
    worktree: Path | None,
    skills_root: Path,
    role: str,
    expected_skills: list[str],
    agents: list[dict[str, Any]],
    skills: list[dict[str, Any]],
    *,
    managed_connection: str | None = None,
    managed_tools: list[str] | None = None,
    mcp_status: dict[str, Any] | None = None,
    lab_tools: set[str] | None = None,
) -> list[str]:
    rules = next((agent["permission"] for agent in agents if agent["name"] == role), None)
    if rules is None:
        return [f"Role {role} is missing. Load the intended OpenCode preset in this project."]
    discovered = {skill["name"]: Path(skill["location"]) for skill in skills}
    problems = []
    for name in expected_skills:
        expected = skills_root / name / "SKILL.md"
        location = discovered.get(name)
        if not expected.is_file() or location is None or location.resolve() != expected.resolve():
            problems.append(
                f"{name} discovery resolved to {location or 'missing'}. "
                f"Point skills.paths or the project skill installation to {expected.parent}."
            )
            continue
        allowed = action(rules, "skill", name)
        if allowed != "allow":
            problems.append(
                f"{role} skill {name} is {allowed}. Review the role's skill rule for this name."
            )
        for ref in sorted(set(REFERENCE.findall(expected.read_text(encoding="utf-8")))):
            path = (location.parent / ref).resolve()
            if not path.is_relative_to(location.parent.resolve()) or not path.is_file():
                problems.append(f"{name} reference {ref} is missing or outside the skill directory.")
                continue
            if not path.is_relative_to(project) and (
                worktree is None or not path.is_relative_to(worktree)
            ):
                directory_rule = path.parent.as_posix() + "/*"
                read = action(rules, "external_directory", directory_rule)
                if read != "allow":
                    problems.append(
                        f"{role} reference {path} is {read} by external_directory. "
                        f"Review a scoped allow for {directory_rule}."
                    )
            read = action(rules, "read", Path(os.path.relpath(path, worktree or project)).as_posix())
            if read != "allow":
                problems.append(f"{role} read rule for {path} is {read}. Review this reference.")
    if managed_connection:
        status = (mcp_status or {}).get(managed_connection, {}).get("status", "missing")
        if status != "connected":
            problems.append(
                f"MCP {managed_connection} is {status}. Check the selected project connection."
            )
        for tool in managed_tools or []:
            if tool not in (lab_tools or set()):
                problems.append(
                    f"Lab discovery is missing {tool}. Check the authorized Lab credential and version."
                )
            name = f"{managed_connection}_{tool}"
            allowed = action(rules, name)
            if allowed != "allow":
                problems.append(f"{role} MCP tool {name} is {allowed}. Review its exact tool rule.")
    return problems


def inspect(
    server: str,
    project: Path,
    skills_root: Path,
    role: str,
    skills_expected: list[str],
    managed_connection: str | None,
    managed_tools: list[str],
    catalog: Path | None,
) -> dict[str, Any]:
    target = urlsplit(server)
    if (target.scheme != "http" or target.hostname not in {"127.0.0.1", "::1", "localhost"}
            or target.username or target.path not in ("", "/") or target.query or target.fragment):
        raise ValueError("Use the local OpenCode HTTP server origin")
    project = project.resolve(strict=True)
    skills_root = skills_root.resolve()
    headers = {"Accept": "application/json"}
    if password := os.environ.get("OPENCODE_SERVER_PASSWORD"):
        username = os.environ.get("OPENCODE_SERVER_USERNAME", "opencode")
        basic = base64.b64encode(f"{username}:{password}".encode()).decode()
        headers["Authorization"] = f"Basic {basic}"
    query = "?" + urlencode({"directory": str(project)})
    connection = http.client.HTTPConnection(target.hostname, target.port, timeout=10)

    def get(path: str) -> Any:
        connection.request("GET", path + query, headers=headers)
        reply = connection.getresponse()
        if reply.status != 200:
            raise ValueError(f"OpenCode {path} returned HTTP {reply.status}. Check server and authentication.")
        payload = reply.read(4 * 1024**2 + 1)
        if len(payload) > 4 * 1024**2:
            raise ValueError(f"OpenCode {path} reply exceeds the readiness limit")
        return json.loads(payload)

    try:
        agents, skills, location = get("/agent"), get("/skill"), get("/path")
        mcp = get("/mcp") if managed_connection else None
    finally:
        connection.close()
    lab_tools = None
    if catalog:
        raw = json.loads(catalog.read_bytes())
        lab_tools = {item["name"] for item in raw.get("result", raw)["tools"]}
    worktree = location.get("worktree")
    problems = assess(
        project, Path(worktree).resolve() if worktree and worktree != "/" else None,
        skills_root, role, skills_expected, agents, skills,
        managed_connection=managed_connection, managed_tools=managed_tools,
        mcp_status=mcp, lab_tools=lab_tools,
    )
    return {"passed": not problems, "role": role, "problems": problems}
