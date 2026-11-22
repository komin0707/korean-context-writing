import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from run_pipeline import assemble_writer, assemble_reviser, assemble_reviewer, context

CORE=("맥락 해석", "화자 구성", "감정의 이유", "독자의 자리",
      "말투의 설계", "후킹과 전개", "근거의 배치")

class ActivePromptV2Tests(unittest.TestCase):
    def test_writer_is_compact_and_keeps_v12_semantics(self):
        content=assemble_writer("공복 유산소 운동을 커뮤니티 톤으로 설명", "확인된 자료", "")
        self.assertLess(len(content), 6500, "Old repeated references have returned")
        for key in CORE:
            self.assertIn(key,content)
        self.assertIn("먼저 읽고 싶게 쓴다",content)
        self.assertIn("답이 궁금해진 순간에는 바로 답한다",content)
        self.assertIn("독자가 가장 재미있게 읽을 부분",content)

    def test_extra_references_stay_archived_outside_writer_prompt(self):
        prompt=assemble_writer("생활 건강 칼럼","검증된 사실","")
        for older_section in ("숫자가 맡을 일","독자가 스스로 채울 여백",
                              "말끝과 작은 표정","독자가 다음 줄을 읽는 이유",
                              "상황에 맞는 단어"):
            self.assertNotIn(older_section,prompt)
        self.assertEqual(context(),(ROOT/'knowledge/voice-priority.md').read_text(encoding="utf-8"))
        self.assertLess(len(context()),2000)

    def test_source_facts_appear_unchanged(self):
        info="공복 운동 중 지방 사용 증가가 관찰됐지만 4주 실험의 체지방 감소에서 확정적인 집단 간 차이는 확인되지 않았다."
        prompt=assemble_writer("운동에 대한 의견 글",info,"")
        self.assertIn(info,prompt)
        self.assertGreater(prompt.index(info),prompt.index('요청한 형식의 완성 원고를 출력한다'))
        self.assertNotIn("멈칫한 건 그다음이다",prompt)

    def test_reviser_compact_and_truthful(self):
        draft="식후에 운동하는 사람의 몸은 어떤가?"
        revised=assemble_reviser("공복 유산소", "연구 근거",draft,{
            "revision_priority":"독자의 의문을 시원하게 해결",
            "issues":[{"repair":"비교 결과를 생활 속 의미로 연결한다"}],
            "what_to_preserve":["연구 제한"]})
        self.assertLess(len(revised),6500)
        self.assertIn(draft,revised)
        self.assertIn("중요한 사실과 살아 있는 관점",revised)
        self.assertIn("연구 설명은 필자의 주장에 필요한 순간",revised)
        self.assertIn("연구 제한",revised)

    def test_reviewer_checks_exposition_burden(self):
        review=assemble_reviewer("공복 유산소","논문","승인 문체","본문")
        self.assertIn("설명 분량이 실제 재미와 이해에 도움이 되는가",review)
        self.assertIn("truthfulness",review)
        self.assertIn("본문",review)

    def test_active_writer_guidance_is_affirmative(self):
        for name in ("SKILL.md","knowledge/voice-priority.md","prompts/writer.md",
                     "prompts/reviser.md","prompts/reviewer.md"):
            content=(ROOT/name).read_text(encoding="utf-8")
            for phrase in ("금지","하지 마라","하지 않는다","피하라",
                           "실패 사례","거절된 표현","모방하지"):
                self.assertNotIn(phrase,content,name)

    def test_prepare_cli_generates_small_prompt(self):
        with tempfile.TemporaryDirectory() as folder:
            result=subprocess.run([sys.executable,str(ROOT/'scripts/run_pipeline.py'),
                "--genre","건강정보","--task","공복 유산소 의견 글",
                "--prepare-only","--output",folder],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            prompt=(Path(folder)/"01_writer_prompt.md").read_text(encoding="utf-8")
            self.assertLess(len(prompt),6500)
            self.assertIn("먼저 읽고 싶게 쓴다",prompt)

if __name__=="__main__":
    unittest.main()
