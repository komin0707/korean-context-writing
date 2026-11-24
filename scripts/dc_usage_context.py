#!/usr/bin/env python3
"""Offline, evidence-linked usage examples from individually reviewed/indexed DC sources.

Never crawls DCInside. Every record contains a link and an independently
authored description instead of post/comment text. Low-confidence entries
must not be presented as direct verification of complete posts/comments.
"""
from __future__ import annotations
import argparse
import json
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CASES=ROOT/'research/dc_usage/indexed_usage_cases.jsonl'

def read_cases(path: Path=CASES):
    return [json.loads(l) for l in path.read_text(encoding='utf-8').splitlines() if l.strip()]

def for_terms(terms,asof='2026-11',max_cases=3,cases=None):
    """Return max_cases independent gallery examples, preferring full-page evidence."""
    cutoff=asof
    termset={s.lower() for s in terms if s.strip()}
    matches=[]
    for c in cases if cases is not None else read_cases():
        if c['date'][:7]>cutoff:
            continue
        variants={s.strip().lower() for s in c['term'].split('/')}
        variants.add(c['term'].lower())
        if not any(t in variants or (len(t)>=3 and t in c['term'].lower()) for t in termset):
            continue
        matches.append(c)
    matches.sort(key=lambda c:(c['evidence']!='read_post',-int(c['date'].replace('-','')),c['gallery']))
    selected=[]
    galleries=set()
    for c in matches:
        if c['gallery'] in galleries:
            continue
        selected.append(c)
        galleries.add(c['gallery'])
        if len(selected)>=max_cases:
            break
    return selected

def render(cases):
    if not cases:
        return ''
    lines=[
        '# DC 게시글 사용 맥락: 간접 요약 참고',
        '검색엔진 색인으로 찾은 글 중 일부를 수동 검토한 사례이며 디시 전체 표본이나 실시간 통계가 아니다.',
        '예시를 그대로 따라 쓰거나 원문의 사람을 조롱하지 말고 실제 발화 목적이 같은 경우에만 참고한다.'
    ]
    for c in cases:
        level=('본문 열람' if c['evidence']=='read_post' else '검색 색인 일부')
        lines += [
            '- '+c['term']+' / '+c['gallery']+' / '+c['date']+' ('+level+')',
            '  상황: '+c['context_summary'],
            '  발화 기능: '+c['speech_act']+' / '+c['tone']+'; 대상: '+c['referent'],
            '  주의: '+c['caution'],
            '  링크: '+c['url']
        ]
    return '\n'.join(lines)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--terms',nargs='+',required=True)
    p.add_argument('--asof',default='2026-11')
    p.add_argument('--limit',type=int,default=3)
    p.add_argument('--format',choices=['text','json'],default='text')
    args=p.parse_args()
    selected=for_terms(args.terms,args.asof,args.limit)
    if args.format=='json':
        print(json.dumps(selected,ensure_ascii=False,indent=2))
    else:
        print(render(selected) or '해당 표현의 검증 가능한 DC 게시글 예시가 아직 없다.')
if __name__=='__main__':
    main()
