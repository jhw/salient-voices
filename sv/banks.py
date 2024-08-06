class SVBank:

    def __init__(self, name, zip_file):
        self.name = name
        self.zip_file = zip_file

class SVBanks(dict):

    def __init__(self, item = []):
        dict.__init__(self, item)

    def get_wav_file(self, sample):
        bank_name, file_path = sample.split("/")
        return self[bank_name].zip_file.open(file_path, 'r')
    
if __name__ == "__main__":
    pass
