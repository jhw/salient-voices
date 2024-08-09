from sv.utils.banks import single_shot_bank
from sv.utils.banks.s3 import init_s3_banks
from sv.sampler import SVBank
from moto import mock_s3

import boto3
import io
import unittest
import zipfile

BucketName = "hello-world"

def convert_zipfile_to_bytesio(zip_file):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_output:
        for zip_info in zip_file.infolist():
            file_content = zip_file.read(zip_info.filename)
            zip_output.writestr(zip_info, file_content)
    zip_buffer.seek(0)
    return zip_buffer

@mock_s3
class S3BanksTest(unittest.TestCase):
    
    def setUp(self, bucket_name = BucketName):
        self.s3 = boto3.client("s3")
        self.s3.create_bucket(Bucket = bucket_name,
                              CreateBucketConfiguration = {'LocationConstraint': 'EU'})
        bank = single_shot_bank(bank_name = "mikey303",
                                file_path = "tests/utils/303 VCO SQR.wav")
        zip_buffer = convert_zipfile_to_bytesio(bank.zip_file)
        self.s3.put_object(Bucket = bucket_name,
                           Key = "banks/mikey303.zip",
                           Body = zip_buffer,
                           ContentType = "application/gzip")
    
    def test_init_s3_banks(self, bucket_name = BucketName):
        try:
            banks = init_s3_banks(s3 = self.s3,
                                  bucket_name = bucket_name)
            self.assertTrue(len(banks) == 1)
            bank = banks[0]
            self.assertTrue(isinstance(bank, SVBank))
            self.assertEqual(bank.name, "mikey303")
            wav_files = bank.zip_file.namelist()
            self.assertTrue(len(wav_files) == 1)
            self.assertTrue("303 VCO SQR.wav" in wav_files)
        except RuntimeError as error:
            self.fail(str(error))

    def tearDown(self, bucket_name = BucketName):
        resp = self.s3.list_objects(Bucket = bucket_name)
        if "Contents" in resp:
            for obj in resp["Contents"]:
                self.s3.delete_object(Bucket = bucket_name,
                                      Key = obj["Key"])
        self.s3.delete_bucket(Bucket = bucket_name)
            
if __name__ == "__main__":
    unittest.main()

