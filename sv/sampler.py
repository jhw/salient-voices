from scipy.io import wavfile

# import rv
import rv.modules # why?
import warnings
import zipfile

warnings.simplefilter("ignore", wavfile.WavFileWarning)

MaxSlots = 120

class SVBank:

    def __init__(self, name, zip_buffer):
        self.name = name
        self.zip_buffer = zip_buffer

    @property
    def zip_file(self): # assume zip_buffer.seek(0) has been called elsewhere
        return zipfile.ZipFile(self.zip_buffer, 'r')

class SVBanks(dict):

    def __init__(self, item = []):
        dict.__init__(self, item)

    def get_wav_file(self, sample):
        bank_name, file_path = sample.split("/")
        if bank_name not in self:
            raise RuntimeError(f"bank {bank_name} not found")
        file_paths = self[bank_name].zip_file.namelist()
        if file_path not in file_paths:
            raise RuntimeError(f"path {file_path} not found in bank {bank_name}")
        return self[bank_name].zip_file.open(file_path, 'r')
        
class SVPool(list):

    def __init__(self, items = []):
        list.__init__(self, items)

    def add(self, sample):
        if sample not in self:
            self.append(sample)
        
class SVBaseSampler(rv.modules.sampler.Sampler):

    def __init__(self, *args, **kwargs):
        rv.modules.sampler.Sampler.__init__(self, *args, **kwargs)
        
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
            1: rv.modules.sampler.Sampler.Channels.mono,
            2: rv.modules.sampler.Sampler.Channels.stereo,
        }[channels]
        sample.data = snd.data.tobytes()
        for key, value in kwargs.items():
            setattr(sample, key, value)
        self.samples[slot] = sample
        return sample

    def lookup(self, sample):
        return self.pool.index(sample)

"""
SVSingleSlotSampler uses default sunvox sampler's chromatic implementation and thus should only accept a single sample for safety
"""
    
class SVSingleSlotSampler(SVBaseSampler):

    def __init__(self, banks, pool,
                 *args, **kwargs):
        SVBaseSampler.__init__(self, *args, **kwargs)
        if len(pool) > 1:
            raise RuntimeError("SVSingleSlotSampler can only accept a single sample")
        self.pool = pool
        notes = list(rv.note.NOTE)
        for i, sample in enumerate(self.pool):
            self.note_samples[notes[i]] = i
            src = banks.get_wav_file(sample)
            self.load_sample(src, i)

"""
SVMultiSlotSampler accepts multiple samples and must then rebase the pitch on all of them so that input pitch is rendered
SVMultiSlotSampler is thus non- chromatic due to the above, although slots between len(pool) and MaxSlots contain the default chromatic implementation
"""
            
class SVMultiSlotSampler(SVBaseSampler):

    def __init__(self, banks, pool,
                 max_slots = MaxSlots,
                 root_note = rv.note.NOTE.C5,
                 *args, **kwargs):
        SVBaseSampler.__init__(self, *args, **kwargs)
        if len(pool) > max_slots:
            raise RuntimeError("SVMultiSlotSampler max slots exceeded")
        self.pool = pool
        notes = list(rv.note.NOTE)
        root = notes.index(root_note)
        for i, sample in enumerate(self.pool):
            self.note_samples[notes[i]] = i
            src = banks.get_wav_file(sample)
            self.load_sample(src, i)
            sv_sample = self.samples[i]
            sv_sample.relative_note += (root-i)
        
if __name__ == "__main__":
    pass
            
