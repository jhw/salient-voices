from sv.utils.urlparse import parse_url

from pydub import AudioSegment
from scipy.io import wavfile

import io
import rv
import rv.modules
import warnings

warnings.simplefilter("ignore", wavfile.WavFileWarning)

MaxSlots = 120

def with_audio_segment(fn):
    def wrapped(self, wav_io, cutoff, **kwargs):
        wav_io.seek(0)
        audio = AudioSegment.from_file(wav_io, format="wav")
        audio_out = fn(self, audio, cutoff, **kwargs)
        wav_out = io.BytesIO()        
        audio_out.export(wav_out, format="wav")
        wav_out.seek(0)
        return wav_out
    return wrapped

class SVSlotSampler(rv.modules.sampler.Sampler):

    def __init__(self, bank, pool, root, max_slots=MaxSlots):
        rv.modules.sampler.Sampler.__init__(self)
        if len(pool) > max_slots:
            raise RuntimeError("sampler max slots exceeded")
        self.sample_strings = list(pool)
        rv_notes = list(rv.note.NOTE)                
        root = rv_notes.index(root)
        for i, sample_string in enumerate(self.sample_strings):
            sample, params = self.parse_sample_string(sample_string)
            # init rv sample and insert into self.samples
            raw_wav_io = bank.get_wav(sample)
            wav_io = self.apply_cutoff(wav_io = raw_wav_io,
                                       cutoff = params["cutoff"])
            rv_sample = self.init_rv_sample(wav_io)
            rv_sample.relative_note += (root + params["pitch"] - i)
            self.samples[i] = rv_sample
            # bind rv sample to keyboard/note
            self.note_samples[rv_notes[i]] = i
            
    def parse_sample_string(self, sample_string,
                            defaults = {"pitch": 0,
                                        "cutoff": 500}): # 4 ticks @ 120 bpm
        sample, params = parse_url(sample_string)
        for k, v in defaults.items():
            params.setdefault(k, v)
        return (sample, params)

    @with_audio_segment
    def apply_cutoff(self, audio, cutoff, fade_out = 3):
        return audio[:cutoff].fade_out(fade_out)
        
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
    
    def index_of(self, sample_string):
        return self.sample_strings.index(sample_string)

if __name__ == "__main__":
    pass
