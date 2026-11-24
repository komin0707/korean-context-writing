import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from dc_usage_context import read_cases, for_terms, render
from analyze_authorized_dc_export import compute

class DCUsageEvidenceTests(unittest.TestCase):
    def test_case_ledger_coverage(self):
        cases=read_cases()
        self.assertGreaterEqual(len(cases),40)
        self.assertGreaterEqual(len({c['gallery'] for c in cases}),30)
        self.assertGreaterEqual(len({c['term'] for c in cases}),20)
        self.assertGreaterEqual(sum(c['date'].startswith('2024') for c in cases),2)
        self.assertGreaterEqual(sum(c['date'].startswith('2025') for c in cases),8)
        self.assertGreaterEqual(sum(c['date'].startswith('2026') for c in cases),25)
    def test_case_ledger_provenance_and_privacy(self):
        cases=read_cases()
        self.assertEqual(len(cases),len({(c['url'],c['term'],c['observed_unit']) for c in cases}))
        for c in cases:
            self.assertTrue(c['url'].startswith('https://gall.dcinside.com/'))
            self.assertIn(c['evidence'],{'read_post','indexed_excerpt'})
            self.assertTrue('2024-11-24'<=c['date']<='2026-11-24')
            self.assertTrue(c['context_summary'])
            self.assertTrue(c['usable_when'])
            self.assertTrue(c['caution'])
            self.assertFalse(c['full_comment_tree_seen'])
            self.assertFalse(c['quote_copied'])
            self.assertFalse(c['usernames_or_ips_saved'])
    def test_positive_vs_ironic_semantics_stay_separate(self):
        rows=for_terms(['느좋'],asof='2026-11',max_cases=15)
        tones={c['tone'] for c in rows}
        self.assertIn('positive',tones)
        self.assertIn('ironic_negative',tones)
        self.assertIn('힙합',{c['gallery'] for c in rows})
    def test_prefer_full_post_sources_and_enforce_cutoff(self):
        cases=for_terms(['밤티'],asof='2026-11',max_cases=3)
        self.assertTrue(cases)
        self.assertEqual(cases[0]['evidence'],'read_post')
        self.assertEqual(for_terms(['밤티'],asof='2025-11'),[])
        self.assertIn('맥락',render(cases))
    def test_metadata_not_full_post_text_is_rendered(self):
        rendered=render(for_terms(['그뭔씹'],max_cases=2))
        self.assertIn('자기',rendered)
        self.assertIn('https://gall.dcinside.com',rendered)
        self.assertIn('검색',rendered)
    def test_optin_only_applies_context(self):
        runner=ROOT/'scripts/run_pipeline.py'
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for flag,name in [(False,'plain'),(True,'opt')]:
                dest=root/name
                args=[sys.executable,str(runner),'--task','패션 브랜드 로고 디자인',
                      '--genre','community','--prepare-only','--output',str(dest)]
                if flag: args+=['--slang-context']
                result=subprocess.run(args,capture_output=True,text=True)
                self.assertEqual(result.returncode,0,result.stderr)
                p=(dest/'01_writer_prompt.md').read_text(encoding='utf8')
                if flag:
                    self.assertIn('# DC 게시글 사용 맥락',p)
                    self.assertTrue((dest/'00_dc_usage_examples.json').exists())
                else:
                    self.assertNotIn('# DC 게시글 사용 맥락',p)
                    self.assertFalse((dest/'00_dc_usage_examples.json').exists())
    def test_authorized_aggregate_no_copied_text(self):
        data=[
          {'date':'2026-11-01','gallery':'AAA','role':'post_title','text':'느좋 감다살'},
          {'date':'2026-11-02','gallery':'BBB','role':'comment','text':'느좋인척'},
          {'date':'2025-07-01','gallery':'AAA','role':'post_body','text':'감다뒤'},
        ]
        result=compute(data)
        self.assertEqual(result['records'],3)
        self.assertEqual(result['term_post_or_comment_presence']['느좋'],2)
        self.assertEqual(result['term_post_or_comment_presence']['감다뒤'],1)
        self.assertNotIn('느좋인척',json.dumps(result,ensure_ascii=False))
        self.assertIn('ambiguous_terms_requiring_contextual_annotation',result)
    def test_rights_basis_required_by_cli(self):
        analyzer=ROOT/'scripts/analyze_authorized_dc_export.py'
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)
            inp=folder/'input.jsonl';inp.write_text('{"date":"2026-10-01","gallery":"X","role":"comment","text":"느좋"}\n',encoding='utf8')
            provenance=folder/'provenance.json'
            output=folder/'out.json'
            provenance.write_text('{"authorized":false}',encoding='utf8')
            x=subprocess.run([sys.executable,str(analyzer),'--input',str(inp),'--provenance',str(provenance),
                '--out',str(output)],capture_output=True,text=True)
            self.assertNotEqual(x.returncode,0)
            self.assertFalse(output.exists())
            provenance.write_text('{"authorized":true,"basis":"Test-only synthetic data"}',encoding='utf8')
            y=subprocess.run([sys.executable,str(analyzer),'--input',str(inp),'--provenance',str(provenance),
                '--out',str(output)],capture_output=True,text=True)
            self.assertEqual(y.returncode,0,y.stderr)
            self.assertEqual(json.loads(output.read_text())['records'],1)

if __name__=='__main__':
    unittest.main()
