import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class V12PreservationTests(unittest.TestCase):
    def test_core_elements_remain_in_skill(self):
        text = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
        for key in ('맥락 해석', '화자 구성', '감정의 이유', '독자의 자리', '말투의 설계', '후킹과 전개', '근거의 배치'):
            self.assertIn(key, text)
        self.assertIn('화자의 존재감', text)
        self.assertNotIn('knowledge/form-selection.md', text)
        self.assertNotIn('knowledge/editorial-voice.md', text)

    def test_writer_receives_only_affirmative_guidance(self):
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'run_pipeline.py'),
                '--task', '만 보 걷기와 연구에 대한 정보성 원고', '--genre', '건강정보',
                '--prepare-only', '--output', temp], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            prompt = (Path(temp) / '01_writer_prompt.md').read_text(encoding='utf-8')
            for phrase in ('맥락 해석', '화자 구성', '감정의 이유', '독자의 자리', '말투의 설계', '후킹과 전개'):
                self.assertIn(phrase, prompt)
            for rejected in ('물 마시기 앱은 내가 점심에 곰탕', '컵으로 마시는 몫'):
                self.assertNotIn(rejected, prompt)
            self.assertEqual((Path(temp)/'00_selected_memory.md').read_text(encoding='utf-8'),
                             (Path(temp)/'00_reviewer_memory.md').read_text(encoding='utf-8'))

    def test_default_examples_respect_user_approval(self):
        sys.path.insert(0, str(ROOT / 'scripts'))
        from run_pipeline import load_examples
        examples = load_examples()
        for line in examples.splitlines():
            self.assertEqual(json.loads(line)['status'], 'approved')

if __name__ == '__main__':
    unittest.main()
