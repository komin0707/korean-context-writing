# 영구 피드백 메모리

- `feedback.jsonl`: 사용자 확인이 있는 피드백만 기록. 자동 생성·자동 리뷰 점수는 승인 근거가 아니다.
- 한 줄은 JSON 한 개. 같은 사용자의 피드백을 덮어쓰지 않고 누적한다.
- `status=approved`는 해당 quote/scope에 한해서만 승인, `partial`은 일부만 괜찮다는 뜻, `rejected`는 거절.
- 저장소를 공유하지 않은 다른 세션은 이 파일을 자동으로 읽지 못한다.
- 원고 전체가 저장되면 민감정보가 포함될 수 있다. 비공개 저장소를 권장하며, 민감한 사건·개인정보는 저장 전 제거한다.

사용:

```bash
python3 scripts/feedback_memory.py status
python3 scripts/feedback_memory.py context --genre 건강정보 --topic '걸음 수 목표'
```
