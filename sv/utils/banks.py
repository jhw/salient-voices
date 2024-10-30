from sv.banks import SVBank, SVBanks

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

def diff_keys(keys, cache_dir = "tmp/banks"):
    diffed_keys = []
    for key in keys:
        bank_name = key.split("/")[-1].split(".")[0]
        zip_filename = f"{cache_dir}/{bank_name}.zip"
        if not os.path.exists(zip_filename):
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
        bank.dump_zip_file(cache_dir)

def load_banks(cache_dir = "tmp/banks"):
    banks = SVBanks()
    for file_name in os.listdir(cache_dir):
        zip_path = f"{cache_dir}/{file_name}"
        bank = SVBank.load_zip_file(zip_path)
        banks.append(bank)
    return banks
        
if __name__ == "__main__":
    pass


