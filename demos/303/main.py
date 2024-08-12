from sv.container import Container
from sv.instruments.three03 import Three03
from sv.utils.banks import single_shot_bank
from random import Random

import os
import re
import sys

def init_bassline(seed):
    def bassline(self, n,
                 root_note = 56):
        rand = Random(seed)
        offset = -1 
        for i in range(n):
            if (i == 0 or
                (rand.random() < 0.33333 and
                 i > offset)):
                length = rand.choice([1, 1, 1 , 2])
                note = root_note + rand.choice([-2, 0, 0, 0, 5])
                freq = rand.choice(["2000", "3000", "4000", "5000"])
                offset = i + length
                yield self.pluck(note = note,
                                 sustain_periods = length,
                                 filter_freq = freq,
                                 i = i)
    return bassline
                            
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
                              n_ticks = 64)
        three03 = Three03(container = container,
                          namespace = "303",
                          sample = "mikey303/303 VCO SQR.wav")
        container.add_instrument(three03)
        bassline = init_bassline(seed)
        three03.play(bassline)
        project = container.render_project()
        if not os.path.exists("tmp"):
            os.mkdir("tmp")
        with open("tmp/demo-303.sunvox", 'wb') as f:
            project.write_to(f)
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
