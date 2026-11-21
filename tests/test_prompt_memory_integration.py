import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class PromptIntegrationTests(unittest.TestCase):
    def test_prompt_includes_actual_feedback(self):
        with tempfile.TemporaryDirectory() as temp:
            result=subprocess.run([sys.executable,str(ROOT/'scripts'/'run_pipeline.py'),
                '--genre','건강정보','--task','물 섭취량 블로그 글','--prepare-only','--output',temp],
                text=True,capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)
            prompt=(Path(temp)/'01_writer_prompt.md').read_text(encoding='utf-8')
            memory=(Path(temp)/'00_selected_memory.md').read_text(encoding='utf-8')
            self.assertIn('물 마시기 앱은 내가 점심에 곰탕',prompt)
            self.assertIn('거절',memory)
            self.assertIn('해당 장르의 피드백 사례 없음',memory)
            self.assertNotIn('이 사람 이미 차석으로 붙었는데?',memory)
if __name__=='__main__':
    unittest.main()
