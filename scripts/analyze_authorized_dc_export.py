#!/usr/bin/env python3
"""Aggregate usage in an already-authorized offline corpus. No site scraping.

Input JSONL records require date, gallery, text, and role. Output retains
only aggregate counts and never copies post text, author handles, or IPs.

Permission/provenance document must attest rights to analyse this data.
This does not procure permission; check the supplied basis yourself.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import date
import json
from pathlib import Path
import re

TERMS={
  "개추": re.compile(r"개추"),
  "억까": re.compile(r"억까"),
  "억빠": re.compile(r"억빠"),
  "느좋": re.compile(r"느좋"),
  "밤티": re.compile(r"밤티"),
  "감다살": re.compile(r"감다살"),
  "감다뒤": re.compile(r"감다뒤"),
  "비틱": re.compile(r"비틱"),
  "딸깍": re.compile(r"딸깍"),
  "그뭔씹": re.compile(r"그뭔씹"),
  "긁혔": re.compile(r"긁혔"),
  "주딱": re.compile(r"주딱"),
  "파딱": re.compile(r"파딱"),
  "스압": re.compile(r"스압"),
  "알빠노": re.compile(r"알빠노"),
  "누칼협": re.compile(r"누칼협"),
  "뇌절": re.compile(r"뇌절"),
  "테토": re.compile(r"테토"),
  "에겐": re.compile(r"에겐"),
  "럭키비키": re.compile(r"럭키비키"),
  "이븐하게": re.compile(r"이븐하게"),
  "ㄹㅇ": re.compile(r"(?<![ㄱ-ㅎ])ㄹㅇ(?![ㄱ-ㅎ])"),
}
AMBIGUOUS={'긁혔':'물리적으로 긁혔을 수도 있음',
           '밤티':'고유명사/아이디일 수도 있음',
           '느좋':'닉네임일 수도 있음',
           '딸깍':'실제 마우스 조작인지 저품질 자동생성 비유인지 구별 필요',
           '테토':'호르몬 과학적 개념과 밈을 구분해야 함',
           '에겐':'호르몬 과학적 개념과 밈을 구분해야 함'}
ROLES={'post_title','post_body','comment'}

def compute(records):
    totals=Counter()
    usage=Counter()
    by_quarter=Counter()
    by_gallery=Counter()
    by_role=Counter()
    per_period=Counter()
    for n,item in enumerate(records,1):
        if not all(k in item for k in ('date','gallery','text','role')):
            raise ValueError(f'Record {n}: required date/gallery/text/role')
        if item['role'] not in ROLES:
            raise ValueError(f'Record {n}: unknown role')
        try:
            when=date.fromisoformat(item['date'])
        except (ValueError,TypeError) as exc:
            raise ValueError(f'Record {n}: invalid date') from exc
        if not isinstance(item['text'],str) or not isinstance(item['gallery'],str):
            raise ValueError(f'Record {n}: text and gallery must be strings')
        q=f'{when.year}Q{(when.month-1)//3+1}'
        totals['records']+=1
        per_period[q]+=1
        for term,regex in TERMS.items():
            if regex.search(item['text']):
                usage[term]+=1
                by_quarter[(q,term)]+=1
                by_gallery[(item['gallery'],term)]+=1
                by_role[(item['role'],term)]+=1
    return {
      'records':totals['records'],
      'records_by_quarter':dict(sorted(per_period.items())),
      'term_post_or_comment_presence':dict(usage.most_common()),
      'term_by_quarter':[
          dict(quarter=q,term=t,record_count=v)
          for (q,t),v in sorted(by_quarter.items())],
      'term_by_gallery':[
          dict(gallery=g,term=t,record_count=v)
          for (g,t),v in sorted(by_gallery.items())],
      'term_by_role':[
          dict(role=g,term=t,record_count=v)
          for (g,t),v in sorted(by_role.items())],
      'ambiguous_terms_requiring_contextual_annotation':AMBIGUOUS,
      'interpretation_limits':[
          'Counts are record-level presence, not number of occurrences or unique speakers.',
          'These counts only describe the provided authorized corpus; not all DC.',
          'No semantic function inferred automatically from term counts.',
          'Term homonyms and ironic usages require independent human annotation.',
          'The script has no network access and never collects websites.',
          'No post text, nicknames, IPs or personal identifiers are written to output.'
      ],
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',type=Path,required=True)
    ap.add_argument('--provenance',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    provenance=json.loads(args.provenance.read_text(encoding='utf-8'))
    if provenance.get('authorized') is not True or not provenance.get('basis'):
        raise SystemExit('Permission evidence required: authorized=true and a documented rights basis')
    if args.input.resolve()==args.out.resolve():
        raise SystemExit('Output path must differ from input')
    def lines():
        with args.input.open(encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)
    result=compute(lines())
    result['provenance_basis_recorded']=str(provenance['basis'])[:150]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Computed privacy-minimized aggregate report from authorized offline records:',result['records'])

if __name__=='__main__':
    main()
