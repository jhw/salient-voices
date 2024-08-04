from rv.modules.sampler import Sampler as RVSampler
from rv.note import NOTE as RVNOTE

from scipy.io import wavfile

import io
import warnings

warnings.simplefilter("ignore", wavfile.WavFileWarning)

MaxSlots = 120

"""
Sampler needs dedicated pool because can't afford to have duplicate samples, given limited number of slots
And duplicate slots can arise because two independently generated patches could utilise the same sample
Keys are used to provide an easy sample lookup mechanism
"""

class SVSamplerPool(list):

    def __init__(self, items = []):
        list.__init__(self, items)
        self.keys = []

    def add(self, sample):
        key = "%s/%s" % (sample["bank"],
                         sample["file"])
        if key not in self.keys:
            self.append(sample)
            self.keys.append(key)
            
class SVSampler(RVSampler):

    def __init__(self, banks, pool, maxslots = MaxSlots, *args, **kwargs):
        RVSampler.__init__(self, *args, **kwargs)
        if len(pool) > maxslots:
            raise RuntimeError("SVBankSampler max slots exceeded")
        self.pool = pool
        notes = list(RVNOTE)
        root = notes.index(RVNOTE.C5)
        for i, sample in enumerate(self.pool):
            self.note_samples[notes[i]] = i
            src = banks.get_wav_file(sample)
            self.load_sample(src, i)
            sv_sample = self.samples[i]
            sv_sample.relative_note += (root-i)
        
    """
    - https://github.com/metrasynth/gallery/blob/master/wicked.mmckpy#L497-L526
    """
        
    def load_sample(self, src, slot, **kwargs):
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
            1: RVSampler.Channels.mono,
            2: RVSampler.Channels.stereo,
        }[channels]
        sample.data = snd.data.tobytes()
        for key, value in kwargs.items():
            setattr(sample, key, value)
        self.samples[slot] = sample
        return sample

    def lookup(self, sample):
        key = "%s/%s" % (sample["bank"],
                         sample["file"])
        return self.pool.keys.index(key)

if __name__ == "__main__":
    pass
            
