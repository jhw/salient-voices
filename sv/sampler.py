from scipy.io import wavfile

import io
import os
import re
# import rv
import rv.modules # why?
import warnings
import zipfile

warnings.simplefilter("ignore", wavfile.WavFileWarning)

MaxSlots = 120

class SVSample(str):

    def __init__(self, value = ""):
        # str.__init__(self, value)
        str.__init__(value)

    @property
    def tokens(self):
        return re.split("\\/|\\#", self)

    @property
    def bank_name(self):
        return self.tokens[0]

    @property
    def file_path(self):
        return self.tokens[1]

    @property
    def tags(self):
        return self.tokens[2:]
        
class SVBank:

    @classmethod
    def load_files(self, bank_name, dir_path, ext = ".wav"):
        zip_buffer = io.BytesIO()
        zip_file = zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False)
        for file_name in os.listdir(dir_path):
            if file_name.endswith(ext):
                file_path = f"{dir_path}/{file_name}"
                wav_data = None
                with open(file_path, 'rb') as wav_file:
                    wav_data = wav_file.read()
                if not wav_data:
                    raise RuntimeError(f"couldn't load {file_path}")
                zip_file.writestr(file_name, wav_data)
        zip_buffer.seek(0)
        return SVBank(name = bank_name,
                      zip_buffer = zip_buffer)
    
    @classmethod
    def load_zip_file(self, zip_path):
        bank_name = zip_path.split("/")[-1].split(".")[0]
        zip_buffer = io.BytesIO()
        with open(zip_path, 'rb') as f:
            zip_buffer.write(f.read())
        zip_buffer.seek(0)
        return SVBank(name = bank_name,
                      zip_buffer = zip_buffer)
    
    def __init__(self, name, zip_buffer):
        self.name = name
        self.zip_buffer = zip_buffer

    @property
    def zip_file(self): # assume zip_buffer.seek(0) has been called elsewhere
        return zipfile.ZipFile(self.zip_buffer, 'r')

    def dump_zip_file(self, dir_path):
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        zip_path = f"{dir_path}/{self.name}.zip"
        with open(zip_path, 'wb') as f:
            f.write(self.zip_buffer.getvalue())    
    
class SVBanks(list):

    def __init__(self, items = []):
        list.__init__(self, items)

    def spawn_pool(self, tag_mapping):
        def filter_tags(file_name, tag_mapping):
            tags = []
            for tag, term in tag_mapping.items():
                if re.search(term, file_name, re.I):
                    tags.append(tag)
            return tags        
        pool, untagged = SVPool(), []
        for bank in self:
            for item in bank.zip_file.infolist():
                wav_file = item.filename
                tags = filter_tags(wav_file, tag_mapping)
                tag_string = "".join([f"#{tag}" for tag in tags])
                sample = f"{bank.name}/{wav_file}{tag_string}"
                if tags != []:
                    pool.append(sample)
                else:
                    untagged.append(sample)
        return pool, untagged
        
    def get_wav_file(self, sample):
        bank_name = SVSample(sample).bank_name
        file_path = SVSample(sample).file_path
        banks = {bank.name: bank for bank in self}
        if bank_name not in banks:
            raise RuntimeError(f"bank {bank_name} not found")
        file_paths = banks[bank_name].zip_file.namelist()
        if file_path not in file_paths:
            raise RuntimeError(f"path {file_path} not found in bank {bank_name}")
        return banks[bank_name].zip_file.open(file_path, 'r')
        
class SVPool(list):

    def __init__(self, items = []):
        list.__init__(self, items)

    def add(self, sample):
        if sample not in self:
            self.append(sample)

    @property
    def tags(self):
        tags = {}
        for sample in self:
            for tag in SVSample(sample).tags:
                tags.setdefault(tag, 0)
                tags[tag] += 1
        return tags
        
    def filter_by_tag(self, tag):
        return [sample for sample in self
                if tag in SVSample(sample).tags]
            
class SVBaseSampler(rv.modules.sampler.Sampler):

    def __init__(self, banks, pool,
                 repitch = True,
                 max_slots = MaxSlots,
                 root_note = rv.note.NOTE.C5):
        rv.modules.sampler.Sampler.__init__(self)
        if len(pool) > max_slots:
            raise RuntimeError("sampler max slots exceeded")
        self.pool = pool
        notes = list(rv.note.NOTE)
        root = notes.index(root_note)
        for i, sample in enumerate(self.pool):
            self.note_samples[notes[i]] = i
            src = banks.get_wav_file(sample)
            self.load_sample(src, i)
            if repitch:
                sv_sample = self.samples[i]
                sv_sample.relative_note += (root-i)
        
    """
    - https://github.com/metrasynth/gallery/blob/master/wicked.mmckpy#L497-L526
    """
        
    def load_sample(self, src, slot):
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
        self.samples[slot] = sample
        return sample

    @property
    def root_notes(self):
        return {}
            
    def index_of(self, sample):
        return self.root_notes[sample]

class SVSlotSampler(SVBaseSampler):

    def __init__(self, banks, pool):
        SVBaseSampler.__init__(self,
                               banks = banks,
                               pool = pool,
                               repitch = True)

    @property
    def root_notes(self):
        return {sample: i
                for i, sample in enumerate(self.pool)}    
        
class SVChromaticSampler(SVBaseSampler):

    def __init__(self, banks, pool):
        SVBaseSampler.__init__(self,
                               banks = banks,
                               pool = pool,
                               repitch = False)

    """
    This is how is is *assumed* to work, but needs checking
    """
        
    @property
    def root_notes(self, max_slots = MaxSlots):
        n = max_slots / len(self.pool)
        return {sample: int(n * (i + 0.5))
                for i, sample in enumerate(self.pool)}
        
if __name__ == "__main__":
    pass
            
