import sv.algos.vitling as nine09

import random
import unittest

class VitlingTest(unittest.TestCase):

    def test_nine09(self, n = 16):
        rand = random.Random()
        for pattern_fn in [nine09.fourfloor_kick,
                           nine09.electro_kick,
                           nine09.backbeat_snare,
                           nine09.skip_snare,
                           # nine09.offbeats_hat,
                           nine09.closed_hat]:
            pattern = pattern_fn(rand = rand,
                                 n = n)
            self.assertEqual(len(pattern), n)

    def test_nine09_offbeats_hat(self, n = 16):
        rand = random.Random()
        patterns = nine09.offbeats_hat(rand = rand,
                                      n = n)
        self.assertEqual(len(patterns), 2)
        for pattern in patterns:
            self.assertEqual(len(pattern), n)
        
if __name__ == "__main__":
    unittest.main()
