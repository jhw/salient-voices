from sv.instruments.three03 import Three03
from sv.sampler import SVBank
from sv.container import Container
from random import Random

import os
import unittest

class ContainerTest(unittest.TestCase):

    def test_play(self, seed = 12345):
        bank = SVBank.load_wav_files(bank_name = "mikey303",
                                     dir_path = "tests")
        container = Container(banks = [bank])
        three03 = Three03(container = container,
                          namespace = "303",
                          sample = "mikey303/303 VCO SQR.wav")
        container.add_instrument(three03)
        rand = Random(seed)
        seeds = {key: int(rand.random() * 1e8)
                 for key in "seq|note|fx".split("|")}
        def bassline(self, n, rand):
            j = -1 
            for i in range(n):
                if i > j:
                    note = self.pluck()
                    yield note.render(i = i)
                    j += 1
        three03.play(generator = bassline,
                     seeds = seeds)
        patches = container.patches
        self.assertTrue(patches != [])
        patch = patches[0]
        self.assertTrue(patch.trigs != [])
        
if __name__ == "__main__":
    unittest.main()
