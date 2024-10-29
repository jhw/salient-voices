from sv.algos.groove import wolgroove
from sv.banks import SVBank
from sv.container import SVContainer
from sv.instruments.three03.mikey303 import Three03

import random
import re

def bassline(self, n, rand,
             block_sizes = [1, 2, 4],
             root_offset = -5,
             note_scale = [0, 0, 0, 0, 12],
             note_density = 0.66666,
             quantise = 2,
             filter_frequencies = ["1000", "1800", "2000", "4000"],
             **kwargs):
    i = 0
    while True:
        volume = wolgroove(rand = rand["vol"],
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
            
def ghost_echo(self, n, rand,
               sample_hold_levels = ["0000", "0400", "0800"],
               quantise = 8,
               **kwargs):
    for i in range(n):
        if 0 == i % quantise:            
            echo_wet_level = rand["fx"].choice(sample_hold_levels)
            echo_feedback_level = rand["fx"].choice(sample_hold_levels)
            trig_block = self.modulation(echo_wet = echo_wet_level,
                                         echo_feedback = echo_feedback_level)
            yield i, trig_block
                            
if __name__ == "__main__":
    try:
        bank = SVBank.load_wav_files(bank_name = "mikey303",
                                     dir_path = "demos/303/mikey303")
        container = SVContainer(banks = [bank],
                                bpm = 240,
                                n_ticks = 32)
        three03 = Three03(container = container,
                          namespace = "303",
                          sample = "mikey303/303 VCO SQR.wav")
        container.add_instrument(three03)
        container.spawn_patch()
        seeds = {key: int(random.random() * 1e8)
                 for key in "seq|note|fx|vol".split("|")}
        three03.play(generator = bassline,
                     seeds = seeds)
        three03.play(generator = ghost_echo,
                     seeds = seeds)
        container.write_project("tmp/demo-303.sunvox")
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
