from sv.algos.euclid import bjorklund

import unittest

class EuclidAlgoTest(unittest.TestCase):

    def test_bjorklund(self, steps = 16, pulses = 11):
        beats = bjorklund(steps = steps,
                          pulses = pulses)
        self.assertEqual(steps, len(beats))
        self.assertEqual(pulses, sum(beats))
        
if __name__ == "__main__":
    unittest.main()
