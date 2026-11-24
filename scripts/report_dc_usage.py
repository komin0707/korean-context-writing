#!/usr/bin/env python3
"""Coverage report from individually curated public search/index examples.

Does not crawl, fetch, or interact with DCInside. Observations are
convenience-sampled and should never be represented as a census.
"""
from __future__ import annotations
import argparse
from collections import Counter
from pathlib import Path
from dc_usage_context import read_cases

ROOT=Path(__file__).resolve().parents[1]
DEFAULT=ROOT/'research/dc_usage/coverage_report.md'
ACT_NAMES={
 'aesthetic_praise':'감각·분위기 칭찬',
 'negative_aesthetic_judgement':'색감·디자인 혹평',
 'solicit_consensus':'공감·추천 요청',
 'claim_fairness':'편파적 평가를 배제한다는 자기 선언',
 'self_deprecating_nerd_explainer':'덕후 지식 설명의 자조적 제목',
 'criticize_low_effort_ai':'자동 생성의 쉬움·품질 문제 지적',
 'dismissive_indifference':'타인 요구를 신경 쓰지 않음',
 'dismiss_responsibility_claim':'선택의 책임을 반문',
 'moderation_norm':'갤러리 자랑·운영 규칙',
}

def describe(cases):
    galleries={x['gallery'] for x in cases}
    terms={x['term'] for x in cases}
    years=Counter(x['date'][:4] for x in cases)
    styles=Counter(x['speech_act'] for x in cases)
    genres=Counter(x['genre'] for x in cases)
    inspected=sum(x['evidence']=='read_post' for x in cases)
    snippets=sum(x['evidence']=='indexed_excerpt' for x in cases)
    lines=['# 디시인사이드 사용 맥락 조사: 확인한 범위',
           '',
           '**이 파일은 디시 전수조사가 아니다.** 검색에 공개 색인된 글을 조건에 맞춰 직접 선별한 편의표본으로, 어휘가 등장한 시점과 대략의 발화 의도를 설명하기 위한 기초 자료다.',
           '',
           '## 표본 수와 한계',
           '',
           f'- 사용 사례: **{len(cases)}건** (동일 글의 다른 표현은 별개 사용 사례로 계산)',
           f'- 확인된 갤러리: **{len(galleries)}개**',
           f'- 서로 다른 관찰 표현/복합 표현: **{len(terms)}개**',
           f'- 게시글 내용까지 확인: **{inspected}건** / 검색 색인 발췌에 의존: **{snippets}건**',
           '- 전체 댓글 원문 분석: **0건** (댓글 시스템 동적 표시 및 별도 권한/수집 문제)',
           '- 임의 표본추출/이용자 대표성/세대별 사용량/분기별 전체 게시글 수: **측정하지 않음**',
           '- 작성자 닉네임·IP·게시글 원문·이미지·댓글 전문은 저장하지 않고 링크와 독립 요약만 기록.',
           '- 실제 날짜는 게시글 표기 또는 색인에서 확인한 기록만 사용하며, 이후 유행 지속 여부를 의미하지 않는다.',
           '',
           '## 연도별 확인 건수', '',
           '| 연도 | 기록된 사용 사례 |', '|---|---:|']
    for year,count in sorted(years.items()):
        lines.append('| '+year+' | '+str(count)+' |')
    lines+=['','## 사용 기능별 빈도 (이 표본에서만)','',
            '| 발화 기능 | 사례 수 |','|---|---:|']
    for function,count in styles.most_common():
        lines.append('| '+ACT_NAMES.get(function,function)+' | '+str(count)+' |')
    lines+=['','## 주제별 갤러리 분포 (이 표본에서만)','',
            '| 주제 | 사례 수 |','|---|---:|']
    for genre,count in genres.most_common():
        lines.append('| '+genre+' | '+str(count)+' |')
    lines+=['','## 모든 사례 링크와 문맥','','각 게시글의 날짜·갤러리·사용 표현·화행 기능·다른 의미·주의점은 indexed_usage_cases.jsonl에 보관한다. 본문 전체나 댓글 원문은 보관하지 않는다.',
            '',
            '## 더 넓은 조사를 위한 필수 조건','','- **수집 승인:** 디시인사이드 약관상 서면 동의 없이 서비스 크롤링을 해서는 안 된다. 사이트가 공식 제공한 접근 권한 또는 재배포·분석 권리가 있는 별도 데이터 확보가 선행되어야 한다.',
            '- **표본 설계:** 메이저·마이너·미니 갤러리, 분야, 글/댓글, 연도·분기, 추천 상위/일반 글을 층화하고 갤러리별 선택확률을 기록해야 한다.',
            '- **상황 라벨링:** 칭찬·조롱·자조·반어·수사적 동의 요청·집단 내부 은어·팬덤 인용을 구분하고 중의성 사례를 보류해야 한다.',
            '- **검증:** 독립 평가자가 문맥을 보고 합의한 사례만 집필 자료로 승격. 특정 단어의 사용 빈도와 쓰임의 적절성은 별도 측정해야 한다.',
            '',
            '## 검토 근거','','디시 정책: https://nstatic.dcinside.com/dc/w/policy/policy_index.html',
            '실제 사례: indexed_usage_cases.jsonl의 URL 필드를 참조.',
            '']
    return '\n'.join(lines)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',type=Path,default=DEFAULT)
    args=ap.parse_args()
    cases=read_cases()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(describe(cases),encoding='utf-8')
    print(f'Generated report for {len(cases)} cases at {args.out}')

if __name__=='__main__':
    main()
