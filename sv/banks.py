from sv.sounds import SVSample

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
        return SVBank(name=bank_name, zip_buffer=zip_buffer)
    
    def __init__(self, name, zip_buffer):
        self.name = name
        self.zip_buffer = zip_buffer

    @property
    def zip_file(self):
        return zipfile.ZipFile(self.zip_buffer, 'r')

    def dump_zip(self, dir_path):
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        zip_path = f"{dir_path}/{self.name}.zip"
        with open(zip_path, 'wb') as f:
            f.write(self.zip_buffer.getvalue())

    def get_wav(self, sample):
        file_paths = self.zip_file.namelist()
        if sample.file_path not in file_paths:
            raise RuntimeError(f"path {sample.file_path} not found in bank {sample.bank_name}")
        with self.zip_file.open(sample.file_path, 'r') as file_entry:
            file_content = file_entry.read()
        return io.BytesIO(file_content)
            
class SVBanks(list):

    @staticmethod
    def load_zip(cache_dir="tmp/banks", filter_fn=lambda x: x.endswith(".zip")):
        banks = SVBanks()
        for file_name in os.listdir(cache_dir):
            if filter_fn(file_name):
                zip_path = f"{cache_dir}/{file_name}"
                bank = SVBank.load_zip(zip_path)
                banks.append(bank)
        return banks
    
    def __init__(self, items=[]):
        list.__init__(self, items)

    def get_wav(self, sample):
        banks = {bank.name: bank for bank in self}
        if sample.bank_name not in banks:
            raise RuntimeError(f"bank {sample.bank_name} not found")
        file_paths = banks[sample.bank_name].zip_file.namelist()
        if sample.file_path not in file_paths:
            raise RuntimeError(f"path {sample.file_path} not found in bank {sample.bank_name}")
        with banks[sample.bank_name].zip_file.open(sample.file_path, 'r') as file_entry:
            file_content = file_entry.read()
        return io.BytesIO(file_content)
    
if __name__ == "__main__":
    pass
