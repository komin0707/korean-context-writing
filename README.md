# 변경 사항: 지속 피드백 메모리 (v1.1.0)

**먼저 [`SETUP_PERSISTENCE.md`](SETUP_PERSISTENCE.md)를 읽어야 합니다.** 이전 v1.0 패키지는 스킬/검수 지침만 있었고, 사용자 피드백을 다음 세션에 전달하는 저장·재호출 기능은 없었습니다. 이번 버전은 `memory/feedback.jsonl`과 `scripts/feedback_memory.py`를 사용해 기존 피드백을 보관하고, `run_pipeline.py --genre ...`로 다음 글에 관련 기록을 실제 주입합니다. 장르 `--genre`는 필수입니다.

이 메모리는 **로컬 폴더 안에서만 자동 유지**됩니다. 여러 기기/Claude Work/ChatGPT Work에서 공통으로 쓰려면 같은 **비공개 원격 저장소**를 연결해 각 세션이 읽고 쓰도록 해야 합니다. 자동 동기화 설정이 없는데 모델이 스스로 기억한다고 말해서는 안 됩니다. 문체 품질을 개선했다는 검증 또한 별개입니다.

---

# Korean Context Writing — 한국어 맥락 창작 배포 패키지 v1.1.0

**용도:** Claude Opus, Claude Code, ChatGPT Work, GPT/Gemini 등에서 한국어 글을 쓰고 수정할 때 맥락·가치관·말투·공감·후킹을 실제 원고에 연결하는 외부 지침과 평가 자료.

**주의:** 이것은 파인튜닝 모델이 아니라 프롬프트/스킬/테스트 묶음이다. 사용자가 승인한 긍정적 문체 사례는 아직 적다. 파일이 있다고 AI 품질이 자동으로 보장되지 않으며, 실행 스크립트의 검사 통과는 '문체가 좋아졌다'의 증명이 아니다.

## 1. 파일 구조

```text
korean-context-writing/
├── SKILL.md                        # 모델이 가장 먼저 읽을 실행 지침
├── profiles/author-voice.yaml      # 창작 화자의 가치관/관찰 습관
├── knowledge/                      # 맥락·관점·공감·말투·후킹·사실성
├── examples/
│   ├── approved.jsonl              # 제한적으로 긍정 평가된 실제 구절
│   ├── partial.jsonl               # 부분 승인이지만 결함 있는 구절
│   ├── rejected.jsonl              # 실패 문장과 원인
│   └── rejected_articles/          # 실패한 실제 원고 5개
├── prompts/
│   ├── writer.md                    # 작성자 단계
│   ├── reviewer.md                  # 문장 인용형 별도 검수
│   ├── reviser.md                   # 원인 기반 재작성
│   ├── WORK_START.md                # Work/Claude Project 시작 지침
│   └── QUICK_START.md               # 한 번에 붙여 넣는 지침
├── tests/
│   ├── scenarios.jsonl             # 장르별 12개 회귀 시나리오
│   ├── evaluation-rubric.md         # 검수 항목/한계
│   └── test_runner.py              # 프롬프트·JSON 검증 단위 테스트
└── scripts/
    ├── run_pipeline.py             # 외부 LLM CLI 연결 가능한 실행기
    └── validate_package.py         # 구조 검사
```

## 2. 설치 및 사용

### Claude Code (권장: 파일 자동 탐색 가능한 환경)

ZIP을 풀어 `korean-context-writing` 폴더를 프로젝트의 `.claude/skills/` 안에 복사한다. 예:

```bash
mkdir -p .claude/skills
cp -R korean-context-writing .claude/skills/
```

이후 Claude에게 `korean-context-writing 스킬을 읽고, [주제]에 대한 한국어 글을 작성해. 긍정·거절 표본의 승인 상태를 지켜.`라고 요청한다. 실제 스킬 인식·부가 파일 읽기는 Claude 환경과 권한에 따라 달라질 수 있다.

### Claude 웹/프로젝트 및 ChatGPT Work

폴더를 해당 작업공간이 **열어볼 수 있는 파일로** 추가하거나 압축 해제하고, `prompts/WORK_START.md` 내용을 프로젝트 지침/작업 시작 메시지로 사용한다. ZIP 파일을 붙였다는 사실만으로 각 문서를 모델이 자동으로 읽었다고 가정하지 않는다. 특히 **필요한 파일을 실제로 열고** 진행하도록 한다. 일단은 작성/자기검수 루프로도 동작하지만, 이는 독립 검수가 아니다.

### 일반 LLM

최소한 `SKILL.md`, `profiles/author-voice.yaml`, `knowledge/*.md`, `examples/*.jsonl`을 컨텍스트로 제공한다. 가장 짧은 시작 지시는 `prompts/QUICK_START.md`. 입력 길이가 제한되면 전체 실패 원고 5개는 요약 메타데이터만 제공하고, 승인 상태가 있는 표본/핵심 지침을 우선한다.

## 3. 단일 명령으로 프롬프트 만들기 (모델 호출 없음)

```bash
python3 scripts/run_pipeline.py --task "독자가 공감할 만한 한국어 생활 칼럼 700자" --prepare-only --output writing_output
```

`writing_output/01_writer_prompt.md`가 만들어진다. 실제 LLM이 호출되지 않으므로 결과물이 생성되지는 않는다.

## 4. 작성자·검수자 CLI 연결 (고급)

두 외부 명령은 **표준입력(stdin)으로 프롬프트를 받고, 표준출력(stdout)으로 텍스트를 반환**해야 한다. 설치한 모델 CLI가 이 입출력 형식을 지원하는지 확인하고 자신이 사용하는 명령으로 바꿔 실행한다. 아래는 **형식 예시일 뿐 특정 CLI의 지원을 보장하지 않는다**.

```bash
python3 scripts/run_pipeline.py \
  --task "한국어 사회 이슈 칼럼 600자" \
  --sources-file my_sources.txt \
  --writer-cmd "your-writer-cli --stdin" \
  --reviewer-cmd "your-reviewer-cli --stdin --json" \
  --max-revisions 2 \
  --output writing_output
```

작성자→리뷰어(JSON+원문 인용)→재작성→재평가 단계를 최대 2회 반복한다. `writing_output/final_draft.md`, `run_status.json`, 초안/리뷰를 보관한다. 서로 다른 CLI를 넘겼다고 서로 다른 모델인지 스크립트가 검증하는 것은 아니다. 실제로 **다른 모델/세션을 지정**하는 것이 권장된다.

의뢰에 외부 자료가 필요한데 `--sources-file`을 지정하지 않으면 모델은 확인된 자료가 없음을 알고 작업해야 한다. 스크립트 자체는 웹 검색이나 팩트체크를 하지 않는다.

## 5. 간단한 구조 검사

```bash
python3 scripts/validate_package.py
python3 -m unittest discover -s tests -p 'test_*.py'
```

이 검사가 통과하는 것은 배포 구성과 프롬프트 구성·JSON 평가가 기능한다는 뜻일 뿐, 실제로 글이 좋다는 뜻이 아니다. 문체·공감·후킹 품질은 `tests/scenarios.jsonl`을 실제 모델에서 돌리고 사용자가 승인한 문체/실제 독자 반응과 비교해야 한다.

## 6. 추천 운영 루프

1. 원고 + 입력 자료를 그대로 저장한다.
2. 작성자 모델에 생성 → 별도 모델/세션에 리뷰 요청 → 필요한 부위만 수정한다.
3. 새 원고를 자동으로 `approved`로 넣지 않는다.
4. 사용자가 '이 부분은 좋다'고 했으면 해당 부분만 승인 상태로 보관하고, 전체 글 승인으로 확대하지 않는다.
5. 반복 실패가 나면 새로운 금지어를 쌓지 말고 `문맥이 바뀌면 표현이 실제로 달라지는가`를 시험한다.
6. 12개 회귀 시나리오에 대한 실제 모델 결과를 축적한 뒤에만 일반화된 개선을 주장한다.

## 7. 패키지 범위

한국어 원고, 문체 교정, 블로그/칼럼/커뮤니티/에세이/대사 중심. **이미지 제작, 캐러셀 디자인, SNS 업로드 자동화는 포함하지 않는다.**
