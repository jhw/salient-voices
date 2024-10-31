from sv.banks import SVBank, SVBanks

import hashlib
import io
import logging
import os

def list_remote_keys(s3, bucket_name, prefix = "banks"):
    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket = bucket_name,
                               Prefix = prefix)
    keys = []
    for page in pages:
        if "Contents" in page:
            for obj in page["Contents"]:
                keys.append(obj["Key"])
    return sorted(keys)

def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def diff_keys(s3, bucket_name, keys, cache_dir="tmp/banks"):
    diffed_keys = []
    for key in keys:
        bank_name = key.split("/")[-1].split(".")[0]
        zip_filename = f"{cache_dir}/{bank_name}.zip"
        if not os.path.exists(zip_filename):
            diffed_keys.append(key)
            continue
        s3_object = s3.head_object(Bucket=bucket_name, Key=key)
        s3_md5 = s3_object["ETag"].strip('"')
        local_md5 = calculate_md5(zip_filename)
        if s3_md5 != local_md5:
            diffed_keys.append(key)    
    return diffed_keys

def sync_banks(s3,
               bucket_name,
               keys,
               cache_dir = "tmp/banks"):
    for key in keys:
        bank_name = key.split("/")[-1].split(".")[0]
        logging.info(f"syncing {bank_name}")
        zip_buffer = io.BytesIO(s3.get_object(Bucket = bucket_name,
                                              Key = key)["Body"].read())        
        bank = SVBank(name = bank_name,
                      zip_buffer = zip_buffer)
        bank.dump_zip(cache_dir)
        
if __name__ == "__main__":
    pass


