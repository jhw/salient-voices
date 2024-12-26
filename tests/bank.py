from sv.bank import SVBank

from scipy.io import wavfile

import base64
import io
import os
import shutil
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

    def test_load_wav(self):
        # Create a test directory with WAV files
        test_dir = "tests/wav_files"
        os.makedirs(test_dir, exist_ok=True)
        wav_files = {
            "sample1.wav": b"Sample 1 Data",
            "sample2.wav": b"Sample 2 Data",
        }
        for file_name, data in wav_files.items():
            with open(os.path.join(test_dir, file_name), 'wb') as f:
                f.write(data)

        # Load WAV files into an SVBank instance
        bank = SVBank.load_wav(test_dir)

        # Verify the bank contains the expected files
        self.assertIsInstance(bank, SVBank)
        zip_file = bank.zip_file
        self.assertIn("sample1.wav", zip_file.namelist())
        self.assertIn("sample2.wav", zip_file.namelist())

        # Verify the file content
        with zip_file.open("sample1.wav") as f:
            self.assertEqual(f.read(), b"Sample 1 Data")
        with zip_file.open("sample2.wav") as f:
            self.assertEqual(f.read(), b"Sample 2 Data")

        # Clean up
        shutil.rmtree(test_dir)

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

    def test_dump_zip(self):
        # Load the test bank
        bank = SVBank.load_zip(self.bank1_path)
        bank.name = "test_bank"  # Assign a name to the bank for dump_zip

        # Dump the ZIP to the output directory
        output_dir = "tests/output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        bank.dump_zip(output_dir)

        # Verify the ZIP file exists in the output directory
        dumped_zip_path = os.path.join(output_dir, f"{bank.name}.zip")
        self.assertTrue(os.path.exists(dumped_zip_path))

        # Verify the contents of the dumped ZIP file
        with zipfile.ZipFile(dumped_zip_path, 'r') as dumped_zip:
            dumped_files = dumped_zip.namelist()
            self.assertIn("sample1.wav", dumped_files)
            self.assertIn("sample2.wav", dumped_files)

            # Verify file content
            with dumped_zip.open("sample1.wav") as f:
                self.assertEqual(f.read(), b"Sample 1 Data")
            with dumped_zip.open("sample2.wav") as f:
                self.assertEqual(f.read(), b"Sample 2 Data")

    def test_dump_wav(self):
        # Load the test bank
        bank = SVBank.load_zip(self.bank1_path)

        # Create an output directory for WAV files
        output_dir = "tests/output_wav"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Dump the WAV files from the bank
        bank.dump_wav(output_dir)

        # Verify the files are dumped correctly
        dumped_files = os.listdir(output_dir)
        self.assertIn("sample1.wav", dumped_files)
        self.assertIn("sample2.wav", dumped_files)

        # Verify the content of the dumped files
        with open(os.path.join(output_dir, "sample1.wav"), "rb") as f:
            self.assertEqual(f.read(), b"Sample 1 Data")
        with open(os.path.join(output_dir, "sample2.wav"), "rb") as f:
            self.assertEqual(f.read(), b"Sample 2 Data")

        # Clean up
        shutil.rmtree(output_dir)

    def test_to_dict(self):
        # Load the test bank
        bank = SVBank.load_zip(self.bank1_path)
        
        # Convert to dictionary
        bank_dict = bank.to_dict()
        
        # Verify the dictionary keys and values
        self.assertIn("sample1.wav", bank_dict)
        self.assertIn("sample2.wav", bank_dict)
        
        # Verify the content of the base64-encoded data
        with bank.zip_file.open("sample1.wav") as f:
            self.assertEqual(
                base64.b64encode(f.read()).decode('utf-8'),
                bank_dict["sample1.wav"]
            )

    def test_from_dict(self):
        # Create a test dictionary
        test_dict = {
            "sample1.wav": base64.b64encode(b"Sample 1 Data").decode('utf-8'),
            "sample2.wav": base64.b64encode(b"Sample 2 Data").decode('utf-8'),
        }

        # Convert back to SVBank
        bank = SVBank.from_dict(test_dict)

        # Verify the bank contents
        zip_file = bank.zip_file
        self.assertIn("sample1.wav", zip_file.namelist())
        self.assertIn("sample2.wav", zip_file.namelist())
        
        # Verify the file data
        with zip_file.open("sample1.wav") as f:
            self.assertEqual(f.read(), b"Sample 1 Data")
        with zip_file.open("sample2.wav") as f:
            self.assertEqual(f.read(), b"Sample 2 Data")
                
    def tearDown(self):
        # Cleanup temporary files
        paths = [
            self.bank1_path,
            self.bank2_path,
            self.empty_bank_path,
            self.invalid_zip_path,
            "tests/large_bank.zip",
            "tests/output",
        ]
        for path in paths:
            if os.path.exists(path):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)


if __name__ == "__main__":
    unittest.main()
