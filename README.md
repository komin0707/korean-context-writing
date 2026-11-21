# Korean Context Writing v1.2.0

한국어 창작을 위한 맥락·화자·감정·말투·후킹 작성 지침과 검수, 누적 피드백 저장 시스템.

## 작성자 실행 자료

1. SKILL.md
2. profiles/author-voice.yaml
3. knowledge/creative-practice.md
4. prompts/writer.md

작성자는 위 지침과 사용자가 명확히 승인한 문체 사례를 사용한다. 원고 작성 지침은 실행할 행동을 긍정형으로 기술한다.

## 별도 검수 자료

- prompts/reviewer.md: 원고를 평가해 구체적인 개선 행동을 도출한다.
- prompts/reviser.md: 개선 행동과 보존할 사실을 사용해 원고를 재작성한다.
- memory/feedback.jsonl 및 examples/rejected.jsonl: 사용자의 평가 기록. 검수 단계에서 활용한다.
- tests/: 실행 경로와 평가 형식의 기능 검사.

작성자 프롬프트와 검수자 프롬프트는 분리되어 있으며, 기존의 거절 문구는 작성자 프롬프트에 포함되지 않는다.

## Claude Code 설치

저장소 폴더를 프로젝트의 .claude/skills/korean-context-writing 에 설치한다. 작업 공간 지침으로 CLAUDE_PROJECT_INSTRUCTIONS.md를 사용할 수 있다.

## Work 및 일반 LLM

SKILL.md, profiles/author-voice.yaml, knowledge/creative-practice.md, prompts/writer.md를 작업 공간에서 읽을 수 있도록 제공한다. prompts/WORK_START.md를 시작 지침으로 사용한다.

## 실행

~~~bash
python3 scripts/validate_package.py
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/run_pipeline.py --task '만 보 걷기에 대한 한국어 글' --genre 건강정보 --prepare-only --output writing_output
~~~

writing_output/01_writer_prompt.md: 긍정형 지침과 승인 사례를 포함한 작성용 프롬프트.
writing_output/00_reviewer_memory.md: 검수 전용 피드백 자료.
writing_output/02_reviewer_prompt_template.md: 독립 검수용 기본 템플릿.

외부 LLM 실행기를 사용할 경우 scripts/run_pipeline.py --help를 참고한다. 검수자 평가는 사람의 승인과 별도로 기록한다.

## 지속 메모리

scripts/feedback_memory.py record로 사용자의 명확한 평가를 저장한다. 현재 저장소는 공개 GitHub에 있으므로 개인적인 내용은 저장소에 추가하기 전에 공개 적합성을 확인한다.

설치 및 동기화 관련 세부 단계는 SETUP_PERSISTENCE.md 참조.
