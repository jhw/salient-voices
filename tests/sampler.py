from sv.banks import SVBank, SVBanks
from sv.sampler import SVSampleRef as SVSample
from sv.sampler import SVSlotSampler, MaxSlots

import os
import rv
import rv.api
import unittest

class SampleTest(unittest.TestCase):

    def test_untagged(self):
        sample = SVSample.parse("mikey303/303 VCO SQR.wav")
        self.assertEqual(sample.bank_name, "mikey303")
        self.assertEqual(sample.file_path, "303 VCO SQR.wav")
        self.assertEqual(sample.tags, [])
    
    def test_tagged(self):
        sample = SVSample.parse("mikey303/303 VCO SQR.wav#303#bass")
        self.assertEqual(sample.bank_name, "mikey303")
        self.assertEqual(sample.file_path, "303 VCO SQR.wav")
        tags = sample.tags
        self.assertEqual(len(tags), 2)
        for tag in ["bass", "303"]:
            self.assertTrue(tag in tags)        

class SamplerTest(unittest.TestCase):

    def setUp(self):
        bank = SVBank.load_zip("tests/mikey303.zip")
        self.banks = SVBanks([bank])
        
    def test_slot_sampler(self):
        tag_mapping = {"bass": "303"}
        pool, _ = self.banks.spawn_pool(tag_mapping)
        sampler = SVSlotSampler(banks = self.banks,
                                pool = pool,
                                root_note = rv.note.NOTE.C5)
        root_notes = sampler.root_notes
        for i, sample in enumerate(pool):
            self.assertEqual(root_notes[sample], i)
        
if __name__ == "__main__":
    unittest.main()
