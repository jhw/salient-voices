from sv.container import Container
from sv.instruments.three03 import Three03
from sv.sampler import SVBank
from random import Random

import os
import re
import sys

def bassline(self, n, rand,
             block_sizes = [2, 3, 4, 5, 6, 7, 8, 9, 10],
             root_offset = -5,
             note_scale = [-2, -2, 0, 0, 0, 0, 3, 3, 12],
             quantise = 4,
             note_density = 0.75,
             filter_frequencies = ["2000", "2800", "3000", "3800", "4000", "4800", "5000"]):
    j = 0    
    for i in range(n):
        if (i >= j and
            0 == i % quantise and
            rand["seq"].random() < note_density):
            block_size = rand["seq"].choice(block_sizes)
            note_offset = root_offset + rand["note"].choice(note_scale)
            sustain_term = 1 + rand["note"].choice(range(block_size - 1))
            filter_freq = rand["fx"].choice(filter_frequencies)
            trig_block = self.note(note = note_offset,
                                   sustain_term = sustain_term, 
                                   filter_freq = filter_freq)
            if (i + sustain_term) < n:
                yield trig_block.render(i = i)
            j = i + block_size

def ghost_echo(self, n, rand,
               wet_levels = ["0000", "2000", "4000", "6000", "8000"],
               quantise = 8):
    for i in range(n):
        if 0 == i % quantise:            
            wet_level = rand["fx"].choice(wet_levels)
            trig_block = self.modulation(mod = "Echo",
                                         ctrl = "wet",
                                         value = wet_level)
            yield trig_block.render(i = i)
                            
if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            raise RuntimeError("please enter seed")
        seed = sys.argv[1]
        if not re.search("^\\d+$", seed):
            raise RuntimeError("seed must be an integer")
        seed = int(seed)
        bank = SVBank.load_wav_files(bank_name = "mikey303",
                                     dir_path = "demos/303")
        container = Container(banks = [bank],
                              bpm = 240,
                              n_ticks = 64)
        three03 = Three03(container = container,
                          namespace = "303",
                          sample = "mikey303/303 VCO SQR.wav")
        container.add_instrument(three03)
        rand = Random(seed)
        seeds = {key: int(rand.random() * 1e8)
                 for key in "seq|note|fx".split("|")}
        three03.play(generator = bassline,
                     seeds = seeds)
        three03.play(generator = ghost_echo,
                     seeds = seeds)
        project = container.render_project()
        if not os.path.exists("tmp"):
            os.mkdir("tmp")
        with open("tmp/demo-303.sunvox", 'wb') as f:
            project.write_to(f)
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
