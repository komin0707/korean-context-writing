import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from revision_guard import check_revision, protected_numbers

CLI=ROOT/'scripts/run_pipeline.py'
FIX=ROOT/'tests/mock_model_cli.py'

def run(temp, *args):
    return subprocess.run([sys.executable,str(CLI),'--task','가벼운 글','--output',str(temp),*args],
                          cwd=ROOT,text=True,capture_output=True)

def model(role):
    return f"{sys.executable} {FIX} {role}"

class V3WorkflowTests(unittest.TestCase):
    def test_dc_tone_is_active_in_writer(self):
        from run_pipeline import assemble_writer
        prompt=assemble_writer("이슈를 커뮤니티용으로 논평", "사실 확인 자료")
        self.assertIn("디시인사이드(DC)",prompt)
        self.assertIn("반말",prompt)
        self.assertIn("다른 문체를 명시적으로 요청받으면",prompt)
        self.assertIn("억지",prompt)
    def test_revision_guard_quotes_and_korean_date_units(self):
        before='2013년 20명에게 물었다. “반드시 해야 한다”라는 말이었다.'
        after='2014년 20명에게 물었다. “해도 된다”라는 말이었다.'
        self.assertIn('2013',protected_numbers(before))
        result=check_revision(before,after)
        self.assertFalse(result['pass'])
        self.assertIn('numbers_changed',result['failures'])
        self.assertIn('quoted_text_changed',result['failures'])
        self.assertTrue(check_revision(before,before)['pass'])
    def test_simple_draft_uses_no_review_or_memory(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)
            result=run(p,'--writer-cmd',model('writer'))
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads((p/'run_status.json').read_text())['status'],'UNREVIEWED_MODEL_OUTPUT')
            self.assertFalse(list(p.glob('review*')))
            self.assertFalse(list(p.glob('*memory*')))
            self.assertIn('테스트용', (p/'final_draft.md').read_text())
    def test_reviewer_accepts_and_does_not_rewrite(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)
            result=run(p,'--writer-cmd',model('writer'),'--reviewer-cmd',model('reviewer'))
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads((p/'run_status.json').read_text())['status'],'MODEL_REVIEW_PROVISIONAL')
            self.assertFalse((p/'draft_1.md').exists())
    def test_major_review_causes_at_most_one_local_revision(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)
            result=run(p,'--writer-cmd',model('writer'),'--reviewer-cmd',model('reviewer_major'))
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertTrue((p/'draft_1.md').is_file())
            self.assertFalse((p/'draft_2.md').exists())
            self.assertEqual(json.loads((p/'run_status.json').read_text())['status'],'MODEL_REVISED_UNVERIFIED')
    def test_polish_identity_preserves_original(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td); original=p/'original_in.md'
            original.write_text('2026년 인터뷰: “이건 진짜다.”',encoding='utf-8')
            result=run(p,'--mode','polish','--draft-file',str(original),
                       '--writer-cmd',model('copy_polish'))
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn('2026년', (p/'final_draft.md').read_text())
            self.assertTrue(json.loads((p/'edit_guard_0.json').read_text())['pass'])
    def test_polish_blocks_changed_evidence_and_restores_original(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td); original=p/'original_in.md'
            sample='2026년 인터뷰: “진짜다.”'
            original.write_text(sample,encoding='utf-8')
            result=run(p,'--mode','polish','--draft-file',str(original),
                       '--writer-cmd',model('bad_polish'))
            self.assertEqual(result.returncode,2,result.stderr)
            self.assertEqual((p/'final_draft.md').read_text().strip(),sample)
            self.assertIn('ROLLED_BACK',json.loads((p/'run_status.json').read_text())['status'])
    def test_invalid_review_does_not_trigger_revision(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)
            result=run(p,'--writer-cmd',model('writer'),'--reviewer-cmd',model('reviewer_bad'))
            self.assertEqual(result.returncode,2,result.stderr)
            self.assertFalse((p/'draft_1.md').exists())
            self.assertEqual(json.loads((p/'run_status.json').read_text())['status'],'REVIEW_INVALID_NEEDS_HUMAN_CHECK')
    def test_preparation_polish_does_not_call_a_model(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td); source=p/'source.md';source.write_text('원문',encoding='utf-8')
            result=run(p,'--mode','polish','--draft-file',str(source),'--prepare-only')
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertTrue((p/'01_polisher_prompt.md').is_file())
            self.assertFalse((p/'final_draft.md').exists())
    def test_no_auto_style_reference_even_when_files_exist(self):
        prompt=(ROOT/'scripts/run_pipeline.py').read_text(encoding='utf-8')
        self.assertNotIn('feedback_memory',prompt)
        self.assertNotIn('approved_writer_context',prompt)
        self.assertNotIn('load_examples(',prompt)

if __name__=='__main__':
    unittest.main()
