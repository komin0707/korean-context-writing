import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from select_slang import choose, read_entries, usage_note, parse_month

class SlangAtlasTests(unittest.TestCase):
    def test_candidate_index_is_unverified_not_writer_context(self):
        candidates=[json.loads(line) for line in (ROOT/'research/candidates_index.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
        self.assertEqual(len(candidates),159)
        self.assertEqual({c['index_assigned_year'] for c in candidates},{2024,2025,2026})
        self.assertTrue(all(c['evidence_level']=='unverified_index_candidate' for c in candidates))
    def test_editorial_schema_and_sources(self):
        entries=read_entries()
        sources=json.loads((ROOT/'research/sources.json').read_text(encoding='utf-8'))
        ids={s['id'] for s in sources}
        self.assertGreaterEqual(len(entries),35)
        self.assertEqual(len(entries),len({e['term'] for e in entries}))
        for e in entries:
            self.assertTrue(e['term'])
            self.assertTrue(e['meaning'])
            self.assertTrue(e['use_when'])
            self.assertTrue(e['avoid_when'])
            self.assertTrue(e['example_original'])
            self.assertTrue(e['source_ids'])
            self.assertLessEqual(parse_month(e['attested']),parse_month(e['latest_attestation']))
            self.assertTrue(set(e['source_ids']).issubset(ids))
            self.assertFalse(e['usage_frequency_measured'])
    def test_context_relevance_and_risk_controls(self):
        matches=choose('패션 브랜드 로고 디자인','community')
        terms={e['term'] for e in matches}
        self.assertIn('느좋',terms)
        self.assertNotIn('밤티',terms)
        self.assertLessEqual(len(matches),3)
    def test_primary_dc_context_can_be_suggested(self):
        terms={e['term'] for e in choose('게임 업데이트 운영','community')}
        self.assertIn('감다뒤',terms)
    def test_generic_topic_recommends_none(self):
        self.assertEqual(choose('내일 회의 일정','community'),[])
        self.assertIn('억지',usage_note([]))
    def test_medical_genre_has_no_slang(self):
        self.assertEqual(choose('중환자 병원 안내','의학'),[])
        self.assertEqual(choose('패션 트렌드','건강정보'),[])
    def test_old_recap_is_not_fresh_slang(self):
        self.assertNotIn('럭키비키',{e['term'] for e in choose('행운 긍정 이야기','community')})
        self.assertIn('럭키비키',{e['term'] for e in choose('럭키비키의 역사','community',include_historical=True)})
    def test_no_future_leak_when_backtesting(self):
        result=choose('패션 브랜드 로고 디자인','community',asof='2025-06')
        self.assertNotIn('느좋',{e['term'] for e in result})
        self.assertNotIn('영크크',{e['term'] for e in result})
    def test_opt_in_pipeline_only(self):
        cli=ROOT/'scripts/run_pipeline.py'
        args=[sys.executable,str(cli),'--task','패션 브랜드 로고 디자인 글','--genre','community','--prepare-only']
        with tempfile.TemporaryDirectory() as td:
            plain=Path(td)/'plain';opt=Path(td)/'opt'
            a=subprocess.run(args+['--output',str(plain)],text=True,capture_output=True)
            b=subprocess.run(args+['--slang-context','--asof-month','2026-11','--output',str(opt)],text=True,capture_output=True)
            self.assertEqual(a.returncode,0,a.stderr)
            self.assertEqual(b.returncode,0,b.stderr)
            x=(plain/'01_writer_prompt.md').read_text(encoding='utf-8')
            y=(opt/'01_writer_prompt.md').read_text(encoding='utf-8')
            self.assertFalse((plain/'00_slang_candidates.json').exists())
            self.assertTrue((opt/'00_slang_candidates.json').is_file())
            self.assertNotIn('# 최근 한국 인터넷 표현: 선택 참고용',x)
            self.assertIn('# 최근 한국 인터넷 표현: 선택 참고용',y)
            self.assertIn('느좋',y)
            self.assertNotIn('밤티 (',y)

if __name__=='__main__':
    unittest.main()
