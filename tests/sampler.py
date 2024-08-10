from sv.utils.banks import single_shot_bank
from sv.sampler import SVBanks, SVPool

import unittest

class BanksTest(unittest.TestCase):

    def test_spawn_pool(self):
        bank = single_shot_bank(bank_name = "mikey303",
                                file_path = "tests/303 VCO SQR.wav")
        banks = SVBanks({bank.name: bank})
        tag_mapping = {"bass": "303"}
        pool, unmapped = banks.spawn_pool(tag_mapping)
        self.assertTrue(isinstance(pool, SVPool))
        self.assertEqual(len(pool), 1)
        self.assertEqual(unmapped, [])
            
if __name__ == "__main__":
    unittest.main()
