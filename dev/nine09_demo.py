from sv.algos.euclid import bjorklund

import random

class InstrumentBase:

    def play(self, generator, n):
        for trigs in generator(self, n):
            for trig in trigs:
                print (trig)

class Nine09(InstrumentBase):

    def __init__(self, sample):
        super().__init__()
        self.sample = sample

    def note(self, i):
        vel = random.choice([0.25, 0.5, 0.75, 1.0])
        return [{"i": i,
                 "sample": self.sample,
                 "vel": vel}]
            
def snare(self, n, steps = 16, pulses = 5):
    beats = bjorklund(steps = steps,
                      pulses = pulses)
    for i in range(n):
        j = i % steps
        if beats[j]:
            yield self.note(i = i)
        
if __name__ == "__main__":
    nine09 = Nine09(sample = "pico-default/29 HC.wav")
    nine09.play(snare, 32)


