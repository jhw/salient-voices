from rv.modules.sampler import Sampler as RVSampler
from rv.note import NOTE as RVNOTE

from scipy.io import wavfile

import io
import warnings

warnings.simplefilter("ignore", wavfile.WavFileWarning)

MaxSlots = 120

class SVBaseSampler(RVSampler):

    def __init__(self, *args, **kwargs):
        RVSampler.__init__(self, *args, **kwargs)
        
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
        return self.pool.index(sample)
    
class SVSimpleSampler(SVBaseSampler):

    def __init__(self, banks, pool, *args, **kwargs):
        SVBaseSampler.__init__(self, *args, **kwargs)
        self.pool = pool
        notes = list(RVNOTE)
        for i, sample in enumerate(self.pool):
            self.note_samples[notes[i]] = i
            src = banks.get_wav_file(sample)
            self.load_sample(src, i)
    
class SVSlotSampler(SVBaseSampler):

    def __init__(self, banks, pool, max_slots = MaxSlots, root_note = RVNOTE.C5, *args, **kwargs):
        SVBaseSampler.__init__(self, *args, **kwargs)
        if len(pool) > max_slots:
            raise RuntimeError("SVBankSampler max slots exceeded")
        self.pool = pool
        notes = list(RVNOTE)
        root = notes.index(root_note)
        for i, sample in enumerate(self.pool):
            self.note_samples[notes[i]] = i
            src = banks.get_wav_file(sample)
            self.load_sample(src, i)
            sv_sample = self.samples[i]
            sv_sample.relative_note += (root-i)
        
if __name__ == "__main__":
    pass
            
