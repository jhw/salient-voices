from sv.banks import SVBank, SVBanks, SVPool
from sv.sounds import SVSample

from scipy.io import wavfile

import io
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
        bank = SVBank.load_zip("tests/mikey303.zip")
        self.assertTrue(isinstance(bank, SVBank))
        self.assertEqual(bank.name, "mikey303")
        assert_wav_files(bank)
        # save zip
        bank.dump_zip("tmp")
        self.assertTrue(os.path.exists("tmp/mikey303.zip"))
        # reload zip
        bank = SVBank.load_zip("tmp/mikey303.zip")
        self.assertTrue(isinstance(bank, SVBank))
        assert_wav_files(bank)
        
class BanksTest(unittest.TestCase):
    
    def test_load(self):        
        banks = SVBanks.load_zip("tests")        
        self.assertTrue(len(banks) == 2)

    def test_filter(self):
        bank = SVBank.load_zip("tests/mikey303.zip")
        banks = SVBanks([bank])
        pool = SVPool([SVSample.parse("mikey303/303 VCO SQR.wav")])
        filtered = banks.filter(name = "filtered",
                              pool = pool)
        wav_files = filtered.zip_file.namelist()
        self.assertEqual(len(wav_files), 1)
        self.assertTrue("303 VCO SQR.wav" in wav_files)
        
    def test_spawn_pool(self):
        bank = SVBank.load_zip("tests/mikey303.zip")
        banks = SVBanks([bank])
        tag_patterns = {"bass": "303"}
        pool, unmapped = banks.spawn_pool(tag_patterns)
        self.assertTrue(isinstance(pool, SVPool))
        self.assertEqual(len(pool), 2)
        self.assertEqual(unmapped, [])

    def test_get_wav(self):
        bank = SVBank.load_zip("tests/mikey303.zip")
        banks = SVBanks([bank])
        sample = SVSample(bank_name="mikey303", file_path="303 VCO SQR.wav", tags=["bass"])
        wav_io = banks.get_wav(sample)
        self.assertIsInstance(wav_io, io.BytesIO)
        wav_io.seek(0)
        rate, data = wavfile.read(wav_io)
        self.assertTrue(rate > 0)
        self.assertTrue(data.size > 0)
        
class PoolTest(unittest.TestCase):

    def test_match(self):
        pool = SVPool()
        pool.add(SVSample.parse("mikey303/303 VCO SQR.wav#bass#303"))
        samples = pool.match(lambda sample: "bass" in sample.tags)
        self.assertTrue(len(samples), 1)
        samples = pool.match(lambda sample: "kick" in sample.tags)
        self.assertEqual(samples, [])
        
if __name__ == "__main__":
    unittest.main()
