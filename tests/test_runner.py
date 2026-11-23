import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from run_pipeline import assemble_writer, assemble_reviewer, parse_review

class RunnerTests(unittest.TestCase):
    def test_writer_keeps_core_without_personal_profile(self):
        prompt=assemble_writer("예제 글 작성","외부 근거","")
        self.assertIn("예제 글 작성",prompt)
        self.assertIn("이 소재에서만 나올 수 있는 생각",prompt)
        self.assertIn("관찰·관계·대화",prompt)
        self.assertNotIn("Korean_Observer_V3",prompt)
        self.assertNotIn("{{TASK}}",prompt)
    def test_accept_with_empty_issues(self):
        review={"decision":"accept","issues":[],"preserve":[],"note":"완성"}
        self.assertEqual(parse_review(json.dumps(review), "원고")["decision"],"accept")
    def test_revise_requires_major_and_real_span(self):
        draft="내일 할 일인데 굳이 지금 보내셨네."
        review={"decision":"revise","issues":[{"severity":"major","span":"굳이","problem":"부자연스러움","repair":"한 문장만 조정"}],"preserve":[]}
        self.assertEqual(parse_review(json.dumps(review,ensure_ascii=False),draft)["decision"],"revise")
        review["issues"][0]["span"]="없던 문장"
        with self.assertRaises(ValueError):
            parse_review(json.dumps(review,ensure_ascii=False),draft)
    def test_no_mandatory_revision_for_minor_issue(self):
        review={"decision":"accept","issues":[{"severity":"minor","span":"원고","problem":"사소","repair":"선택"}],"preserve":[]}
        self.assertEqual(parse_review(json.dumps(review,ensure_ascii=False),"원고")["decision"],"accept")
        review["decision"]="revise"
        with self.assertRaises(ValueError):
            parse_review(json.dumps(review,ensure_ascii=False),"원고")
    def test_review_max_three(self):
        draft="문장"
        review={"decision":"revise","issues":[{"severity":"major","span":"문장","problem":"p","repair":"r"}]*4}
        with self.assertRaises(ValueError):
            parse_review(json.dumps(review,ensure_ascii=False),draft)
