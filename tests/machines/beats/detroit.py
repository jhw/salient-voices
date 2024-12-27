from sv.algos.euclid import bjorklund, TidalPatterns
from sv.algos.groove import perkons
from sv.bank import SVBank
from sv.container import SVContainer
from sv.machines.beats.detroit import DetroitMachine
from sv.sampler import SVSamplePool

import inspect
import random
import re
import unittest

def Beat(self, n, rand, pattern, groove, temperature, **kwargs):   
    for i in range(n):
        if rand["sample"].random() < temperature:
            self.toggle_sample() 
        volume = groove(i = i,
                        rand = rand["vol"])
        if pattern(i):
            trig_block = self.note(volume = volume)
            yield i, trig_block

def GhostEcho(self, n, rand, bpm, tpb,
              sample_hold_levels = ["0000", "2000", "4000", "6000", "8000"],
              quantise = 4,
              **kwargs):
    for i in range(n):
        if 0 == i % int(quantise * tpb):
            wet_level = rand["fx"].choice(sample_hold_levels)
            feedback_level = rand["fx"].choice(sample_hold_levels)
            delay_value = hex(int(128 * bpm * tpb * 3 / 10))
            trig_block = self.modulation(echo_delay = delay_value,
                                         echo_wet = wet_level,
                                         echo_feedback = feedback_level)
            yield i, trig_block

def random_pattern_fn(patterns, tpb):
    pattern_kwargs = {k: v * tpb for k, v in zip(["pulses", "steps"],
                                                 random.choice(patterns))}
    return bjorklund(**pattern_kwargs)

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

def add_track(container, pool, name, filter_fn, bpm,  tpb,
              max_density = 0.9,
              min_density = 0.1,
              temperature = 0.5,
              patterns = [pattern[:2] for pattern in TidalPatterns]):
    samples = pool.filter(filter_fn)
    random.shuffle(samples)        
    machine = DetroitMachine(container = container,
                             namespace = name,
                             colour = random_colour(),
                             samples = samples)
    container.add_machine(machine)
    seeds = {key: int(random.random() * 1e8)
             for key in "sample|vol|fx".split("|")}
    track_patterns = [[pulses, steps] for pulses, steps in patterns
                      if (pulses/steps < max_density and
                          pulses/steps > min_density)]
    pattern_fn = random_pattern_fn(patterns = track_patterns,
                                   tpb = tpb)
    groove_fn = random_groove_fn(tpb)
    env = {"pattern": pattern_fn,
           "groove": groove_fn,
           "temperature": temperature,
           "bpm": bpm,
           "tpb": tpb}
    machine.render(generator = Beat,
                   seeds = seeds,
                   env = env)
    machine.render(generator = GhostEcho,
                   seeds = seeds,
                   env = env)

class DetroitMachineTest(unittest.TestCase):
    
    def test_detroit_machine(self,
                             tracks = [{"name": "kick",
                                        "filter_fn": (lambda x: re.search("BD", str(x))),
                                        "max_density": 0.6,
                                        "min_density": 0.2},
                                       {"name": "clap",
                                        "filter_fn": (lambda x: re.search("(SD)|(HC)", str(x))),
                                        "max_density": 0.4,
                                        "min_density": 0.1},
                                       {"name": "hat",
                                        "filter_fn": (lambda x: re.search("(OH)|(CH)|(HH)", str(x))),
                                        "max_density": 0.9,
                                        "min_density": 0.5}],
                             bpm = 120,
                             tpb = 1,
                             n_ticks = 32):
        bank = SVBank.load_zip("tests/pico-default.zip")
        pool = bank.spawn_pool()
        container = SVContainer(bank = bank,
                                bpm = bpm,
                                tpb = tpb,
                                n_ticks = n_ticks)
        container.spawn_patch(colour = random_colour())
        for track in tracks:
            add_track(container = container,
                      pool = pool,
                      bpm = bpm,
                      tpb = tpb,
                      **track)
        patches = container.patches
        self.assertTrue(patches != [])
        patch = patches[0]
        self.assertTrue(patch.trigs != [])
        container.write_project("tmp/detroit-machine-demo.sunvox")
        
if __name__ == "__main__":
    unittest.main()
