from sv.sampler import SVSample

import io
import os
import re
import zipfile

class SVBank:

    @staticmethod
    def load_wav_files(bank_name, dir_path,
                       filter_fn = lambda x: x.endswith(".wav")):
        zip_buffer = io.BytesIO()
        zip_file = zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False)
        for file_name in os.listdir(dir_path):
            if filter_fn(file_name):
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
    
    @staticmethod
    def load_zip_file(zip_path):
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
    def zip_file(self):
        return zipfile.ZipFile(self.zip_buffer, 'r')

    def join(self, bank):
        bank_zip_file = bank.zip_file
        zip_buffer_temp = io.BytesIO(self.zip_buffer.getvalue())
        with zipfile.ZipFile(zip_buffer_temp, 'a', zipfile.ZIP_DEFLATED) as zip_file:
            for item in bank_zip_file.infolist():
                wav_data = bank_zip_file.read(item.filename)
                zip_file.writestr(item.filename, wav_data)
        self.zip_buffer = zip_buffer_temp
        self.zip_buffer.seek(0)
        return self

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
            
if __name__ == "__main__":
    pass
            