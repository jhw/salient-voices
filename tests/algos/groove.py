from sv.algos.groove import wolgroove

from random import Random

import unittest

class GrooveTest(unittest.TestCase):

    def test_wolgroove(self, steps = 16, pulses = 11):
        rand = Random(22682)
        values = [wolgroove(rand = rand, i = i)
                  for i in range(16)]
        self.assertEqual(values[0], 1)
        self.assertTrue(min(values[1:]) > 0)
        self.assertTrue(max(values[1:]) < 1)
        
if __name__ == "__main__":
    unittest.main()
