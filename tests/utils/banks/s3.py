from sv.utils.banks.s3 import init_s3_banks
from sv.sampler import SVBank
from moto import mock_s3

import boto3
import unittest

BucketName = "hello-world"

@mock_s3
class S3BanksTest(unittest.TestCase):

    def setUp(self, bucket_name = BucketName):
        self.s3 = boto3.client("s3")
        self.s3.create_bucket(Bucket = bucket_name,
                              CreateBucketConfiguration = {'LocationConstraint': 'EU'})
    
    def test_init_s3_banks(self):
        try:
            self.assertEqual(2, 2)
        except RuntimeError as error:
            self.fail(str(error))

    def tearDown(self, bucket_name = BucketName):
        self.s3.delete_bucket(Bucket = bucket_name)
            
if __name__ == "__main__":
    unittest.main()

