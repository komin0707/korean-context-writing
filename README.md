# Korean Context Writing v3.1.1-preview

소재에 맞는 생각을 찾는 **집필**과 이미 좋은 원고를 보존하는 **국소 윤문**을 나눈 한국어 글쓰기 스킬.

## 기본 말투

별도 요청이 없는 커뮤니티·이슈 글은 **디시인사이드(DC) 반말·직설적인 게시글 말투**를 사용한다. ㅋㅋ·욕설·밈은 문맥에 맞을 때만 쓰며, 따로 지정된 문체가 있으면 그 문체를 우선한다.

## 2024~2026 한국 커뮤니티 언어 아카이브 (별도 미검증 기능)

2024년 11월~2026년 11월 전후의 신조어·밈·댓글 형식을 조사한다. **현재 159개 수집 후보 + 40개 출처 기반 용례 정리**, 모든 인터넷 표현을 망라한 것은 아니다.

- 후보: research/candidates_index.jsonl — 공개 목록에서 분류연도가 2024~2026인 용어만 수집한 것으로, 실제 등장 시기나 사용 적합성은 **미확인**.
- 용례 검토: lexicon/verified.jsonl — 의미·쓰는 상황·피해야 할 상황·직접 작성한 예문·날짜·출처, DC 1차 게시글 표본 일부 포함.
- 출처: research/sources.json — 기사와 사전 링크, 날짜 및 한계.
- 선택 도구: scripts/select_slang.py — 현재 주제와 관련된 후보만 최대 3개 추천. 글에 반드시 넣으라는 뜻 아님.

사용 예시:

    python3 scripts/select_slang.py --topic "패션 브랜드 로고 디자인" --genre community --asof 2026-11

원고에 **선택 자료를 추가하고 싶을 때만**:

    python3 scripts/run_pipeline.py --task "패션 브랜드 로고 디자인에 대한 커뮤니티 글" --genre community --slang-context --asof-month 2026-11 --prepare-only --output /tmp/slang-demo

기본 집필에는 자동 유행어 삽입이 없고, 기존 3.0.1의 기능이 그대로 유지된다.

수집 후보 목록을 나중에 직접 새로고침하려면 (추가 패키지 requests, beautifulsoup4 필요):

    python3 scripts/refresh_slang_candidates.py --years 2024 2025 2026

새로 수집된 이름은 검토 전 후보이며, 실제 뜻·시기·용례를 자동 승인하지 않는다.

## 디시 게시글 사용 맥락 조사 (추가 연구 브랜치)

**디시 전체를 전수조사하지는 않았다.** 디시 이용약관의 사전 동의 없는 크롤링 제한 때문에, 공개 검색 색인에서 개별적으로 확인할 수 있는 사례와 사람이 읽은 일부 게시글만 분석했다.

- research/dc_usage/indexed_usage_cases.jsonl — 여러 갤러리의 실제 표현을 날짜·발화 기능·사용 대상·주의점·근거 URL로 정리. 작성자 이름과 댓글 원문은 저장하지 않음.
- research/dc_usage/pragmatic_patterns.md — 13개 발화 기능의 차이를 소재별로 해설.
- research/dc_usage/coverage_report.md — 확인한 사례 수, 기간, 갤러리, 검토 수준, 불균형과 누락 범위.
- research/dc_usage/study_protocol.md — 향후 서면 권한을 얻은 경우의 본 조사 설계.
- scripts/dc_usage_context.py — 특정 유행어의 실제 게시글 맥락 0~3개를 독립 요약으로 조회.
- scripts/report_dc_usage.py — 관측 범위를 다시 계산.
- scripts/analyze_authorized_dc_export.py — 별도로 허가받은 JSONL 자료가 있을 때만 오프라인 건수 집계(네트워크·직접 크롤링 없음).

    python3 scripts/dc_usage_context.py --terms 느좋 --asof 2026-11 --limit 3
    python3 scripts/report_dc_usage.py

기존 --slang-context를 지정하면 정리된 어휘 뜻과 함께 관련된 디시 사용 맥락 최대 3개까지 참고자료로 붙인다. 기본 집필은 이전처럼 유행어 목록을 자동 삽입하지 않는다. **현재 41개 사례 중 본문 전체 확인 13개, 색인 일부 확인 28개이고 댓글 전체 분석은 아직 0건이다.**

## 2.1에서 유지한 것

맥락·화자·감정·독자·말투·후킹·근거의 우선순위, 짧고 직접적인 활성 집필 프롬프트, 소재에만 있는 신선한 생각 찾기.

## 외부 GitHub에서 선별한 것

- [im-not-ai](https://github.com/epoko77-ai/im-not-ai): 꼭 필요한 구간만 윤문하고 원본 대비 수치·직접 인용을 확인하는 설계. 85개 규칙과 강제 다중 에이전트는 제외.
- [screenwriting-skills](https://github.com/jtydhr88/screenwriting-skills): 관찰·인물 관계·대사 기능을 **선택적 렌즈**로 정리. 극본 단계표·story-bible은 제외.
- 상세 출처 및 제외 사항: docs/borrowed-design.md.

**개인 메모리 시스템을 사용하지 않는다.** 사용자 프로필, 과거 피드백, 승인 문체 예시가 자동으로 로드되지 않는다. 과거 v2.1의 examples/와 memory/ 데이터·관련 스크립트는 v3 브랜치에서 제거했다. 이전 기록은 v2.1 main 브랜치에만 남아 있다. 특정 문체를 꼭 참고시키고 싶다면 이번 작업의 파일을 --style-file로 직접 지정한다.

## 실행

프롬프트만 준비 (모델 호출 없음):

    python3 scripts/run_pipeline.py --task "운동 영상만 저장하는 습관" --genre 커뮤니티 --prepare-only --output /tmp/v3-draft

집필 (입력을 표준입력으로 받고 결과를 표준출력으로 내보내는 별도 모델 CLI 필요):

    python3 scripts/run_pipeline.py --task "운동 영상만 저장하는 습관" --writer-cmd "YOUR_MODEL_WRAPPER" --output /tmp/v3-draft

이미 작성된 원고의 국소 윤문:

    python3 scripts/run_pipeline.py --mode polish --task "말투와 중복만 보수적으로 윤문" --draft-file draft.md --writer-cmd "YOUR_MODEL_WRAPPER" --output /tmp/v3-polish

선택적 검토와 최대 1회 국소 수정:

    python3 scripts/run_pipeline.py --task "주어진 자료로 이슈 논평" --writer-cmd "YOUR_MODEL_WRAPPER" --reviewer-cmd "YOUR_REVIEWER_WRAPPER" --max-revisions 1

- 검토 모델이 없으면 초안 1회로 종료.
- 검토 모델이 accept라고 하면 재작성하지 않음.
- 명백한 주요 문제가 인용되었을 때만 최대 1회 국소 수정.
- 숫자나 따옴표 안의 원문이 달라지면 안전상 초안을 보존하고 경고.
- 이 게이트는 의미·사실 정확성을 완전히 판정하지 못한다. final_draft.md는 사용자 승인으로 간주하지 않는다.
- 별도 모델 CLI를 제공하지 않는 준비 모드만으로 글의 실제 품질을 주장할 수 없다.

## 테스트

    python3 scripts/validate_package.py
    python3 -m unittest discover -s tests -p 'test_*.py'

**v2.1 정식본은 main 브랜치에 보존된다.** v3는 별도 브랜치에서 검증한다.
