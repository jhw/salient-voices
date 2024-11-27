from sv.algos.euclid import bjorklund, TidalPatterns
from sv.banks import SVBank, SVBanks
from sv.container import SVContainer
from sv.machines.beats.detroit import Detroit
from sv.sample import SVSample

import inspect
import random
import unittest

def Beat(self, n, rand, quantise = 2, **kwargs):   
    for i in range(n):
        self.randomise_sound(rand["sample"])
        if 0 == i % quantise:
            trig_block = self.note(volume = 1)
            yield i, trig_block

def GhostEcho(self, n, rand,
              sample_hold_levels = ["0000", "2000", "4000", "6000", "8000"],
              quantise = 4,
              **kwargs):
    for i in range(n):
        if 0 == i % quantise:            
            wet_level = rand["fx"].choice(sample_hold_levels)
            feedback_level = rand["fx"].choice(sample_hold_levels)
            trig_block = self.modulation(echo_wet = wet_level,
                                         echo_feedback = feedback_level)
            yield i, trig_block

class DetroitFXBeatsTest(unittest.TestCase):
    
    def test_detroit(self, tracks = [{"tag": "hat"}]):
        bank = SVBank.load_zip("tests/pico-default.zip")
        banks = SVBanks([bank])
        container = SVContainer(banks = banks,
                                bpm = 120,
                                n_ticks = 64)
        container.spawn_patch()
        base_wav = random.choice(["40 CH", "41 CH", "45 OH", "46 OH"])
        base_sample = SVSample.parse(f"pico-default/{base_wav}.wav")
        samples = [base_sample,
                   base_sample]
        for fx in [SVSample.FX.REV,
                   SVSample.FX.REV,
                   SVSample.FX.RET2,
                   SVSample.FX.RET4,
                   SVSample.FX.RET8,
                   SVSample.FX.RET16]:
            sample = base_sample.clone()
            sample.fx = fx
            samples.append(sample)
        machine = Detroit(container = container,
                          namespace = "hat",
                          samples = samples)
        container.add_machine(machine)
        seeds = {key: int(random.random() * 1e8)
                 for key in "sample|fx".split("|")}
        machine.render(generator = Beat,
                       seeds = seeds)
        machine.render(generator = GhostEcho,
                       seeds = seeds)
        patches = container.patches
        self.assertTrue(patches != [])
        patch = patches[0]
        self.assertTrue(patch.trigs != [])
        container.write_project("tmp/detroit-fx-demo.sunvox")
        
if __name__ == "__main__":
    unittest.main()
