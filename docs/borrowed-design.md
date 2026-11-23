# v3.0 설계 근거: 다른 GitHub 스킬에서 필요한 것만 채택

이 문서는 참고 구조의 출처와 제외 범위를 기록한다. 외부 프로젝트의 전체 규칙이나 독립적인 소스 코드를 복제하지 않았다.

| 원천 | 실제 참고 지점 | v3.0 적용 | 명시적 제외 |
|---|---|---|---|
| [im-not-ai](https://github.com/epoko77-ai/im-not-ai) (skills/humanize-korean/SKILL.md, agents/humanize-finalizer.md, scripts/verify_gates.py) | 목적에 따른 light·standard 처리, 글에 있는 문제만 겨냥, 원문 대비 숫자·직접 인용 보존 확인 | draft는 최소 단계, polish는 국소 윤문, 선택적 검토, 결정적 revision_guard.py | AI 문체 85개 분류의 통째 이식, 점수·AI 판별 주장, 다수 에이전트 강제, 50% 변경률 차단 |
| [screenwriting-skills](https://github.com/jtydhr88/screenwriting-skills) (sw-workflow, sw-premise-theme, sw-dialogue) | 필요한 방법만 선택, 소재의 고유 관점, 등장인물 말의 숨은 의도 | knowledge/craft-lenses.md의 3개 선택 렌즈 | story-bible·세션/개인 메모리, 극본 단계표·3막 강제, 인물 갈등 공식, 작품별 대본·책 발췌 복제 |

**사용자 요구에 따라 개인 메모리 프로젝트는 범위 밖이다.** v2.1의 과거 메모리·승인 문체 예시·프로필 파일은 v3 브랜치에서 제거했다. 이전 실험 자료는 main v2.1에만 보존된다. scripts/run_pipeline.py는 사용자 프로필·장기 메모리·승인 발췌 파일을 읽지 않는다.

두 원천은 MIT 라이선스다. 이 버전은 원본 코드를 복제하지 않고 구조적 아이디어를 독립적으로 구현했다.

## 성공을 판정하는 기준

코드 테스트는 프롬프트가 올바르게 전달되고 검수 계약이 지켜지는지만 확인한다. 자연스러운 한국어, 독창적인 시각, 원고의 재미는 실제 생성 모델과 사람의 평가가 있어야 판정할 수 있다. 특히 삭제·윤문은 새로운 생각을 저절로 만들어 주지 않는다.
