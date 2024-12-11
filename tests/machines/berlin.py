import sv.algos.groove.perkons as perkons
from sv.banks import SVBank
from sv.container import SVContainer
from sv.machines.berlin import Berlin, BerlinSound
from sv.sounds import SVSample

import inspect
import random
import unittest

def BassLine(self, n, rand, tpb, groove, temperature,
             root_offset = -4,
             offsets = [0, 0, 0, -2],
             note_density = 0.5,
             quantise = 1,
             **kwargs):
    i = 0
    while True:
        if rand["sound"].random() < temperature:
            self.randomise_sound(rand["sound"])
        note = root_offset + rand["note"].choice(offsets)
        volume = groove(rand = rand["vol"], i = i)
        if (rand["seq"].random() < note_density and
              0 == i % (quantise * tpb)):
            block =  self.note(note = note,
                               volume = volume)
            yield i, block
            i += self.sound.sustain_term # NB
        i += 1
        if i >= n:
            break

def random_sound(tpb,
                 terms = [0.5, 0.5, 0.5, 1, 2]
                 frequencies = ["2000", "3000", "3000", "3000", "5000"]):
    return BerlinSound(sustain_term = int(random.choice(terms) * tbp),
                       filter_freq = random.choice(frequencies))
        
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

    def test_berlin(self,
                    temperature = 0.5,
                    bpm = 120,
                    tpb = 2,
                    n_ticks = 16,
                    n_sounds = 16):
        bank = SVBank.load_zip("sv/machines/berlin/mikey303.zip")
        container = SVContainer(banks = [bank],
                                bpm = bpm,
                                tpb = tpb,
                                n_ticks = n_ticks)
        sounds = [random_sound(tpb) for i in range(n_sounds)]
        machine = Berlin(container = container,
                         namespace = "303",
                         sounds = sounds,
                         colour = random_colour(),
                         sample = SVSample.parse("mikey303/303 VCO SQR.wav"),
                         echo_wet = 16,
                         echo_feedback = 16,
                         echo_delay = int(bpm * 3 * tpb / 10))
        container.add_machine(machine)
        container.spawn_patch(colour = random_colour())
        seeds = {key: int(random.random() * 1e8)
                 for key in "sound|seq|note|fx|vol".split("|")}
        groove_fn = random_groove_fn(tpb)
        env = {"groove": groove_fn,
               "temperature": temperature,
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
