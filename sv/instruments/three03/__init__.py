from sv.instruments import InstrumentBase, load_yaml
from sv.model import SVNoteTrig, SVNoteOffTrig, SVFXTrig

class Three03(InstrumentBase):

    Modules = load_yaml(__file__, "modules.yaml")
    
    def __init__(self, container, namespace, sample,
                 filter_resonance = "585", # max 599; no idea re format
                 echo_wet = 64,
                 echo_feedback = 64,
                 echo_delay = 192,
                 reverb_wet = 4):
        super().__init__(container = container,
                         namespace = namespace)
        self.sample = sample
        self.defaults = {"Filter": {"resonance": filter_resonance},
                         "Echo": {"wet": echo_wet,
                                  "feedback": echo_feedback,
                                  "delay": echo_delay},
                         "Reverb": {"wet": reverb_wet}}

    def pluck(self,
              note, i,
              attack_ms = "0010",
              decay_ms = "0010",
              sustain_level = "0800",
              sustain_periods = 1,
              release_ms = "0300",
              filter_freq = "4000"):
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
                         value = filter_freq,
                         i = i),
                SVNoteOffTrig(mod = f"{self.namespace}MultiSynth",
                              i = i + sustain_periods)]
    
if __name__ == "__main__":
    pass
