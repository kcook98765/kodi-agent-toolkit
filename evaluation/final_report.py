"""Generate factual trial reports mechanically after OpenCode terminates."""
import json
from pathlib import Path

from kodi_agent_toolkit.reporting import build_report, render_report
from assess import tool_payload, validation_record


def write_final_report(directory: Path, assessment: dict, output_directory: Path | None = None) -> dict:
    output_directory = directory if output_directory is None else output_directory
    output_directory.mkdir(parents=True, exist_ok=True)
    events = json.loads((directory / 'events.json').read_text())
    calls = [e for e in events if e.get('type') == 'tool_use']
    validation, composed = None, None
    for event in calls:
        candidate = validation_record(event)
        if candidate: validation = candidate
        part, state = event['part'], event['part']['state']
        if part.get('tool') == 'kodi_review' and state.get('status') == 'completed' and state.get('input', {}).get('operation') == 'compose':
            envelope, record, error = tool_payload(state)
            if not error and envelope.get('process_exit') in (0,1) and not envelope.get('timed_out'):
                composed = dict(record)
                composed['validation_report'] = record.get('validation_report') or {
                    'passed': record.get('static_passed'), 'source_snapshot': record.get('source_snapshot'),
                    'checks': record.get('validation_checks', {})}
    provenance = json.loads((directory / 'provenance.json').read_text())
    summary = json.loads((directory / 'summary.json').read_text())
    gates = assessment.get('automatic_gates', {})
    # Historical tool-order gates are diagnostic only; retained old scorecards
    # are not edited. Current task completion uses the independent actual gates.
    required = {k:v for k,v in gates.items() if k not in assessment.get('legacy_gates', [])}
    report = build_report(directory / 'project/fixtures/script.toolkit.sample', validation,
        review=composed, before=provenance['initial_fixture_files'],
        execution={'completed': gates.get('execution_completed') is True and gates.get('final_response_complete') is True,
                   'required_gates': required},
        artifacts=['events.json','summary.json','provenance.json','assessment.json'])
    report['model'] = summary['model']
    report['task'] = summary['task']
    report['scope'] = 'Recorded agent workflow and static checks; natural-language model answer is separately unverified'
    report['model_answer_artifact'] = 'events.json'
    (output_directory / 'final-report.json').write_text(json.dumps(report, indent=2))
    (output_directory / 'final-report.md').write_text(render_report(report))
    return report
