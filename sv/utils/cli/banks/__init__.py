import io
import os
import re
import zipfile

class StaticZipBank(dict):

    def __init__(self, zip_buffer):
        self.zip_buffer = zip_buffer

    @property
    def zip_file(self):
        return zipfile.ZipFile(self.zip_buffer, 'r')

    @property
    def file_names(self):
        return self.zip_file.namelist()

    def get_wav(self, file_name):
        if file_name not in self.file_names:
            raise RuntimeError(f"path {file_name} not found in bank")
        with self.zip_file.open(file_name, 'r') as file_entry:
            file_content = file_entry.read()
        return io.BytesIO(file_content)

class StaticFilesBank(dict):
    
    def __init__(self, pattern, root_dir = "samples"):
        dict.__init__(self, {})
        self.paths = self.init_paths(pattern = pattern,
                                     root_dir = root_dir)
        self.root_dir = root_dir

    def init_paths(self, pattern, root_dir):
        paths = []
        for root, _, files in os.walk(root_dir):
            for file_name in files:
                if file_name.lower().endswith('.wav'):
                    file_path = os.path.join(root, file_name)
                    if re.search(pattern, file_path) != None:
                        relative_path = os.path.relpath(file_path, root_dir)
                        paths.append(relative_path)
        return paths

    def file_names(self):
        return self.paths
    
    def load_wav_lazily(fn):
        def wrapped(self, sample):
            if sample not in self:
                if sample not in self.paths:
                    raise RuntimeError(f"{sample} not found")
                file_name = f"{self.root_dir}/{sample}"
                with open(file_name, 'rb') as f:
                    self[sample] = io.BytesIO(f.read())
            return fn(self, sample)
        return wrapped

    @load_wav_lazily
    def get_wav(self, sample):
        return self[sample]
    
if __name__ == "__main__":
    pass
