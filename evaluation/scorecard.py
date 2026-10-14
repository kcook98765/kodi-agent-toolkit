"""Verify immutable baseline and collect numeric, independently reviewed trials."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def baseline():
    source = ROOT / "evaluation/pilot-results.json"
    original = json.loads(source.read_text())
    recorded = json.loads((ROOT / "evaluation/phase4-baseline.json").read_text())
    if hashlib.sha256(source.read_bytes()).hexdigest() != recorded["pilot_sha256"]:
        raise ValueError("Original Phase 4 results changed")
    by_label = {trial["label"]: trial for trial in original["trials"]}
    categories = Counter()
    for trial in recorded["trials"]:
        prior = by_label[trial["label"]]
        if (trial["original_verdict"], trial["original_note"], trial["original_origin"]) != (prior["reviewer_verdict"], prior["reviewer_note"], prior["likely_origin"]):
            raise ValueError("Baseline annotation changed an original answer/judgment")
        categories.update(trial["categories"])
    if len(recorded["trials"]) != len(by_label) or dict(categories) != recorded["category_counts"]:
        raise ValueError("Baseline scorecard totals disagree")
    return {"original_preserved": True, "trials": len(by_label), "grade_counts": dict(Counter(t["reviewer_verdict"] for t in by_label.values())), "category_counts": dict(categories), "method": recorded["coding_method"]}

def collect(private: Path):
    trials = []
    for directory in sorted((private / "runs").iterdir()):
        if not (directory / "assessment.json").is_file():
            continue
        assessment = json.loads((directory / "assessment.json").read_text())
        summary = assessment["summary"]
        provenance = json.loads((directory / "provenance.json").read_text())
        verdict_file = directory / "independent-verdict.json"
        verdict = json.loads(verdict_file.read_text()) if verdict_file.exists() else {"verdict": "not-reviewed", "note": "Semantic/task acceptance not yet independently reviewed"}
        condition = "A" if not summary["skill_enabled"] else "B" if provenance.get("skill_revision") not in (None, "working-tree") else "C"
        trials.append({"label": summary["label"], "model": summary["model"].split("/", 1)[-1], "task": summary["task"], "condition": condition,
                       "skill_revision": provenance.get("skill_revision"), "skill_catalog": summary.get("skill_catalog"), "skill_routing": provenance.get("skill_routing", "forced"), "tool_scope": summary.get("tool_scope"), "mcp_scope": provenance.get("mcp_scope"),
                       "duration_seconds": summary["duration_seconds"], "completed_tool_events": summary["valid_calls"], "failed_tool_events": summary["failed_calls"], "usage": summary["usage"], "skill_loaded": summary["skill_loaded"],
                       "automatic_gates": assessment["automatic_gates"], "metrics": {key: assessment["metrics"].get(key) for key in ("missing_path_errors", "repeated_missing_path_errors", "schema_argument_errors", "identical_input_repeats", "final_words", "tool_output_characters", "last_step_finish_reason", "step_cap_response", "final_fixture_path_mentions", "unverified_final_fixture_citations")},
                       "initial_fixture_tree_sha256": provenance["initial_fixture_tree_sha256"], "source_hashes": provenance["source_hashes"], "copied_skill_hashes": provenance["copied_skill_hashes"], "cache_manifest_sha256": provenance["cache_manifest_sha256"], "independent_review": verdict})
    return {"schema_version": 1, "reviewer": "Codex independent artifact judgments, not user human sign-off", "phase4_baseline": baseline(), "trials": trials,
            "grade_counts": dict(Counter(t["independent_review"]["verdict"] for t in trials)),
            "limits": ["Bounded heterogeneous sequential pilot, not statistical accuracy or model ranking.", "A/B/C compare skills under current tools/harness, not historical inference/server state.", "Contract/static pass never proves model semantics or Kodi runtime behavior.", "Token/cache usage is cumulative SDK reporting, not billing or unique context.", "Repeated inputs are observational and can be necessary.", "No operator intervention inside model trials; between-trial harness fixes are retained with provenance."]}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=Path, help="Private evidence root containing runs/, never published directly")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = collect(args.runs) if args.runs else baseline()
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")

if __name__ == "__main__":
    main()
