from sv.instruments import SVInstrumentBase, SVTrigBlock, load_yaml
from sv.trigs import SVSampleTrig, SVModTrig, ctrl_value

import rv
import rv.api

class Detroit(SVInstrumentBase):

    Modules = load_yaml(__file__, "modules.yaml")
    
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
             note = 0,
             volume = 1.0,
             level = 1.0):
        cloned_sample = self.sample.clone()
        cloned_sample["note"] = note
        trigs = [SVSampleTrig(target = f"{self.namespace}Beat",
                                  sample = cloned_sample,
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
