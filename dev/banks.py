from sv.sampler import SVBank
from sv.utils import is_online
from sv.utils.banks.s3 import init_s3_banks

import logging
import os

def load_banks(cache_dir):
    banks = []
    for file_name in os.listdir(cache_dir):
        zip_path = f"{cache_dir}/{file_name}"
        bank = SVBank.load_zipfile(zip_path)
        banks.append(bank)
    return banks

def save_banks(banks, cache_dir):
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    for bank in banks:
        bank.dump_zipfile(cache_dir)

def init_banks(s3, bucket_name, cache_dir = "tmp/banks"):
    if os.path.exists(cache_dir):
        logging.info(f"loading banks from {cache_dir}")
        return load_banks(cache_dir)
    elif is_online():            
        logging.info(f"loading banks from s3 {bucket_name}")
        banks = init_s3_banks(s3, bucket_name)
        logging.info(f"saving banks to {cache_dir}")            
        save_banks(banks, cache_dir)
        return banks
    else:
        raise RuntimeError("no cached banks and not online, sorry")

if __name__ == "__main__":
    pass
