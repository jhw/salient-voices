from scipy.io import wavfile

# import rv
import rv.modules # why?
import warnings

warnings.simplefilter("ignore", wavfile.WavFileWarning)

MaxSlots = 120
                    
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

    def __init__(self, banks, pool, root_note,
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
        
if __name__ == "__main__":
    pass
            
