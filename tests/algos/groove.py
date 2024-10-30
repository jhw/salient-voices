from sv.algos.groove import wol_groove

import sv.algos.groove.perkons as perkons
from random import Random

import unittest

class GrooveTest(unittest.TestCase):

    def test_wol_groove(self, steps = 16, pulses = 11):
        rand = Random(22682)
        values = [wol_groove(rand = rand, i = i)
                  for i in range(16)]
        self.assertEqual(values[0], 1)
        self.assertTrue(min(values[1:]) > 0)
        self.assertTrue(max(values[1:]) < 1)

    def test_perkons(self, n = 16):
        rand = Random()
        for pattern_fn in [perkons.swing,
                           perkons.shifted_swing,
                           perkons.push,
                           perkons.pull,
                           perkons.humanise,
                           perkons.dynamic]:
            pattern = [pattern_fn(rand = rand,
                                  i = i)
                       for i in range(n)]
            self.assertTrue(max(pattern) > 0.8)
            self.assertTrue(min(pattern) > 0.2)
        
if __name__ == "__main__":
    unittest.main()
