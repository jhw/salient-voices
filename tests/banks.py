from sv.banks import SVBank, SVBanks
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

    def test_get_wav(self):
        bank = SVBank.load_zip("tests/mikey303.zip")
        sample = SVSample(bank_name="mikey303", file_path="303 VCO SQR.wav", tags=["bass"])
        wav_io = bank.get_wav(sample)
        self.assertIsInstance(wav_io, io.BytesIO)
        wav_io.seek(0)
        rate, data = wavfile.read(wav_io)
        self.assertTrue(rate > 0)
        self.assertTrue(data.size > 0)
        
class BanksTest(unittest.TestCase):
    
    def test_load(self):        
        banks = SVBanks.load_zip("tests")        
        self.assertTrue(len(banks) == 2)

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
                
if __name__ == "__main__":
    unittest.main()
