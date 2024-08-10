from sv.utils.slicing import slice_wav_equal, slice_wav_custom
from pydub import AudioSegment

import io
import unittest
import zipfile

class SlicingTest(unittest.TestCase):

    def test_slice_equal(self):
        try:
            wav_data = None
            with open("tests/utils/sample-project.wav", 'rb') as file:
                wav_data = file.read()
            if not wav_data:
                raise RuntimeError("wav file not loaded")
            wav_io = io.BytesIO(wav_data)
            zip_paths = ["slice-1.wav", "slice-2.wav"]
            zip_buffer = slice_wav_equal(wav_io = wav_io,
                                         zip_paths = zip_paths)
            self.assertTrue(isinstance(zip_buffer, io.BytesIO))
            zip_file = zipfile.ZipFile(zip_buffer, 'r')
            zipped_paths = zip_file.namelist()
            for zip_path in zip_paths:
                self.assertTrue(zip_path in zipped_paths)
        except RuntimeError as error:
            self.fail(str(error))

    def test_slice_custom(self):
        try:
            wav_data = None
            with open("tests/utils/sample-project.wav", 'rb') as file:
                wav_data = file.read()
            if not wav_data:
                raise RuntimeError("wav file not loaded")
            wav_io = io.BytesIO(wav_data)
            audio_io = AudioSegment.from_file(wav_io, format = "wav")
            n = len(audio_io)
            zip_items = [{"zip_path": "slice-1.wav",
                          "start_time": 0,
                          "end_time": int(n/2)},                         
                         {"zip_path": "slice-2.wav",
                          "start_time": int(n/2),
                          "end_time": n}]
            zip_buffer = slice_wav_custom(audio_io = audio_io,
                                          zip_items = zip_items)
            self.assertTrue(isinstance(zip_buffer, io.BytesIO))
            zip_file = zipfile.ZipFile(zip_buffer, 'r')
            zipped_paths = zip_file.namelist()
            for zip_item in zip_items:
                self.assertTrue(zip_item["zip_path"] in zipped_paths)
        except RuntimeError as error:
            self.fail(str(error))
            
if __name__ == "__main__":
    unittest.main()
