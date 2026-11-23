"""v3.0 explicit non-integration of personal memory."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class PromptIntegrationTests(unittest.TestCase):
    def test_no_autoloaded_memory_or_examples(self):
        with tempfile.TemporaryDirectory() as temp:
            result=subprocess.run([sys.executable,str(ROOT/'scripts/run_pipeline.py'),
              '--genre','건강정보','--task','물 섭취량 블로그 글',
              '--prepare-only','--output',temp],text=True,capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)
            contents=(Path(temp)/'01_writer_prompt.md').read_text(encoding='utf-8')
            self.assertNotIn('물 마시기 앱은 내가 점심에 곰탕',contents)
            self.assertNotIn('이 사람 이미 차석으로 붙었는데?',contents)
            self.assertNotIn('Korean_Observer_V3',contents)
            self.assertFalse(list(Path(temp).glob('*memory*')))
            runner=(ROOT/'scripts/run_pipeline.py').read_text(encoding='utf-8')
            self.assertNotIn('from feedback_memory import',runner)
            self.assertNotIn('approved_writer_context(',runner)
            self.assertFalse((ROOT/"memory").exists())
            self.assertFalse((ROOT/"SETUP_PERSISTENCE.md").exists())
