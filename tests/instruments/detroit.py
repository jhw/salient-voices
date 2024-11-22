from sv.algos.euclid import bjorklund, TidalPatterns
from sv.algos.groove import perkons
from sv.banks import SVBank, SVBanks
from sv.container import SVContainer
from sv.instruments.detroit import Detroit
from sv.sampler import SVSampleRef as SVSample

import random
import unittest
import yaml

PoolTagPatterns = yaml.safe_load("""
kick: (kick)|(kik)|(kk)|(bd)
clap: (clap)|(clp)|(cp)|(hc)
hat: (oh)|(ch)|(open)|(closed)|(hh)|(hat)
""")

def Beat(self, n, rand, pattern, groove, **kwargs):   
    for i in range(n):
        if pattern(i):
            volume = groove(i)
            trig_block = self.note(volume = volume)
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

def random_pattern_fn(patterns = TidalPatterns):
    pattern_kwargs = {k: v for k, v in zip(["pulses", "steps"],
                                           random.choice(patterns))}
    return bjorklund(**pattern_kwargs)

def random_groove_fn():
    return perkons.shifted_swing

class DetroitTest(unittest.TestCase):

    def test_detroit(self):
        bank = SVBank.load_zip("tests/pico-default.zip")
        banks = SVBanks([bank])
        pool, _ = banks.spawn_pool(tag_patterns = PoolTagPatterns)
        container = SVContainer(banks = banks,
                                bpm = 120,
                                n_ticks = 128)
        samples = pool.match(lambda sample: "kick" in sample.tags)
        detroit = Detroit(container = container,
                          namespace = "kick",
                          samples = samples)
        container.add_instrument(detroit)
        container.spawn_patch()
        seeds = {key: int(random.random() * 1e8)
                 for key in "sample|fx".split("|")}
        pattern_fn = random_pattern_fn()
        groove_fn = random_groove_fn()
        env = {"pattern": pattern_fn,
               "groove": groove_fn}
        detroit.render(generator = Beat,
                       seeds = seeds,
                       env = env)
        detroit.render(generator = GhostEcho,
                       seeds = seeds)
        patches = container.patches
        self.assertTrue(patches != [])
        patch = patches[0]
        self.assertTrue(patch.trigs != [])
        container.write_project("tmp/detroit-demo.sunvox")
        
if __name__ == "__main__":
    unittest.main()
