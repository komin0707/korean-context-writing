# Korean Context Writing v1.4.0

한국어의 사회적·심리적 맥락, 화자의 관점, 감정의 이유, 자연스러운 언어의 호흡을 하나의 글로 엮는 창작 스킬입니다.

## 작성 경로

SKILL.md와 knowledge/editorial-voice.md, knowledge/creative-practice.md, profiles/author-voice.yaml, prompts/writer.md를 기준으로 작성합니다. 글의 출발점은 필자가 이 이야기를 꺼내는 이유가 되는 중심 관찰입니다. 원고의 목적과 매체는 실제 과제로부터 결정됩니다.

사용자 승인이 확인된 문체 자료를 작성 경로에 활용합니다. 과거 거절 사례와 평가 기록은 저장소에서 별도로 보관합니다. 검수 모델은 작성된 원고를 읽고 긍정형 개선 방향을 도출합니다.

## 실행

python3 scripts/validate_package.py

python3 -m unittest discover -s tests -p test_*.py

python3 scripts/run_pipeline.py --task '하루 만 보 목표를 재해석한 글' --genre 건강정보 --prepare-only --output writing_output

writing_output/01_writer_prompt.md에 작성 지침이 준비됩니다. 외부 작성 모델을 연결하려면 scripts/run_pipeline.py --help를 참고합니다.

## 다른 LLM에서 사용

Claude Code에서 폴더를 프로젝트의 .claude/skills/korean-context-writing 아래에 둡니다. Work와 일반 LLM에서는 SKILL.md 및 실행 자료를 작업공간에 제공하고 prompts/WORK_START.md를 사용합니다.

## 누적 피드백

scripts/feedback_memory.py record 명령으로 사용자가 명시적으로 평가한 사례를 저장합니다. 현재 GitHub 저장소는 공개이므로 기록 내용은 외부에서도 열람할 수 있습니다.

기능 테스트는 실행 경로와 파일 구성을 확인합니다. 실제 LLM의 문체·공감·독자 반응은 생성 원고에 대한 평가로 따로 검증합니다.
