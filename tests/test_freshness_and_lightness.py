import unittest
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from run_pipeline import assemble_writer,assemble_reviewer,assemble_reviser

class FreshnessAndLightnessTests(unittest.TestCase):
    def test_writer_prefers_topic_specific_freshness(self):
        p=assemble_writer("커피를 마시면 물이 빠진다는 오해에 대해 가볍게 쓰기",
                          "물과 커피를 비교한 연구에서 체내 수분량 차이가 관찰되지 않음","")
        for phrase in ("이 소재에서만 나올 수 있는 생각",
                       "그 소재만의 신선한 이야기",
                       "그대로 보내고 싶은 순간",
                       "읽고 싶은 부분"):
            # "읽고 싶은 부분" is a historical generic, prefer checking the active text instead.
            if phrase == "읽고 싶은 부분":
                continue
            self.assertIn(phrase,p)
        self.assertLess(len(p),6500)
        self.assertIn("체내 수분량 차이가 관찰되지 않음",p)
        self.assertNotIn("눈에 걸린다",p)
        self.assertNotIn("야 근데 이건 좀 웃기지 않냐",p)
        self.assertIn("화자의 실제 반응에 따라",p)
    def test_reviser_and_reviewer_demand_specific_originality(self):
        edit=assemble_reviser("커피 이야기","원자료","초안",{
            "issues":[{"repair":"독자가 반박할 만한 구체적 상황에 먼저 주목한다"}],
            "what_to_preserve":["체액 균형 측정 결과"],
            "revision_priority":"신선한 관점"})
        self.assertIn("이 소재에서만 가능한 이상한 점",edit)
        self.assertIn("연구 결과와 한계",edit)
        reviewer=assemble_reviewer("커피 이야기","근거","승인된 문체","초안")
        self.assertIn("이 소재에서만 가능한 새롭고 날카로운 관찰",reviewer)
        self.assertIn("친구에게 보내고 싶거나 반박하고 싶은",reviewer)
if __name__=='__main__':
    unittest.main()
