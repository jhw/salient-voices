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
        
    def test_load_save_zip(self):
        if os.path.exists("tmp/mikey303.zip"):
            os.system("rm tmp/mikey303.zip")
        bank = single_shot_bank(bank_name = "mikey303",
                                file_path = "tests/303 VCO SQR.wav")
        bank.dump_zip_file("tmp")
        self.assertTrue(os.path.exists("tmp/mikey303.zip"))
        bank = SVBank.load_zip_file("tmp/mikey303.zip")
        self.assertTrue(isinstance(bank, SVBank))

    def test_load_files(self):
        if not os.path.exists("tmp"):
            os.mkdir("tmp")
        os.system("rm tmp/*.wav")
        os.system("cp \"tests/303 VCO SQR.wav\" tmp/")
        bank = SVBank.load_files(bank_name = "mikey303",
                                 dir_path = "tmp")
        self.assertTrue(isinstance(bank, SVBank))
        self.assertEqual(bank.name, "mikey303")
        wav_files = bank.zip_file.namelist()
        self.assertEqual(len(wav_files), 1)
        self.assertTrue("303 VCO SQR.wav" in wav_files)
        os.system("rm tmp/*.wav")
        
class BanksTest(unittest.TestCase):

    def test_spawn_pool(self):
        bank = single_shot_bank(bank_name = "mikey303",
                                file_path = "tests/303 VCO SQR.wav")
        banks = SVBanks([bank])
        tag_mapping = {"bass": "303"}
        pool, unmapped = banks.spawn_pool(tag_mapping)
        self.assertTrue(isinstance(pool, SVPool))
        self.assertEqual(len(pool), 1)
        self.assertEqual(unmapped, [])

class PoolTest(unittest.TestCase):

    def test_tags(self):
        pool = SVPool()
        pool.add("mikey303/303 VCO SQR.wav#bass#303")
        tags = pool.tags
        self.assertEqual(len(tags), 2)
        for tag in ["bass", "303"]:
            self.assertTrue(tag in tags)
            self.assertEqual(tags[tag], 1)

    def test_filter_by_tag(self):
        pool = SVPool()
        pool.add("mikey303/303 VCO SQR.wav#bass#303")
        samples = pool.filter_by_tag("bass")
        self.assertTrue(len(samples), 1)
        samples = pool.filter_by_tag("kick")
        self.assertEqual(samples, [])
        
if __name__ == "__main__":
    unittest.main()
