import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class PragmaticsAndEmpathyTests(unittest.TestCase):
    def test_full_writer_prompt_preserves_v12_core_and_added_depth(self):
        with tempfile.TemporaryDirectory() as d:
            r = subprocess.run([sys.executable,str(ROOT/'scripts'/'run_pipeline.py'),
                '--task','주말 운동에 대한 자연스러운 한국어 건강정보 글','--genre','건강정보',
                '--prepare-only','--output',d], capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
            content=(Path(d)/'01_writer_prompt.md').read_text(encoding='utf-8')
            for word in ('맥락 해석','화자 구성','감정의 이유','독자의 자리','말투의 설계','후킹과 전개',
                         '상황에 맞는 단어','감정의 원인과 강도','독자가 느낄 만한 이유','조사와 말끝의 맥락'):
                self.assertIn(word,content)
            self.assertNotIn('셈이 이상하게 꼬여요',content)
            self.assertNotIn('컵으로 마시는 몫',content)
            reviewer=(Path(d)/'00_reviewer_memory.md').read_text(encoding='utf-8')
            self.assertNotIn('셈이 이상하게 꼬여요',reviewer)

    def test_reviser_receives_same_positive_guidance(self):
        sys.path.insert(0,str(ROOT/'scripts'))
        from run_pipeline import assemble_reviser
        prompt=assemble_reviser('건강정보 글','주어진 근거','초안', {
            'issues':[{'repair':'실제 이해관계와 행동을 보여 준다'}],
            'revision_priority':'화자의 평가를 표현에 연결한다',
            'what_to_preserve':['확인된 연구 결과']})
        for word in ('상황에 맞는 단어','감정의 원인과 강도','독자가 느낄 만한 이유'):
            self.assertIn(word,prompt)

    def test_authoring_guidance_is_affirmative(self):
        files=['SKILL.md','knowledge/korean-expression.md','knowledge/emotion-and-reader.md',
               'knowledge/creative-practice.md','prompts/writer.md','prompts/reviser.md']
        for name in files:
            text=(ROOT/name).read_text(encoding='utf-8')
            for word in ('하지 마라','금지','피하라','모방하지','거절된 표현','실패 사례'):
                self.assertNotIn(word,text,name)

if __name__=='__main__':
    unittest.main()
