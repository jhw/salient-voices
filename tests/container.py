from sv.instruments.three03.mikey303 import Three03
from sv.banks import SVBank
from sv.container import SVContainer

import os
import random
import unittest

class ContainerTest(unittest.TestCase):

    def test_play(self, seed = 12345):
        bank = SVBank.load_wav_files(bank_name = "mikey303",
                                     dir_path = "tests")
        container = SVContainer(banks = [bank])
        three03 = Three03(container = container,
                          namespace = "303",
                          sample = "mikey303/303 VCO SQR.wav")
        container.add_instrument(three03)
        container.spawn_patch()
        seeds = {key: int(random.random() * 1e8)
                 for key in "seq|note|fx".split("|")}
        def bassline(self, n, rand, **kwargs):
            j = -1 
            for i in range(n):
                if i > j:
                    trig_block = self.note()
                    yield i, trig_block
                    j += 1
        three03.play(generator = bassline,
                     seeds = seeds)
        patches = container.patches
        self.assertTrue(patches != [])
        patch = patches[0]
        self.assertTrue(patch.trig_patch.trigs != [])
        
if __name__ == "__main__":
    unittest.main()
