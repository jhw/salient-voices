import io
import zipfile

class StaticBank(dict):

    @staticmethod
    def load_zip(zip_path):
        zip_buffer = io.BytesIO()
        with open(zip_path, 'rb') as f:
            zip_buffer.write(f.read())
        zip_buffer.seek(0)
        return SimpleZipBank(zip_buffer=zip_buffer)

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

if __name__ == "__main__":
    pass
