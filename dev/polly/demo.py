from sv.banks import SVBank, SVBanks
from sv.container import SVContainer
from sv.machines.beats.detroit import Detroit

import logging
import random
import sys

logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format="%(levelname)s: %(message)s")

def Speak(self, n, **kwargs):
    for i in range(n):
        if 0 == i % 4:
            note = -2 if (3 == i / 4) else 0
            trig_block = self.note(note)
            yield i, trig_block
            self.increment_sound()

if __name__ == "__main__":
    try:
        bank = SVBank.load_zip("dev/polly/numbers.zip")
        banks = SVBanks([bank])
        pool, _ = banks.spawn_pool(tag_patterns = {"voice": ".*"})
        samples = pool.match(lambda x: True)
        container = SVContainer(banks = banks,
                                bpm = 120,
                                n_ticks = 32)
        container.spawn_patch()
        detroit = Detroit(container = container,
                          namespace = "voice",
                          samples = samples,
                          relative_note = -12,
                          sample_cutoff = 1e10,
                          echo_wet = 0)
        container.add_machine(detroit)
        detroit.render(generator = Speak)
        container.write_project("tmp/polly-demo.sunvox")
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
