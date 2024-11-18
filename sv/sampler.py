from scipy.io import wavfile

import re
# import rv
import rv.modules # why?
import warnings

warnings.simplefilter("ignore", wavfile.WavFileWarning)

MaxSlots = 120

class SVSampleRef(dict):

    @staticmethod
    def parse(sample_str):
        tokens = re.split("\\/|\\#", sample_str)
        return SVSampleRef(bank_name = tokens[0],
                           file_path = tokens[1],
                           tags = tokens[2:])
    
    def __init__(self, bank_name, file_path, tags = []):
        dict.__init__(self)
        self["bank_name"] = bank_name
        self["file_path"] = file_path
        self["tags"] = tags

    @property
    def bank_name(self):
        return self["bank_name"]

    @property
    def file_path(self):
        return self["file_path"]

    @property
    def tags(self):
        return self["tags"]

    """
    - required by Sampler for sample index lookup
    """
    
    def __str__(self):
        tag_string = "".join([f"#{tag}" for tag in sorted(self.tags)])
        return f"{self.bank_name}/{self.file_path}{tag_string}"

class SVBaseSampler(rv.modules.sampler.Sampler):

    def __init__(self, banks, pool,
                 max_slots = MaxSlots):
        rv.modules.sampler.Sampler.__init__(self)
        if len(pool) > max_slots:
            raise RuntimeError("sampler max slots exceeded")
        self.pool = pool
        
    """
    - https://github.com/metrasynth/gallery/blob/master/wicked.mmckpy#L497-L526
    """
        
    def load_sample(self, src, i):
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
        self.samples[i] = sample
        return sample

class SVSlotSampler(SVBaseSampler):

    """
    class Sampler:
        self.note_samples = self.NoteSampleMap()
        self.samples = [None] * 128
    class Sampler.Sample:
        self.relative_note = 16
    """
    
    def __init__(self, banks, pool, root_note,
                 max_slots = MaxSlots):
        SVBaseSampler.__init__(self,
                               banks = banks,
                               pool = pool)
        notes = list(rv.note.NOTE)
        root = notes.index(root_note)
        for i, sample in enumerate(self.pool):
            # insert sample into slot
            self.note_samples[notes[i]] = i
            src = banks.get_wav(sample)
            self.load_sample(src, i)
            # remap pitch
            sample = self.samples[i]
            sample.relative_note += (root-i)

    def index_of(self, sample):
        sample_strings = [str(sample) for sample in self.pool]
        return sample_strings.index(str(sample))

if __name__ == "__main__":
    pass
            
