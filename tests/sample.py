from sv.sample import SVSample

import unittest

class SVSampleTest(unittest.TestCase):

    def test_untagged_without_querystring(self):
        sample = SVSample.parse("mikey303/303 VCO SQR.wav")
        self.assertEqual(sample.bank_name, "mikey303")
        self.assertEqual(sample.file_path, "303 VCO SQR.wav")
        self.assertEqual(sample.tags, [])
        self.assertEqual(sample.querystring, {"note": 0})
        self.assertEqual(sample.note, 0)

    def test_tagged_without_querystring(self):
        sample = SVSample.parse("mikey303/303 VCO SQR.wav#303#bass")
        self.assertEqual(sample.bank_name, "mikey303")
        self.assertEqual(sample.file_path, "303 VCO SQR.wav")
        self.assertEqual(set(sample.tags), {"303", "bass"})
        self.assertEqual(sample.querystring, {"note": 0})
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
        self.assertEqual(sample.querystring, {"note": 0})
        self.assertEqual(sample.note, 0)

    # note
        
    def test_invalid_note_querystring(self):
        sample = SVSample.parse("mikey303/303 VCO SQR.wav?note=invalid")
        self.assertEqual(sample.bank_name, "mikey303")
        self.assertEqual(sample.file_path, "303 VCO SQR.wav")
        self.assertEqual(sample.tags, [])
        # Invalid note should fall back to default 0
        self.assertEqual(sample.querystring, {"note": 0})
        self.assertEqual(sample.note, 0)

    def test_empty_string(self):
        with self.assertRaises(RuntimeError):
            SVSample.parse("")

    def test_no_file_path(self):
        sample = SVSample.parse("mikey303/")
        self.assertEqual(sample.bank_name, "mikey303")
        self.assertEqual(sample.file_path, "")
        self.assertEqual(sample.tags, [])
        self.assertEqual(sample.querystring, {"note": 0})
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

    # FX

    def test_untagged_with_querystring_fx(self):
        sample = SVSample.parse("mikey303/303 VCO SQR.wav?fx=rev")
        self.assertEqual(sample.bank_name, "mikey303")
        self.assertEqual(sample.file_path, "303 VCO SQR.wav")
        self.assertEqual(sample.tags, [])
        self.assertEqual(sample.querystring, {"note": 0, "fx": "rev"})
        self.assertEqual(sample.note, 0)
        self.assertEqual(sample.fx, SVSample.FX.REV)

    def test_tagged_with_querystring_fx(self):
        sample = SVSample.parse("mikey303/303 VCO SQR.wav?note=64&fx=ret2#303#bass")
        self.assertEqual(sample.bank_name, "mikey303")
        self.assertEqual(sample.file_path, "303 VCO SQR.wav")
        self.assertEqual(set(sample.tags), {"303", "bass"})
        self.assertEqual(sample.querystring, {"note": 64, "fx": "ret2"})
        self.assertEqual(sample.note, 64)
        self.assertEqual(sample.fx, SVSample.FX.RET2)

    def test_querystring_with_default_fx(self):
        sample = SVSample.parse("mikey303/303 VCO SQR.wav?")
        self.assertEqual(sample.bank_name, "mikey303")
        self.assertEqual(sample.file_path, "303 VCO SQR.wav")
        self.assertEqual(sample.tags, [])
        self.assertEqual(sample.querystring, {"note": 0})
        self.assertEqual(sample.note, 0)
        self.assertIsNone(sample.fx)

    def test_invalid_fx_querystring(self):
        sample = SVSample.parse("mikey303/303 VCO SQR.wav?fx=invalid")
        self.assertEqual(sample.bank_name, "mikey303")
        self.assertEqual(sample.file_path, "303 VCO SQR.wav")
        self.assertEqual(sample.tags, [])
        # Invalid fx should fall back to None
        self.assertEqual(sample.querystring, {"note": 0})
        self.assertEqual(sample.note, 0)
        self.assertIsNone(sample.fx)

    def test_round_trip_str_with_fx(self):
        sample_str = "mikey303/303 VCO SQR.wav?note=64&fx=rev#303#bass"
        sample = SVSample.parse(sample_str)
        self.assertEqual(str(sample), sample_str)

    def test_round_trip_default_fx(self):
        sample_str = "mikey303/303 VCO SQR.wav?note=64#303#bass"
        sample = SVSample.parse(sample_str)
        self.assertEqual(str(sample), sample_str)

    def test_fx_property(self):
        sample = SVSample("mikey303", "303 VCO SQR.wav", note=32, fx=SVSample.FX.RET4, tags=["bass"])
        self.assertEqual(sample.fx, SVSample.FX.RET4)
        self.assertEqual(sample.querystring, {"note": 32, "fx": "ret4"})
        sample.fx = SVSample.FX.RET2
        self.assertEqual(sample.fx, SVSample.FX.RET2)
        self.assertEqual(sample.querystring, {"note": 32, "fx": "ret2"})
        sample.fx = None
        self.assertIsNone(sample.fx)
        self.assertEqual(sample.querystring, {"note": 32})
        self.assertEqual(str(sample), "mikey303/303 VCO SQR.wav?note=32#bass")
                 
if __name__ == "__main__":
    unittest.main()
