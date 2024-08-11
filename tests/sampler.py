from sv.utils.banks import single_shot_bank
from sv.sampler import SVSample, SVBank, SVBanks, SVPool

import os
import unittest

class SampleTest(unittest.TestCase):

    def test_untagged(self):
        sample = SVSample("mikey303/303 VCO SQR.wav")
        self.assertEqual(sample.bank_name, "mikey303")
        self.assertEqual(sample.file_path, "303 VCO SQR.wav")
        self.assertEqual(sample.tags, [])
    
    def test_tagged(self):
        sample = SVSample("mikey303/303 VCO SQR.wav#303#bass")
        self.assertEqual(sample.bank_name, "mikey303")
        self.assertEqual(sample.file_path, "303 VCO SQR.wav")
        tags = sample.tags
        self.assertEqual(len(tags), 2)
        for tag in ["bass", "303"]:
            self.assertTrue(tag in tags)        

class BankTest(unittest.TestCase):
        
    def test_load_save_cycle(self):
        if os.path.exists("tmp/mikey303.zip"):
            os.system("rm tmp/mikey303.zip")
        bank = single_shot_bank(bank_name = "mikey303",
                                file_path = "tests/303 VCO SQR.wav")
        bank.dump_zipfile("tmp")
        self.assertTrue(os.path.exists("tmp/mikey303.zip"))
        bank = SVBank.load_zipfile("tmp/mikey303.zip")
        self.assertTrue(isinstance(bank, SVBank))
            
class BanksTest(unittest.TestCase):

    def test_spawn_pool(self):
        bank = single_shot_bank(bank_name = "mikey303",
                                file_path = "tests/303 VCO SQR.wav")
        banks = SVBanks([bank])
        tag_mapping = {"bass": "303"}
        pool, unmapped = banks.spawn_pool(tag_mapping)
        print (pool)
        self.assertTrue(isinstance(pool, SVPool))
        self.assertEqual(len(pool), 1)
        self.assertEqual(unmapped, [])

class PoolTest(unittest.TestCase):

    def test_hello(self):
        self.assertEqual(2, 2)        
        
if __name__ == "__main__":
    unittest.main()
