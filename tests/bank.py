from sv.bank import SVBank

from scipy.io import wavfile

import io
import os
import unittest

class BankTest(unittest.TestCase):

    def test_get_wav(self):
        bank = SVBank.load_zip("tests/mikey303.zip")
        wav_io = bank.get_wav("303 VCO SQR.wav")
        self.assertIsInstance(wav_io, io.BytesIO)
        wav_io.seek(0)
        rate, data = wavfile.read(wav_io)
        self.assertTrue(rate > 0)
        self.assertTrue(data.size > 0)
                        
if __name__ == "__main__":
    unittest.main()
