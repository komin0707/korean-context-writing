#!/usr/bin/env python3
"""Offline fixture CLI for plumbing tests, never a prose-quality evaluation."""
import json
import sys
role = sys.argv[1]
prompt = sys.stdin.read()
if role in {"writer", "writer_rewrite"}:
    print("테스트용 문장입니다. 실제 품질은 평가하지 않습니다.")
elif role == "copy_polish":
    print(prompt.split("## 현재 원고\n", 1)[1].split("\n## 근거 자료", 1)[0].strip())
elif role == "bad_polish":
    print("2027년 이야기입니다. \"변경된 인용\"")
elif role == "reviewer":
    print(json.dumps({"decision":"accept", "issues":[], "preserve":["테스트용 문장입니다"], "note":"모의 응답"},ensure_ascii=False))
elif role == "reviewer_major":
    print(json.dumps({"decision":"revise", "issues":[{"severity":"major","span":"테스트용 문장입니다","problem":"모의 문제","repair":"모의 최소 수정"}], "preserve":[], "note":"모의 응답"},ensure_ascii=False))
elif role == "reviewer_bad":
    print(json.dumps({"decision":"revise", "issues":[{"severity":"major","span":"본문에 없는 문장","problem":"조작","repair":"수정"}]},ensure_ascii=False))
else:
    raise SystemExit("Unknown fixture role")
