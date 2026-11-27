from pathlib import Path

from kodi_agent_toolkit.opencode_readiness import assess


def test_reports_effective_role_denials_and_stale_discovery(tmp_path: Path) -> None:
    project = tmp_path / "project"
    root = tmp_path / "current" / "skills"
    old = tmp_path / "old" / "skills"
    skill = "kodi-version-compatibility"
    manifest = root / skill / "SKILL.md"
    reference = manifest.parent / "references" / "versions.md"
    reference.parent.mkdir(parents=True)
    manifest.write_text("Read references/versions.md for evidence.", encoding="utf-8")
    reference.touch()
    rules = [
        {"permission": "*", "pattern": "*", "action": "allow"},
        {"permission": "skill", "pattern": "*", "action": "deny"},
        {"permission": "external_directory", "pattern": "*", "action": "deny"},
        {"permission": "external_directory", "pattern": old.as_posix() + "/**", "action": "allow"},
        {"permission": "lab_managed_gui", "pattern": "*", "action": "deny"},
    ]
    agents = [{"name": "role", "permission": rules}]
    stale = assess(project, None, root, "role", [skill], agents,
                   [{"name": skill, "location": str(old / skill / "SKILL.md")}])
    assert len(stale) == 1 and "Point skills.paths" in stale[0]
    skills = [{"name": skill, "location": str(manifest)}]
    problems = assess(
        project, None, root, "role", [skill], agents, skills, managed_connection="lab",
        managed_tools=["managed_gui"], mcp_status={"lab": {"status": "connected"}},
        lab_tools=set(),
    )
    assert len(problems) == 4
    assert any("skill " + skill + " is deny" in problem for problem in problems)
    assert any("versions.md is deny by external_directory" in problem for problem in problems)
    assert any("discovery is missing managed_gui" in problem for problem in problems)
    assert any("lab_managed_gui is deny" in problem for problem in problems)
    rules.extend([
        {"permission": "skill", "pattern": skill, "action": "allow"},
        {"permission": "external_directory", "pattern": reference.parent.as_posix() + "/*", "action": "allow"},
        {"permission": "lab_managed_gui", "pattern": "*", "action": "allow"},
    ])
    assert not assess(
        project, None, root, "role", [skill], agents, skills, managed_connection="lab",
        managed_tools=["managed_gui"], mcp_status={"lab": {"status": "connected"}},
        lab_tools={"managed_gui"},
    )
