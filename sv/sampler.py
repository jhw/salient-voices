from pydub import AudioSegment
from scipy.io import wavfile

from sv.sounds import SVSample

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

def with_audio_segment(fn):
    def wrapped(self, wav_io, start, cutoff, **kwargs):
        wav_io.seek(0)
        audio = AudioSegment.from_file(wav_io, format="wav")
        audio_out = fn(self, audio, start = start, cutoff = cutoff, **kwargs)
        wav_out = io.BytesIO()        
        audio_out.export(wav_out, format="wav")
        wav_out.seek(0)
        return wav_out
    return wrapped
    
class SVSlotSampler(SVBaseSampler):

    def __init__(self, banks, pool, root, max_slots=MaxSlots):
        SVBaseSampler.__init__(self, banks=banks, pool=pool)
        self.sample_strings = [str(sample) for sample in self.pool]
        rv_notes = list(rv.note.NOTE)                
        root = rv_notes.index(root)
        for i, sample in enumerate(self.pool):
            # init rv sample and insert into self.samples
            raw_wav_io = banks.get_wav(sample)
            wav_io = self.apply_fx(sample, raw_wav_io)
            rv_sample = self.init_rv_sample(wav_io)
            rv_sample.relative_note += (root + sample.note - i)
            self.samples[i] = rv_sample
            # bind rv sample to keyboard/note
            self.note_samples[rv_notes[i]] = i

    def apply_fx(self, sample, wav_io):
        sample_dict = sample.as_dict()
        if sample.fx == SVSample.FX.REV:
            return self.apply_reverse(wav_io, **sample_dict)
        elif sample.fx == SVSample.FX.RET2:
            return self.apply_retrig(wav_io, n_retrigs = 2, **sample_dict)
        elif sample.fx == SVSample.FX.RET4:
            return self.apply_retrig(wav_io, n_retrigs = 4, **sample_dict)
        elif sample.fx == SVSample.FX.RET8:
            return self.apply_retrig(wav_io, n_retrigs = 8, **sample_dict)
        elif sample.fx == SVSample.FX.RET16:
            return self.apply_retrig(wav_io, n_retrigs = 16, **sample_dict)
        else:
            return self.apply_trim(wav_io, **sample_dict)

    def trim_audio(self, audio, start, cutoff, fade_out = 3):
        return audio[start:cutoff].fade_out(fade_out)
        
    @with_audio_segment
    def apply_trim(self, audio, start, cutoff, **kwargs):
        return self.trim_audio(audio, start = start, cutoff = cutoff)
        
    @with_audio_segment
    def apply_reverse(self, audio, start, cutoff, **kwargs):
        return self.trim_audio(audio, start = start, cutoff = cutoff).reverse()

    @with_audio_segment
    def apply_retrig(self, audio, start, cutoff, n_retrigs, **kwargs):        
        trimmed_audio = self.trim_audio(audio, start = start, cutoff = cutoff)
        audio_duration = cutoff - start
        slice_duration = audio_duration // n_retrigs
        first_slice = trimmed_audio[:slice_duration]
        return first_slice * n_retrigs

    def index_of(self, sample):
        return self.sample_strings.index(str(sample))

if __name__ == "__main__":
    pass
