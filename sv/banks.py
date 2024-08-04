import io
import os
import zipfile

def list_s3_keys(s3, bucket_name, prefix):
    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket = bucket_name,
                               Prefix = prefix)
    keys = []
    for page in pages:
        if "Contents" in page:
            for obj in page["Contents"]:
                keys.append(obj["Key"])
    return keys

def list_cached(cache_dir):
    if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    cached = []
    for item in os.listdir(cache_dir):
        if item.endswith(".zip"):
            bank_name = item.split(".")[0]
            cached.append(bank_name)
    return sorted(cached)

class SVBank:

    def __init__(self, name, zipfile):
        self.name = name
        self.zipfile = zipfile

    @property
    def wavfiles(self):
        return [item.filename
                for item in self.zipfile.infolist()]

class SVBanks(dict):

    @classmethod
    def initialise(self,
                   s3,
                   bucket_name,
                   prefix = "banks",
                   cache_dir = "tmp/banks"):
        s3_keys, cached = (list_s3_keys(s3, bucket_name, prefix),
                           list_cached(cache_dir))
        banks = {}
        for s3_key in s3_keys:
            bank_name = s3_key.split("/")[-1].split(".")[0]
            cache_file_name = "%s/%s.zip" % (cache_dir, bank_name)
            if bank_name not in cached:
                print ("INFO: fetching %s" % s3_key)
                buf = io.BytesIO(s3.get_object(Bucket = bucket_name,
                                               Key = s3_key)["Body"].read())
                with open(cache_file_name, 'wb') as f:
                    f.write(buf.getvalue())
                zf = zipfile.ZipFile(buf, "r")
            else:
                zf = zipfile.ZipFile(cache_file_name)
            bank = SVBank(name = bank_name,
                          zipfile = zf)
            banks[bank_name] = bank
        return SVBanks(banks)
        
    def __init__(self, item = {}):
        dict.__init__(self, item)

    def get_wav_file(self, sample):
        return self[sample["bank"]].zipfile.open(sample["file"], 'r')

if __name__ == "__main__":
    pass
