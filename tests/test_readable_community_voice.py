import tempfile
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class ReadableCommunityVoiceTests(unittest.TestCase):
    def test_writer_has_teen_readability_and_community_voice(self):
        with tempfile.TemporaryDirectory() as d:
            run = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "run_pipeline.py"),
                 "--task", "일상 운동을 설명하는 자연스러운 한국어 글",
                 "--genre", "건강정보", "--prepare-only", "--output", d],
                text=True, capture_output=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            prompt = (Path(d) / "01_writer_prompt.md").read_text(encoding="utf-8")
            for phrase in (
                "고2 친구", "커뮤니티에서 하소연하듯 말하는 온도",
                "읽자마자 알아듣는 말", "숫자가 맡을 일",
                "독자가 읽고 남길 한 가지", "감정의 이유", "후킹과 전개"):
                self.assertIn(phrase, prompt)
            for phrase in ("멈칫한 건 그다음이다", "눈에 걸린다", "셈이 이상하게 꼬여요"):
                self.assertNotIn(phrase, prompt)

    def test_reviser_receives_same_priorities(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        from run_pipeline import assemble_reviser
        prompt = assemble_reviser("생활 글", "근거", "초안", {
            "revision_priority": "일상어로 이해",
            "issues": [{"repair": "실제 상황을 통해 설명한다"}],
            "what_to_preserve": ["연구의 한계"]
        })
        for phrase in ("고2 친구", "숫자가 맡을 일",
                       "커뮤니티에서 하소연하듯 말하는 온도"):
            self.assertIn(phrase, prompt)

    def test_positive_authored_guidance(self):
        for path in ("SKILL.md", "knowledge/evidence-selection.md",
                     "knowledge/korean-expression.md", "prompts/writer.md",
                     "prompts/reviser.md"):
            content = (ROOT / path).read_text(encoding="utf-8")
            for phrase in ("하지 마라", "피하라", "금지", "실패 사례", "거절된 표현"):
                self.assertNotIn(phrase, content, path)

if __name__ == "__main__":
    unittest.main()
