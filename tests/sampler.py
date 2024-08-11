from sv.utils.banks import single_shot_bank
from sv.sampler import SVBanks, SVBank, SVPool

import os
import unittest

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

    def test_load_save_cycle(self):
        if os.path.exists("tmp/mikey303.zip"):
            os.system("rm tmp/mikey303.zip")
        bank = single_shot_bank(bank_name = "mikey303",
                                file_path = "tests/303 VCO SQR.wav")
        bank.dump_zipfile("tmp")
        self.assertTrue(os.path.exists("tmp/mikey303.zip"))
        bank = SVBank.load_zipfile("tmp/mikey303.zip")
        self.assertTrue(isinstance(bank, SVBank))
        
if __name__ == "__main__":
    unittest.main()
