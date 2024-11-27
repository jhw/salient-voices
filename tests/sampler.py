from sv.banks import SVBank, SVBanks
from sv.sampler import SVSlotSampler

import rv
import rv.note
import unittest
         
class SamplerTest(unittest.TestCase):

    def setUp(self):
        bank = SVBank.load_zip("tests/mikey303.zip")
        self.banks = SVBanks([bank])
        
    def test_slot_sampler(self):
        tag_mapping = {"bass": "303"}
        pool, _ = self.banks.spawn_pool(tag_mapping)
        sampler = SVSlotSampler(banks = self.banks,
                                pool = pool,
                                root = rv.note.NOTE.C5,
                                cutoff = 0.5,
                                bpm = 120)
        samples = [sample for sample in sampler.samples
                   if sample]
        self.assertEqual(len(samples), 2)
        
if __name__ == "__main__":
    unittest.main()
