import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class ReaderImaginationTests(unittest.TestCase):
    def test_writer_receives_imaginable_scene_guidance(self):
        with tempfile.TemporaryDirectory() as d:
            cmd=[sys.executable,str(ROOT/'scripts/run_pipeline.py'),
                 '--task','운동할 시간이 부족한 사람을 위한 생활정보 글',
                 '--genre','건강정보','--prepare-only','--output',d]
            run=subprocess.run(cmd,capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr)
            prompt=(Path(d)/'01_writer_prompt.md').read_text(encoding='utf-8')
            for term in ('맥락 해석','화자 구성','감정의 이유','독자의 자리',
                         '말투의 설계','후킹과 전개','독자가 머릿속으로 장면을 그리는 글',
                         '독자가 스스로 채울 여백','정보 글에서의 생생함'):
                self.assertIn(term,prompt)
            for rejected in ('셈이 이상하게 꼬여요','컵으로 마시는 몫'):
                self.assertNotIn(rejected,prompt)

    def test_reviser_and_reviewer_consider_reader_imagination(self):
        sys.path.insert(0,str(ROOT/'scripts'))
        from run_pipeline import assemble_reviser,assemble_reviewer
        rev=assemble_reviser('정보 글','근거','원고',{'issues':[],
                            'revision_priority':'독자의 머릿속에 장면이 떠오르도록',
                            'what_to_preserve':['사실']})
        self.assertIn('독자가 머릿속으로 장면을 그리는 글',rev)
        review=assemble_reviewer('정보 글','근거','승인된 문체','원고')
        self.assertIn('머릿속에 그릴 수 있고',review)

    def test_positive_guidance_in_core(self):
        for path in ('SKILL.md','knowledge/reader-imagination.md','prompts/writer.md','prompts/reviser.md'):
            content=(ROOT/path).read_text(encoding='utf-8')
            for term in ('하지 마라','하지 않는다','금지','피하라','실패 사례','거절된 표현'):
                self.assertNotIn(term,content,path)

if __name__=='__main__':
    unittest.main()
