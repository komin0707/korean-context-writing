import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_pipeline import assemble_writer, assemble_reviewer, parse_review, load_examples


class RunnerTests(unittest.TestCase):
    def test_build_writer(self):
        result = assemble_writer("예제 글 작성", "외부 자료 없음", load_examples())
        self.assertIn("예제 글 작성", result)
        self.assertIn("감정", result)
        self.assertNotIn("{{TASK}}", result)

    def test_validate_review(self):
        draft = "내일 할 일인데 굳이 지금 보내셨네."
        data = {"decision": "provisional", "scores": dict.fromkeys(("context", "stance", "voice", "empathy", "hook", "truthfulness"), 3),
                "issues": [{"span": "굳이", "problem": "반복 여부 확인 필요", "repair": "대안이 있는지 확인"}]}
        self.assertEqual(parse_review(json.dumps(data, ensure_ascii=False), draft)["decision"], "provisional")

    def test_partial_voice_forces_revision(self):
        draft = "글이 있다."
        scores = dict.fromkeys(("context", "stance", "voice", "empathy", "hook", "truthfulness"), 3)
        scores["voice"] = 2
        data = {"decision": "provisional", "scores": scores,
                "issues": [{"severity": "minor", "span": "글", "problem": "말투", "repair": "자연스러운 한국어로 구성"}]}
        self.assertEqual(parse_review(json.dumps(data, ensure_ascii=False), draft)["decision"], "revise")

    def test_major_issue_forces_revision(self):
        draft = "글이 있다."
        scores = dict.fromkeys(("context", "stance", "voice", "empathy", "hook", "truthfulness"), 3)
        data = {"decision": "provisional", "scores": scores,
                "issues": [{"severity": "major", "span": "글", "problem": "감정", "repair": "정서가 생기는 이유를 반영"}]}
        self.assertEqual(parse_review(json.dumps(data, ensure_ascii=False), draft)["decision"], "revise")

    def test_no_fake_span(self):
        draft = "커피도 수분이다."
        data = {"decision": "provisional", "scores": dict.fromkeys(("context", "stance", "voice", "empathy", "hook", "truthfulness"), 3),
                "issues": [{"span": "누구나 슬퍼했다", "problem": "과장", "repair": "수정"}]}
        with self.assertRaises(ValueError):
            parse_review(json.dumps(data, ensure_ascii=False), draft)

    def test_zero_score_cannot_pass(self):
        draft = "글이 있다."
        scores = dict.fromkeys(("context", "stance", "voice", "empathy", "hook", "truthfulness"), 3)
        scores["empathy"] = 0
        data = {"decision": "provisional", "scores": scores, "issues": [{"span": "글", "problem": "원인 없음", "repair": "재작성"}]}
        self.assertEqual(parse_review(json.dumps(data, ensure_ascii=False), draft)["decision"], "revise")


if __name__ == "__main__":
    unittest.main()
