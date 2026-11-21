#!/usr/bin/env python3
"""Offline stub for pipeline wiring test ONLY; it never evaluates prose quality."""
import json
import sys

role = sys.argv[1]
prompt = sys.stdin.read()
if role == "writer":
    print("테스트용 문장입니다. 실제 품질은 평가하지 않습니다.")
elif role == "reviewer":
    print(json.dumps({
        "decision": "provisional",
        "scores": dict.fromkeys(("context", "stance", "voice", "empathy", "hook", "truthfulness"), 2),
        "issues": [{"severity": "minor", "span": "테스트용 문장입니다", "problem": "오프라인 실행 확인을 위한 인공 테스트 문장", "repair": "실제 LLM 품질 판정으로 사용하지 말 것"}],
        "counterfactual": "테스트 해당 없음",
        "what_to_preserve": ["테스트 문자열"],
        "revision_priority": "없음",
        "verification_note": "모의 검수이며 실제 LLM 품질 평가가 아니다"
    }, ensure_ascii=False))
else:
    raise SystemExit("unknown mock role")
