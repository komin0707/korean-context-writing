import json
import tempfile
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class KoreanSentenceGuidanceTests(unittest.TestCase):
    def test_writer_receives_sentence_craft(self):
        with tempfile.TemporaryDirectory() as tmp:
            result=subprocess.run([sys.executable, str(ROOT/'scripts/run_pipeline.py'),
                '--task', '생활 운동에 관한 근거 기반 원고 작성', '--genre', '건강정보',
                '--prepare-only', '--output', tmp], capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            prompt=(Path(tmp)/'01_writer_prompt.md').read_text(encoding='utf-8')
            for token in ('실제 한국어 표현을 고르는 과정','주어와 동사의 관계','조사와 말끝의 맥락',
                          '문장 사이의 실제 관계','감정의 원인과 강도'):
                self.assertIn(token,prompt)
            for rejected in ('컵으로 마시는 몫','물 마시기 앱은 내가 점심에 곰탕'):
                self.assertNotIn(rejected,prompt)

    def test_reviser_receives_same_sentence_guidance(self):
        sys.path.insert(0,str(ROOT/'scripts'))
        from run_pipeline import assemble_reviser
        review={'revision_priority':'문장 호흡','issues':[{'repair':'행동을 나타내는 동사를 골라 뜻을 전달한다'}],
                'what_to_preserve':['자료의 수치']}
        prompt=assemble_reviser('건강정보 원고','근거자료','실제 원고',review)
        self.assertIn('실제 한국어 표현을 고르는 과정',prompt)
        self.assertIn('행동을 나타내는 동사',prompt)

if __name__=='__main__':
    unittest.main()
