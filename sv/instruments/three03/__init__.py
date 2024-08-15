from sv.instruments import InstrumentBase, SVNote, load_yaml
from sv.model import SVNoteTrig, SVModTrig

class Three03(InstrumentBase):

    Modules = load_yaml(__file__, "modules.yaml")
    
    def __init__(self, container, namespace, sample,
                 filter_resonance = "575", # max 599; no idea re format
                 echo_wet = 16,
                 echo_feedback = 16,
                 echo_delay = 192,
                 reverb_wet = 2):
        super().__init__(container = container,
                         namespace = namespace)
        self.sample = sample
        self.defaults = {"Filter": {"resonance": filter_resonance},
                         "Echo": {"wet": echo_wet,
                                  "feedback": echo_feedback,
                                  "delay": echo_delay},
                         "Reverb": {"wet": reverb_wet}}

    def pluck(self,
              note = 0,
              slide_to = False,
              slide_to_level = "0030",
              attack_ms = "0008",
              decay_ms = "0018",
              sustain_level = "0800",
              release_ms = "0300",
              filter_freq = "4000"):
        trigs = [SVNoteTrig(mod = f"{self.namespace}MultiSynth",
                            sample_mod = f"{self.namespace}Sampler",
                            sample = self.sample,
                            note = note),
                 SVModTrig(target = f"{self.namespace}Sound2Ctl/out_max",
                          value = filter_freq)]
        if not slide_to:            
            trigs += [SVModTrig(target = f"{self.namespace}ADSR/attack_ms",
                               value = attack_ms),
                      SVModTrig(target = f"{self.namespace}ADSR/decay_ms",
                               value = decay_ms),
                      SVModTrig(target = f"{self.namespace}ADSR/sustain_level",
                               value = sustain_level),
                      SVModTrig(target = f"{self.namespace}ADSR/release_ms",
                                value = release_ms)]
        else:
            """
            Now what? There's no support for built in effects controllers!
            """
            pass            
        return SVNote(trigs = trigs)
    
if __name__ == "__main__":
    pass
