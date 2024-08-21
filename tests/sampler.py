from sv.sampler import SVSample, SVBank, SVBanks, SVPool, SVSlotSampler, SVChromaticSampler, MaxSlots

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

class SamplerTest(unittest.TestCase):

    def setUp(self):
        bank = SVBank.load_wav_files(bank_name = "mikey303",
                                     dir_path = "tests")
        self.banks = SVBanks([bank])
        tag_mapping = {"bass": "303"}
        self.pool, _ = self.banks.spawn_pool(tag_mapping)
            
    def test_slot_sampler(self):
        sampler = SVSlotSampler(banks = self.banks,
                                pool = self.pool)
        root_notes = sampler.root_notes
        for i, sample in enumerate(self.pool):
            self.assertEqual(root_notes[sample], i)

    def test_chromatic_sampler(self, max_slots = MaxSlots):
        sampler = SVChromaticSampler(banks = self.banks,
                                     pool = self.pool)
        block_size = int(max_slots / len(self.pool))
        root_notes = sampler.root_notes                
        for i, sample in enumerate(self.pool):
            root_note = int((i + 0.5) * block_size)
            self.assertEqual(root_notes[sample], root_note)
        
if __name__ == "__main__":
    unittest.main()
