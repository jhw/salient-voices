import sv.algos.groove.perkons as perkons
from sv.banks import SVBank
from sv.container import SVContainer
from sv.machines.bass.berlin import Berlin
from sv.sample import SVSample

import random
import unittest

def simple_note(self, n, i, rand, tpb, root_offset,
                note_offsets = [0, 0, 0, -2],
                sustain_terms = [0.5, 0.5, 0.5, 2],
                filter_frequencies = ["2000", "3000", "3000", "3000", "5000"]):
    note = root_offset + rand["note"].choice(note_offsets)
    volume = perkons.humanise(rand = rand["vol"], i = int(i / tpb))
    terms = [term for term in sustain_terms
             if (term * tpb) <= (n - i)]
    if terms == []:
        return None, None
    term = int(rand["note"].choice(terms) * tpb)
    freq = rand["fx"].choice(filter_frequencies)
    block =  self.note(note = note,
                       volume = volume,
                       sustain_term = term, 
                       filter_freq = freq)
    return block, term

def BassLine(self, n, rand, tpb,
             root_offset = -4,
             note_density = 0.5,
             quantise = 1,
             **kwargs):
    i = 0
    while True:
        if i >= n:
            break
        elif (rand["seq"].random() < note_density and
              0 == i % (quantise * tpb)):
            block, term = simple_note(self,
                                      n = n,
                                      i = i,
                                      rand = rand,
                                      tpb = tpb,
                                      root_offset = root_offset)
            if not block:
                break
            yield i, block
            i += 1 + term
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
                         echo_wet = 16,
                         echo_feedback = 16,
                         echo_delay = int(36 * tpb))
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
