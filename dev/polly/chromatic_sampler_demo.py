from sv.banks import SVBank, SVBanks
from sv.container import SVContainer

from sv.instruments import SVInstrumentBase, SVTrigBlock, load_yaml
from sv.model import SVSlotSampleTrig, SVModTrig, ctrl_value

import logging
import rv
import rv.api
import sys
import yaml

logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format="%(levelname)s: %(message)s")

Modules = yaml.safe_load("""
- name: Beat
  class: sv.sampler.SVSlotSampler
  links:
    - Output
""")

class Nine09(SVInstrumentBase):

    Modules = Modules
    
    def __init__(self, container, namespace, samples,
                 sample_index = 0,
                 relative_note = 0):
        super().__init__(container = container,
                         namespace = namespace,
                         root = rv.note.NOTE.C5 + relative_note)
        self.defaults = {}
        self.samples = samples
        self.sample_index = sample_index

    def increment_sample(self):
        self.sample_index = (self.sample_index + 1) % len(self.samples)
        
    @property
    def sample(self):
        return self.samples[self.sample_index]
        
    def note(self,
             volume = 1.0,
             level = 1.0):
        trigs = [SVSlotSampleTrig(target = f"{self.namespace}Beat",
                                  sample = self.sample,
                                  vel = volume * level)]
        return SVTrigBlock(trigs = trigs)

def Speak(self, n, **kwargs):
    for i in range(n):
        if 0 == i % 4:
            trig_block = self.note()
            yield i, trig_block
            # self.increment_sample()

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
                        relative_note = -12)
        container.add_instrument(nine09)
        nine09.render(generator = Speak)
        container.write_project("tmp/polly-chromatic-sampler-demo.sunvox")
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
