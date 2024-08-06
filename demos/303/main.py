from sv.banks import SVBank
from sv.model import SVNoteTrig, SVNoteOffTrig, SVPatch
from sv.project import SVProject

from rv.note import NOTE as RVNOTE

import io
import os
import yaml
import zipfile

def load_yaml(attr):
    return yaml.safe_load(open(f"{attr}.yaml").read())

Modules = load_yaml("modules")

def init_bank(bank_name, file_path):
    with open(file_path, 'rb') as wav_file:
        wav_data = wav_file.read()
    zip_buffer = io.BytesIO()
    zip_file = zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False)
    file_name = file_path.split("/")[-1]
    zip_file.writestr(file_name, wav_data)
    return SVBank(name = bank_name,
                 zip_file = zip_file)

if __name__ == "__main__":
    try:
        bank = init_bank(bank_name = "mikey303",
                         file_path = "303 VCO SQR.wav")
        trigs = [SVNoteTrig(mod = "MultiSynth",
                            sample_mod = "Sampler",
                            sample = "mikey303/303 VCO SQR.wav",
                            note = RVNOTE.G4,
                            i = 0),                 
                 SVNoteOffTrig(mod = "MultiSynth",
                               i = 1)]
        patch = SVPatch(trigs = trigs,
                        n_ticks = 16)
        project = SVProject().render(patches = [patch],
                                     modules = Modules,
                                     banks = [bank],
                                     bpm = 124)
        if not os.path.exists("tmp"):
            os.mkdir("tmp")
        with open("tmp/demo-303.sunvox", 'wb') as f:
            project.write_to(f)
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
