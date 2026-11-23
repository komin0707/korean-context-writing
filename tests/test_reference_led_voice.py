import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from run_pipeline import assemble_writer, assemble_reviser, approved_writer_context, load_examples

class ReferenceLedVoiceTests(unittest.TestCase):
    def test_user_endorsed_example_is_now_retrievable(self):
        approved=load_examples()
        self.assertIn('근데 시발 내가 왜 안심함?',approved)
        self.assertIn('커닝은 수석이 했는데',approved)
        self.assertIn('본인이 입 안 열어도 잡을 수 있냐',approved)

    def test_community_prompt_receives_actual_approved_excerpt(self):
        topic='스트레칭 연구를 재료로 커뮤니티 글 작성'
        refs=approved_writer_context('건강정보',topic)
        prompt=assemble_writer(topic,'정적 스트레칭이 수행에 미치는 영향은 조건에 따라 달라짐',refs)
        self.assertIn('근데 시발 내가 왜 안심함?',prompt)
        self.assertIn('커닝은 수석이 했는데',prompt)
        self.assertIn('화자의 생각',prompt)
        self.assertIn('장 구성의 복제 대신',prompt)
        self.assertLess(len(prompt),6500)

    def test_noncommunity_health_prompt_gets_mechanism_not_issue_quotes(self):
        topic='물 섭취량 블로그 글'
        refs=approved_writer_context('건강정보',topic)
        prompt=assemble_writer(topic,'수분에 대한 근거',refs)
        self.assertNotIn('근데 시발 내가 왜 안심함?',prompt)
        self.assertIn('자연스럽게 말로 튀어나오는 생기',prompt)
        self.assertLess(len(prompt),6500)

    def test_direct_skill_entrypoints_open_reference(self):
        for entry in ('SKILL.md', 'CLAUDE_PROJECT_INSTRUCTIONS.md',
                      'prompts/QUICK_START.md', 'prompts/WORK_START.md'):
            self.assertIn('knowledge/story-motion.md',
                          (ROOT/entry).read_text(encoding='utf-8'))

    def test_research_notes_do_not_dominate_community_voice(self):
        refs=approved_writer_context('건강정보','운동 후 단백질 쉐이크 커뮤니티 글')
        p=assemble_writer('운동 후 단백질 쉐이크 커뮤니티 글',
                          '메타분석 연구 수 23건, 525명. 섭취 타이밍보다 총량이 중요할 수 있음.',refs)
        self.assertIn('논문을 소개하는 사람이 아니라',p)
        self.assertIn('논문의 이름·연도·표본·통계',p)
        self.assertIn('실제 경험이 주어지지 않았다면',p)
        self.assertIn('메타분석 연구 수 23건',p)
        self.assertIn('근데 시발 내가 왜 안심함?',p)

    def test_reviser_uses_same_reasoning_not_a_four_step_card(self):
        prompt=assemble_reviser('이슈 논평','근거','초안',{
             'issues':[{'repair':'글의 웃긴 장면을 더 선명하게'}],
             'what_to_preserve':['자연스러운 말끝'],
             'revision_priority':'관점을 살리기'})
        self.assertIn('자연스럽게 말로 튀어나오는 생기',prompt)
        self.assertIn('자연스러운 말끝',prompt)
        self.assertNotIn('concrete_moment',prompt)
        self.assertLess(len(prompt),6500)

if __name__=='__main__':
    unittest.main()
