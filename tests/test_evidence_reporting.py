"""Adversarial semantic boundaries and mechanically recorded task outcomes."""
import copy
from pathlib import Path
import tempfile
import unittest

from kodi_agent_toolkit.evidence import classify, source_snapshot
from kodi_agent_toolkit.review import validate_review
from kodi_agent_toolkit.reporting import build_report, render_report, STAGES
from test_review import report, REVIEW_ADDON, VALID_ADDON, PRIVACY_CANDIDATE


def checked(addon=REVIEW_ADDON):
    return {'passed': True, 'source_snapshot': source_snapshot(addon), 'checks': {
        s: {'status':'passed','passed':True,'completed':True,'errors':[],
            'warnings':['Official warning retained'] if s == 'official_checker' else []} for s in STAGES}}


class EvidenceBoundaryTests(unittest.TestCase):
    def classify(self, addon, draft, deterministic=None):
        return classify(addon, validate_review(addon, draft), deterministic or [])

    def test_direct_flow_has_canonical_conditional_support_not_model_truth(self):
        draft = report()
        draft['model_findings'][0]['title'] = 'Every password was stolen by remote servers'
        result = self.classify(REVIEW_ADDON, draft)
        supported = result['evidence_supported_contextual_issues'][0]
        self.assertIn('If sensitive and executed', supported['observation'])
        self.assertFalse(supported['runtime_verified'])
        self.assertNotIn('stolen', supported['observation'])
        self.assertIn('stolen', supported['model_claim']['title'])
        self.assertEqual(result['confirmed_deterministic_errors'], [])

    def test_valid_control_cannot_support_invented_privacy_issue(self):
        addon=REVIEW_ADDON.parents[1]/'review-clean/script.toolkit.sample'
        draft=report()
        f=draft['model_findings'][0]
        f.update(line=10,quote='xbmc.log("Private setting configured", xbmc.LOGINFO)',related_evidence=[])
        result=self.classify(addon,draft)
        self.assertEqual(result['evidence_supported_contextual_issues'],[])
        self.assertEqual(len(result['unverified_observations']),1)

    def test_fabricated_and_known_requirement_bases_never_prove_a_requirement(self):
        for basis in ('Kodi requires encryption of every setting','dependency-minimum','log-level-integer'):
            draft=report()
            draft['model_findings'][0]['requirement_basis']=basis
            result=self.classify(REVIEW_ADDON,draft)
            self.assertEqual(result['evidence_supported_contextual_issues'],[])
            self.assertEqual(len(result['unverified_observations']),1)

    def test_severity_and_reproduction_prose_cannot_certify_blocker(self):
        draft=report()
        draft['model_findings'][0].update(confidence='demonstrated',severity='blocker',
            reproduction={'steps':'invented','observed':'invented','expected':'invented'})
        result=self.classify(REVIEW_ADDON,draft)
        self.assertEqual(result['evidence_supported_contextual_issues'],[])
        self.assertEqual(result['unverified_observations'][0]['severity'],'advisory')

    def test_duplicate_claims_and_checker_records_are_not_extra_defects(self):
        draft=report()
        clone=copy.deepcopy(draft['model_findings'][0]); clone['title']='Same flow different wording'
        draft['model_findings'].append(clone)
        result=self.classify(REVIEW_ADDON,draft)
        self.assertEqual(len(result['duplicate_findings']),1)
        self.assertEqual(len(result['evidence_supported_contextual_issues']),1)
        draft=report(); draft['model_findings'][0]['reason']='Literal checker warning'
        result=self.classify(REVIEW_ADDON,draft,[{'severity':'warning','message':'Literal checker warning'}])
        self.assertEqual(len(result['duplicate_findings']),1)
        self.assertEqual(result['confirmed_deterministic_errors'],[])

    def test_bad_locations_keep_diagnostics_and_never_become_verified(self):
        for field,value in (('path','imaginary.py'),('path','../default.py'),('line',999),('line',8)):
            draft=report(); draft['model_findings'][0][field]=value
            result=self.classify(REVIEW_ADDON,draft)
            self.assertEqual(result['evidence_supported_contextual_issues'],[])
            self.assertEqual(result['unverified_observations'][0]['structural_validation'],'rejected')
            self.assertTrue(result['unverified_observations'][0]['reasons'])

    def test_unseen_renamed_direct_flow_and_counterexamples(self):
        with tempfile.TemporaryDirectory() as t:
            addon=Path(t)
            (addon/'resources').mkdir()
            (addon/'resources/settings.xml').write_text('<settings><setting id="session_token"><control><hidden>true</hidden></control></setting></settings>')
            base='import xbmc\nimport xbmcaddon\ndef run():\n    cfg = xbmcaddon.Addon()\n    value = cfg.getSetting("session_token")\n    xbmc.log(value, xbmc.LOGINFO)\n'
            for body,expected in ((base,True),(base.replace('xbmc.log(value,','xbmc.log("configured",'),False),
                (base.replace('    xbmc.log','    value = "redacted"\n    xbmc.log'),False),
                (base.replace('def run():','def run(xbmc):'),False),
                (base.replace('import xbmc\n','import pretend as xbmc\n'),False),
                (base.replace('import xbmc\n','import xbmc\nimport pretend as xbmc\n'),False),
                (base.replace('import xbmc\n','import xbmc\nfrom pretend import xbmc\n'),False),
                (base.replace('import xbmc\n','import xbmc\nfrom pretend import *\n'),False)):
                (addon/'code.py').write_text(body)
                f=copy.deepcopy(PRIVACY_CANDIDATE); f.update(path='code.py',line=len(body.splitlines()),
                    quote=body.splitlines()[-1].strip(),related_evidence=[])
                draft=report(f); draft['coverage']['reviewed_files']=['code.py','resources/settings.xml']
                result=self.classify(addon,draft)
                self.assertEqual(bool(result['evidence_supported_contextual_issues']),expected)

    def test_public_setting_logging_is_not_a_supported_privacy_defect(self):
        draft=report()
        draft['model_findings'][0]['related_evidence']=[]
        with tempfile.TemporaryDirectory() as t:
            import shutil
            addon=Path(t)/'addon';shutil.copytree(REVIEW_ADDON,addon)
            (addon/'resources/settings.xml').write_text('<settings><setting id="private_value"><control><hidden>false</hidden></control></setting></settings>')
            self.assertEqual(self.classify(addon,draft)['evidence_supported_contextual_issues'],[])

    def test_line_ranges_are_rejected_rather_than_assumed_valid(self):
        draft=report();draft['model_findings'][0]['line_end']=999
        checked=validate_review(REVIEW_ADDON,draft)
        self.assertFalse(checked['passed'])
        self.assertIn('unknown fields',str(checked['rejected_findings']))

    def test_empty_valid_review_has_no_generated_findings(self):
        draft=report();draft['model_findings']=[];draft['coverage']['reviewed_files']=['addon.xml','default.py']
        self.assertTrue(all(not v for v in self.classify(VALID_ADDON,draft).values()))


class RecordedReportingTests(unittest.TestCase):
    def test_current_complete_standalone_checks_pass_and_preserve_warnings(self):
        result=build_report(VALID_ADDON,checked(VALID_ADDON))
        self.assertEqual(result['outcome'],'PASS')
        self.assertEqual(result['checks'][-1]['warnings'],['Official warning retained'])

    def test_incomplete_agent_and_false_required_gate_cannot_pass(self):
        for record in ({'completed':False,'required_gates':{'checked':True}},
                       {'completed':True,'required_gates':{'reproduced':False}},
                       {'completed':True,'required_gates':{}}):
            result=build_report(VALID_ADDON,checked(VALID_ADDON),execution=record)
            self.assertEqual(result['outcome'],'PARTIAL')

    def test_stale_source_missing_stage_and_crashed_checker_cannot_pass(self):
        for mode in ('stale','missing','crash'):
            data=checked(VALID_ADDON)
            if mode=='stale':data['source_snapshot']['default.py']='invented'
            if mode=='missing':del data['checks']['types']
            if mode=='crash':data['checks']['official_checker'].update(completed=False,passed=False,status='error')
            result=build_report(VALID_ADDON,data)
            self.assertEqual(result['outcome'],'BLOCKED',result)

    def test_actual_failed_check_is_fail_not_successful_completed_call(self):
        data=checked(VALID_ADDON);data['passed']=False
        data['checks']['types'].update(status='failed',passed=False,errors=['Original type diagnostic'])
        result=build_report(VALID_ADDON,data)
        self.assertEqual(result['outcome'],'FAIL')
        self.assertEqual(result['verified_findings'][0]['message'],'Original type diagnostic')

    def test_changes_are_hash_differences_not_model_recollection(self):
        before=source_snapshot(VALID_ADDON);before['default.py']='before edit';before['removed.py']='gone'
        result=build_report(VALID_ADDON,checked(VALID_ADDON),before=before)
        self.assertEqual(result['changes'],[{'path':'default.py','change':'modified'},{'path':'removed.py','change':'removed'}])

    def test_rejected_review_and_unverified_claim_stay_partial(self):
        draft=report();draft['model_findings'][0]['requirement_basis']='fiction'
        contract=validate_review(REVIEW_ADDON,draft)
        review={'validation_report':checked(),'contract_passed':True,'contract_report':contract,
                'finding_categories':classify(REVIEW_ADDON,contract,[])}
        result=build_report(REVIEW_ADDON,review=review)
        self.assertEqual(result['outcome'],'PARTIAL')
        self.assertEqual(result['verified_findings'],[])

    def test_empty_contextual_draft_cannot_certify_general_review_completion(self):
        draft=report();draft['model_findings']=[]
        contract=validate_review(REVIEW_ADDON,draft)
        review={'validation_report':checked(),'contract_passed':True,'contract_report':contract,
                'finding_categories':classify(REVIEW_ADDON,contract,[])}
        result=build_report(REVIEW_ADDON,review=review)
        self.assertEqual(result['outcome'],'PARTIAL')
        self.assertEqual(result['static_outcome'],'PASS')

    def test_test_exit_code_and_completion_are_recorded_not_inferred(self):
        for test,outcome in (({'completed':True,'exit_code':0},'PASS'),
                             ({'completed':True,'exit_code':1},'FAIL'),
                             ({'completed':False,'exit_code':0},'BLOCKED')):
            self.assertEqual(build_report(VALID_ADDON,checked(VALID_ADDON),tests=[test])['outcome'],outcome)

    def test_markdown_is_bounded_and_includes_all_required_sections(self):
        data=build_report(VALID_ADDON,checked(VALID_ADDON));data['remaining_problems']=['long\ntext'*500]*100
        text=render_report(data)
        self.assertLess(len(text),13000)
        for title in ('Task outcome','Changes actually made','Checks executed','Verified findings','Unverified suggestions','Remaining problems','Artifacts'):
            self.assertIn(title,text)

    def test_powershell_utf16_record_is_read_by_actual_cli(self):
        import json,subprocess,sys
        with tempfile.TemporaryDirectory() as t:
            record=Path(t)/'record.json'
            record.write_text(json.dumps(checked(VALID_ADDON)),encoding='utf-16')
            p=subprocess.run([sys.executable,'-m','kodi_agent_toolkit.cli','report-build',str(VALID_ADDON),'--validation',str(record)],capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stderr)
            self.assertEqual(json.loads(p.stdout)['outcome'],'PASS')
