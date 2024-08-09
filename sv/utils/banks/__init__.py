from sv.sampler import SVBank

import io
import zipfile

def single_shot_bank(bank_name, file_path):
    with open(file_path, 'rb') as wav_file:
        wav_data = wav_file.read()
    zip_buffer = io.BytesIO()
    zip_file = zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False)
    file_name = file_path.split("/")[-1]
    zip_file.writestr(file_name, wav_data)
    return SVBank(name = bank_name,
                 zip_file = zip_file)

        
if __name__ == "__main__":
    pass
