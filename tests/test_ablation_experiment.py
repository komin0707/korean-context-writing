import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/'experiments/ablation/run.py'
spec=importlib.util.spec_from_file_location('ablation_experiment',FILE)
ab=importlib.util.module_from_spec(spec)
spec.loader.exec_module(ab)

class AblationTests(unittest.TestCase):
    def test_all_variants_hold_identical_facts_and_task(self):
        case=ab.load_case('01_운동_편의점')
        prompts=ab.all_prompts(case)
        self.assertEqual(set(prompts),{'A_v21','B_current','C_no_example'})
        for prompt in prompts.values():
            self.assertIn(case['facts'],prompt)
            self.assertIn(case['task'],prompt)

    def test_main_baseline_is_not_current_code(self):
        case=ab.load_case('02_운동영상_저장')
        prompts=ab.all_prompts(case)
        self.assertIn(ab.git_main_file('SKILL.md'),prompts['A_v21'])
        self.assertNotIn('SUCCESSFUL THOUGHT MOVEMENT',prompts['A_v21'])
        self.assertIn('SUCCESSFUL THOUGHT MOVEMENT',prompts['B_current'])
        self.assertNotIn('SUCCESSFUL THOUGHT MOVEMENT',prompts['C_no_example'])
        self.assertIn('근데 시발 내가 왜 안심함?',prompts['B_current'])
        self.assertNotIn('근데 시발 내가 왜 안심함?',prompts['C_no_example'])

    def test_editor_does_not_request_new_ideas(self):
        p=ab.editor_prompt('첫 문단 ㅋㅋ','근거')
        self.assertIn('삭제 중심 편집',p)
        self.assertIn('첫 문단 ㅋㅋ',p)
        self.assertIn('근거',p)
        self.assertIn('없던 인물·경험·감정',p)

    def test_samples_are_generated_without_auto_ranking(self):
        with tempfile.TemporaryDirectory() as tmp:
            result=subprocess.run(
                [sys.executable,str(FILE),'--case','02_운동영상_저장','--output',tmp,
                 '--model-cmd',f'{sys.executable} tests/mock_model_cli.py writer','--samples','2'],
                cwd=ROOT,text=True,capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)
            dest=Path(tmp)/'02_운동영상_저장'
            self.assertEqual(len(list(dest.glob('*_draft_*.md'))),8)
            self.assertFalse((dest/'winner.md').exists())
            self.assertTrue((dest/'D_B_cut_draft_02.md').exists())

    def test_prepare_cli_has_no_generation(self):
        case_id='03_단백질_타이밍'
        with tempfile.TemporaryDirectory() as tmp:
            result=subprocess.run([sys.executable,str(FILE),'--case',case_id,
                                   '--output',tmp],text=True,capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)
            dest=Path(tmp)/case_id
            self.assertEqual(len(list(dest.glob('*_prompt.md'))),3)
            self.assertFalse(list(dest.glob('*_draft.md')))
            self.assertTrue((dest/'human_review.md').is_file())

if __name__=='__main__':
    unittest.main()
