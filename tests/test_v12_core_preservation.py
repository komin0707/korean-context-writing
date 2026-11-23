import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class V12PreservationTests(unittest.TestCase):
    def test_core_elements_remain_in_skill(self):
        text=(ROOT/'SKILL.md').read_text(encoding='utf-8')
        for key in ('맥락 해석','화자 구성','감정의 이유','독자의 자리','말투의 설계','후킹과 전개','근거의 배치'):
            self.assertIn(key,text)
        self.assertIn('화자의 존재감',text)
        self.assertIn('답이 궁금해진 순간에는 바로 답한다',text)
    def test_writer_no_forced_bad_sample(self):
        with tempfile.TemporaryDirectory() as temp:
            result=subprocess.run([sys.executable,str(ROOT/'scripts/run_pipeline.py'),
                 '--task','만 보 걷기 정보성 원고','--genre','건강정보',
                 '--prepare-only','--output',temp],text=True,capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)
            contents=(Path(temp)/'01_writer_prompt.md').read_text(encoding='utf-8')
            self.assertIn('맥락 해석',contents)
            self.assertIn('화자 구성',contents)
            self.assertNotIn('컵으로 마시는 몫',contents)
            self.assertNotIn('00_selected_memory',contents)
    def test_explicit_style_example_is_opt_in_only(self):
        sys.path.insert(0,str(ROOT/'scripts'))
        from run_pipeline import assemble_writer
        self.assertNotIn('여기만',assemble_writer('글','근거'))
        self.assertIn('여기만',assemble_writer('글','근거','여기만'))
