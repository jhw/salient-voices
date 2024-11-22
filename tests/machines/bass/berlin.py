import sv.algos.groove.perkons as perkons
from sv.banks import SVBank
from sv.container import SVContainer
from sv.machines.bass.berlin import Berlin
from sv.sampler import SVSampleRef as SVSample

import random
import unittest

def BassLine(self, n, rand,
             block_sizes = [1, 2, 4],
             root_offset = -5,
             note_scale = [-2, 0, 0, 0, 5],
             note_density = 0.66666,
             quantise = 2,
             filter_frequencies = ["1000", "1800", "2000"],
             **kwargs):
    i = 0
    while True:
        volume = perkons.humanise(rand = rand["vol"],
                                  i = i)
        if i >= (n - 2):
            break
        elif (rand["seq"].random() < note_density and
              0 == i % quantise):
            block_size = rand["seq"].choice(block_sizes)
            note_offset = root_offset + rand["note"].choice(note_scale)
            sustain_term = min(n - (i + 1), rand["note"].choice(block_sizes))
            filter_freq = rand["fx"].choice(filter_frequencies)
            trig_block = self.note(note = note_offset,
                                   volume = volume,
                                   sustain_term = sustain_term, 
                                   filter_freq = filter_freq)
            yield i, trig_block
            i += 1 + sustain_term
        else:
            i += 1
            
def GhostEcho(self, n, rand,
              sample_hold_levels = ["0000", "0400", "0800"],
              quantise = 8,
              **kwargs):
    for i in range(n):
        if 0 == i % quantise:            
            wet_level = rand["fx"].choice(sample_hold_levels)
            feedback_level = rand["fx"].choice(sample_hold_levels)
            trig_block = self.modulation(echo_wet = wet_level,
                                         echo_feedback = feedback_level)
            yield i, trig_block

class BerlinBassTest(unittest.TestCase):

    def test_berlin(self):
        bank = SVBank.load_zip("sv/machines/bass/berlin/mikey303.zip")
        container = SVContainer(banks = [bank],
                                bpm = 240,
                                n_ticks = 128)
        machine = Berlin(container = container,
                         namespace = "303",
                         sample = SVSample.parse("mikey303/303 VCO SQR.wav"))
        container.add_machine(machine)
        container.spawn_patch()
        seeds = {key: int(random.random() * 1e8)
                 for key in "seq|note|fx|vol".split("|")}
        machine.render(generator = BassLine,
                       seeds = seeds)
        machine.render(generator = GhostEcho,
                       seeds = seeds)
        patches = container.patches
        self.assertTrue(patches != [])
        patch = patches[0]
        self.assertTrue(patch.trigs != [])
        container.write_project("tmp/berlin-demo.sunvox")
        
if __name__ == "__main__":
    unittest.main()
