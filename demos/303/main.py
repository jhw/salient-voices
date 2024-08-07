from sv.banks import SVBank
from sv.model import SVNoteTrig, SVNoteOffTrig, SVFXTrig, SVPatch
from sv.project import SVProject

import io
import os
import yaml
import zipfile

def load_yaml(attr):
    return yaml.safe_load(open(f"demos/303/{attr}.yaml").read())

Modules = load_yaml("modules")

def single_shot_bank(bank_name, file_path):
    with open(file_path, 'rb') as wav_file:
        wav_data = wav_file.read()
    zip_buffer = io.BytesIO()
    zip_file = zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False)
    file_name = file_path.split("/")[-1]
    zip_file.writestr(file_name, wav_data)
    return SVBank(name = bank_name,
                 zip_file = zip_file)

def single_note(sample, note, adsr, filter_max, filter_resonance, i, length = 1):
    return [SVNoteTrig(mod = "MultiSynth",
                       sample_mod = "Sampler",
                       sample = sample,
                       note = note,
                       i = i),                 
            SVFXTrig(target = "ADSR/attack_ms",
                     value = adsr[0],
                     i = i),
            SVFXTrig(target = "ADSR/decay_ms",
                     value = adsr[1],
                     i = i),
            SVFXTrig(target = "ADSR/sustain_level",
                     value = adsr[2],
                     i = i),
            SVFXTrig(target = "ADSR/release_ms",
                     value = adsr[3],
                     i = i),
            SVFXTrig(target = "Sound2Ctl/out_max",
                     value = filter_max,
                     i = i),
            SVFXTrig(target = "Filter/resonance",
                     value = filter_resonance,
                     i = i),
            SVNoteOffTrig(mod = "MultiSynth",
                          i = i + length)]
    
if __name__ == "__main__":
    try:
        bank = single_shot_bank(bank_name = "mikey303",
                                file_path = "demos/303/303 VCO SQR.wav")
        trigs = single_note(sample = "mikey303/303 VCO SQR.wav",
                            note = 56,
                            adsr = ["0010",
                                    "0010",
                                    "0800",
                                    "0300"],
                            filter_max = "5000",
                            filter_resonance = "7000",
                            i = 0,
                            length = 1)
        patch = SVPatch(trigs = trigs,
                        n_ticks = 8)
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
