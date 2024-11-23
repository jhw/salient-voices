from enum import Enum
from scipy.io import wavfile
from urllib.parse import parse_qs

import re
# import rv
import rv.modules  # why?
import warnings

warnings.simplefilter("ignore", wavfile.WavFileWarning)

MaxSlots = 120

class SVSampleRef(dict):

    class FX(Enum):
        REV = "rev"
        RET2 = "ret2"
        RET4 = "ret4"

    @staticmethod
    def parse(sample_str):
        if not sample_str:
            raise RuntimeError("Input string cannot be empty")
        
        # Split tags first
        tag_split = sample_str.split("#")
        sample_and_qs = tag_split[0]
        tags = tag_split[1:] if len(tag_split) > 1 else []

        # Parse bank_name, file_path, and query string
        path_and_query = sample_and_qs.split("?")
        path = path_and_query[0]
        query_string = path_and_query[1] if len(path_and_query) > 1 else ""

        # Extract bank_name and file_path
        tokens = path.split("/", 1)
        if len(tokens) < 2 or not tokens[0]:
            raise RuntimeError("Bank name cannot be empty")
        bank_name = tokens[0]
        file_path = tokens[1] if len(tokens) > 1 else ""

        # Parse query string into a dictionary
        query_dict = parse_qs(query_string)
        try:
            note = int(query_dict.get("note", [0])[0])  # Default note to 0 if not provided
        except ValueError:
            note = 0

        fx_value = query_dict.get("fx", [None])[0]
        fx = SVSampleRef.FX(fx_value) if fx_value in SVSampleRef.FX._value2member_map_ else None

        return SVSampleRef(
            bank_name=bank_name,
            file_path=file_path,
            note=note,
            fx=fx,
            tags=tags
        )

    def __init__(self, bank_name, file_path, note=0, fx=None, tags=None):
        dict.__init__(self)
        self["bank_name"] = bank_name
        self["file_path"] = file_path
        self["note"] = note
        self["fx"] = fx
        self["tags"] = tags or []

    def clone(self):
        return SVSampleRef(
            bank_name=self.bank_name,
            file_path=self.file_path,
            note=self.note,
            fx=self.fx,
            tags=list(self.tags)
        )
        
    @property
    def bank_name(self):
        return self["bank_name"]

    @property
    def file_path(self):
        return self["file_path"]

    @property
    def note(self):
        return self["note"]

    @note.setter
    def note(self, value):
        self["note"] = value

    @property
    def fx(self):
        return self["fx"]

    @fx.setter
    def fx(self, value):
        if value is not None and not isinstance(value, SVSampleRef.FX):
            raise ValueError(f"fx must be an instance of SVSampleRef.FX or None, got {value}")
        self["fx"] = value

    @property
    def querystring(self):
        qs = {"note": self["note"]}
        if self["fx"] is not None:
            qs["fx"] = self["fx"].value
        return qs

    @property
    def tags(self):
        return self["tags"]

    def __str__(self):
        query_parts = [
            f"{key}={value}" for key, value in self.querystring.items() if not (key == "note" and value == 0)
        ]
        query_string = "?" + "&".join(query_parts) if query_parts else ""
        tag_string = "".join([f"#{tag}" for tag in sorted(self.tags)])
        return f"{self.bank_name}/{self.file_path}{query_string}{tag_string}"
    
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
