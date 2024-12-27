from sv.machines import SVMachineTrigs
from sv.trigs import SVModTrig, controller_value

class SVBeatsApi:
    
    def __init__(self,
                 samples,
                 sample_index = 0,
                 pitches = [0],
                 pitch_index = 0,
                 cutoffs = [500],
                 cutoff_index = 0,
                 **kwargs):
        self.samples = samples
        self.sample_index = sample_index
        self.pitches = pitches
        self.pitch_index = pitch_index
        self.cutoffs = cutoffs
        self.cutoff_index = cutoff_index

    # sample
        
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

    # pitch
        
    def toggle_pitch(self):
        self.pitch_index = 1 - int(self.pitch_index > 0)

    def increment_pitch(self):
        self.pitch_index = (self.pitch_index + 1) % len(self.pitches)

    def decrement_pitch(self):
        self.pitch_index = (self.pitch_index - 1) % len(self.pitches)

    def randomise_pitch(self, rand):
        self.pitch_index = rand.choice(list(range(len(self.pitches))))

    @property
    def pitch(self):
        return self.pitches[self.pitch_index]

    # cutoff
        
    def toggle_cutoff(self):
        self.cutoff_index = 1 - int(self.cutoff_index > 0)

    def increment_cutoff(self):
        self.cutoff_index = (self.cutoff_index + 1) % len(self.cutoffs)

    def decrement_cutoff(self):
        self.cutoff_index = (self.cutoff_index - 1) % len(self.cutoffs)

    def randomise_cutoff(self, rand):
        self.cutoff_index = rand.choice(list(range(len(self.cutoffs))))

    @property
    def cutoff(self):
        return self.cutoffs[self.cutoff_index]

    # methods

    def modulation(self,
                   level=1.0,
                   echo_delay=None,
                   echo_wet=None,
                   echo_feedback=None):
        trigs = []
        if echo_delay:
            delay_level = int(level * controller_value(echo_delay))
            trigs.append(SVModTrig(target=f"{self.namespace}Echo/delay",
                                   value=delay_level))
        if echo_wet:
            wet_level = int(level * controller_value(echo_wet))
            trigs.append(SVModTrig(target=f"{self.namespace}Echo/wet",
                                   value=wet_level))
        if echo_feedback:
            trigs.append(SVModTrig(target=f"{self.namespace}Echo/feedback",
                                   value=echo_feedback))
        return SVMachineTrigs(trigs=trigs)

if __name__ == "__main__":
    pass
