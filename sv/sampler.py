from scipy.io import wavfile

import io
import os
import re
# import rv
import rv.modules # why?
import warnings
import zipfile

warnings.simplefilter("ignore", wavfile.WavFileWarning)

MaxSlots = 120

class SVSample(str):

    @staticmethod
    def create(bank_name, file_name, tags):
        tag_string = "".join([f"#{tag}" for tag in sorted(tags)])
        return SVSample(f"{bank_name}/{file_name}{tag_string}")
    
    def __init__(self, value = ""):
        # str.__init__(self, value)
        str.__init__(value)

    @property
    def tokens(self):
        return re.split("\\/|\\#", self)

    @property
    def bank_name(self):
        return self.tokens[0]

    @property
    def file_path(self):
        return self.tokens[1]

    @property
    def tags(self):
        return self.tokens[2:]
                    
class SVBaseSampler(rv.modules.sampler.Sampler):

    def __init__(self, banks, pool,
                 max_slots = MaxSlots):
        rv.modules.sampler.Sampler.__init__(self)
        if len(pool) > max_slots:
            raise RuntimeError("sampler max slots exceeded")
        self.pool = pool
        notes = list(rv.note.NOTE)
        for i, sample in enumerate(self.pool):
            self.note_samples[notes[i]] = i
            src = banks.get_wav(sample)
            self.load_sample(src, i)
        
    """
    - https://github.com/metrasynth/gallery/blob/master/wicked.mmckpy#L497-L526
    """
        
    def load_sample(self, src, slot):
        sample = self.Sample()
        freq, snd = wavfile.read(src)
        if snd.dtype.name == 'int16':
            sample.format = self.Format.int16
        elif snd.dtype.name == 'float32':
            sample.format = self.Format.float32
        else:
            raise RuntimeError("dtype %s Not supported" % snd.dtype.name)
        if len(snd.shape) == 1:
            size, = snd.shape
            channels = 1
        else:
            size, channels = snd.shape
        sample.rate = freq
        sample.channels = {
            1: rv.modules.sampler.Sampler.Channels.mono,
            2: rv.modules.sampler.Sampler.Channels.stereo,
        }[channels]
        sample.data = snd.data.tobytes()
        self.samples[slot] = sample
        return sample

    @property
    def root_notes(self):
        return {}
            
    def index_of(self, sample):
        return self.root_notes[sample]

class SVSlotSampler(SVBaseSampler):

    def __init__(self, banks, pool,
                 root_note = rv.note.NOTE.C5,
                 max_slots = MaxSlots):
        SVBaseSampler.__init__(self,
                               banks = banks,
                               pool = pool)
        notes = list(rv.note.NOTE)
        root = notes.index(root_note)
        for i, sample in enumerate(self.pool):
            sv_sample = self.samples[i]
            sv_sample.relative_note += (root-i)

    @property
    def root_notes(self):
        return {sample: i
                for i, sample in enumerate(self.pool)}    

"""
Simply can't be bothered doing all the repitch work for Chromatic sampler
The uses cases are either many- slot/unchromatic (SVSlotSampler) or single- slot/chromatic (SVChromaticSampler); there is no (eg) dual- slot/chromatic use case
So simplest to raise exception if more than a single sample passed, and then rely on SVBaseSampler default chromatic behaviour which pitches the (chromatic) mid- point at C5 
Althiough some kind of offset behaviour might be useful in the future
"""
    
class SVChromaticSampler(SVBaseSampler):

    def __init__(self, banks, pool,
                 root_note = rv.note.NOTE.C5,
                 max_slots = MaxSlots):
        if len(pool) != 1:
            raise RuntimeError("SVChromaticSampler takes a single- sample pool only")
        SVBaseSampler.__init__(self,
                               banks = banks,
                               pool = pool)

    """
    This technically works for multiple notes but RuntimeError raise above should ensure there is only ever one
    """
        
    @property
    def root_notes(self, max_slots = MaxSlots):
        n = max_slots / len(self.pool)
        return {sample: int(n * (i + 0.5))
                for i, sample in enumerate(self.pool)}
        
if __name__ == "__main__":
    pass
            
