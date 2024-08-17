from sv.instruments import InstrumentBase, SVTrigBlock, load_yaml
from sv.model import SVNoteTrig, SVNoteOffTrig, SVModTrig

class Three03(InstrumentBase):

    Modules = load_yaml(__file__, "modules.yaml")
    
    def __init__(self, container, namespace, sample,
                 filter_resonance = "575", # no idea re format; doesn't seem to correspond to either of the values in the UI; max seems to be around "599"
                 echo_wet = 16, # seems to required integer format; no sure why won't take hex
                 echo_feedback = 16, # seems to required integer format; no sure why won't take hex
                 echo_delay = 192,
                 reverb_wet = 2): # setting as integer as easier when wanting tiny amounts only
        super().__init__(container = container,
                         namespace = namespace)
        self.sample = sample
        self.defaults = {"Filter": {"resonance": filter_resonance},
                         "Echo": {"wet": echo_wet,
                                  "feedback": echo_feedback,
                                  "delay": echo_delay},
                         "Reverb": {"wet": reverb_wet}}

    def note(self,
             note = 0,
             attack_ms = "0008",
             decay_ms = "0018",
             sustain_level = "0800",
             sustain_term = None,
             release_ms = "0300",
             filter_freq = "4000"):
        trigs = [SVNoteTrig(target = f"{self.namespace}MultiSynth",
                            sample_mod = f"{self.namespace}Sampler",
                            sample = self.sample,
                            note = note),
                 SVModTrig(target = f"{self.namespace}Sound2Ctl/out_max",
                          value = filter_freq)]
        trigs += [SVModTrig(target = f"{self.namespace}ADSR/attack_ms",
                            value = attack_ms),
                  SVModTrig(target = f"{self.namespace}ADSR/decay_ms",
                            value = decay_ms),
                  SVModTrig(target = f"{self.namespace}ADSR/sustain_level",
                            value = sustain_level),
                  SVModTrig(target = f"{self.namespace}ADSR/release_ms",
                            value = release_ms)]
        if sustain_term:
            trigs.append(SVNoteOffTrig(target = f"{self.namespace}MultiSynth",
                                       i = sustain_term))
        return SVTrigBlock(trigs = trigs)

    def modulation(self,
                   echo_wet = None,
                   echo_feedback = None,
                   filter_resonance = None,
                   filter_roll_off = None):
        trigs = []
        if echo_wet:
            trigs.append(SVModTrig(target = f"{self.namespace}Echo/wet",
                                   value = echo_wet))
        if echo_feedback:
            trigs.append(SVModTrig(target = f"{self.namespace}Echo/feedback",
                                   value = echo_feedback))
        if filter_resonance:
            trigs.append(SVModTrig(target = f"{self.namespace}Filter/resonance",
                                   value = filter_resonance))
        if filter_roll_off:
            trigs.append(SVModTrig(target = f"{self.namespace}Filter/roll_off",
                                   value = filter_roll_off))
        return SVTrigBlock(trigs = trigs)

    
if __name__ == "__main__":
    pass
