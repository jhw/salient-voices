from sv.instruments import InstrumentBase, SVTrigBlock, load_yaml
from sv.model import SVNoteTrig, SVModTrig

class Nine09(InstrumentBase):

    Modules = load_yaml(__file__, "modules.yaml")
    
    def __init__(self, container, namespace, samples,
                 sample_index = 0,
                 echo_wet = 64, # '2000'
                 echo_feedback = 64): # '2000'
        super().__init__(container = container,
                         namespace = namespace)
        self.defaults = {"Echo": {"wet": echo_wet,
                                  "feedback": echo_feedback}}

        self.samples = samples
        self.sample_index = sample_index

    def toggle_sample(self):
        self.sample_index = 1 - int(self.sample_index > 0)

    def randomise_sample(self, rand):
        self.sample_index = rand.choice(list(range(len(self.samples))))
        
    @property
    def sample(self):
        return self.samples[self.sample_index]
        
    def note(self, note,
             volume = 1):
        trigs = [SVNoteTrig(target = f"{self.namespace}Beat",
                            sample = self.sample,
                            note = note,
                            vel = volume)]
        return SVTrigBlock(trigs = trigs)

    def modulation(self,
                   echo_wet = None,
                   echo_feedback = None):
        trigs = []
        if echo_wet:
            trigs.append(SVModTrig(target = f"{self.namespace}Echo/wet",
                                   value = echo_wet))
        if echo_feedback:
            trigs.append(SVModTrig(target = f"{self.namespace}Echo/feedback",
                                   value = echo_feedback))
        return SVTrigBlock(trigs = trigs)
    
if __name__ == "__main__":
    pass
