from sv.instruments import InstrumentBase, load_yaml, add_to_patch
from sv.model import SVNoteTrig, SVNoteOffTrig, SVFXTrig

class Three03(InstrumentBase):

    Modules = load_yaml(__file__, "modules.yaml")
    
    def __init__(self, container, namespace, sample = "mikey303/303 VCO SQR.wav"):
        super().__init__(container = container,
                         namespace = namespace)
        self.sample = sample

    @add_to_patch
    def hello_world(self,
                    note, i,
                    attack_ms = "0010",
                    decay_ms = "0010",
                    sustain_level = "0800",
                    sustain_periods = 1,
                    release_ms = "0300",
                    filter_freq_max = "5000",
                    filter_resonance = "7000"):
        return [SVNoteTrig(mod = f"{self.namespace}MultiSynth",
                           sample_mod = f"{self.namespace}Sampler",
                           sample = self.sample,
                           note = note,
                           i = i),                 
                SVFXTrig(target = f"{self.namespace}ADSR/attack_ms",
                         value = attack_ms,
                         i = i),
                SVFXTrig(target = f"{self.namespace}ADSR/decay_ms",
                         value = decay_ms,
                         i = i),
                SVFXTrig(target = f"{self.namespace}ADSR/sustain_level",
                         value = sustain_level,
                         i = i),
                SVFXTrig(target = f"{self.namespace}ADSR/release_ms",
                         value = release_ms,
                         i = i),
                SVFXTrig(target = f"{self.namespace}Sound2Ctl/out_max",
                         value = filter_freq_max,
                         i = i),
                SVFXTrig(target = f"{self.namespace}Filter/resonance",
                         value = filter_resonance,
                         i = i),
                SVNoteOffTrig(mod = f"{self.namespace}MultiSynth",
                              i = i + sustain_periods)]
    
if __name__ == "__main__":
    pass
