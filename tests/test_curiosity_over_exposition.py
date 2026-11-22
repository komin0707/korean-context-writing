import tempfile
import subprocess
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class CuriosityOverExpositionTests(unittest.TestCase):
    def test_writer_is_driven_by_sustained_curiosity(self):
        with tempfile.TemporaryDirectory() as out:
            cmd=[sys.executable,str(ROOT/'scripts/run_pipeline.py'),
                 '--task','주말 늦잠에 대한 흥미로운 커뮤니티 글',
                 '--genre','건강정보','--prepare-only','--output',out]
            run=subprocess.run(cmd,capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr)
            prompt=(Path(out)/'01_writer_prompt.md').read_text(encoding='utf-8')
            for key in ('맥락 해석','감정의 이유','독자의 자리','후킹과 전개',
                        '독자가 다음 줄을 읽는 이유','독자가 읽는 동안 계속 알고 싶어 할 의문',
                        '결정적인 근거','숫자가 맡을 일'):
                self.assertIn(key,prompt)
            for rejected in ('셈이 이상하게 꼬여요','컵으로 마시는 몫',
                             '멈칫한 건 그다음이다'):
                self.assertNotIn(rejected,prompt)

    def test_reviser_and_reviewer_track_curiosity(self):
        sys.path.insert(0,str(ROOT/'scripts'))
        from run_pipeline import assemble_reviewer,assemble_reviser
        draft='주말에 몰아서 잔 사람들 이야기.'
        reviewer=assemble_reviewer('주말 잠','근거','승인된 표현',draft)
        self.assertIn('각 문단에서 다음 문장을 읽을 이유',reviewer)
        revision=assemble_reviser('주말 잠','근거',draft,{
            'revision_priority':'궁금증이 이어지도록 전개',
            'issues':[{'repair':'독자가 답을 궁금해하는 지점에서 근거를 제시한다'}],
            'what_to_preserve':['연구의 불확실성']})
        self.assertIn('독자가 다음 줄을 읽는 이유',revision)
        self.assertIn('그래서 어떻게 됐는데?',revision)

    def test_writer_instructions_are_affirmative(self):
        for path in ['SKILL.md','knowledge/creative-practice.md','knowledge/evidence-selection.md',
                     'prompts/writer.md','prompts/reviser.md']:
            data=(ROOT/path).read_text(encoding='utf-8')
            for x in ('금지','하지 마라','하지 않는다','피하라','실패 사례','거절된 표현'):
                self.assertNotIn(x,data,path)

if __name__ == '__main__':
    unittest.main()
