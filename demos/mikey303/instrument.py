from sv.instruments import SVInstrumentBase, SVTrigBlock, load_yaml
# from sv.model import SVChromaticSampleTrig, SVNoteOffTrig, SVModTrig
from sv.model import SVNoteOffTrig, SVModTrig
from demos.mikey303.model import SVChromaticSampleTrig

import rv
import rv.api

class Three03(SVInstrumentBase):

    Modules = load_yaml(__file__, "modules.yaml")
    
    def __init__(self, container, namespace, sample,
                 relative_note = 0,
                 filter_resonance = "575", # no idea re format; doesn't seem to correspond to either of the values in the UI; max seems to be around "599"
                 echo_wet = 64, # '2000'
                 echo_feedback = 64, # '2000'
                 reverb_wet = 2): # setting as integer as easier when wanting tiny amounts only
        super().__init__(container = container,
                         namespace = namespace,
                         root = rv.note.NOTE.C5 + relative_note)
        self.sample = sample
        self.defaults = {"Filter": {"resonance": filter_resonance},
                         "Echo": {"wet": echo_wet,
                                  "feedback": echo_feedback},
                         "Reverb": {"wet": reverb_wet}}

    def note(self,
             note = 0,
             volume = 1.0,
             attack_ms = "0008",
             decay_ms = "0018",
             sustain_level = "0800",
             sustain_term = None,
             release_ms = "0300",
             filter_freq = "4000"):
        trigs = [SVChromaticSampleTrig(target = f"{self.namespace}MultiSynth",
                                       sample_mod = f"{self.namespace}Sampler",
                                       sample = self.sample,
                                       note = note,
                                       vel = volume),
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
