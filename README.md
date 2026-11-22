# Korean Context Writing — v1.9.0 (v1.2 핵심 복원)

이 버전은 v1.2의 한국어 맥락 창작 구조를 기준으로 한다. **맥락, 화자의 가치관과 관점, 감정이 생기는 이유, 독자 입장과 공감, 자연스러운 한국어 말투, 후킹**을 글 속에서 서로 연결하는 것이 목표다.

## 작성에 사용되는 파일

- `SKILL.md`: v1.2의 중심 원칙과 10단계 사고 구조
- `profiles/author-voice.yaml`: 화자의 가치 기준과 표현 습관
- `knowledge/creative-practice.md, knowledge/korean-expression.md, knowledge/emotion-and-reader.md`: 맥락, 실제 한국어 주어·동사·연어·조사·어미와 문장 사이의 연결
- `prompts/writer.md`: 원고 작성 프롬프트

작성 단계에는 긍정형 지침과 사용자에게 명확하게 승인된 사례만 전달한다. 편집 기록은 별도로 보관한다. 현재 승인된 전체 원고 표본은 부족하므로 실제 문체의 만족도는 사용자 검증이 필요하다.

## 실행

```bash
python3 scripts/validate_package.py
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/run_pipeline.py --genre 건강정보 --task '만 보 걷기 원고 작성' --prepare-only --output writing_output
```

`writing_output/01_writer_prompt.md`가 작성용 프롬프트다. `--prepare-only`는 모델을 호출하지 않는다. 실제 LLM 호출 방법은 `python3 scripts/run_pipeline.py --help`에서 확인할 수 있다.

Claude Code에서는 프로젝트의 `.claude/skills/korean-context-writing/` 아래에 설치한다. Work나 일반 LLM은 위 작성 자료를 접근 가능한 작업 공간에 넣고 `prompts/WORK_START.md`를 사용한다.

사용자의 평가를 기록하려면 `scripts/feedback_memory.py record`를 사용한다. 현재 GitHub 저장소는 **공개** 상태이므로 저장하는 내용의 공개 적합성을 확인해야 한다. 동기화 방법은 `SETUP_PERSISTENCE.md`를 따른다.

기능 테스트는 스킬 구성과 프롬프트 주입·피드백 격리를 검사한다. 실제 Opus 원고의 자연스러움·감정·공감·후킹은 별도 실사용 검증 대상이다.
\n- \`knowledge/reader-imagination.md\`: 독자 머릿속에 장면을 만드는 지침\n