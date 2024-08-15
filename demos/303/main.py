from sv.container import Container
from sv.instruments.three03 import Three03
from sv.sampler import SVBank
from random import Random

import os
import re
import sys

def random_note(self, rand,
                root_offset = -5,
                note_scale = [-2, 0, 0, 0, 3, 12],
                note_lengths = [2, 3, 4, 5, 6, 7],
                filter_frequencies = ["3000", "4000", "5000", "6000"]):
    note_offset = root_offset + rand["note"].choice(note_scale)
    note_length = rand["note"].choice(note_lengths)
    filter_freq = rand["fx"].choice(filter_frequencies)
    return self.pluck(note = note_offset,
                      sustain_periods = note_length,
                      filter_freq = filter_freq)

def random_sequence(self,
                    rand,
                    seq_length):
    seq = [None for i in range(seq_length)]
    j = -1
    for i in range(seq_length):
        if i > j:
            seq[i] = random_note(self, rand)
            j = i + seq[i].offset
    return seq

def bassline(self, n, rand,
             seq_length = 64):
    seq = random_sequence(self,
                          rand,
                          seq_length = seq_length)
    for i in range(n):
        j = i % seq_length
        note = seq[j]
        if note:
            yield note.render(i = i)
                            
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
        project = container.render_project()
        if not os.path.exists("tmp"):
            os.mkdir("tmp")
        with open("tmp/demo-303.sunvox", 'wb') as f:
            project.write_to(f)
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
