# 한국어 글쓰기 프로젝트 v3.0

집필 요청이면 SKILL.md, knowledge/voice-priority.md, knowledge/craft-lenses.md, prompts/writer.md를 따른다. 극본 작법 렌즈는 상황에 맞는 경우에만 한 가지 참고한다. 커뮤니티·이슈 글의 기본 문체는 디시인사이드(DC)식 반말과 직설적인 실제 게시글 말투다. ㅋㅋ·욕설·밈을 억지로 남발하지 않고 소재에 맞는 생각으로 웃긴다. 사용자가 다른 문체를 지정하면 그 요청을 우선한다.

2024~2026년 신조어 조사가 필요한 경우에만 lexicon/verified.jsonl과 scripts/select_slang.py의 주제별 선택 결과를 참고한다. 뜻뿐 아니라 쓰는 상황과 피할 상황을 고려하고 필요하지 않으면 넣지 않는다. research/candidates_index.jsonl은 미검증 후보 목록이며 직접 집필에 사용하지 않는다. 실제 디시 문맥이 필요한 경우 research/dc_usage/pragmatic_patterns.md와 scripts/dc_usage_context.py를 참고할 수 있지만, 표본은 검색 색인 편의표본이지 디시 전수조사가 아니다.

이미 작성된 원고를 다듬는 요청이면 prompts/polisher.md를 따른다. 원래의 사실·인용·말투를 존중하고 문제가 보이는 부분만 국소 수정한다. 검수가 필요한 경우에만 prompts/reviewer.md를 사용하며, 근거가 있는 중대한 문제만 재작성 대상으로 삼는다.

개인 메모리, 사용자 프로필, 과거 승인 표현 검색 기능은 v3.0에 없다. 과거 프로젝트와 사용자 피드백을 자동으로 불러오거나 저장하지 않는다. current task에 제공된 자료만 사용한다.
