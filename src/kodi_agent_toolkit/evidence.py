"""Small deterministic review boundary. No prose truth classifier or rule engine.

Structural acceptance is not semantic support. Only a deliberately narrow AST
pattern has independently supported semantics; all other defects remain claims.
"""
from __future__ import annotations

import ast
import copy
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

POLICY_BASES = {
    "dependency-minimum": {
        "url": "https://kodi.wiki/view/Addon.xml#version_attribute",
        "observation": "An import version specifies a minimum dependency version.",
    },
    "log-level-integer": {
        "url": "https://xbmc.github.io/docs.kodi.tv/master/kodi-base/d6/db2/group__python__xbmc.html",
        "observation": "xbmc.log accepts an integer level; matching stubs check its type.",
    },
}


def source_snapshot(addon: Path) -> dict[str, str]:
    from .checker_runner import inspect_source
    return {p.as_posix(): hashlib.sha256((addon / p).read_bytes()).hexdigest()
            for p in inspect_source(addon)}


def _setting_log(lines: list[str], line: int) -> dict | None:
    """Prove only adjacent, direct getSetting -> xbmc.log in one function.

    Deliberately excludes aliases, intervening control flow, rebinding, nested functions
    and transforms. False negatives remain unverified rather than guesses.
    """
    try:
        tree = ast.parse("\n".join(lines))
    except (SyntaxError, ValueError, RecursionError):
        return None
    # Require unmodified module imports and no rebinding anywhere. This is
    # conservative even when the rebinding is in an unrelated function.
    if not any(isinstance(n, ast.Import) and any(a.name == 'xbmc' and a.asname is None
               for a in n.names) for n in tree.body):
        return None
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                bound = alias.asname or alias.name.split('.')[0]
                if bound in {'xbmc', 'xbmcaddon'} and not (
                        isinstance(node, ast.Import) and alias.name == bound
                        and alias.asname is None):
                    return None
                if isinstance(node, ast.ImportFrom) and alias.name == '*':
                    return None
    if any(isinstance(n, ast.Name) and n.id in {'xbmc', 'xbmcaddon'}
           and isinstance(n.ctx, ast.Store) for n in ast.walk(tree)):
        return None
    if any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name in {'xbmc', 'xbmcaddon'}
           for n in ast.walk(tree)):
        return None
    if any(isinstance(n, (ast.Attribute, ast.Name)) and isinstance(n.ctx, (ast.Store, ast.Del))
           and (isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)
                and n.value.id in {'xbmc', 'xbmcaddon'}) for n in ast.walk(tree)):
        return None
    for fn in tree.body:
        if (not isinstance(fn, ast.FunctionDef) or fn.decorator_list or len(fn.body) != 3
                or fn.args.args or fn.args.posonlyargs or fn.args.kwonlyargs
                or fn.args.vararg or fn.args.kwarg):
            continue
        body = fn.body
        for i in range(2, len(body)):
            setup, read, emit = body[i-2:i+1]
            if not all(isinstance(n, ast.Assign) and len(n.targets) == 1
                       and isinstance(n.targets[0], ast.Name) for n in (setup, read)):
                continue
            creator, getter = setup.value, read.value
            if not (isinstance(creator, ast.Call) and isinstance(creator.func, ast.Attribute)
                    and isinstance(creator.func.value, ast.Name)
                    and creator.func.value.id == 'xbmcaddon' and creator.func.attr == 'Addon'
                    and not creator.args and not creator.keywords):
                continue
            if not any(isinstance(n, ast.Import) and any(a.name == 'xbmcaddon' and a.asname is None
                       for a in n.names) for n in tree.body):
                continue
            if not (isinstance(getter, ast.Call) and isinstance(getter.func, ast.Attribute)
                    and isinstance(getter.func.value, ast.Name)
                    and getter.func.value.id == setup.targets[0].id
                    and getter.func.attr == 'getSetting' and len(getter.args) == 1
                    and isinstance(getter.args[0], ast.Constant)
                    and isinstance(getter.args[0].value, str) and not getter.keywords):
                continue
            if not isinstance(emit, ast.Expr) or not isinstance(emit.value, ast.Call):
                continue
            call = emit.value
            if (isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Name)
                    and call.func.value.id == 'xbmc' and call.func.attr == 'log'
                    and call.args and isinstance(call.args[0], ast.Name)
                    and call.args[0].id == read.targets[0].id and not call.keywords
                    and emit.lineno == line):
                return {"rule": "direct-setting-log", "setting": getter.args[0].value,
                        "read_line": read.lineno, "log_line": emit.lineno}
    return None


def classify(addon: Path, contract: dict, deterministic: list[dict]) -> dict[str, list]:
    """Return clear categories, retaining original claims and rejection reasons.

    Never call an arbitrary model assertion a confirmed defect. Known basis IDs
    identify documentation only; they do not establish applicability or truth.
    """
    from .review import _root, _source_lines, EvidenceError
    cache: dict[str, list[str]] = {}
    groups: dict[str, list] = {key: [] for key in
        ('confirmed_deterministic_errors', 'evidence_supported_contextual_issues',
         'recommendations', 'unverified_observations', 'duplicate_findings')}
    groups['confirmed_deterministic_errors'] = [copy.deepcopy(x) for x in deterministic
                                                if x.get('severity') == 'error']
    messages = {x.get('message', '').strip() for x in deterministic}
    seen = set()
    for finding in contract.get('accepted_findings', []):
        claim = copy.deepcopy(finding)
        identity = json.dumps([claim['path'], claim['line'], claim['quote'],
                               claim['category']], sort_keys=True)
        record: dict[str, Any] = {'model_claim': claim, 'path': claim['path'],
                                  'line': claim['line'], 'structural_validation': 'passed'}
        if identity in seen or claim.get('reason', '').strip() in messages or claim.get('title', '').strip() in messages:
            record.update(reason='Duplicate anchor/category or exact canonical diagnostic',
                          classification='duplicate')
            groups['duplicate_findings'].append(record)
            continue
        seen.add(identity)
        basis = claim.get('requirement_basis')
        if basis is not None:
            record['requirement_basis'] = copy.deepcopy(POLICY_BASES.get(basis))
            record['basis_status'] = 'identified-only' if basis in POLICY_BASES else 'unknown'
        support = None
        if (claim['category'] == 'privacy' and claim['severity'] == 'material'
                and claim['confidence'] == 'source-supported' and basis is None
                and not any(e.get('role') == 'counterevidence' for e in claim.get('related_evidence', []))):
            try:
                support = _setting_log(_source_lines(_root(addon), claim['path'], cache), claim['line'])
                if support:
                    settings_path = 'resources/settings.xml'
                    if settings_path not in contract.get('coverage', {}).get('reviewed_files', []):
                        support = None
                    else:
                        text = '\n'.join(_source_lines(_root(addon), settings_path, cache))
                        if '<!DOCTYPE' in text.upper() or '<!ENTITY' in text.upper():
                            support = None
                        else:
                            settings = ET.fromstring(text)
                            concealed = any(s.get('id') == support['setting'] and
                                any((n.text or '').strip().lower() == 'true' for n in s.findall('control/hidden'))
                                for s in settings.iter('setting'))
                            if concealed:
                                support['settings_path'] = settings_path
                            else:
                                support = None
            except (EvidenceError, OSError, ValueError, ET.ParseError):
                support = None
                record['source_status'] = 'unavailable or changed after anchoring'
        if support:
            # Canonical factual prose replaces model prose in the supported view.
            # No claim of actual secret content, exposure, execution or policy.
            record.update(classification='evidence-supported contextual issue', severity='material',
                          observation='A UI-concealed setting value is passed unchanged to xbmc.log. If sensitive and executed, it can enter the Kodi log.',
                          independent_support=support, semantic_scope='direct static data flow only',
                          runtime_verified=False)
            groups['evidence_supported_contextual_issues'].append(record)
        elif (claim['severity'] == 'advisory' and claim['confidence'] == 'source-supported'
              and claim['category'] == 'correctness' and basis is None):
            record.update(classification='recommendation', severity='advisory',
                          semantic_verification='not-performed', reason='Nonbreaking model suggestion; no verified defect')
            groups['recommendations'].append(record)
        else:
            record.update(classification='unverified observation', severity='advisory',
                          reason='No independent semantic support for the claimed consequence, severity or applicable Kodi requirement',
                          semantic_verification='not-performed')
            groups['unverified_observations'].append(record)
    for rejected in contract.get('rejected_findings', []):
        groups['unverified_observations'].append({
            'classification': 'unverified observation', 'structural_validation': 'rejected',
            'model_claim': copy.deepcopy(rejected.get('finding')),
            'reasons': copy.deepcopy(rejected.get('errors', [])), 'severity': 'advisory'})
    return groups
