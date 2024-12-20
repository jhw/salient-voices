from sv.sample import SVSample
import unittest

class SampleTest(unittest.TestCase):

    def test_core_usage(self):
        sample = SVSample.parse("mikey303/303 VCO SQR.wav")
        self.assertEqual(sample.bank_name, "mikey303")
        self.assertEqual(sample.file_path, "303 VCO SQR.wav")

    def test_empty_string(self):
        with self.assertRaises(RuntimeError):
            SVSample.parse("")

    def test_no_file_path(self):
        sample = SVSample.parse("mikey303/")
        self.assertEqual(sample.bank_name, "mikey303")
        self.assertEqual(sample.file_path, "")

    def test_no_bank_name(self):
        with self.assertRaises(RuntimeError):
            SVSample.parse("/303 VCO SQR.wav")

    def test_round_trip(self):
        sample_str = "mikey303/303 VCO SQR.wav"
        sample = SVSample.parse(sample_str)
        self.assertEqual(str(sample), sample_str)

if __name__ == "__main__":
    unittest.main()
