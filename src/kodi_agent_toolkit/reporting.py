"""Concise reports from trusted tool records, never from a model's summary.

Input records must come from the operator/tooling, not model-authored JSON.
Hashes detect stale results, not forgery. This is a report builder, not an
authentication system or a runtime verifier.
"""
from __future__ import annotations

import copy
from pathlib import Path

from .evidence import source_snapshot

STAGES = ('syntax', 'manifest', 'paths', 'package', 'types', 'official_checker')


def build_report(addon: Path, validation: dict | None = None, *, review: dict | None = None,
                 execution: dict | None = None, before: dict | None = None,
                 artifacts: list[str] | None = None, tests: list[dict] | None = None,
                 observations: list[dict] | None = None) -> dict:
    result = {'schema_version': 1, 'outcome': 'BLOCKED', 'changes': [], 'checks': [],
              'verified_findings': [], 'unverified_suggestions': [], 'remaining_problems': [],
              'artifacts': artifacts or [], 'scope': 'Recorded checks only; runtime not established',
              'limits': ['Records must originate from trusted tools/operator, not model prose.',
                         'Source hashes detect staleness, not forged records or every file race.',
                         'PASS covers the declared recorded workflow, never all-version code correctness.']}
    problems = result['remaining_problems']
    current = source_snapshot(addon)
    if before is not None:
        if not isinstance(before, dict) or not all(isinstance(k, str) and isinstance(v, str) for k,v in before.items()):
            raise ValueError('before must be a trusted file-hash snapshot')
        result['changes'] = [{'path': p, 'change': 'added' if p not in before else 'removed' if p not in current else 'modified'}
                             for p in sorted(before.keys() | current.keys()) if before.get(p) != current.get(p)]
    if review is not None:
        problems.append('General contextual semantics require independent review; coverage completion is a model claim')
        validation = review.get('validation_report', validation)
        groups = review.get('finding_categories', {})
        if not isinstance(groups, dict) or 'unverified_observations' not in groups:
            problems.append('Independent contextual classification is missing')
            groups = {}
        result['verified_findings'].extend(copy.deepcopy(groups.get('evidence_supported_contextual_issues', [])))
        result['unverified_suggestions'].extend(copy.deepcopy(groups.get('recommendations', []) + groups.get('unverified_observations', [])))
        if review.get('contract_passed') is not True:
            problems.append('Contextual draft rejected or not completed')
        if review.get('contract_report', {}).get('coverage', {}).get('complete') is not True:
            problems.append('Contextual coverage is incomplete or unrecorded')
        if result['unverified_suggestions']:
            problems.append('Contextual suggestions retain unverified semantics')
    stale = not validation or validation.get('source_snapshot') != current
    failed = False
    blocked = stale
    if stale:
        problems.append('Current source has no matching validation snapshot; recheck required')
        # Do not expose stale contextual findings as verified either.
        result['unverified_suggestions'].extend(result['verified_findings'])
        result['verified_findings'] = []
    if validation:
        checks = validation.get('checks', {})
        for stage in STAGES:
            check = checks.get(stage, {})
            allowed = {'passed','not_applicable'} if stage == 'types' else {'passed'}
            complete = (check.get('passed') is True and check.get('status') in allowed
                        and (stage != 'official_checker' or check.get('completed') is True)
                        and not check.get('infrastructure_errors'))
            result['checks'].append({'name': stage, 'status': check.get('status', 'missing'),
                                     'completed_successfully': complete and not stale,
                                     'errors': copy.deepcopy(check.get('errors', [])),
                                     'warnings': copy.deepcopy(check.get('warnings', []))})
            if not stale and check.get('status') == 'failed':
                # A checker crash is incomplete infrastructure, even if it also
                # produced a diagnostic; independent manifest failure still FAIL.
                if stage == 'official_checker' and check.get('completed') is not True:
                    blocked = True
                else:
                    failed = True
                    result['verified_findings'].extend({'classification': 'confirmed deterministic error',
                        'source': stage, 'message': message} for message in check.get('errors', []))
            if not complete:
                problems.append(f'{stage}: {check.get("status", "missing")}')
                blocked |= check.get('status') in {'error','skipped','missing','passed','not_applicable'} or not check
        if validation.get('passed') is not True and not failed and not blocked:
            blocked = True
            problems.append('Validation did not establish completion')
    result['static_outcome'] = 'FAIL' if failed else 'BLOCKED' if blocked else 'PASS'
    for test in tests or []:
        # These are operator-recorded subprocess outcomes, never inferred from
        # a test name or a model's statement that tests passed.
        result['checks'].append(copy.deepcopy(test))
        if test.get('completed') is not True or type(test.get('exit_code')) is not int:
            blocked = True
            problems.append('Test execution incomplete')
        elif test['exit_code'] != 0:
            failed = True
            problems.append('Recorded test execution failed')
    for observation in observations or []:
        result['checks'].append({'name': 'runtime observation', 'record': copy.deepcopy(observation),
                                 'scope': 'Recorded observation only; no implied runtime repair success'})
    if execution is not None:
        gates = execution.get('required_gates', {})
        if (execution.get('completed') is not True or not gates
                or any(value is not True for value in gates.values())):
            problems.append('Agent workflow incomplete: ' + ', '.join(k for k,v in gates.items() if v is not True))
        result['agent_completion'] = copy.deepcopy(execution)
    result['outcome'] = 'FAIL' if failed else 'BLOCKED' if blocked else 'PARTIAL' if problems else 'PASS'
    return result


def render_report(report: dict) -> str:
    """Bounded Markdown; full claims/diagnostics remain in JSON artifacts."""
    lines = [f'Task outcome: **{report["outcome"]}**', '', report['scope'], '']
    for title, values in (
        ('Changes actually made', [f'{x["path"]}: {x["change"]}' for x in report['changes']]),
        ('Checks executed', [f'{x.get("name", "check")}: {x.get("status", x.get("exit_code", "recorded"))}'
                            + (f'; warnings: {"; ".join(x["warnings"])}' if x.get('warnings') else '')
                            for x in report['checks']]),
        ('Verified findings', [x.get('observation', x.get('message', 'Evidence-supported contextual issue')) for x in report['verified_findings']]),
        ('Unverified suggestions', [f'{len(report["unverified_suggestions"])} retained in JSON; none treated as confirmed defects'] if report['unverified_suggestions'] else []),
        ('Remaining problems', report['remaining_problems']),
        ('Artifacts', report['artifacts']),
    ):
        lines.append(f'{title}:')
        lines.extend('- ' + str(x).replace('\n', ' ')[:500] for x in values[:20])
        if not values: lines.append('- None recorded')
        if len(values) > 20: lines.append(f'- {len(values)-20} further records in JSON')
        lines.append('')
    return '\n'.join(lines)
