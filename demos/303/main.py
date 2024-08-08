from sv.banks import single_shot_bank
from sv.model import SVNoteTrig, SVNoteOffTrig, SVFXTrig, SVPatch
from sv.project import SVProject

import os
import yaml

def load_yaml(attr):
    return yaml.safe_load(open(f"demos/303/{attr}.yaml").read())

Modules = load_yaml("modules")

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
        patches = []
        for i in range(2):
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
                            n_ticks = 16)
            patches.append(patch)
        project = SVProject().render_project(patches = patches,
                                             modules = Modules,
                                             banks = [bank],
                                             bpm = 124,
                                             wash = True,
                                             breaks = True)
        if not os.path.exists("tmp"):
            os.mkdir("tmp")
        with open("tmp/demo-303.sunvox", 'wb') as f:
            project.write_to(f)
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
