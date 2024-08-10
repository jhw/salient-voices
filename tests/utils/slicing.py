from sv.utils.slicing import slice_wav

import io
import os
import unittest
import zipfile

class SlicingTest(unittest.TestCase):

    def test_slicing(self):
        try:
            wav_data = None
            with open("tests/utils/sample-project.wav", 'rb') as file:
                wav_data = file.read()
            if not wav_data:
                raise RuntimeError("wav file not loaded")
            wav_buffer = io.BytesIO(wav_data)
            zip_paths = ["slice-1.wav", "slice-2.wav"]
            zip_file = slice_wav(wav_io = wav_buffer,
                                 zip_paths = zip_paths)
            self.assertTrue(isinstance(zip_file, zipfile.ZipFile))
            zipped_paths = zip_file.namelist()
            for zip_path in zip_paths:
                self.assertTrue(zip_path in zipped_paths)
        except RuntimeError as error:
            self.fail(str(error))
            
if __name__ == "__main__":
    unittest.main()
