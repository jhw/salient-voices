from sv.banks import SVBank, SVBanks
from sv.sampler import SVSampleRef as SVSample
from sv.sampler import SVSlotSampler

import rv
import rv.note
import unittest

class SVSampleRefTest(unittest.TestCase):

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

class SamplerTest(unittest.TestCase):

    def setUp(self):
        bank = SVBank.load_zip("tests/mikey303.zip")
        self.banks = SVBanks([bank])
        
    def test_slot_sampler(self):
        tag_mapping = {"bass": "303"}
        pool, _ = self.banks.spawn_pool(tag_mapping)
        sampler = SVSlotSampler(banks = self.banks,
                                pool = pool,
                                root_note = rv.note.NOTE.C5)
        samples = [sample for sample in sampler.samples
                   if sample]
        self.assertEqual(len(samples), 2)
        
if __name__ == "__main__":
    unittest.main()
