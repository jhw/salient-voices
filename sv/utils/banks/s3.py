from sv.sampler import SVBank

import io

def _list_keys(s3, bucket_name, prefix):
    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket = bucket_name,
                               Prefix = prefix)
    keys = []
    for page in pages:
        if "Contents" in page:
            for obj in page["Contents"]:
                keys.append(obj["Key"])
    return keys

def _load_bank(s3,
                 bucket_name ,
                 s3_key):
    bank_name = s3_key.split("/")[-1].split(".")[0]
    zip_buffer = io.BytesIO(s3.get_object(Bucket = bucket_name,
                                          Key = s3_key)["Body"].read())
    # START TEMP CODE
    import zipfile
    print (zipfile.ZipFile(zip_buffer, 'r'))
    # END TEMP CODE
    return SVBank(name = bank_name,
                  zip_buffer = zip_buffer)

def init_s3_banks(s3,
                  bucket_name,
                  prefix = "banks"):
    s3_keys = _list_keys(s3, bucket_name, prefix)
    return [_load_bank(s3 = s3,
                       bucket_name = bucket_name,
                       s3_key = s3_key)
            for s3_key in s3_keys]

if __name__ == "__main__":
    pass


