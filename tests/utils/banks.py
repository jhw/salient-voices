from sv.banks import SVBank
from sv.utils.banks import list_remote_keys, diff_keys, sync_banks, load_banks
from moto import mock_s3

import boto3
import io
import os
import unittest

BucketName = "hello-world"

@mock_s3
class BankUtilsTest(unittest.TestCase):
    
    def setUp(self, bucket_name = BucketName):
        self.s3 = boto3.client("s3")
        self.s3.create_bucket(Bucket = bucket_name,
                              CreateBucketConfiguration = {'LocationConstraint': 'EU'})
        bank = SVBank.load_wav_files(bank_name = "mikey303",
                                     dir_path = "tests")
        self.s3.put_object(Bucket = bucket_name,
                           Key = "banks/mikey303.zip",
                           Body = bank.zip_buffer.getvalue(),
                           ContentType = "application/gzip")

    def test_sync_lifecycle(self,
                            cache_dir = "tmp/banks",
                            bucket_name = BucketName):
        # init cache
        try:
            os.system(f"rm -rf {cache_dir}")
        except:
            pass
        os.makedirs(cache_dir)
        # list keys
        keys = list_remote_keys(s3 = self.s3,
                                bucket_name = bucket_name)
        self.assertEqual(len(keys), 1)
        # diff keys
        diffed_keys = diff_keys(s3 = self.s3,
                                bucket_name = bucket_name,
                                keys = keys)
        self.assertEqual(len(diffed_keys), 1)
        # sync banks
        sync_banks(s3 = self.s3,
                   bucket_name = bucket_name,
                   keys = keys)
        # re- diff keys
        diffed_keys = diff_keys(s3 = self.s3,
                                bucket_name = bucket_name,
                                keys = keys)
        self.assertEqual(diffed_keys, [])
        # load banks
        banks = load_banks()
        self.assertTrue(len(banks) == 1)
        # check bank properties
        bank = banks[0]        
        self.assertTrue(isinstance(bank, SVBank))
        self.assertEqual(bank.name, "mikey303")        
        wav_files = bank.zip_file.namelist()
        self.assertTrue(len(wav_files) == 2)
        for wav_file in ["303 VCO SQR.wav",
                         "303 VCO SAW.wav"]:                          
            self.assertTrue(wav_file in wav_files)
        
    def tearDown(self, bucket_name = BucketName):
        # clean cache
        """
        try:
            os.system(f"rm -rf {cache_dir}")
        except:
            pass
        """
        # clean s3
        resp = self.s3.list_objects(Bucket = bucket_name)
        if "Contents" in resp:
            for obj in resp["Contents"]:
                self.s3.delete_object(Bucket = bucket_name,
                                      Key = obj["Key"])
        self.s3.delete_bucket(Bucket = bucket_name)
            
if __name__ == "__main__":
    unittest.main()

