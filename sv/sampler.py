from pydub import AudioSegment
from scipy.io import wavfile

from sv.sample import SVSample

import io
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

def with_audio_segment(fn):
    def wrapped(self, wav_io, t, **kwargs):
        wav_io.seek(0)
        audio = AudioSegment.from_file(wav_io, format="wav")
        audio_out = fn(self, audio, t, **kwargs)
        wav_out = io.BytesIO()        
        audio_out.export(wav_out, format="wav")
        wav_out.seek(0)
        return wav_out
    return wrapped
    
class SVSlotSampler(SVBaseSampler):

    def __init__(self, banks, pool, root, cutoff, bpm, max_slots=MaxSlots):
        SVBaseSampler.__init__(self, banks=banks, pool=pool)
        self.sample_strings = [str(sample) for sample in self.pool]
        self.cutoff = cutoff
        rv_notes = list(rv.note.NOTE)                
        root = rv_notes.index(root)
        for i, sample in enumerate(self.pool):
            # init rv sample and insert into self.samples
            raw_wav_io = banks.get_wav(sample)
            wav_io = self.apply_fx(sample, raw_wav_io, bpm)
            rv_sample = self.init_rv_sample(wav_io)
            rv_sample.relative_note += (root + sample.note - i)
            self.samples[i] = rv_sample
            # bind rv sample to keyboard/note
            self.note_samples[rv_notes[i]] = i

    def apply_fx(self, sample, wav_io, bpm):
        t = int(1000 * self.cutoff * 60 / bpm)
        if sample.fx == SVSample.FX.REV:
            return self.apply_reverse(wav_io, t)
        elif sample.fx == SVSample.FX.RET2:
            return self.apply_retrig(wav_io, t, n = 2)
        elif sample.fx == SVSample.FX.RET4:
            return self.apply_retrig(wav_io, t, n = 4)
        elif sample.fx == SVSample.FX.RET8:
            return self.apply_retrig(wav_io, t, n = 8)
        elif sample.fx == SVSample.FX.RET16:
            return self.apply_retrig(wav_io, t, n = 16)
        else:
            return self.apply_trim(wav_io, t)

    @with_audio_segment
    def apply_trim(self, audio, t, **kwargs):
        trimmed_audio = audio[:t]
        return trimmed_audio
        
    @with_audio_segment
    def apply_reverse(self, audio, t, **kwargs):
        trimmed_audio = audio[:t]
        reversed_audio = trimmed_audio.reverse()
        return reversed_audio

    @with_audio_segment
    def apply_retrig(self, audio, t, n, **kwargs):
        trimmed_audio = audio[:t]        
        slice_duration = t // n
        first_slice = trimmed_audio[:slice_duration]
        retriggered_audio = first_slice * n
        return retriggered_audio

    def index_of(self, sample):
        return self.sample_strings.index(str(sample))

if __name__ == "__main__":
    pass
