from sv.sampler import SVSample

import io
import os
import re
import zipfile

class SVBank:
    
    @staticmethod
    def load_zip(zip_path):
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

    def subset(self, name, file_list):
        subset_buffer = io.BytesIO()
        with zipfile.ZipFile(subset_buffer, 'w') as subset_zip:
            for item in self.zip_file.infolist():
                if item.filename in file_list:
                    with self.zip_file.open(item, 'r') as source_file:
                        subset_zip.writestr(item.filename, source_file.read())
        subset_buffer.seek(0)
        return SVBank(name = name,
                      zip_buffer = subset_buffer)
    
    def dump_zip(self, dir_path):
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        zip_path = f"{dir_path}/{self.name}.zip"
        with open(zip_path, 'wb') as f:
            f.write(self.zip_buffer.getvalue())    
    
class SVBanks(list):

    @staticmethod
    def load_zip(cache_dir = "tmp/banks",
                 filter_fn = lambda x: x.endswith(".zip")):
        banks = SVBanks()
        for file_name in os.listdir(cache_dir):
            if filter_fn(file_name):
                zip_path = f"{cache_dir}/{file_name}"
                bank = SVBank.load_zip(zip_path)
                banks.append(bank)
        return banks
    
    def __init__(self, items = []):
        list.__init__(self, items)

    def match_tags(self, file_name, tag_mapping):
        tags = []
        for tag, term in tag_mapping.items():
            if re.search(term, file_name, re.I):
                tags.append(tag)
        return tags        
        
    def spawn_pool(self, tag_mapping):
        pool, untagged = SVPool(), []
        for bank in self:
            for item in bank.zip_file.infolist():
                tags = self.match_tags(item.filename, tag_mapping)
                sample = SVSample.create(bank_name = bank.name,
                                         file_name = item.filename,
                                         tags = tags)
                if tags != []:
                    pool.append(sample)
                else:
                    untagged.append(sample)
        return pool, untagged
        
    def get_wav(self, sample):
        banks = {bank.name: bank for bank in self}
        sample = SVSample(sample)
        if sample.bank_name not in banks:
            raise RuntimeError(f"bank {bank_name} not found")
        file_paths = banks[sample.bank_name].zip_file.namelist()
        if sample.file_path not in file_paths:
            raise RuntimeError(f"path {file_path} not found in bank {bank_name}")
        return banks[sample.bank_name].zip_file.open(sample.file_path, 'r')
        
class SVPool(list):

    def __init__(self, items = []):
        list.__init__(self, items)

    def add(self, sample):
        if sample not in self:
            self.append(sample)

    """
    @property
    def tags(self):
        tags = {}
        for sample in self:
            for tag in SVSample(sample).tags:
                tags.setdefault(tag, 0)
                tags[tag] += 1
        return tags
    """
        
    def match(self, tag):
        return [sample for sample in self
                if tag in SVSample(sample).tags]
            
if __name__ == "__main__":
    pass
            
