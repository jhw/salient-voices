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
        
        # Open a new zip file for writing
        with zipfile.ZipFile(new_zip_buffer, 'w') as new_zip:
            # Add all files from the current bank
            for file_name in self.zip_file.namelist():
                with self.zip_file.open(file_name) as file_entry:
                    new_zip.writestr(file_name, file_entry.read())

            # Add all files from the other bank, avoiding duplicates
            for file_name in other_bank.zip_file.namelist():
                if file_name not in self.zip_file.namelist():
                    with other_bank.zip_file.open(file_name) as file_entry:
                        new_zip.writestr(file_name, file_entry.read())

        # Replace the current bank's zip buffer with the merged one
        self.zip_buffer = new_zip_buffer
        self.zip_buffer.seek(0)
                
if __name__ == "__main__":
    pass
