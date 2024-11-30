import sv.algos.groove.perkons as perkons
from sv.banks import SVBank
from sv.container import SVContainer
from sv.machines.bass.berlin import Berlin
from sv.sample import SVSample

import random
import unittest

def BassLine(self, n, rand, tpb,
             block_sizes = [1, 1, 1, 4],
             root_offset = -4,
             note_scale = [-0, 0, 0, -2],
             note_density = 0.333333,
             quantise = 1,
             filter_frequencies = ["3000", "3000", "3000", "4000"],
             **kwargs):
    i = 0
    while True:
        volume = perkons.humanise(rand = rand["vol"], i = i)
        block_size = rand["seq"].choice(block_sizes)
        note_offset = root_offset + rand["note"].choice(note_scale)
        sustain_term = min(n - (i + 1), rand["note"].choice(block_sizes))
        filter_freq = rand["fx"].choice(filter_frequencies)
        has_note = rand["seq"].random() < note_density
        if i >= n:
            break
        elif (has_note and
              0 == i % (quantise * tpb)):
            trig_block = self.note(note = note_offset,
                                   volume = volume,
                                   sustain_term = sustain_term, 
                                   filter_freq = filter_freq)
            yield i, trig_block
            i += 1 + sustain_term
        else:
            i += 1
            
class BerlinBassTest(unittest.TestCase):

    def test_berlin(self, tpb = 2):
        bank = SVBank.load_zip("sv/machines/bass/berlin/mikey303.zip")
        container = SVContainer(banks = [bank],
                                bpm = 120 * tpb,
                                n_ticks = 32 * tpb)
        machine = Berlin(container = container,
                         namespace = "303",
                         sample = SVSample.parse("mikey303/303 VCO SQR.wav"),
                         echo_delay = 36 * tpb)
        container.add_machine(machine)
        container.spawn_patch()
        seeds = {key: int(random.random() * 1e8)
                 for key in "seq|note|fx|vol".split("|")}
        env = {"tpb": tpb}
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
