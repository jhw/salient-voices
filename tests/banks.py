from sv.banks import SVBank, SVBanks, SVPool

import os
import unittest

class BankTest(unittest.TestCase):
        
    def test_serialisation(self):
        def assert_wav_files(bank):
            wav_files = bank.zip_file.namelist()
            self.assertEqual(len(wav_files), 2)
            for wav_file in ["303 VCO SQR.wav",
                             "303 VCO SAW.wav"]:                          
                self.assertTrue(wav_file in wav_files)
        # load files
        bank = SVBank.load_wav_files(bank_name = "mikey303",
                                     dir_path = "tests")
        self.assertTrue(isinstance(bank, SVBank))
        self.assertEqual(bank.name, "mikey303")
        assert_wav_files(bank)
        # save zip
        bank.dump_zip_file("tmp")
        self.assertTrue(os.path.exists("tmp/mikey303.zip"))
        # reload zip
        bank = SVBank.load_zip_file("tmp/mikey303.zip")
        self.assertTrue(isinstance(bank, SVBank))
        assert_wav_files(bank)

    def test_join(self):
        def assert_wav_files(bank, wav_files):
            bank_wav_files = bank.zip_file.namelist()
            self.assertEqual(len(wav_files), len(bank_wav_files))
            for wav_file in wav_files:
                self.assertTrue(wav_file in bank_wav_files)
        bank1 = SVBank.load_wav_files(bank_name = "mikey303a",
                                      dir_path = "tests",
                                      filter_fn = lambda x: x.endswith(".wav") and "SQR" in x)
        assert_wav_files(bank1, ["303 VCO SQR.wav"])
        bank2 = SVBank.load_wav_files(bank_name = "mikey303b",
                                      dir_path = "tests",
                                      filter_fn = lambda x: x.endswith(".wav") and "SAW" in x)
        assert_wav_files(bank2, ["303 VCO SAW.wav"])
        joined_bank = bank1.join(bank2)
        self.assertEqual(joined_bank.name, "mikey303a")
        wav_files = joined_bank.zip_file.namelist()
        self.assertEqual(len(wav_files), 2)
        for wav_file in ["303 VCO SQR.wav",
                         "303 VCO SAW.wav"]:
            self.assertTrue(wav_file in wav_files)
        
class BanksTest(unittest.TestCase):

    def test_spawn_pool(self):
        bank = SVBank.load_wav_files(bank_name = "mikey303",
                                     dir_path = "tests")
        banks = SVBanks([bank])
        tag_mapping = {"bass": "303"}
        pool, unmapped = banks.spawn_pool(tag_mapping)
        self.assertTrue(isinstance(pool, SVPool))
        self.assertEqual(len(pool), 2)
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
