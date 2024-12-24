from sv.sampler import SVSamplePool

import io
import os
import re
import zipfile
            
class SVBank:
    
    @staticmethod
    def load_zip(zip_path):
        zip_buffer = io.BytesIO()
        with open(zip_path, 'rb') as f:
            zip_buffer.write(f.read())
        zip_buffer.seek(0)
        return SVBank(zip_buffer=zip_buffer)

    @staticmethod
    def load_wav(root_dir):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for root, _, files in os.walk(root_dir):
                for file_name in files:
                    if file_name.lower().endswith('.wav'):
                        file_path = os.path.join(root, file_name)
                        with open(file_path, 'rb') as f:
                            zip_file.writestr(file_name, f.read())
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

    def join(self, other_bank):
        # Create a new zip buffer for the merged contents
        new_zip_buffer = io.BytesIO()
        existing_files = set(self.zip_file.namelist())
        
        # Open a new zip file for writing
        with zipfile.ZipFile(new_zip_buffer, 'w') as new_zip:
            # Add all files from the current bank
            for file_name in self.zip_file.namelist():
                with self.zip_file.open(file_name) as file_entry:
                    new_zip.writestr(file_name, file_entry.read())

            # Add all files from the other bank, avoiding duplicates
            for file_name in other_bank.zip_file.namelist():
                if file_name not in existing_files:
                    with other_bank.zip_file.open(file_name) as file_entry:
                        new_zip.writestr(file_name, file_entry.read())
                    existing_files.add(file_name)

        # Replace the current bank's zip buffer with the merged one
        self.zip_buffer = new_zip_buffer
        self.zip_buffer.seek(0)

    def dump_zip(self, dir_path):
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        zip_path = f"{dir_path}/{self.name}.zip"
        with open(zip_path, 'wb') as f:
            f.write(self.zip_buffer.getvalue())

    def dump_wav(self, dir_path):
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        for file_name in self.zip_file.namelist():
            file_path = os.path.join(dir_path, file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with self.zip_file.open(file_name, 'r') as file_entry:
                with open(file_path, 'wb') as f:
                    f.write(file_entry.read())
        
if __name__ == "__main__":
    pass
