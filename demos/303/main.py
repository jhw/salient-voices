from sv.container import Container
from sv.instruments.three03 import Three03
from sv.utils.banks import single_shot_bank

import os, random

def bassline(self, n,
             root_note = 56):
    offset = -1 
    for i in range(n):
        if (random.random() < 0.5 and
            i > offset):
            sustain_periods = random.choice([1, 2])
            note = root_note + random.choice([-2, -2, 0, 0, 0, 5, 12])
            offset = i + sustain_periods
            yield self.pluck(note = note,
                             sustain_periods = sustain_periods,
                             i = i)
                            
if __name__ == "__main__":
    try:
        bank = single_shot_bank(bank_name = "mikey303",
                                file_path = "demos/303/303 VCO SQR.wav")
        container = Container(banks = [bank],
                              n_ticks = 32)
        three03 = Three03(container = container,
                          namespace = "303")
        container.add_instrument(three03)
        three03.play(bassline)
        project = container.render_project()
        if not os.path.exists("tmp"):
            os.mkdir("tmp")
        with open("tmp/demo-303.sunvox", 'wb') as f:
            project.write_to(f)
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
