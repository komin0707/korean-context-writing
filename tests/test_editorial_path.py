import tempfile
import subprocess
import unittest
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class EditorialPathTests(unittest.TestCase):
    def test_active_writer_prompt(self):
        with tempfile.TemporaryDirectory() as d:
            r=subprocess.run([sys.executable,str(ROOT/'scripts/run_pipeline.py'),
                '--task','만 보 걸음 수 건강 글','--genre','건강정보','--prepare-only','--output',d],
                capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
            prompt=(Path(d)/'01_writer_prompt.md').read_text(encoding='utf-8')
            self.assertIn('생각이 살아 있는 한국어 원고',prompt)
            self.assertIn('이 이야기를 꺼내는 이유',prompt)
            self.assertNotIn('글의 형식과 시점 선택',prompt)
            self.assertNotIn('컵으로 마시는 몫',prompt)
            review=(Path(d)/'00_reviewer_memory.md').read_text(encoding='utf-8')
            self.assertNotIn('컵으로 마시는 몫',review)
