from sv.utils.banks import single_shot_bank
from sv.sampler import SVBank

import unittest

class BanksTest(unittest.TestCase):

    def test_single_shot_bank(self):
        try:
            bank = single_shot_bank(bank_name = "mikey303",
                                    file_path = "tests/303 VCO SQR.wav")
            self.assertTrue(isinstance(bank, SVBank))
            self.assertEqual(bank.name, "mikey303")
            wav_files = bank.zip_file.namelist()
            self.assertTrue(len(wav_files) == 1)
            self.assertTrue("303 VCO SQR.wav" in wav_files)
        except RuntimeError as error:
            self.fail(str(error))
            
if __name__ == "__main__":
    unittest.main()
