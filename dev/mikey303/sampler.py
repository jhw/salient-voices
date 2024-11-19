from sv.sampler import SVBaseSampler, MaxSlots

import rv

"""
This sampler does no repicthing ie relies on RV sampler default behaviour
A single note is inserted at C5 and has chromatic variants on either side
Note no munging of RV sampler internals or repitching is done here (where is noyte_sample actually set in this case?)
"""

class SVSingleSlotDefaultSampler(SVBaseSampler):

    def __init__(self, banks, pool,
                 root_note = rv.note.NOTE.C5,
                 max_slots = MaxSlots):
        if len(pool) != 1:
            raise RuntimeError("SVChromaticSampler takes a single- sample pool only")
        SVBaseSampler.__init__(self,
                               banks = banks,
                               pool = pool)
        notes = list(rv.note.NOTE)
        for i, sample in enumerate(self.pool):
            self.note_samples[notes[i]] = i
            src = banks.get_wav(sample)
            self.load_sample(src, i)

    @property
    def root_notes(self, max_slots = MaxSlots):
        n = max_slots / len(self.pool)
        return {str(sample): int(n * (i + 0.5))
                for i, sample in enumerate(self.pool)}

    def index_of(self, sample):
        return self.root_notes[str(sample)]
    
if __name__ == "__main__":
    pass
            
