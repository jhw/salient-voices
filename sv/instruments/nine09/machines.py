from sv.algos.euclid import bjorklund, TidalPatterns
from sv.model import SVNoteTrig, SVFXTrig

import copy
import random

def random_seed():
    return int(1e8*random.random())

def Q(seed):
    q = random.Random()
    q.seed(seed)
    return q

class EuclidSequencer:
    
    def __init__(self,
                 name,
                 tag,
                 params,
                 samples = None,
                 seeds = None,
                 patterns = TidalPatterns,
                 **kwargs):
        self.name = name
        self.tag = tag
        self.modulation = params["modulation"]
        self.density = params["density"]
        self.nsamples = params["nsamples"]
        self.samples = samples
        self.seeds = seeds
        self.patterns = patterns

    @property
    def params(self):
        return {"modulation": self.modulation,
                "density": self.density,
                "nsamples": self.nsamples}

    def randomise(self, pool, mapping, **kwargs):
        sample_pool = pool.filter_by_tag(mapping[self.tag])
        self.samples = [random.choice(sample_pool)
                        for i in range(self.nsamples)]
        self.seeds = {k:random_seed()
                      for k in "sample|trig|pattern|volume".split("|")}
        
    def clone(self):
        return EuclidSequencer(name = self.name,
                               tag = self.tag,
                               params = copy.deepcopy(self.params),
                               samples = copy.deepcopy(self.samples),
                               seeds = copy.deepcopy(self.seeds))

    def random_pattern(self, q):
        pulses, steps = q["pattern"].choice(self.patterns)[:2] # because some of Tidal euclid rhythms have 3 parameters
        return bjorklund(pulses = pulses,
                         steps = steps)

    def switch_pattern(self, q, i, temperature):
        return (0 == i % self.modulation["pattern"]["step"] and
                q["pattern"].random() < self.modulation["pattern"]["threshold"] * temperature)

    def random_sample(self, q):
        return q["sample"].choice(self.samples)
        
    def switch_sample(self, q, i, temperature):
        return (0 == i % self.modulation["sample"]["step"] and
                q["sample"].random() < self.modulation["sample"]["threshold"] * temperature)

    def groove(self, q, i, n = 5, var = 0.1, drift = 0.1):
        for j in range(n + 1):
            k = 2 ** (n - j)
            if 0 == i % k:
                sigma = q.gauss(0, var)
                return 1 - max(0, min(1, j * drift + sigma))

    """
    volume used for muting
    muting needs to be volume based in avoid messing with seeds (trig order would be messed up if you simply deleted trigs
    """
    
    def render(self, n_ticks, density, temperature, volume = 1.0, **kwargs):
        q = {k:Q(v) for k, v in self.seeds.items()}
        sample, pattern = (self.random_sample(q),
                           self.random_pattern(q))
        for i in range(n_ticks):
            if self.switch_sample(q, i, temperature):
                sample = self.random_sample(q)
            elif self.switch_pattern(q, i, temperature):
                pattern = self.random_pattern(q)
            beat = bool(pattern[i % len(pattern)])
            if q["trig"].random() < (self.density * density) and beat:
                trigvol = self.groove(q["volume"], i) * volume
                if trigvol > 0:
                    yield SVNoteTrig(mod = self.name,
                                     sample = sample,
                                     vel = trigvol,
                                     i = i)
                    
class SampleHoldModulator:
    
    def __init__(self,
                 name,
                 params,
                 seeds = None,
                 **kwargs):
        self.name = name
        self.step = params["step"]
        self.range = params["range"]
        self.increment = params["increment"]
        self.seeds = seeds

    @property
    def params(self):
        return {"step": self.step,
                "range": self.range,
                "increment": self.increment}

    def randomise(self, **kwargs):
        self.seeds = {"level": random_seed()}

    def clone(self):
        return SampleHoldModulator(name = self.name,
                                   params = copy.deepcopy(self.params),
                                   seeds = copy.deepcopy(self.seeds))

    def render(self,
               n_ticks,
               min_value = '0000',
               max_value = '8000',
               **kwargs):
        min_val, max_val = (int(min_value, 16),
                            int(max_value, 16))
        q = Q(self.seeds["level"])
        for i in range(n_ticks):
            v = self.sample_hold(q, i)
            if v != None: # explicit because could return zero
                value = int(v * (max_val - min_val) + min_val)
                yield SVFXTrig(target = self.name,
                               value = value,
                               i = i)

    def sample_hold(self, q, i):
        if 0 == i % self.step:
            floor, ceil = self.range
            v = floor + (ceil - floor) * q.random()
            return self.increment * int(0.5 + v / self.increment)

if __name__=="__main__":
    pass

