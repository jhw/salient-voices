from sv.bank import SVBank

from scipy.io import wavfile

import io
import os
import unittest
import zipfile


class BankTest(unittest.TestCase):

    def setUp(self):
        # Setup temporary zip files for testing
        self.bank1_path = "tests/bank1.zip"
        self.bank2_path = "tests/bank2.zip"
        self.empty_bank_path = "tests/empty_bank.zip"
        self.invalid_zip_path = "tests/invalid_bank.zip"

        self.create_test_zip(self.bank1_path, {
            "sample1.wav": b"Sample 1 Data",
            "sample2.wav": b"Sample 2 Data",
        })
        self.create_test_zip(self.bank2_path, {
            "sample2.wav": b"Sample 2 Data Different",
            "sample3.wav": b"Sample 3 Data",
        })
        self.create_test_zip(self.empty_bank_path, {})

        with open(self.invalid_zip_path, 'wb') as f:
            f.write(b"This is not a valid zip file")

    def create_test_zip(self, path, files):
        with zipfile.ZipFile(path, 'w') as zip_file:
            for file_name, data in files.items():
                zip_file.writestr(file_name, data)

    def test_load_zip(self):
        bank = SVBank.load_zip(self.bank1_path)
        self.assertIsInstance(bank, SVBank)
        self.assertIn("sample1.wav", bank.zip_file.namelist())
        self.assertIn("sample2.wav", bank.zip_file.namelist())

    def test_load_empty_zip(self):
        bank = SVBank.load_zip(self.empty_bank_path)
        self.assertIsInstance(bank, SVBank)
        self.assertEqual(len(bank.zip_file.namelist()), 0)

    def test_spawn_pool(self):
        bank = SVBank.load_zip(self.bank1_path)
        pool = bank.spawn_pool()
        self.assertIsInstance(pool, list)
        self.assertIn("sample1.wav", pool)
        self.assertIn("sample2.wav", pool)

    def test_spawn_pool_empty_bank(self):
        bank = SVBank.load_zip(self.empty_bank_path)
        pool = bank.spawn_pool()
        self.assertIsInstance(pool, list)
        self.assertEqual(len(pool), 0)

    def test_get_wav(self):
        bank = SVBank.load_zip(self.bank1_path)
        wav_io = bank.get_wav("sample1.wav")
        self.assertIsInstance(wav_io, io.BytesIO)
        wav_io.seek(0)
        self.assertEqual(wav_io.read(), b"Sample 1 Data")

    def test_get_wav_missing_sample(self):
        bank = SVBank.load_zip(self.bank1_path)
        with self.assertRaises(RuntimeError):
            bank.get_wav("missing_sample.wav")

    def test_join(self):
        bank1 = SVBank.load_zip(self.bank1_path)
        bank2 = SVBank.load_zip(self.bank2_path)

        # Join bank2 into bank1
        bank1.join(bank2)

        # Check resulting files in bank1
        joined_files = bank1.zip_file.namelist()
        self.assertIn("sample1.wav", joined_files)
        self.assertIn("sample2.wav", joined_files)  # Original from bank1
        self.assertIn("sample3.wav", joined_files)

        # Validate content of files
        sample1_data = bank1.get_wav("sample1.wav").read()
        sample2_data = bank1.get_wav("sample2.wav").read()
        sample3_data = bank1.get_wav("sample3.wav").read()

        self.assertEqual(sample1_data, b"Sample 1 Data")
        self.assertEqual(sample2_data, b"Sample 2 Data")  # Original from bank1
        self.assertEqual(sample3_data, b"Sample 3 Data")

    def test_join_empty_banks(self):
        empty_bank1 = SVBank.load_zip(self.empty_bank_path)
        empty_bank2 = SVBank.load_zip(self.empty_bank_path)

        empty_bank1.join(empty_bank2)

        self.assertEqual(len(empty_bank1.zip_file.namelist()), 0)

    def test_join_large_number_of_files(self):
        large_bank_path = "tests/large_bank.zip"
        files = {f"sample{i}.wav": f"Sample {i} Data".encode() for i in range(100)}
        self.create_test_zip(large_bank_path, files)

        large_bank = SVBank.load_zip(large_bank_path)
        bank1 = SVBank.load_zip(self.bank1_path)
        bank1.join(large_bank)

        joined_files = bank1.zip_file.namelist()
        self.assertGreaterEqual(len(joined_files), 100)

    def tearDown(self):
        # Cleanup temporary files
        paths = [
            self.bank1_path,
            self.bank2_path,
            self.empty_bank_path,
            self.invalid_zip_path,
            "tests/large_bank.zip",
        ]
        for path in paths:
            if os.path.exists(path):
                os.remove(path)


if __name__ == "__main__":
    unittest.main()
