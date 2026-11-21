import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from feedback_memory import (make_entry, append_entry, read_entries,
                             context_text, pick_entries, canonical_genre)

class PersistentMemoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.log = Path(self.temp.name) / 'memory.jsonl'

    def tearDown(self):
        self.temp.cleanup()

    def test_feedback_stays_after_reopening(self):
        entry = make_entry('rejected','건강정보','물 섭취량','컵으로 마시는 몫','어휘 결합이 어색함')
        append_entry(entry, self.log)
        self.assertEqual(read_entries(self.log)[0]['reason'], '어휘 결합이 어색함')
        self.assertIn('컵으로 마시는 몫', context_text('건강정보','하루 물 2L',self.log))

    def test_no_silent_approval(self):
        with self.assertRaises(ValueError):
            make_entry('approved','정보','걷기','어떤 원고','좋음',confirmed_by='model')
        with self.assertRaises(ValueError):
            make_entry('approved','정보','걷기','어떤 원고','')

    def test_different_genre_not_as_model(self):
        append_entry(make_entry('approved','이슈논평','세무사','아니 내가 왜 안심함','관점의 전환'), self.log)
        append_entry(make_entry('rejected','건강정보','물 2L','컵으로 마시는 몫','표현이 어색함'),self.log)
        selected=pick_entries('건강정보','물 2L',log=self.log)
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]['status'], 'rejected')

    def test_scope_is_not_upgraded(self):
        item=make_entry('partial','건강정보','물 2L','한 문장','일부만 괜찮음')
        append_entry(item,self.log)
        self.assertEqual(read_entries(self.log)[0]['scope'], 'excerpt')
        self.assertEqual(read_entries(self.log)[0]['status'], 'partial')

    def test_format_is_valid_jsonl(self):
        for i in range(3):
            append_entry(make_entry('rejected','건강정보',str(i),'한 문장','거절'),self.log)
        self.assertEqual(len(self.log.read_text(encoding='utf-8').splitlines()),3)
        self.assertEqual(len(read_entries(self.log)),3)

if __name__=='__main__':
    unittest.main()
