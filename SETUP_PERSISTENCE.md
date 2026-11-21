# 지속형 한국어 글쓰기 — 실제 운영 방법

> 이 문서는 **한 번의 교정이 다음 글에 자동 반영되도록 하는 외부 기억 시스템**의 설치법이다. 모델이 스킬을 읽는다고 실제 가중치를 재학습하지는 않는다. 메모리 파일을 저장/공유하고 매번 불러오는 것이 핵심이다.

## 0. 무엇이 작동하나

- `memory/feedback.jsonl`: 과거 피드백 영구 저장. 편집·버전관리 가능한 한 줄 JSON 객체 기록.
- `scripts/feedback_memory.py`: **사용자가 실제로 승인/부분 승인/거절한** 표현과 사유를 기록하고, 다음 원고에 관련 사례를 재검색.
- `scripts/run_pipeline.py`: 작성자 프롬프트를 만들 때 **현재 장르와 주제에 관련된 저장 피드백**을 읽어 넣는다. 작성/검수 모델을 연결했다면 실제로 글쓰기 루프 실행 가능.
- `profiles/author-voice.yaml`, `knowledge/`: 작가의 기준과 한국어 창작 규칙. 단순 사용자의 호감/불호로 사실 판단을 변경하지 않는다.
- `tests/`: 저장·재호출·장르 분리·무단 승인 차단 테스트.

**한계:** 이 시스템은 사용자가 좋아할 문장을 예측하는 학습모델이 아니다. 사용자 피드백을 다음 세션에 계속 전달하고 과거 오류를 다시 검토할 수 있는 **재현 가능한 피드백 메모리**다. 사람 평가 없이는 품질 향상 자체를 입증하지 못한다.

## 1. 한 컴퓨터에서 설치 후 사용 (macOS/Linux/Windows Python 3)

```bash
# 폴더 안에서 실행
cd korean-context-writing
python3 scripts/feedback_memory.py status
```

처음 실행하면 기존에 평가된 구절이 기록되어 있다. `approved`는 0개다. 예전 대화에서 긍정 반응이 있었던 한 구절도 **전체 승인 아닌 부분 승인**으로만 기록했기 때문이다.

주제와 장르를 전달해 프롬프트 준비:

```bash
python3 scripts/run_pipeline.py \
  --genre 건강정보 \
  --task '만 보 걷기의 효과를 연구를 바탕으로, 자연스러운 한국어 관점 글로 작성' \
  --prepare-only \
  --output runs/manbo
```

생성된 `runs/manbo/01_writer_prompt.md`를 Claude Opus/Work에 전달한다. `00_selected_memory.md`에서 실제 선택된 피드백을 직접 확인할 수 있다. **이 명령은 LLM을 부르지 않는다.** 별도 LLM CLI가 있으면 기존 `run_pipeline.py`의 `--writer-cmd` / `--reviewer-cmd`를 사용한다.

### 사용자가 원고를 거절했을 때: 정확히 1회 기록

```bash
python3 scripts/feedback_memory.py record \
  --status rejected \
  --genre 건강정보 \
  --topic '만 보 걷기' \
  --file runs/manbo/final_draft.md \
  --scope whole_article \
  --reason '사용자가 전체 원고를 거절함. 구체적인 거절 사유는 추가 확인 필요.'
```

`final_draft.md`가 없는 수동 작업이라면 실제 작성된 `.md`를 `--file`로 지정한다. 사용자가 어휘 하나만 거절하면 `--quote '...' --scope excerpt`를 쓴다. AI가 자기 추측으로 거절 사유를 꾸며서 '사용자 피드백'으로 저장하면 안 된다.

### 좋은 문장을 사용자가 명시적으로 승인했을 때

```bash
python3 scripts/feedback_memory.py record \
  --status approved \
  --genre 이슈논평 \
  --topic '직장 내 불공평한 부탁' \
  --quote '실제로 사용자가 승인한 짧은 문장을 넣는다' \
  --scope excerpt \
  --reason '사용자가 특정 문장의 관찰/말투를 긍정 평가함'
```

승인하지 않은 원고에 `approved`를 붙이지 않는다. 모델 자신의 점수/검수 결과도 승인으로 취급하지 않는다.

이후 다시 `run_pipeline.py --genre ... --task ... --prepare-only`를 실행하면, **새로 기록한 관련 피드백**이 포함된 프롬프트가 생성된다. 매번 사람이 같은 설명을 반복할 필요가 없게 만드는 실제 메커니즘이다.

## 2. Claude Code에서 반복 작업을 줄이기

- 프로젝트의 `.claude/skills/korean-context-writing/`에 폴더 전체를 둔다.
- 프로젝트 루트의 `CLAUDE.md`에 이 패키지의 `CLAUDE_PROJECT_INSTRUCTIONS.md` 내용을 넣는다.
- 글쓰기 전에 실행 도구가 허용되면 `scripts/feedback_memory.py context` 또는 `scripts/run_pipeline.py --prepare-only`로 피드백을 읽게 한다.
- 사용자 반응이 **실제로 확인된 경우에만** `feedback_memory.py record`로 저장하게 한다.
- 파일 쓰기가 불가능하면 `저장 완료`라고 답하지 않는다.

Claude Code/에이전트가 스킬을 읽는 것과 스크립트를 실제로 호출하는 것은 다르다. **실행 기록**에서 `record` 실행 여부를 확인해야 한다.

## 3. Work/Claude 웹 등 서로 다른 세션을 잇기

컴퓨터 안의 파일은 다른 클라우드 세션에서 자동 접근할 수 없다. **공통 저장 위치**가 필요하다. 다음 중 하나를 선택한다.

**추천: 개인 GitHub 비공개 저장소**

1. `korean-context-writing` 폴더를 새 **비공개** 저장소에 올린다. 개인 피드백과 원고가 들어가므로 공개 저장소는 권하지 않는다.
2. Claude Code/Work에서 같은 저장소를 읽을 수 있도록 연결한다. 지원되는 연결/권한은 사용하는 앱의 실제 상태에 따르며, 연결이 안 된다면 해당 세션은 누적 기억을 사용할 수 없다.
3. 작업 시작 시 최신 `memory/feedback.jsonl`과 스킬 파일을 읽게 하고, 사용자 반응을 받은 뒤 변경사항을 **같은 저장소에 커밋/반영**하게 한다.
4. 다음 세션은 저장소 최신 버전을 다시 읽는다. 이것이 기기와 모델을 넘어서는 '기억'의 실체다.

로컬 Git 명령 예시 (새 비공개 원격 저장소 URL이 준비된 경우):

```bash
git init
git add SKILL.md profiles knowledge examples prompts scripts memory tests README.md SETUP_PERSISTENCE.md
 git commit -m 'Initialize Korean writing memory'
git branch -M main
git remote add origin <본인의 비공개 GitHub 저장소 URL>
git push -u origin main
```

이후 연결된 프로젝트에서 피드백 파일을 갱신했다면 `git add memory/feedback.jsonl && git commit -m 'Add explicit writing feedback' && git push`를 실행한다. 다른 기기에서는 먼저 `git pull --ff-only`로 최신 변경사항을 가져온다. **동시에 여러 세션이 수정하면 충돌 병합이 필요**하다.

비공개 GitHub를 사용할 수 없다면, 모든 세션이 읽고 **수정까지 할 수 있는** 같은 Drive 폴더나 저장소에 두어도 된다. 단순히 ZIP을 각 세션에 따로 업로드하면 서로 독립된 복사본이라 누적되지 않는다.

## 4. 독립 검수는 별도 기능이다

저장된 피드백을 불러오는 것과, 현재 글이 좋은지를 판정하는 것은 다르다.

- 작성자 모델: 현재 과제 + 관련 피드백 + 원문 자료 사용
- 검수 모델/별도 세션: 실제 문장을 인용하며 자연스러움, 맥락, 공감, 후킹, 사실성 검토
- 수정자: 검수의 구체적 오류만 수정
- **사용자 평가**: 승인/거절 여부를 영구 피드백으로 기록

독립 검수에서 높은 점수를 받더라도 사용자 승인으로 기록하면 안 된다. 같은 모델을 두 번 실행했다고 독립 평가가 자동으로 생기는 것도 아니다.

## 5. 설치 확인

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/feedback_memory.py status
```

검사는 **저장·검색·메모리 호출** 기능만 확인한다. 한국어 글쓰기 결과가 우수하다는 증명은 아니다.
