# Claude 한국어 글쓰기 프로젝트 지침

1. SKILL.md, profiles/author-voice.yaml, knowledge/form-selection.md, knowledge/creative-practice.md, prompts/writer.md를 읽고 글의 형식과 시점을 결정해 원고를 작성한다.
2. 현재 매체와 독자, 근거 자료를 확인해 화자의 관점·정서·말투·후킹에 연결한다.
3. 사용자가 명시적으로 승인한 문체 자료를 다음 원고의 참고 사례로 사용한다.
4. 완성 원고는 편집 단계에서 prompts/reviewer.md로 평가한다. 평가자가 도출한 개선 행동을 prompts/reviser.md로 반영한다.
5. 사용자의 평가가 확인되면 scripts/feedback_memory.py record로 기록하고 공통 저장소에 반영한다.
6. 새로운 세션에서도 최신 저장소의 지침과 승인 자료를 읽는다.

프롬프트 준비: python3 scripts/run_pipeline.py --task "글쓰기 주제" --genre 건강정보 --prepare-only --output writing_output
