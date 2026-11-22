import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'experiments/voice_lock/run.py'
spec=importlib.util.spec_from_file_location('voice_lock_experiment',PATH)
voice=importlib.util.module_from_spec(spec)
spec.loader.exec_module(voice)

CARD={
  'observation':'사람이 목표를 정하는 게 아니라 목표가 사람을 움직이는 상황',
  'concrete_moment':'잘 준비하다가 걸음 수를 보고 다시 일어나는 순간',
  'speaker_stance':'건강 관리가 숙제처럼 느껴지는 것이 이상하다',
  'emotional_turn':'처음엔 웃다가 나도 그럴 수 있겠다고 느낀다',
  'fact_boundary':'만 보 아래에서도 걷기의 건강 이득은 관찰되나 개인의 결과를 확정할 수 없다',
  'why_this_is_worth_telling':'내가 비슷하게 행동하고 있기 때문이다'
}

class VoiceLockExperimentTests(unittest.TestCase):
    def test_unchanged_writer_core_after_variant_injection(self):
        task='걸음 수 집착에 관한 커뮤니티 글'
        src='관찰 연구에서는 만 보 미만에도 건강상 이득과 연관성이 있었다'
        pair=voice.pair_prompts(task,'건강정보',src,CARD)
        prefix=voice.variant_task(task,CARD)
        self.assertTrue(prefix.startswith(task))
        self.assertIn(CARD['observation'],pair['variant'])
        self.assertEqual(pair['variant'].replace(prefix,task,1),pair['baseline'])
        self.assertIn(src,pair['variant'])
        self.assertIn(src,pair['baseline'])
    def test_angle_prompt_does_not_seed_supposed_good_draft(self):
        p=voice.angle_prompt('만보 글','관찰 사실')
        self.assertIn('이 이야기를 지금 굳이 누군가에게 하고 싶은',p)
        self.assertIn('만보 글',p)
        self.assertIn('관찰 사실',p)
        self.assertNotIn('멈칫한 건 그다음',p)
    def test_validation(self):
        self.assertEqual(voice.parse_card(json.dumps(CARD,ensure_ascii=False)),CARD)
        for bad in ('[]','{}','{"observation":"a"}','not json'):
            with self.assertRaises((ValueError,TypeError,json.JSONDecodeError)):
                voice.parse_card(bad)
    def test_voice_files_are_not_experiment_files(self):
        for file in ['SKILL.md','knowledge/voice-priority.md',
                     'prompts/writer.md','profiles/author-voice.yaml',
                     'scripts/run_pipeline.py']:
            self.assertNotIn('experiments/voice_lock/run.py',(ROOT/file).read_text(encoding='utf-8'))

if __name__=='__main__':
    unittest.main()
