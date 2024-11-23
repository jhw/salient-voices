from pydub import AudioSegment
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

    def init_rv_sample(self, wav_io):
        rv_sample = self.Sample()
        freq, snd = wavfile.read(wav_io)
        if snd.dtype.name == 'int16':
            rv_sample.format = self.Format.int16
        elif snd.dtype.name == 'float32':
            rv_sample.format = self.Format.float32
        else:
            raise RuntimeError(f"dtype {snd.dtype.name} Not supported")
        if len(snd.shape) == 1:
            size, = snd.shape
            channels = 1
        else:
            size, channels = snd.shape
        rv_sample.rate = freq
        rv_sample.channels = {
            1: rv.modules.sampler.Sampler.Channels.mono,
            2: rv.modules.sampler.Sampler.Channels.stereo,
        }[channels]
        rv_sample.data = snd.data.tobytes()
        return rv_sample
    
class SVSlotSampler(SVBaseSampler):

    def __init__(self, banks, pool, root_note, bpm, max_slots=MaxSlots):
        SVBaseSampler.__init__(self, banks=banks, pool=pool)
        self.sample_strings = [str(sample) for sample in self.pool]
        rv_notes = list(rv.note.NOTE)                
        root = rv_notes.index(root_note)
        for i, sample in enumerate(self.pool):
            # init rv sample and insert into self.samples
            raw_wav_io = banks.get_wav(sample)
            if sample.fx :
                wav_io = self.apply_fx(sample, wav_io, 60 / bpm)
            else:
                wav_io = raw_wav_io
            rv_sample = self.init_rv_sample(wav_io)
            rv_sample.relative_note += (root + sample.note - i)
            self.samples[i] = rv_sample
            # bind rv sample to keyboard/note
            self.note_samples[rv_notes[i]] = i

    def apply_fx(self, sample, wav_io, t):
        if sample.fx == "rev":
            self.apply_rev(wav_io, t)
        elif sample.fx == "ret2":
            self.apply_ret(wav_io, t, n = 2)
        elif sample.fx == "ret4":
            self.apply_ret(wav_io, bpm, n = 4)
        else:
            raise RuntimeError(f"fx {sample.fx} not supported")

    def apply_rev(wav_io, t):
        pass

    def apply_ret(wav_io, bpm, t):
        pass

    def index_of(self, sample):
        return self.sample_strings.index(str(sample))

if __name__ == "__main__":
    pass
