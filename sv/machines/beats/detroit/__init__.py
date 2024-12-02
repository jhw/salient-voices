from sv.machines import SVSamplerMachine, SVMachineTrigs, load_yaml
from sv.trigs import SVSampleTrig, SVModTrig, controller_value

import rv
import rv.api

class Detroit(SVSamplerMachine):

    Modules = load_yaml(__file__, "modules.yaml")
    
    def __init__(self, container, namespace, samples,
                 sample_cutoff = 0.5,
                 sample_index = 0,
                 relative_note = 0,
                 echo_delay = 36,
                 echo_delay_unit = 3, # tick
                 echo_wet = 0,
                 echo_feedback = 0,
                 colour = [127, 127, 127],
                 **kwargs):
        super().__init__(container = container,
                         namespace = namespace,
                         root = rv.note.NOTE.C5 + relative_note,
                         cutoff = sample_cutoff,
                         colour = colour)
        self.defaults = {"Echo": {"wet": echo_wet,
                                  "feedback": echo_feedback,
                                  "delay": echo_delay,
                                  "delay_unit": echo_delay_unit}}
        self.samples = samples
        self.sample_index = sample_index

    def toggle_sound(self):
        self.sample_index = 1 - int(self.sample_index > 0)

    def increment_sound(self):
        self.sample_index = (self.sample_index + 1) % len(self.samples)

    def decrement_sound(self):
        self.sample_index = (self.sample_index - 1) % len(self.samples)
        
    def randomise_sound(self, rand):
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
        return SVMachineTrigs(trigs = trigs)

    def modulation(self,                   
                   level = 1.0,
                   echo_wet = None,
                   echo_feedback = None):
        trigs = []
        if echo_wet:
            wet_level = int(level * controller_value(echo_wet))
            trigs.append(SVModTrig(target = f"{self.namespace}Echo/wet",
                                   value = wet_level))
        if echo_feedback:
            trigs.append(SVModTrig(target = f"{self.namespace}Echo/feedback",
                                   value = echo_feedback))
        return SVMachineTrigs(trigs = trigs)
    
if __name__ == "__main__":
    pass
