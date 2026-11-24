#!/usr/bin/env python3
"""Manually refresh *candidate labels* from one public index.

The index assigns year labels but does not establish origin, popularity,
community-specific usage or safe contextual use. It does not overwrite
the independently reviewed lexicon.

Optional research-only deps: requests and beautifulsoup4.
"""
import argparse
import json
from pathlib import Path
from urllib.parse import urljoin

ROOT=Path(__file__).resolve().parents[1]
SOURCE='https://trendict.yigolab.com/trend/'
OUTPUT=ROOT/'research/candidates_index.jsonl'

def fetch(years: set[str]) -> list[dict]:
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError as exc:
        raise SystemExit('Research refresh requires: pip install requests beautifulsoup4') from exc
    response=requests.get(SOURCE,timeout=20,headers={
        'User-Agent':'Mozilla/5.0 (compatible; KoreanContextWritingResearch/0.1)'})
    response.raise_for_status()
    response.encoding='utf-8'
    page=BeautifulSoup(response.text,'html.parser')
    records=[]
    for a in page.select('li > a[href^="./"]'):
        year_el=a.parent.select_one('.index-year')
        year=year_el.get_text(' ',strip=True) if year_el else ''
        if year not in years:
            continue
        term=a.get_text(' ',strip=True)
        if not term:
            continue
        records.append({
            'term':term,
            'index_assigned_year':int(year),
            'source':SOURCE,
            'source_detail':urljoin(SOURCE,a.get('href','')),
            'evidence_level':'unverified_index_candidate',
            'note':'Index year is source metadata, NOT attested first use, current popularity or usage suitability.'
        })
    return records

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--years',nargs='+',default=['2024','2025','2026'])
    ap.add_argument('--out',type=Path,default=OUTPUT)
    ap.add_argument('--dry-run',action='store_true')
    args=ap.parse_args()
    result=fetch(set(args.years))
    if not result:
        raise SystemExit('No candidates returned; leaving existing file unchanged')
    if args.dry_run:
        print('DRY_RUN candidate count',len(result))
    else:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(''.join(json.dumps(e,ensure_ascii=False)+'\n' for e in result),encoding='utf-8')
        print('Wrote',len(result),'unverified candidate labels to',args.out)
        print('Manual review required before promoting to lexicon/verified.jsonl')

if __name__=='__main__':
    main()
