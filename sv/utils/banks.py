from sv.banks import SVBank, SVBanks

import io
import logging

def load_banks(cache_dir = "tmp/banks"):
    banks = SVBanks()
    for file_name in os.listdir(cache_dir):
        zip_path = f"{cache_dir}/{file_name}"
        bank = SVBank.load_zipfile(zip_path)
        banks.append(bank)
    return banks

def sync_banks(s3,
               bucket_name,
               cache_dir = "tmp/banks"):
    def list_keys(s3, bucket_name, prefix = "banks"):
        paginator = s3.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket = bucket_name,
                                   Prefix = prefix)
        keys = []
        for page in pages:
            if "Contents" in page:
                for obj in page["Contents"]:
                    keys.append(obj["Key"])
        return sorted(keys)
    keys = list_keys(s3, bucket_name)
    for key in keys:
        bank_name = key.split("/")[-1].split(".")[0]
        logging.info(f"syncing {bank_name}")
        zip_buffer = io.BytesIO(s3.get_object(Bucket = bucket_name,
                                              Key = key)["Body"].read())        
        bank = SVBank(name = bank_name,
                      zip_buffer = zip_buffer)
        bank.dump_zipfile(cache_dir)

if __name__ == "__main__":
    pass


