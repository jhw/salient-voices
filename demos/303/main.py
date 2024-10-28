from sv.banks import SVBank
from sv.container import SVContainer
from sv.instruments.three03 import Three03
from random import Random

import os
import random
import re

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
               sample_hold_levels = ["0000", "2000", "4000", "6000", "8000"],
               quantise = 8):
    for i in range(n):
        if 0 == i % quantise:            
            echo_wet_level = rand["fx"].choice(sample_hold_levels)
            echo_feedback_level = rand["fx"].choice(sample_hold_levels)
            trig_block = self.modulation(echo_wet = echo_wet_level,
                                         echo_feedback = echo_feedback_level)
            yield trig_block.render(i = i)
                            
if __name__ == "__main__":
    try:
        bank = SVBank.load_wav_files(bank_name = "mikey303",
                                     dir_path = "demos/303")
        container = SVContainer(banks = [bank],
                                bpm = 240,
                                n_ticks = 64)
        three03 = Three03(container = container,
                          namespace = "303",
                          sample = "mikey303/303 VCO SQR.wav")
        container.add_instrument(three03)
        rand = {key: Random(int(random.random() * 1e8))
                 for key in "seq|note|fx".split("|")}
        three03.play(generator = bassline,
                     rand = rand)
        three03.play(generator = ghost_echo,
                     rand = rand)
        project = container.render_project()
        if not os.path.exists("tmp"):
            os.mkdir("tmp")
        with open("tmp/demo-303.sunvox", 'wb') as f:
            project.write_to(f)
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
