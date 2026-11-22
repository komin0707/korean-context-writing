# v2.1 말투 고정, 생각만 바꾸는 대조 실험

**메인 스킬 무수정**. 이 브랜치의 \`SKILL.md\`, \`knowledge/voice-priority.md\`, \`prompts/writer.md\`, \`profiles/author-voice.yaml\`, \`scripts/run_pipeline.py\`는 기준 버전과 동일해야 한다.

이 실험은 '새로운 말투를 만들기'가 아니라, 같은 말투의 작성 모델에 **관찰 카드 한 장만 더 전달**했을 때 글이 달라지는지 검증한다.

- 기존 원고: 현재 v2.1 작성 프롬프트 그대로 사용
- 실험 원고: 같은 작성 프롬프트의 **의뢰 부분에만** 짧은 관찰 카드 내용 추가
- 카드 생성: 별도 LLM 호출, 오직 '글을 쓰고 싶은 이유'와 화자의 반응을 찾는 데 집중
- 근거 제공: 두 원고에 똑같은 사실 자료 전달
- 사실 검증: 별도 단계에서 동일한 기준으로 진행

## 사용법

원고 전문보다 확인된 사실·조건을 취재 메모 \`facts.md\`로 준비한다.

\`\`\`bash
python3 experiments/voice_lock/run.py \
  --task '만보계 목표를 소재로 한 가벼운 커뮤니티 글' \
  --genre 건강정보 --sources-file facts.md --output /tmp/voice-test
\`\`\`

출력되는 \`01_angle_prompt.md\`를 Opus 새 세션에서 실행하고 JSON 응답을 \`angle.json\`에 저장한다.

\`\`\`bash
python3 experiments/voice_lock/run.py \
  --task '만보계 목표를 소재로 한 가벼운 커뮤니티 글' \
  --genre 건강정보 --sources-file facts.md \
  --mode build --angle-file angle.json --output /tmp/voice-test
\`\`\`

생성된 \`02_baseline_writer_prompt.md\`와 \`03_variant_writer_prompt.md\`를 동일한 Opus 설정과 각각 새 대화에서 실행한다. 또는 표준입력 프롬프트를 받아 표준출력에 응답하는 모델 CLI를 갖췄다면 \`--mode run --model-cmd '명령어'\`로 세 단계를 자동 실행한다.

평가는 작성 조건을 가리고 진행한다. 기존보다 **자연스러운 말투를 유지**하면서도 **소재만의 관찰 / 화자의 실제 가치관 / 감정의 흐름 / 불필요한 설명량 / 사실 정확성**을 비교한다. 관점만 좋아져도 문체가 망가지면 기존 스킬에 반영하지 않는다.

**검증 범위:** 이 스크립트는 두 입력과 자동 실행 방법을 보장할 뿐, 모델이 실제로 재미있게 쓰는지를 보장하지 않는다.
