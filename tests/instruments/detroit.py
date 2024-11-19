from sv.banks import SVBank
from sv.container import SVContainer
from sv.instruments.detroit import Detroit
from sv.sampler import SVSampleRef as SVSample

import random
import unittest

def Beat(self, n, **kwargs):
    for i in range(n):
        if 0 == i % 4:
            trig_block = self.note()
            yield i, trig_block

def GhostEcho(self, n, rand,
              sample_hold_levels = ["0000", "2000", "4000", "6000", "8000"],
              quantise = 8,
              **kwargs):
    for i in range(n):
        if 0 == i % quantise:            
            wet_level = rand["fx"].choice(sample_hold_levels)
            feedback_level = rand["fx"].choice(sample_hold_levels)
            trig_block = self.modulation(echo_wet = wet_level,
                                         echo_feedback = feedback_level)
            yield i, trig_block
            
class DetroitTest(unittest.TestCase):

    def test_detroit(self):
        bank = SVBank.load_zip("tests/pico-default.zip")
        container = SVContainer(banks = [bank],
                                bpm = 120,
                                n_ticks = 128)
        sample = SVSample.parse("pico-default/00 BD.wav")
        detroit = Detroit(container = container,
                          namespace = "909",
                          samples = [sample])
        container.add_instrument(detroit)
        container.spawn_patch()
        seeds = {key: int(random.random() * 1e8)
                 for key in ["fx"]}
        detroit.render(generator = Beat,
                       seeds = seeds)
        detroit.render(generator = GhostEcho,
                       seeds = seeds)
        patches = container.patches
        self.assertTrue(patches != [])
        patch = patches[0]
        self.assertTrue(patch.trigs != [])
        container.write_project("tmp/detroit-demo.sunvox")
        
if __name__ == "__main__":
    unittest.main()
