import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class SpokenVoiceAndPunctuationTests(unittest.TestCase):
    def test_writer_guidance_retains_core_and_allows_expression(self):
        with tempfile.TemporaryDirectory() as d:
            result = subprocess.run([sys.executable,str(ROOT/'scripts/run_pipeline.py'),
                '--task','주말 운동에 대한 사람다운 한국어 의견 글',
                '--genre','건강정보','--prepare-only','--output',d],
                capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            prompt=(Path(d)/'01_writer_prompt.md').read_text(encoding='utf-8')
            for text in ('맥락 해석','화자 구성','감정의 이유','독자의 자리',
                         '말투의 설계','후킹과 전개','말끝과 작은 표정',
                         '설명·의견·감상·여담·짧은 반응','....','~~~',':)'):
                self.assertIn(text,prompt)
            for phrase in ('셈이 이상하게 꼬여요','컵으로 마시는 몫'):
                self.assertNotIn(phrase,prompt)

    def test_reviser_gets_conversation_guidance(self):
        sys.path.insert(0,str(ROOT/'scripts'))
        from run_pipeline import assemble_reviser
        result=assemble_reviser('블로그','자료','초안', {'issues':[],
            'revision_priority':'자연스러운 문장 호흡과 말투',
            'what_to_preserve':['근거']})
        for word in ('말끝과 작은 표정','설명·의견·감상·여담·짧은 반응'):
            self.assertIn(word,result)

    def test_directives_are_affirmative(self):
        for file in ('SKILL.md','knowledge/korean-expression.md',
                     'knowledge/creative-practice.md','prompts/writer.md',
                     'prompts/reviser.md'):
            data=(ROOT/file).read_text(encoding='utf-8')
            for negative in ('하지 마라','하지 않는다','금지','피하라',
                             '거절된 표현','실패 사례'):
                self.assertNotIn(negative,data,file)

if __name__ == '__main__':
    unittest.main()
