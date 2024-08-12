import random

class InstrumentBase:

    def play(self, generator, n):
        for trigs in generator(self, n):
            for trig in trigs:
                print (trig)

class Three03(InstrumentBase):

    def __init__(self, sample):
        super().__init__()
        self.sample = sample

    def note(self, i, note, length):
        return [{"i": i,
                 "sample": self.sample,
                 "note": note},
                {"i": i + length,
                 "note": None}]
            
def bassline(self, n, root_note = 56):
    last = -1 
    for i in range(n):
        if (random.random() < 1/3 and
            i > last):
            length = random.choice([1, 2, 3])
            note = root_note + random.choice([-2, 0, 5, 12])
            last = i + length
            yield self.note(i = i,
                            note = note,
                            length = length)
            
if __name__ == "__main__":
    three03 = Three03(sample = "mikey303/303 VCO SQR.wav")
    three03.play(bassline, 32)

