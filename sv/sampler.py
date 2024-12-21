from scipy.io import wavfile

import io
import rv
import rv.modules
import warnings

warnings.simplefilter("ignore", wavfile.WavFileWarning)

MaxSlots = 120
    
class SVBaseSampler(rv.modules.sampler.Sampler):

    def __init__(self, bank, pool, max_slots=MaxSlots):
        rv.modules.sampler.Sampler.__init__(self)
        if len(pool) > max_slots:
            raise RuntimeError("sampler max slots exceeded")
        self.pool = list(pool) # NB pool is set- based and needs converting to a list for indexation into by index_of()

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

class SVSlotSampler(SVBaseSampler):

    def __init__(self, bank, pool, root, max_slots=MaxSlots):
        SVBaseSampler.__init__(self, bank=bank, pool=pool)
        rv_notes = list(rv.note.NOTE)                
        root = rv_notes.index(root)
        for i, note_adjusted_sample in enumerate(self.pool):
            sample, relative_note = self.parse_sample(note_adjusted_sample)
            relative_note = int(relative_note)
            # init rv sample and insert into self.samples
            wav_io = bank.get_wav(sample)
            rv_sample = self.init_rv_sample(wav_io)
            rv_sample.relative_note += (root + relative_note - i)
            self.samples[i] = rv_sample
            # bind rv sample to keyboard/note
            self.note_samples[rv_notes[i]] = i

    def parse_sample(self, note_adjusted_sample):
        tokens = note_adjusted_sample.split("#")
        return (tokens[0], int(tokens[1])) if len(tokens) > 1 else (tokens[0], 0)

    def index_of(self, note_adjusted_sample):
        return self.pool.index(note_adjusted_sample)

if __name__ == "__main__":
    pass
