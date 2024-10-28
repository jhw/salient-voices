from sv.algos.euclid import bjorklund, TidalPatterns
from sv.model import SVNoteTrig, SVFXTrig

def class_name(self):
    return str(self.__class__).split("'")[1]

class EuclidSequencer:
    
    def __init__(self,
                 name,
                 params,
                 samples,
                 patterns = TidalPatterns,
                 **kwargs):
        self.name = name
        self.modulation = params["modulation"]
        self.density = params["density"]
        self.samples = samples
        self.patterns = patterns

    @property
    def params(self):
        return {"modulation": self.modulation,
                "density": self.density}
        
    def to_json(self):
        return {"class": class_name(self),
                "name": self.name,
                "params": self.params,
                "samples": self.samples}
                
    def random_pattern(self, rand):
        pulses, steps = rand["pattern"].choice(self.patterns)[:2] # because some of Tidal euclid rhythms have 3 parameters
        return bjorklund(pulses = pulses,
                         steps = steps)

    def switch_pattern(self, rand, i, temperature):
        return (0 == i % self.modulation["pattern"]["step"] and
                rand["pattern"].random() < self.modulation["pattern"]["threshold"] * temperature)

    def random_sample(self, rand):
        return rand["sample"].choice(self.samples)
        
    def switch_sample(self, rand, i, temperature):
        return (0 == i % self.modulation["sample"]["step"] and
                rand["sample"].random() < self.modulation["sample"]["threshold"] * temperature)

    def groove(self, rand, i, n = 5, var = 0.1, drift = 0.1):
        for j in range(n + 1):
            k = 2 ** (n - j)
            if 0 == i % k:
                sigma = rand.gauss(0, var)
                return 1 - max(0, min(1, j * drift + sigma))

    def __call__(self, rand, nticks, density, temperature, volume = 1.0, **kwargs):
        sample = self.random_sample(rand)
        pattern = self.random_pattern(rand)
        for i in range(nticks):
            if self.switch_sample(rand, i, temperature):
                sample = self.random_sample(rand)
            elif self.switch_pattern(rand, i, temperature):
                pattern = self.random_pattern(rand)
            beat = bool(pattern[i % len(pattern)])
            if rand["trig"].random() < (self.density * density) and beat:
                trigvol = self.groove(rand["volume"], i) * volume
                if trigvol > 0:
                    yield SVNoteTrig(mod = self.name,
                                     sample = sample,
                                     vel = trigvol,
                                     i = i)
                    
class SampleHoldModulator:
    
    def __init__(self,
                 name,
                 params,
                 **kwargs):
        self.name = name
        self.step = params["step"]
        self.range = params["range"]
        self.increment = params["increment"]

    @property
    def params(self):
        return {"step": self.step,
                "range": self.range,
                "increment": self.increment}
        
    def to_json(self):
        return {"class": class_name(self),
                "name": self.name,
                "params": self.params}
        
    def __call__(self,
                 rand,
                 nticks,
                 min_val = int('0000', 16),
                 max_val = int('8000', 16),
                 **kwargs):
        for i in range(nticks):
            v = self.sample_hold(rand, i)
            if v != None: # explicit because could return zero
                value = int(v * (max_val - min_val) + min_val)
                yield SVFXTrig(target = self.name,
                               value = value,
                               i = i)

    def sample_hold(self, rand, i):
        if 0 == i % self.step:
            floor, ceil = self.range
            v = floor + (ceil - floor) * rand["level"].random()
            return self.increment * int(0.5 + v / self.increment)

if __name__=="__main__":
    pass

