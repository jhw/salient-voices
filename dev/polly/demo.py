from sv.banks import SVBank, SVBanks
from sv.container import SVContainer
from sv.instruments.nine09.samples import Nine09

import logging
import sys

logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format="%(levelname)s: %(message)s")

def Speak(self, n, **kwargs):
    for i in range(n):
        if 0 == i % 4:
            trig_block = self.note()
            yield i, trig_block
            self.increment_sample()

if __name__ == "__main__":
    try:
        bank = SVBank.load_zip("dev/polly/numbers.zip")
        banks = SVBanks([bank])
        pool, _ = banks.spawn_pool(tag_patterns = {"voice": ".*"})
        samples = pool.match(lambda x: True)
        container = SVContainer(banks = banks,
                                bpm = 120,
                                n_ticks = 64)
        container.spawn_patch()
        nine09 = Nine09(container = container,
                        namespace = "voice",
                        samples = samples,
                        relative_note = -12,
                        echo_wet = 0)
        container.add_instrument(nine09)
        nine09.render(generator = Speak)
        container.write_project("tmp/polly-voice-sampler-demo.sunvox")
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
