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

    def init_rv_sample(self, src):
        rv_sample = self.Sample()
        freq, buf = wavfile.read(src)
        if buf.dtype.name == 'int16':
            rv_sample.format = self.Format.int16
        elif buf.dtype.name == 'float32':
            rv_sample.format = self.Format.float32
        else:
            raise RuntimeError(f"dtype {buf.dtype.name} Not supported")
        if len(buf.shape) == 1:
            size, = buf.shape
            channels = 1
        else:
            size, channels = buf.shape
        rv_sample.rate = freq
        rv_sample.channels = {
            1: rv.modules.sampler.Sampler.Channels.mono,
            2: rv.modules.sampler.Sampler.Channels.stereo,
        }[channels]
        rv_sample.data = buf.data.tobytes()
        return rv_sample

class SVSlotSampler(SVBaseSampler):

    def __init__(self, banks, pool, root_note, bpm, max_slots=MaxSlots):
        SVBaseSampler.__init__(self, banks=banks, pool=pool)
        self.sample_strings = [str(sample) for sample in self.pool]
        rv_notes = list(rv.note.NOTE)                
        root = rv_notes.index(root_note)
        for i, sample in enumerate(self.pool):
            # init rv sample and insert into self.samples
            src = banks.get_wav(sample)
            rv_sample = self.init_rv_sample(src)
            rv_sample.relative_note += (root + sample.note - i)
            self.samples[i] = rv_sample
            # bind rv sample to keyboard/note
            self.note_samples[rv_notes[i]] = i

    def index_of(self, sample):
        return self.sample_strings.index(str(sample))

if __name__ == "__main__":
    pass
