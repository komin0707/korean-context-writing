import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class EvidenceAndNaturalReactionTests(unittest.TestCase):
    def test_writer_has_v12_core_and_evidence_selection(self):
        with tempfile.TemporaryDirectory() as d:
            run=subprocess.run([sys.executable,str(ROOT/'scripts/run_pipeline.py'),
                '--task','근력운동과 건강에 관한 친근한 한국어 글',
                '--genre','건강정보','--prepare-only','--output',d],
                capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr)
            prompt=(Path(d)/'01_writer_prompt.md').read_text(encoding='utf-8')
            for phrase in ('맥락 해석','화자 구성','감정의 이유','독자의 자리',
                '말투의 설계','후킹과 전개','독자가 읽고 남길 한 가지',
                '숫자가 맡을 일','연구가 말한 범위','반응이 말에 실리는 순간'):
                self.assertIn(phrase,prompt)
            for rejected in ('멈칫한 건 그다음이다', '눈에 걸린다', '셈이 이상하게 꼬여요'):
                self.assertNotIn(rejected,prompt)

    def test_reviser_has_same_evidence_guidance(self):
        sys.path.insert(0,str(ROOT/'scripts'))
        from run_pipeline import assemble_reviser
        prompt=assemble_reviser('글','근거','원고',{
            'revision_priority':'독자의 판단을 중심으로',
            'issues':[{'repair':'인물의 선택과 실제 의미를 연결한다'}],
            'what_to_preserve':['핵심 사실']})
        self.assertIn('숫자가 맡을 일',prompt)
        self.assertIn('연구가 말한 범위',prompt)

    def test_positive_guidance(self):
        for name in ['SKILL.md','prompts/writer.md','knowledge/evidence-selection.md',
                     'knowledge/korean-expression.md','prompts/reviser.md']:
            text=(ROOT/name).read_text(encoding='utf-8')
            for term in ('금지','하지 마라','하지 않는다','피하라','거절된 표현','실패 사례'):
                self.assertNotIn(term,text,name)

if __name__ == '__main__':
    unittest.main()
