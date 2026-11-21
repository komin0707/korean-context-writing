#!/usr/bin/env python3
"""Persistent, auditable feedback memory for Korean writing.

- UTF-8 JSONL is human-editable and Git-friendly.
- Only explicit user feedback gets stored. Generated/reviewed output is NEVER approved automatically.
- Retrieval uses genre/topic and conservative character n-gram matching, not an LLM quality guess.
- This is external memory, not training or a promise of literary quality.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import uuid
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / 'memory' / 'feedback.jsonl'
GENRES = {
    '건강정보': {'건강','건강정보','생활정보','건강/생활정보','정보','의학','의료'},
    '이슈논평': {'이슈','논평','이슈/커뮤니티 논평','커뮤니티','사회이슈','시사'},
    '감정경험': {'감정','경험','에세이','직장불만','직장 불만 커뮤니티 글','카톡','대화'},
}


def canonical_genre(genre: str) -> str:
    genre = re.sub(r'\s+', '', genre.strip())
    for root, keys in GENRES.items():
        normalized_keys = {re.sub(r'\s+', '', key) for key in keys}
        if genre in normalized_keys:
            return root
    # Match multi-part source labels such as '건강/생활정보 블로그' conservatively.
    if any(k in genre for k in ('건강','생활정보','의료','의학','수분')):
        return '건강정보'
    if any(k in genre for k in ('이슈','논평','시사')):
        return '이슈논평'
    if any(k in genre for k in ('감정','에세이','직장불만','대화')):
        return '감정경험'
    return genre or '일반'


def read_entries(log: Path = LOG) -> list[dict]:
    if not log.exists():
        return []
    entries = []
    for i, line in enumerate(log.read_text(encoding='utf-8').splitlines(), 1):
        if line.strip():
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f'Invalid JSONL at {log}:{i}: {exc}') from exc
            if item.get('status') not in {'approved','partial','rejected'}:
                raise ValueError(f'Invalid status at line {i}')
            entries.append(item)
    return entries


def append_entry(entry: dict, log: Path = LOG) -> None:
    log.parent.mkdir(parents=True, exist_ok=True)
    # Append a single line; avoid rewriting past feedback.
    with log.open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(entry, ensure_ascii=False, separators=(',',':')) + '\n')
        stream.flush()
        os.fsync(stream.fileno())


def make_entry(status: str, genre: str, topic: str, quote: str, reason: str,
               source: str = '', scope: str = 'excerpt', confirmed_by: str = 'user') -> dict:
    if status not in {'approved','partial','rejected'}:
        raise ValueError('status must be approved, partial, or rejected')
    if confirmed_by != 'user':
        raise ValueError('Only explicit user feedback can enter this memory')
    if not quote.strip() or not reason.strip():
        raise ValueError('quote and reason required; do not infer silent approval')
    if scope not in {'excerpt','whole_article'}:
        raise ValueError('scope must be excerpt or whole_article')
    return {
        'id': 'fb_' + uuid.uuid4().hex[:12],
        'timestamp': dt.datetime.now(dt.timezone.utc).isoformat(),
        'status': status, 'genre': canonical_genre(genre),
        'topic': topic.strip(), 'scope': scope,
        'quote': quote.strip(), 'reason': reason.strip(),
        'source': source, 'confirmed_by': 'user'
    }


def grams(s: str) -> set[str]:
    s = re.sub(r'[^가-힣A-Za-z0-9]+','', s.lower())
    if len(s) < 2:
        return {s} if s else set()
    return {s[i:i+2] for i in range(len(s)-1)}


def relevance(entry: dict, genre: str, topic: str) -> float:
    genre_match = canonical_genre(entry.get('genre','')) == canonical_genre(genre)
    g1, g2 = grams(entry.get('topic','')), grams(topic)
    overlap = len(g1 & g2) / max(1, len(g1 | g2))
    # Out-of-genre failures should almost never dominate selected examples.
    return (5 if genre_match else -2) + 6*overlap + (0.5 if entry.get('scope')=='excerpt' else 0)


def pick_entries(genre: str, topic: str, limit_per_status: int = 2,
                 log: Path = LOG) -> list[dict]:
    entries = read_entries(log)
    selected = []
    for status in ('approved','partial','rejected'):
        ranked = sorted((e for e in entries if e['status']==status),
                        key=lambda e: relevance(e, genre, topic), reverse=True)
        matched = [e for e in ranked if canonical_genre(e.get('genre','')) == canonical_genre(genre)]
        # If no same-genre samples, omit (do NOT teach unrelated voices as templates).
        selected.extend(matched[:limit_per_status])
    return selected


def context_text(genre: str, topic: str, log: Path = LOG) -> str:
    entries = pick_entries(genre, topic, log=log)
    headings = {
        'approved': '사용자가 긍정적으로 승인한 표현 — 이 범위 안에서만 참고',
        'partial': '부분 승인 — 결함도 반드시 함께 볼 것',
        'rejected': '사용자가 거절한 표현 — 절대로 긍정 예시로 모방하지 말 것',
    }
    chunks = [f'# 누적 피드백 메모리\n장르: {canonical_genre(genre)} / 주제: {topic}',
              '참고 자료는 단어 암기/금지어 목록이 아니라 실제 승인 범위와 실패 원인을 구분한 사례다. 일치하는 예시가 없으면 없다고 인식하라. 새로운 글은 생성했다는 이유로 승인하지 마라.']
    for status, heading in headings.items():
        matches = [e for e in entries if e['status']==status]
        chunks.append(f'## {heading}')
        if not matches:
            chunks.append('(해당 장르의 피드백 사례 없음)')
        for e in matches:
            span = e['quote'][:1400]
            chunks.append(f"- ID {e['id']} | 범위 {e.get('scope','excerpt')} | 소재 {e.get('topic','')}\n  원문: {span!r}\n  사용자 피드백/판단: {e['reason']}")
    return '\n'.join(chunks) + '\n'


def bootstrap(root: Path = ROOT) -> int:
    log = root/'memory'/'feedback.jsonl'
    if read_entries(log):
        return 0
    n = 0
    for filename, status in [('approved.jsonl','partial'),('partial.jsonl','partial'),('rejected.jsonl','rejected')]:
        data_path = root/'examples'/filename
        if not data_path.exists():
            continue
        for line in data_path.read_text(encoding='utf-8').splitlines():
            if not line.strip():
                continue
            item = json.loads(line)
            # Original 'approved' is marked positive_partial, not full-document approval.
            quote = item.get('quote','')
            reason = item.get('reason') or item.get('feedback') or item.get('learn') or '기존 평가에 따른 자료'
            append_entry(make_entry(status, item.get('genre','일반'),
                                    item.get('genre','일반'), quote, reason,
                                    source='기존 패키지: '+filename,
                                    scope='excerpt'), log)
            n += 1
    return n


def cli() -> int:
    parser = argparse.ArgumentParser(description='Persistent human-feedback log for Korean writing')
    sub = parser.add_subparsers(dest='cmd', required=True)
    sub.add_parser('init', help='Seed prior explicitly assessed examples, once')
    rec = sub.add_parser('record', help='Persist user-confirmed feedback')
    rec.add_argument('--status', '--verdict', dest='status', choices=['approved','partial','rejected'], required=True)
    rec.add_argument('--genre', required=True)
    rec.add_argument('--topic', required=True)
    gp = rec.add_mutually_exclusive_group(required=True)
    gp.add_argument('--quote')
    gp.add_argument('--file', type=Path)
    rec.add_argument('--reason', required=True)
    rec.add_argument('--source', default='user feedback in current session')
    rec.add_argument('--scope', choices=['excerpt','whole_article'], default='excerpt')
    ctx = sub.add_parser('context', help='Select relevant feedback for next writing task')
    ctx.add_argument('--genre', required=True)
    ctx.add_argument('--topic', required=True)
    ctx.add_argument('--out', type=Path)
    sub.add_parser('status', help='Show durable log counts')
    args = parser.parse_args()
    if args.cmd == 'init':
        print(f'Initialized {bootstrap()} examples (or already initialized).')
    elif args.cmd == 'record':
        quote = args.file.read_text(encoding='utf-8') if args.file else args.quote
        entry = make_entry(args.status,args.genre,args.topic,quote,args.reason,args.source,args.scope)
        append_entry(entry)
        print(f'SAVED {entry["id"]} to {LOG}; only supplied status was stored')
    elif args.cmd == 'context':
        content = context_text(args.genre, args.topic)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(content,encoding='utf-8')
            print(f'Wrote {args.out}')
        else:
            print(content)
    elif args.cmd == 'status':
        counts = Counter(e['status'] for e in read_entries())
        print(f'Persistent path: {LOG}\nCounts: {dict(counts)}')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(cli())
    except (ValueError, OSError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(2)
