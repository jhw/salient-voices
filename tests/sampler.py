from sv.banks import SVBank, SVBanks
from sv.sampler import SVSampleRef as SVSample

import unittest

class SampleTest(unittest.TestCase):

    def test_untagged(self):
        sample = SVSample.parse("mikey303/303 VCO SQR.wav")
        self.assertEqual(sample.bank_name, "mikey303")
        self.assertEqual(sample.file_path, "303 VCO SQR.wav")
        self.assertEqual(sample.tags, [])
    
    def test_tagged(self):
        sample = SVSample.parse("mikey303/303 VCO SQR.wav#303#bass")
        self.assertEqual(sample.bank_name, "mikey303")
        self.assertEqual(sample.file_path, "303 VCO SQR.wav")
        tags = sample.tags
        self.assertEqual(len(tags), 2)
        for tag in ["bass", "303"]:
            self.assertTrue(tag in tags)        
        
if __name__ == "__main__":
    unittest.main()
