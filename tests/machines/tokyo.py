from sv.algos.euclid import bjorklund, TidalPatterns
from sv.algos.groove import perkons
from sv.container import SVContainer
from sv.machines.tokyo import TokyoKick, TokyoSnare, TokyoHat

import inspect
import random
import unittest
import yaml

def Beat(self, n, rand, pattern, groove, temperature, **kwargs):   
    for i in range(n):
        if rand["note"].random() < temperature:
            self.toggle_sound() 
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

def add_track(container, tag, klass, bpm, tpb,
              notes = list(range(120)),
              max_density = 0.9,
              min_density = 0.1,
              temperature = 0.5,
              patterns = [pattern[:2] for pattern in TidalPatterns]):
    notes = list(notes)
    random.shuffle(notes)
    machine = klass(container = container,
                    namespace = tag,
                    colour = random_colour(),
                    sounds = notes)
    container.add_machine(machine)
    seeds = {key: int(random.random() * 1e8)
             for key in "note|vol|fx".split("|")}
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

class TokyoTest(unittest.TestCase):
    
    def test_tokyo(self,
                   tracks = [{"tag": "kick",
                              "klass": TokyoKick,
                              "max_density": 0.6,
                              "min_density": 0.2},
                             {"tag": "snare",
                              "klass": TokyoSnare,
                              "max_density": 0.4,
                              "min_density": 0.1},
                             {"tag": "hat",
                              "klass": TokyoHat,
                              "max_density": 0.9,
                              "min_density": 0.5}],
                   bpm = 120,
                   tpb = 1,
                   n_ticks = 32):
        container = SVContainer(banks = [],
                                bpm = bpm,
                                n_ticks = n_ticks)
        container.spawn_patch(colour = random_colour())
        for track in tracks:
            add_track(container = container,
                      bpm = bpm,
                      tpb = tpb,
                      **track)
        patches = container.patches
        self.assertTrue(patches != [])
        patch = patches[0]
        self.assertTrue(patch.trigs != [])
        container.write_project("tmp/tokyo-demo.sunvox")
        
if __name__ == "__main__":
    unittest.main()
