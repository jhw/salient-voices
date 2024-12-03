from sv.machines import SVSamplerMachine, SVMachineTrigs, load_yaml
from sv.trigs import SVNoteOffTrig, SVModTrig, SVSampleTrig

import rv
import rv.api

class Berlin(SVSamplerMachine):

    Modules = load_yaml(__file__, "modules.yaml")
    
    def __init__(self, container, namespace, sample,
                 relative_note = 0,
                 filter_resonance = "575", # no idea re format; doesn't seem to correspond to either of the values in the UI; max seems to be around "599"
                 echo_delay = 36,
                 echo_delay_unit = 3, # tick
                 echo_wet = 32, # '1000'
                 echo_feedback = 32, # '1000'
                 reverb_wet = 2, # setting as integer as easier when wanting tiny amounts only
                 colour = [127, 127, 127]):
        super().__init__(container = container,
                         namespace = namespace,
                         root = rv.note.NOTE.C5 + relative_note,
                         colour = colour)
        self.sample = sample
        self.defaults = {"Filter": {"resonance": filter_resonance},
                         "Echo": {"wet": echo_wet,
                                  "feedback": echo_feedback,
                                  "delay": echo_delay,
                                  "delay_unit": echo_delay_unit},
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
        cloned_sample = self.sample.clone()
        cloned_sample["note"] = note
        trigs = [SVSampleTrig(target = f"{self.namespace}MultiSynth",
                              sampler_mod = f"{self.namespace}Sampler",
                              sample = cloned_sample,
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
        return SVMachineTrigs(trigs = trigs)

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
        return SVMachineTrigs(trigs = trigs)

    
if __name__ == "__main__":
    pass
