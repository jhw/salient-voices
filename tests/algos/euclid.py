from sv.algos.euclid import bjorklund

import unittest

class EuclidAlgoTest(unittest.TestCase):

    def test_bjorklund(self, steps = 16, pulses = 11):
        pattern_fn = bjorklund(steps = steps,
                               pulses = pulses)
        pattern = [pattern_fn(i) for i in range(steps)]
        self.assertEqual(steps, len(pattern))
        self.assertEqual(pulses, sum(pattern))
        
if __name__ == "__main__":
    unittest.main()
