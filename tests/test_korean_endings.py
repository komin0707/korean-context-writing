import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class EndingRhythmTests(unittest.TestCase):
    def test_writer_prompt_uses_rhythm_by_sentence_role(self):
        with tempfile.TemporaryDirectory() as path:
            cmd=[sys.executable,str(ROOT/'scripts/run_pipeline.py'),'--task',
                 '오래 앉아 일하는 사람의 생활 건강 글','--genre','건강정보',
                 '--prepare-only','--output',path]
            run=subprocess.run(cmd,capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr)
            prompt=(Path(path)/'01_writer_prompt.md').read_text(encoding='utf-8')
            for text in ('문장 끝과 호흡의 리듬','단정·연결·질문·생략','문장 자체의 길이'):
                self.assertIn(text,prompt)
            self.assertIn('감정의 원인과 강도',prompt)

    def test_reviser_prompt_has_rhythm_guidance(self):
        sys.path.insert(0,str(ROOT/'scripts'))
        from run_pipeline import assemble_reviser
        prompt=assemble_reviser('생활정보','근거','본문',{'issues':[], 'revision_priority':'문장 호흡'})
        self.assertIn('문장 끝과 호흡의 리듬',prompt)
        self.assertIn('실제 한국어 말의 호흡',prompt)

if __name__=='__main__':
    unittest.main()
