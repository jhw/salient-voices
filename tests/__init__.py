from sv.sampler import SVSamplePool

import io
import zipfile
            
class SVBank:
    
    @staticmethod
    def load_zip(zip_path):
        zip_buffer = io.BytesIO()
        with open(zip_path, 'rb') as f:
            zip_buffer.write(f.read())
        zip_buffer.seek(0)
        return SVBank(zip_buffer=zip_buffer)
    
    def __init__(self, zip_buffer):
        self.zip_buffer = zip_buffer

    @property
    def zip_file(self):
        return zipfile.ZipFile(self.zip_buffer, 'r')

    def spawn_pool(self):
        return SVSamplePool(self.zip_file.namelist())

    def get_wav(self, sample):
        file_paths = self.zip_file.namelist()
        if sample not in file_paths:
            raise RuntimeError(f"path {sample} not found in bank")
        with self.zip_file.open(sample, 'r') as file_entry:
            file_content = file_entry.read()
        return io.BytesIO(file_content)

if __name__ == "__main__":
    pass
