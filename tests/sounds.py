from sv.sounds import SVSample
import unittest


class SVSampleTest(unittest.TestCase):

    def test_untagged_without_querystring(self):
        sample = SVSample.parse("mikey303/303 VCO SQR.wav")
        self.assertEqual(sample.bank_name, "mikey303")
        self.assertEqual(sample.file_path, "303 VCO SQR.wav")
        self.assertEqual(sample.tags, [])
        self.assertEqual(sample.querystring, {})
        self.assertEqual(sample.note, 0)

    def test_tagged_without_querystring(self):
        sample = SVSample.parse("mikey303/303 VCO SQR.wav#303#bass")
        self.assertEqual(sample.bank_name, "mikey303")
        self.assertEqual(sample.file_path, "303 VCO SQR.wav")
        self.assertEqual(set(sample.tags), {"303", "bass"})
        self.assertEqual(sample.querystring, {})
        self.assertEqual(sample.note, 0)

    def test_untagged_with_querystring(self):
        sample = SVSample.parse("mikey303/303 VCO SQR.wav?note=64")
        self.assertEqual(sample.bank_name, "mikey303")
        self.assertEqual(sample.file_path, "303 VCO SQR.wav")
        self.assertEqual(sample.tags, [])
        self.assertEqual(sample.querystring, {"note": 64})
        self.assertEqual(sample.note, 64)

    def test_tagged_with_querystring(self):
        sample = SVSample.parse("mikey303/303 VCO SQR.wav?note=64#303#bass")
        self.assertEqual(sample.bank_name, "mikey303")
        self.assertEqual(sample.file_path, "303 VCO SQR.wav")
        self.assertEqual(set(sample.tags), {"303", "bass"})
        self.assertEqual(sample.querystring, {"note": 64})
        self.assertEqual(sample.note, 64)

    def test_querystring_with_default_note(self):
        sample = SVSample.parse("mikey303/303 VCO SQR.wav?")
        self.assertEqual(sample.bank_name, "mikey303")
        self.assertEqual(sample.file_path, "303 VCO SQR.wav")
        self.assertEqual(sample.tags, [])
        self.assertEqual(sample.querystring, {})
        self.assertEqual(sample.note, 0)

    def test_invalid_note_querystring(self):
        sample = SVSample.parse("mikey303/303 VCO SQR.wav?note=invalid")
        self.assertEqual(sample.bank_name, "mikey303")
        self.assertEqual(sample.file_path, "303 VCO SQR.wav")
        self.assertEqual(sample.tags, [])
        self.assertEqual(sample.querystring, {})
        self.assertEqual(sample.note, 0)

    def test_empty_string(self):
        with self.assertRaises(RuntimeError):
            SVSample.parse("")

    def test_no_file_path(self):
        sample = SVSample.parse("mikey303/")
        self.assertEqual(sample.bank_name, "mikey303")
        self.assertEqual(sample.file_path, "")
        self.assertEqual(sample.tags, [])
        self.assertEqual(sample.querystring, {})
        self.assertEqual(sample.note, 0)

    def test_no_bank_name(self):
        with self.assertRaises(RuntimeError):
            SVSample.parse("/303 VCO SQR.wav")

    def test_round_trip_str(self):
        sample_str = "mikey303/303 VCO SQR.wav?note=64#303#bass"
        sample = SVSample.parse(sample_str)
        self.assertEqual(str(sample), sample_str)

    def test_round_trip_default_note(self):
        sample_str = "mikey303/303 VCO SQR.wav#303#bass"
        sample = SVSample.parse(sample_str)
        self.assertEqual(str(sample), sample_str)

    def test_note_property(self):
        sample = SVSample("mikey303", "303 VCO SQR.wav", note=32, tags=["bass"])
        self.assertEqual(sample.note, 32)
        self.assertEqual(sample.querystring, {"note": 32})
        sample.note = 64
        self.assertEqual(sample.note, 64)
        self.assertEqual(sample.querystring, {"note": 64})
        self.assertEqual(str(sample), "mikey303/303 VCO SQR.wav?note=64#bass")

    # FX Tests

    def test_untagged_with_querystring_fx(self):
        # Add a cutoff value to ensure the test passes
        sample = SVSample.parse("mikey303/303 VCO SQR.wav?fx=rev&cutoff=50")
        self.assertEqual(sample.bank_name, "mikey303")
        self.assertEqual(sample.file_path, "303 VCO SQR.wav")
        self.assertEqual(sample.tags, [])
        self.assertEqual(sample.querystring, {"fx": "rev", "cutoff": 50})
        self.assertEqual(sample.fx, SVSample.FX.REV)
        self.assertEqual(sample.cutoff, 50)

    def test_tagged_with_querystring_fx(self):
        # Add a cutoff value to ensure the test passes
        sample = SVSample.parse("mikey303/303 VCO SQR.wav?note=64&fx=ret2&cutoff=70#303#bass")
        self.assertEqual(sample.bank_name, "mikey303")
        self.assertEqual(sample.file_path, "303 VCO SQR.wav")
        self.assertEqual(set(sample.tags), {"303", "bass"})
        self.assertEqual(sample.querystring, {"note": 64, "fx": "ret2", "cutoff": 70})
        self.assertEqual(sample.note, 64)
        self.assertEqual(sample.fx, SVSample.FX.RET2)
        self.assertEqual(sample.cutoff, 70)

    def test_querystring_with_default_fx(self):
        sample = SVSample.parse("mikey303/303 VCO SQR.wav?")
        self.assertEqual(sample.bank_name, "mikey303")
        self.assertEqual(sample.file_path, "303 VCO SQR.wav")
        self.assertEqual(sample.tags, [])
        self.assertEqual(sample.querystring, {})
        self.assertEqual(sample.note, 0)
        self.assertIsNone(sample.fx)

    def test_invalid_fx_querystring(self):
        sample = SVSample.parse("mikey303/303 VCO SQR.wav?fx=invalid")
        self.assertEqual(sample.bank_name, "mikey303")
        self.assertEqual(sample.file_path, "303 VCO SQR.wav")
        self.assertEqual(sample.tags, [])
        self.assertEqual(sample.querystring, {})
        self.assertEqual(sample.note, 0)
        self.assertIsNone(sample.fx)

    def test_round_trip_str_with_fx(self):
        # Add a cutoff value to ensure the test passes
        sample_str = "mikey303/303 VCO SQR.wav?note=64&fx=rev&cutoff=50#303#bass"
        sample = SVSample.parse(sample_str)
        self.assertEqual(str(sample), sample_str)

    def test_round_trip_default_fx(self):
        sample_str = "mikey303/303 VCO SQR.wav?note=64#303#bass"
        sample = SVSample.parse(sample_str)
        self.assertEqual(str(sample), sample_str)

    def test_fx_property(self):
        sample = SVSample("mikey303", "303 VCO SQR.wav", note=32, fx=SVSample.FX.RET4, cutoff=50, tags=["bass"])
        self.assertEqual(sample.fx, SVSample.FX.RET4)
        self.assertEqual(sample.querystring, {"note": 32, "fx": "ret4", "cutoff": 50})
        sample.fx = SVSample.FX.RET2
        self.assertEqual(sample.fx, SVSample.FX.RET2)
        self.assertEqual(sample.querystring, {"note": 32, "fx": "ret2", "cutoff": 50})
        sample.fx = None
        self.assertIsNone(sample.fx)
        self.assertEqual(sample.querystring, {"note": 32, "cutoff": 50})
        self.assertEqual(str(sample), "mikey303/303 VCO SQR.wav?note=32&cutoff=50#bass")

    def test_start_cutoff_validation(self):
        with self.assertRaises(ValueError):
            SVSample.parse("bank1/file.wav?start=100&cutoff=50")

    def test_valid_start_cutoff(self):
        sample = SVSample.parse("bank1/file.wav?start=50&cutoff=100")
        self.assertEqual(sample.start, 50)
        self.assertEqual(sample.cutoff, 100)


if __name__ == "__main__":
    unittest.main()
