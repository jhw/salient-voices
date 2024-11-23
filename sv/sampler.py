from scipy.io import wavfile

import rv
import rv.modules
import warnings

warnings.simplefilter("ignore", wavfile.WavFileWarning)

MaxSlots = 120
    
class SVBaseSampler(rv.modules.sampler.Sampler):

    def __init__(self, banks, pool, max_slots=MaxSlots):
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
            raise RuntimeError(f"dtype {snd.dtype.name} Not supported")
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

    def __init__(self, banks, pool, root_note, bpm, max_slots=MaxSlots):
        SVBaseSampler.__init__(self, banks=banks, pool=pool)
        notes = list(rv.note.NOTE)
        root = notes.index(root_note)
        self.sample_strings = [str(sample) for sample in self.pool]
        for i, sample in enumerate(self.pool):
            # Insert sample into slot
            self.note_samples[notes[i]] = i
            src = banks.get_wav(sample)
            self.load_sample(src, i)
            # Remap pitch
            self.samples[i].relative_note += (root + sample.note - i)

    def index_of(self, sample):
        return self.sample_strings.index(str(sample))

if __name__ == "__main__":
    pass
