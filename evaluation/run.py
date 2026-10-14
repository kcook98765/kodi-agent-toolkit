"""Sequential actual-OpenCode evaluation in disposable repositories."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import threading
import time
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from processes import launch_options, stop_tree

ROOT = Path(__file__).resolve().parents[1]
TASKS = json.loads((ROOT / "evaluation/tasks.json").read_text())
PRIVATE = Path(os.environ.get("KODI_EVAL_PRIVATE", str(Path.home() / ".local/share/kodi-agent-toolkit/evaluation")))
# Exact-value redaction is opt-in; never search another application's credentials.
TOKENS = [Path(name).read_text(encoding="utf-8").strip()
          for name in os.environ.get("KODI_EVAL_SECRET_FILES", "").split(os.pathsep) if name]

def clean(value):
    if isinstance(value, dict):
        return {key: "[REDACTED]" if key.lower() in {"authorization", "cookie", "token"} else clean(item)
                for key, item in value.items()}
    if isinstance(value, list):
        return [clean(x) for x in value]
    if isinstance(value, str):
        for token in TOKENS:
            if token:
                value = value.replace(token, "[CREDENTIAL REDACTED]")
        return re.sub(r"data:image/[^;]+;base64,[A-Za-z0-9+/=]+", "[IMAGE REDACTED]", value)
    return value

def run(model, task, enabled, label, timeout=180, skill_revision=None):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,119}", label):
        raise ValueError("Label must be one safe filename component")
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    revision = None
    if skill_revision:
        revision = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "--verify", skill_revision + "^{commit}"], text=True).strip()
    model_id = model
    if "/" not in model_id:
        raise ValueError("Use an explicit provider/model ID from your private OpenCode configuration")
    output = PRIVATE / "runs" / label
    if output.exists():
        raise ValueError("Use a fresh label; existing evidence is preserved")
    project = output / "project"
    project.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(project)], check=True)
    shutil.copy2(ROOT / "AGENTS.md", project / "AGENTS.md")
    addon = project / "fixtures/script.toolkit.sample"
    shutil.copytree(ROOT / "fixtures" / TASKS[task]["fixture"] / "script.toolkit.sample", addon)
    if task == "boundary":
        shutil.copytree(ROOT / "fixtures/valid/script.toolkit.sample", output / "outside-test")
    if TASKS[task].get("missing_manifest"):
        (addon / "addon.xml").unlink()
    tools = project / ".opencode/tools"
    tools.mkdir(parents=True)
    shutil.copy2(ROOT / ".opencode/tools/kodi_validate.ts", tools)
    shutil.copytree(ROOT / ".opencode/lib", project / ".opencode/lib")
    if task.startswith('review'):
        shutil.copy2(ROOT / ".opencode/tools/kodi_review.ts", tools)
    # Reuse the installed OpenCode SDK; no package installation during agent trials.
    sdk = Path(os.environ.get("OPENCODE_SDK_DIR", str(Path.home() / ".config/opencode/node_modules")))
    (project / ".opencode/node_modules").symlink_to(sdk, target_is_directory=True)
    if enabled:
        name = TASKS[task]["skill"]
        if revision:
            prefix = ".agents/skills/" + ("" if os.environ.get("KODI_EVAL_SKILL_CATALOG") == "all" else name + "/")
            paths = subprocess.check_output(["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", revision, "--", prefix], text=True).splitlines()
            if not paths:
                raise ValueError("No skills at requested revision")
            for name in paths:
                destination = project / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(subprocess.check_output(["git", "-C", str(ROOT), "show", revision + ":" + name]))
        elif os.environ.get("KODI_EVAL_SKILL_CATALOG") == "all":
            shutil.copytree(ROOT / ".agents/skills", project / ".agents/skills")
        else:
            shutil.copytree(ROOT / ".agents/skills" / name, project / ".agents/skills" / name)
    permission = {"*": "deny", "external_directory": "deny"}
    if enabled:
        permission["skill"] = {TASKS[task]["skill"]: "allow", "*": "deny"}
        # Pattern order matters: allow must follow the fallback.
        permission["skill"] = {"*": "deny", ("kodi-*" if os.environ.get("KODI_EVAL_SKILL_CATALOG") == "all" else TASKS[task]["skill"]): "allow"}
    if task in {"debug", "mcp-health", "runtime-addon"}:
        permission.update({"read": "allow", "kodi_lab_target_list": "allow",
                           "kodi_lab_target_status": "allow", "kodi_lab_inspect_ui_state": "allow"})
        if os.environ.get("KODI_EVAL_MCP_SCOPE") == "broad" or task == "runtime-addon":
            permission.update({"kodi_lab_addon_list": "allow", "kodi_lab_screenshot_capture": "allow"})
    else:
        permission.update({"read": "allow", "glob": "allow", "grep": "allow", "kodi_validate": "allow"})
    if os.environ.get("KODI_EVAL_TOOL_SCOPE") == "narrow" and task not in {"debug", "mcp-health", "runtime-addon"}:
        permission.pop("glob", None)
        permission.pop("grep", None)
    if task.startswith('review'):
        permission["kodi_review"] = "allow"
    if task in {"api-fix", "api-fix-contract", "api-fix-nexus"}:
        permission["edit"] = {"*": "deny", "fixtures/script.toolkit.sample/default.py": "allow"}
    agent = {"mode": "primary", "description": "Disposable local toolkit evaluation",
             "steps": 14, "temperature": 0, "permission": permission,
             "prompt": "Complete only the requested task using permitted tools. Report observed results and limitations; no deployments, settings changes, host commands, production access or model reconfiguration. If a tool operation is denied, do not try alternate write tools or repeat the same denied operation; report the boundary and stop."
                       + (" FIRST invoke the native skill tool with the appropriate available skill name before reading addon files or using MCP. Follow its instructions and load references only when needed. If no relevant skill is available, report that blocker." if enabled and os.environ.get("KODI_EVAL_SKILL_ROUTING", "forced") == "forced" else "")}
    config = {"$schema": "https://opencode.ai/config.json", "share": "disabled", "autoupdate": False,
              "agent": {"toolkit-eval": agent}}
    file = output / "opencode-private.json"
    file.write_text(json.dumps(config, indent=2))
    file.chmod(0o600)
    prompt = TASKS[task]["prompt"].replace("fixtures/addon", "fixtures/script.toolkit.sample")
    if enabled and os.environ.get("KODI_EVAL_SKILL_ROUTING", "forced") == "forced":
        prompt = "First use the native skill tool to load the toolkit skill most relevant to this task. Do this before other tool calls; then follow the loaded skill.\n\n" + prompt
    (output / "prompt.txt").write_text(prompt)
    env = os.environ.copy()
    env["OPENCODE_CONFIG"] = str(file)
    env["PATH"] = str(Path.home() / ".opencode/bin") + os.pathsep + env.get("PATH", "")
    env.update({"KODI_TOOLKIT_PYTHON": os.environ.get("KODI_TOOLKIT_PYTHON", sys.executable),
                "KODI_TOOLKIT_CLI": str(ROOT / "scripts/validation-cli.py"),
                "KODI_TOOLKIT_INDEX_CACHE": os.environ.get("KODI_TOOLKIT_INDEX_CACHE", str(ROOT / ".local/index-cache"))})
    if TASKS[task].get("missing_cache"):
        env["KODI_TOOLKIT_INDEX_CACHE"] = str(output / "deliberately-missing-cache")
    run_directory = project / TASKS[task].get("start_directory", ".")
    run_directory.mkdir(parents=True, exist_ok=True)
    env["PWD"] = str(run_directory)
    env["KODI_EVAL_PROJECT_ROOT"] = str(project)
    cmd = [os.environ.get("OPENCODE_BIN", shutil.which("opencode") or str(Path.home() / ".opencode/bin/opencode")),
           "run", "--dir", str(run_directory), "--pure", "--format", "json", "--model", model_id, "--agent", "toolkit-eval",
           "--title", label, prompt]
    initial_files = {str(f.relative_to(addon)): hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(addon.rglob("*")) if f.is_file()}
    initial_tree = hashlib.sha256(json.dumps(initial_files, sort_keys=True).encode()).hexdigest()
    sources = [ROOT / "requirements-dev.lock", ROOT / "evaluation/processes.py"] + list((ROOT / "src/kodi_agent_toolkit").glob("*.py")) + list((ROOT / ".opencode/tools").glob("*.ts")) + list((ROOT / ".opencode/lib").glob("*.ts")) + [ROOT / "evaluation/run.py", ROOT / "evaluation/tasks.json", ROOT / "AGENTS.md"]
    source_hashes = {str(f.relative_to(ROOT)): hashlib.sha256(f.read_bytes()).hexdigest() for f in sources}
    copied_skills = {str(f.relative_to(project)): hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((project / ".agents/skills").rglob("*")) if f.is_file()}
    cache_file = Path(env["KODI_TOOLKIT_INDEX_CACHE"]) / "manifest.json"
    provenance = {"initial_fixture_files": initial_files, "initial_fixture_tree_sha256": initial_tree, "source_hashes": source_hashes, "copied_skill_hashes": copied_skills, "skill_revision": revision or "working-tree", "task_definition": TASKS[task], "skill_routing": os.environ.get("KODI_EVAL_SKILL_ROUTING", "forced"), "mcp_scope": os.environ.get("KODI_EVAL_MCP_SCOPE", "narrow"), "cache_manifest_sha256": hashlib.sha256(cache_file.read_bytes()).hexdigest() if cache_file.exists() else None}
    (output / "provenance.json").write_text(json.dumps(provenance, indent=2))
    start = time.monotonic()
    process = subprocess.Popen(cmd, cwd=run_directory, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, **launch_options())
    stderr = []
    def collect():
        for line in process.stderr:
            stderr.append(clean(line))
    thread = threading.Thread(target=collect, daemon=True)
    thread.start()
    termination = {"timed_out": False, "reason": None}
    def deadline():
        termination.update(timed_out=True, reason="trial timeout")
        stop_tree(process)
    timer = threading.Timer(timeout, deadline)
    timer.start()
    events = []
    denied_operations = 0
    for line in process.stdout:
        try:
            event = clean(json.loads(line))
        except ValueError:
            continue
        event["elapsed_seconds"] = round(time.monotonic() - start, 3)
        events.append(event)
        if event.get("type") == "tool_use":
            state = event["part"]["state"]
            if state.get("status") == "error" and "rule which prevents" in state.get("error", ""):
                denied_operations += 1
                if denied_operations >= 2:
                    termination["reason"]="two denied operations"
                    stop_tree(process)
            print(json.dumps({"trial": label, "seconds": event["elapsed_seconds"], "tool": event["part"]["tool"],
                              "status": state["status"], "input": state.get("input"), "error": state.get("error")})[:1800], flush=True)
        elif event.get("type") == "text":
            print(json.dumps({"trial": label, "text": event["part"].get("text", "")})[:2200], flush=True)
    process.wait(timeout=10)
    timer.cancel()
    thread.join(2)
    (output / "events.json").write_text(json.dumps(events, indent=2))
    (output / "stderr.txt").write_text("".join(stderr))
    tools_used = [x for x in events if x.get("type") == "tool_use"]
    steps = [x["part"].get("tokens", {}) for x in events if x.get("type") == "step_finish"]
    result = {"label": label, "model": model_id, "task": task, "skill_enabled": enabled, "skill_catalog": os.environ.get("KODI_EVAL_SKILL_CATALOG", "relevant-only"), "tool_scope": os.environ.get("KODI_EVAL_TOOL_SCOPE", "standard"),
              "duration_seconds": round(time.monotonic() - start, 3), "exit_code": process.returncode, "termination": termination,
              "valid_calls": sum(x["part"]["state"]["status"] == "completed" for x in tools_used),
              "denied_operation_stop": denied_operations >= 2,
              "failed_calls": sum(x["part"]["state"]["status"] != "completed" for x in tools_used),
              "skill_loaded": [x["part"]["state"].get("input", {}).get("name") for x in tools_used
                               if x["part"]["tool"] == "skill" and x["part"]["state"]["status"] == "completed"],
              "first_useful_seconds": next((x["elapsed_seconds"] for x in tools_used
                                         if x["part"]["state"]["status"] == "completed"), None),
              "usage": {"input": sum(x.get("input", 0) for x in steps),
                        "output": sum(x.get("output", 0) for x in steps),
                        "cached_read": sum(x.get("cache", {}).get("read", 0) for x in steps)},
              "fixture_source_sha256": hashlib.sha256((addon / "default.py").read_bytes()).hexdigest()}
    (output / "summary.json").write_text(json.dumps(result, indent=2))
    from assess import assess
    from final_report import write_final_report
    assessment = assess(label, private=PRIVATE)
    final = write_final_report(output, assessment)
    result['recorded_task_outcome'] = final['outcome']
    print(json.dumps(result), flush=True)
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="Explicit provider/model ID from private OpenCode configuration")
    parser.add_argument("--task", choices=TASKS, required=True)
    parser.add_argument("--condition", choices=["baseline", "skill"], required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--skill-revision", help="Read skill files only from a local commit; tools/harness stay current for matched A/B/C comparisons")
    args = parser.parse_args()
    run(args.model, args.task, args.condition == "skill", args.label, args.timeout, args.skill_revision)
