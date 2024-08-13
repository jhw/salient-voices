from sv.container import Container
from sv.instruments.three03 import Three03
from sv.utils.banks import single_shot_bank
from random import Random

import os
import re
import sys

def bassline(self, n, rand,
             root_offset = -4,
             note_density = 0.33333,
             note_scale = [-2, 0, 0, 0, 5],
             note_lengths = [1, 1, 1, 2],
             # filter_frequencies = ["2000", "2800", "3000", "3800"]):
             filter_frequencies = ["2800", "3000", "3800", "4000"]):
    j = -1 
    for i in range(n):
        if (i == 0 or
            (rand.random() < note_density and
             i > j)):
            note_offset = root_offset + rand.choice(note_scale)
            note_length = rand.choice(note_lengths)
            filter_freq = rand.choice(filter_frequencies)
            j = i + note_length
            yield self.pluck(note = note_offset,
                             sustain_periods = note_length,
                             filter_freq = filter_freq,
                             i = i)
                            
if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            raise RuntimeError("please enter seed")
        seed = sys.argv[1]
        if not re.search("^\\d+$", seed):
            raise RuntimeError("seed must be an integer")
        seed = int(seed)
        bank = single_shot_bank(bank_name = "mikey303",
                                file_path = "demos/303/303 VCO SQR.wav")
        container = Container(banks = [bank],
                              bpm = 120,
                              n_ticks = 32)
        three03 = Three03(container = container,
                          namespace = "303",
                          sample = "mikey303/303 VCO SQR.wav")
        container.add_instrument(three03)
        three03.play(generator = bassline,
                     rand = Random(seed))
        project = container.render_project()
        if not os.path.exists("tmp"):
            os.mkdir("tmp")
        with open("tmp/demo-303.sunvox", 'wb') as f:
            project.write_to(f)
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
