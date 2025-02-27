from scipy.io import wavfile

import io
import warnings

import rv
import rv.modules

warnings.simplefilter("ignore", wavfile.WavFileWarning)

MaxSlots = 120

class SVSlotSampler(rv.modules.sampler.Sampler):

    def __init__(self, bank, pool, root, max_slots=MaxSlots):
        rv.modules.sampler.Sampler.__init__(self)
        if len(pool) > max_slots:
            raise RuntimeError("sampler max slots exceeded")
        self.sv_samples = samples = list(pool)
        rv_notes = list(rv.note.NOTE)                
        root = rv_notes.index(root)
        for i, sample in enumerate(samples):
            # init rv sample and insert into self.samples
            wav_io = bank.get_wav(sample)
            rv_sample = self.init_rv_sample(wav_io)
            rv_sample.relative_note += (root - i)
            self.rv_samples[i] = rv_sample
            # bind rv sample to keyboard/note
            self.note_samples[rv_notes[i]] = i

    @property
    def rv_samples(self):
        return self.samples
            
    """
    - https://github.com/metrasynth/gallery/blob/master/wicked.mmckpy#L497-L526
    """

    def init_rv_sample(self, wav_io):
        rv_sample = self.Sample()
        try:
            freq, snd = wavfile.read(wav_io)
        except ValueError as e:
            raise RuntimeError(f"Unsupported WAV file format: {e}")
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
    
    def index_of(self, sample):
        return self.sv_samples.index(sample)

if __name__ == "__main__":
    pass
