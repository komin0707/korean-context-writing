#!/usr/bin/env python3
"""Select *optional* usage-aware Korean internet expressions, not forced slang.

Built-in stdlib only; curated lexicon has explicit sources and caution flags.
A date refers to last evidence reviewed, never a live frequency measurement.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LEXICON=ROOT/'lexicon/verified.jsonl'
MEDIA_KINDS={'media_meme','image_meme','character_meme','video_format','sound_meme'}
NICHE_AUDIENCES={'fandom_specific','niche_online'}
DATE_FORMAT=re.compile(r'^\d{4}-\d{2}$')

def parse_month(month: str) -> dt.date:
    if not DATE_FORMAT.fullmatch(month):
        raise ValueError('Month must be YYYY-MM')
    year,mon=map(int,month.split('-'))
    return dt.date(year,mon,1)

def read_entries(path: Path = LEXICON) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]

def months_between(a: dt.date,b: dt.date) -> int:
    return (b.year-a.year)*12+(b.month-a.month)

def choose(topic: str, genre: str, asof: str='2026-11', limit: int=3,
           max_age_months: int=12, include_historical: bool=False,
           include_risky: bool=False, entries: list[dict] | None = None) -> list[dict]:
    if limit<1: return []
    now=parse_month(asof)
    topic=topic.strip()
    genre=genre.lower()
    if genre in {'medical','clinical','science','legal','의학','의료','임상','법률','건강정보','의학정보'}:
        return []
    allow_media=genre in {'shortform','fandom','video','릴스','틱톡','숏폼','팬덤'}
    result=[]
    for item in entries if entries is not None else read_entries():
        last=parse_month(item['latest_attestation'])
        first=parse_month(item['attested'])
        if first>now or last>now:
            continue
        age=months_between(last,now)
        mentioned=(item['term'] in topic or any(v in topic for v in item.get('variants',[]) if len(v)>=2))
        matched=[k for k in item['topic_triggers'] if len(k)>1 and k in topic]
        if not (mentioned or matched):
            continue
        if item['evidence_level']=='dictionary_only' and not mentioned:
            continue
        if item['risk']=='high' and not (mentioned and include_risky):
            continue
        if item['risk']=='medium' and not (mentioned or include_risky or
            (len(matched)>=2 and item['evidence_level'] in {'primary_community_attestation','news_and_primary_community'})):
            continue
        if item['kind'] in MEDIA_KINDS and not (allow_media or mentioned):
            continue
        if item['channel_evidence'] in NICHE_AUDIENCES and not (allow_media or mentioned):
            continue
        if age>max_age_months and not (include_historical or mentioned):
            continue
        score=(20 if mentioned else 0)+len(matched)*3+max(0,12-age)
        if item['evidence_level'].startswith('primary_') or item['evidence_level']=='news_and_primary_community':
            score+=2
        result.append((score,item))
    result.sort(key=lambda pair:(-pair[0],pair[1]['term']))
    return [dict(item, relevance_score=score,
                 age_since_last_documented_months=months_between(parse_month(item['latest_attestation']),now))
            for score,item in result[:limit]]

def usage_note(items: list[dict]) -> str:
    if not items:
        return '이번 소재에 잘 맞는 검증된 최근 유행어를 찾지 못했다. 유행어를 억지로 넣지 말고 자연스러운 DC 문장으로 작성한다.'
    lines=['# 최근 한국 인터넷 표현: 선택 참고용', '최대 한 표현만 자연스럽게 맞으면 사용한다. 불필요하면 아무것도 사용하지 않는다.',
           '아래 시점은 출처에서 확인한 시기이지 실시간 유행 순위나 실제 사용 빈도가 아니다.']
    for x in items:
        lines.extend([
            '- '+x['term']+' ('+x['latest_attestation']+' 확인, '+x['kind']+', 위험='+x['risk']+')',
            '  뜻: '+x['meaning'],
            '  어울리는 상황: '+x['use_when'],
            '  어색하거나 부적절한 상황: '+x['avoid_when'],
            '  작성한 예시: '+x['example_original'],
            '  출처 ID: '+', '.join(x['source_ids'])])
    return '\n'.join(lines)

def main() -> None:
    ap=argparse.ArgumentParser(description='Select optional recent slang with context and age checks')
    ap.add_argument('--topic',required=True)
    ap.add_argument('--genre',default='community')
    ap.add_argument('--asof',default='2026-11')
    ap.add_argument('--limit',type=int,default=3)
    ap.add_argument('--max-age-months',type=int,default=12)
    ap.add_argument('--include-historical',action='store_true')
    ap.add_argument('--include-risky',action='store_true')
    ap.add_argument('--format',choices=('note','json'),default='note')
    args=ap.parse_args()
    selected=choose(args.topic,args.genre,args.asof,args.limit,args.max_age_months,
                    args.include_historical,args.include_risky)
    if args.format=='json':
        print(json.dumps(selected,ensure_ascii=False,indent=2))
    else:
        print(usage_note(selected))

if __name__=='__main__':
    main()
