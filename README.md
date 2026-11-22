# Korean Context Writing v2.0.0

실제 한국어를 쓰는 한 사람의 관점, 감정과 독자의 관심을 중심으로 하는 글쓰기 스킬.

**이번 개정의 이유:** 누적 지침을 길게 전달하는 방식에서는 설명형 원고가 반복됐다. 활성 집필 프롬프트를 짧고 직접적인 우선순위 중심으로 교체했다.

## 집필에서 실제로 읽는 자료

- `SKILL.md`: v1.2부터 유지한 맥락·관점·감정·공감·말투·후킹의 핵심
- `knowledge/voice-priority.md`: 독자가 궁금해할 것과 설명의 적절한 위치
- `profiles/author-voice.yaml`: 화자의 관점과 관계
- `prompts/writer.md`: 집필 요청

나머지 `knowledge/` 파일은 심화 검토용이며 집필 기본 프롬프트에는 연결되지 않는다.

## 실행

```bash
python3 scripts/validate_package.py
python3 -m unittest discover -s tests -p test_*.py
python3 scripts/run_pipeline.py --task '공복 유산소에 대한 커뮤니티 글' --genre 건강정보 --prepare-only --output writing_output
```

`--prepare-only`는 실제 모델 생성 없이 집필 프롬프트만 준비한다. 별도의 모델 CLI 설정은 `python3 scripts/run_pipeline.py --help`를 참고한다.

승인된 사용자 문체 예시는 집필 참고 자료로 활용하며, 피드백과 비승인 기록은 별도 보관한다. 공개 저장소에 저장할 자료의 공개 적합성을 확인한다.

기능 테스트는 활성 지침이 정확히 전달되는지 확인한다. 실제 읽는 재미와 AI 말투 개선 여부는 생성 원고와 사용자 평가로만 판단할 수 있다.
