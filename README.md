# Korean Context Writing v3.0.0

소재에 맞는 생각을 찾는 **집필**과 이미 좋은 원고를 보존하는 **국소 윤문**을 나눈 한국어 글쓰기 스킬.

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
