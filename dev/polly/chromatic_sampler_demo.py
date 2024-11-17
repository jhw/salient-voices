from sv.banks import SVBank, SVBanks
from sv.container import SVContainer
from sv.instruments import SVInstrumentBase, SVTrigBlock, load_yaml
from sv.model import SVChromaticSampleTrig, SVModTrig, ctrl_value
from sv.sampler import SVBaseSampler, MaxSlots

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
  class: dev.polly.chromatic_sampler_demo.SVChromaticSampler
  links:
    - Output
""")

class SVChromaticSampler(SVBaseSampler):

    def __init__(self, banks, pool,
                 root_note = rv.note.NOTE.C5,
                 max_slots = MaxSlots):
        SVBaseSampler.__init__(self,
                               banks = banks,
                               pool = pool)

    @property
    def root_notes(self, max_slots = MaxSlots):
        n = max_slots / len(self.pool)
        roots = {sample: int(n * (i + 0.5))
                 for i, sample in enumerate(self.pool)}
        logging.info(roots)
        return roots
        
class VolcaSample(SVInstrumentBase):

    Modules = Modules
    
    def __init__(self, container, namespace, samples,
                 sample_index = 0):
        super().__init__(container = container,
                         namespace = namespace,
                         root = rv.note.NOTE.C5)        
        self.defaults = {}
        self.samples = samples
        self.sample_index = sample_index

    def toggle_sample(self):
        self.sample_index = 1 - int(self.sample_index > 0)
        
    @property
    def sample(self):
        return self.samples[self.sample_index]
        
    def note(self,
             volume = 1.0,
             level = 1.0):
        trigs = [SVChromaticSampleTrig(note = -16,
                                       target = f"{self.namespace}Beat",
                                       sample = self.sample,
                                       vel = volume * level)]
        return SVTrigBlock(trigs = trigs)

def Speak(self, n, **kwargs):
    for i in range(n):
        if 0 == i % 4:
            trig_block = self.note()
            yield i, trig_block
            # self.toggle_sample()

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
        volca_sample = VolcaSample(container = container,
                                   namespace = "voice",
                                   samples = samples)
        container.add_instrument(volca_sample)
        volca_sample.render(generator = Speak)
        container.write_project("tmp/polly-chromatic-sampler-demo.sunvox")
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
