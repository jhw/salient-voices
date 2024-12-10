from sv.algos.euclid import bjorklund, TidalPatterns
from sv.algos.groove import perkons
from sv.banks import SVBank, SVBanks
from sv.container import SVContainer
from sv.machines.detroit import Detroit
from sv.sounds import SVSample

import inspect
import random
import unittest

def Beat(self, n, rand, groove, threshold = 0.5, **kwargs):   
    for i in range(n):
        self.randomise_sound(rand["sound"])
        volume = groove(i = i,
                        rand = rand["vol"])
        if rand["beat"].random() < threshold:
            trig_block = self.note(volume = volume)
            yield i, trig_block

def GhostEcho(self, n, rand,
              sample_hold_levels = ["0000", "2000", "4000", "6000", "8000"],
              quantise = 4,
              **kwargs):
    for i in range(n):
        if 0 == i % quantise:            
            wet_level = rand["fx"].choice(sample_hold_levels)
            feedback_level = rand["fx"].choice(sample_hold_levels)
            trig_block = self.modulation(echo_delay = "1200",
                                         echo_wet = wet_level,
                                         echo_feedback = feedback_level)
            yield i, trig_block

def random_groove_fn(tpb, mod = perkons):
    fn_names = [name for name, _ in inspect.getmembers(mod, inspect.isfunction)]
    fn = getattr(mod, random.choice(fn_names))
    def wrapped(i, **kwargs):
        if 0 == i % tpb:
            j = int(i / tpb)
            return fn(j, **kwargs)
        else:
            return 0
    return wrapped

def random_colour(offset = 64,
                  contrast = 128,
                  n = 256):
    for i in range(n):
        color = [int(offset + random.random() * (255 - offset))
                 for i in range(3)]
        if (max(color) - min(color)) > contrast:
            return color
    raise RuntimeError("couldn't find suitable random colour")
            
class DetroitFXTest(unittest.TestCase):
    
    def test_detroit(self,
                     tracks = [{"tag": "hat"}],
                     tpb = 1):
        bank = SVBank.load_zip("tests/pico-default.zip")
        banks = SVBanks([bank])
        container = SVContainer(banks = banks,
                                bpm = 120,
                                n_ticks = 32)
        container.spawn_patch(colour = random_colour())
        base_wav = random.choice(["40 CH", "41 CH", "45 OH", "46 OH"])
        base_sample = SVSample.parse(f"pico-default/{base_wav}.wav?cutoff=10000")
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
                          colour = random_colour(),
                          sounds = samples)
        container.add_machine(machine)
        seeds = {key: int(random.random() * 1e8)
                 for key in "beat|sound|fx|vol".split("|")}
        groove_fn = random_groove_fn(tpb)
        env = {"groove": groove_fn}
        machine.render(generator = Beat,
                       seeds = seeds,
                       env = env)
        machine.render(generator = GhostEcho,
                       seeds = seeds)
        patches = container.patches
        self.assertTrue(patches != [])
        patch = patches[0]
        self.assertTrue(patch.trigs != [])
        container.write_project("tmp/detroit-fx-demo.sunvox")
        
if __name__ == "__main__":
    unittest.main()
