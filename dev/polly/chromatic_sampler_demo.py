from sv.banks import SVBank, SVBanks
from sv.container import SVContainer
# from sv.instruments.nine09.samples import Nine09

from sv.instruments import SVInstrumentBase, SVTrigBlock, load_yaml
from sv.model import SVSlotSampleTrig, SVModTrig, ctrl_value

import logging
import rv
import rv.api
import sys
import yaml

Modules = yaml.safe_load("""
- name: Beat
  class: sv.sampler.SVSlotSampler
  links:
    - Echo
- name: Echo
  class: rv.modules.echo.Echo
  defaults:
    delay: 36
    delay_unit: 3 # tick
  links:
    - Output
""")

class Nine09(SVInstrumentBase):

    Modules = Modules
    
    def __init__(self, container, namespace, samples,
                 sample_index = 0,
                 relative_note = 0,
                 echo_wet = 64, # '2000'
                 echo_feedback = 64): # '2000'
        super().__init__(container = container,
                         namespace = namespace,
                         root = rv.note.NOTE.C5 + relative_note)
        self.defaults = {"Echo": {"wet": echo_wet,
                                  "feedback": echo_feedback}}

        self.samples = samples
        self.sample_index = sample_index

    def toggle_sample(self):
        self.sample_index = 1 - int(self.sample_index > 0)

    def increment_sample(self):
        self.sample_index = (self.sample_index + 1) % len(self.samples)

    def decrement_sample(self):
        self.sample_index = (self.sample_index - 1) % len(self.samples)
        
    def randomise_sample(self, rand):
        self.sample_index = rand.choice(list(range(len(self.samples))))
        
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

    def modulation(self,
                   level = 1.0,
                   echo_wet = None,
                   echo_feedback = None):
        trigs = []
        if echo_wet:
            wet_level = int(level * ctrl_value(echo_wet))
            trigs.append(SVModTrig(target = f"{self.namespace}Echo/wet",
                                   value = wet_level))
        if echo_feedback:
            trigs.append(SVModTrig(target = f"{self.namespace}Echo/feedback",
                                   value = echo_feedback))
        return SVTrigBlock(trigs = trigs)
    
if __name__ == "__main__":
    pass

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
        container.write_project("tmp/polly-chromatic-sampler-demo.sunvox")
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
