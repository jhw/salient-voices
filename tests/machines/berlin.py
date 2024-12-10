import sv.algos.groove.perkons as perkons
from sv.banks import SVBank
from sv.container import SVContainer
from sv.machines.berlin import Berlin
from sv.sounds import SVSample

import inspect
import random
import unittest

def simple_note(self, n, i, tpb, rand, groove, root_offset, offsets, terms, frequencies):
    note = root_offset + rand["note"].choice(offsets)
    volume = groove(rand = rand["vol"], i = i)
    term = int(rand["note"].choice(terms) * tpb)
    freq = rand["fx"].choice(frequencies)
    block =  self.note(note = note,
                       volume = volume,
                       sustain_term = term, 
                       filter_freq = freq)
    return block, term

def BassLine(self, n, rand, tpb, groove,
             root_offset = -4,
             offsets = [0, 0, 0, -2],
             terms = [0.5, 0.5, 0.5, 2],
             frequencies = ["2000", "3000", "3000", "3000", "5000"],
             note_density = 0.5,
             quantise = 1,
             **kwargs):
    i = 0
    while True:
        if (rand["seq"].random() < note_density and
              0 == i % (quantise * tpb)):
            block, term = simple_note(self,
                                      n = n,
                                      i = i,
                                      tpb = tpb,
                                      rand = rand,
                                      groove = groove,
                                      root_offset = root_offset,
                                      offsets = offsets,
                                      terms = terms,
                                      frequencies = frequencies)
            yield i, block
            i += term
        i += 1
        if i >= n:
            break

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

class BerlinTest(unittest.TestCase):

    def test_berlin(self, tpb = 2):
        bank = SVBank.load_zip("sv/machines/berlin/mikey303.zip")
        container = SVContainer(banks = [bank],
                                bpm = 120 * tpb,
                                n_ticks = 32 * tpb)
        machine = Berlin(container = container,
                         namespace = "303",
                         colour = random_colour(),
                         sample = SVSample.parse("mikey303/303 VCO SQR.wav"),
                         echo_wet = 16,
                         echo_feedback = 16,
                         echo_delay = int(36 * tpb))
        container.add_machine(machine)
        container.spawn_patch(colour = random_colour())
        seeds = {key: int(random.random() * 1e8)
                 for key in "seq|note|fx|vol".split("|")}
        groove_fn = random_groove_fn(tpb)
        env = {"groove": groove_fn,
               "tpb": tpb}
        machine.render(generator = BassLine,
                       seeds = seeds,
                       env = env)
        patches = container.patches
        self.assertTrue(patches != [])
        patch = patches[0]
        self.assertTrue(patch.trigs != [])
        container.write_project("tmp/berlin-demo.sunvox")
        
if __name__ == "__main__":
    unittest.main()
