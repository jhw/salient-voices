from sv.machines import SVSamplerMachine, SVMachineTrigs, load_yaml
from sv.trigs import SVNoteOffTrig, SVModTrig, SVSampleTrig

import rv
import rv.api

class BerlinSound:

    def __init__(self,
                 attack_ms = "0008",
                 decay_ms = "0018",
                 sustain_level = "0800",
                 sustain_term = None,
                 release_ms = "0300",
                 filter_freq = "4000"):
        self.attack_ms = attack_ms
        self.decay_ms = decay_ms
        self.sustain_level = sustain_level
        self.sustain_term = sustain_term
        self.release_ms = release_ms
        self.filter_freq = filter_freq

class Berlin(SVSamplerMachine):

    Modules = load_yaml(__file__, "modules.yaml")
    
    def __init__(self, container, namespace, sample,
                 relative_note = 0,
                 filter_resonance = "575", # no idea re format; doesn't seem to correspond to either of the values in the UI; max seems to be around "599"
                 echo_delay = 36,
                 echo_delay_unit = 3, # tick
                 echo_wet = 32, # '1000'
                 echo_feedback = 32, # '1000'
                 colour = [127, 127, 127],
                 **kwargs):
        super().__init__(container = container,
                         namespace = namespace,
                         root = rv.note.NOTE.C5 + relative_note,
                         colour = colour)
        self.sample = sample
        self.defaults = {"Filter": {"resonance": filter_resonance},
                         "Echo": {"wet": echo_wet,
                                  "feedback": echo_feedback,
                                  "delay": echo_delay,
                                  "delay_unit": echo_delay_unit}}

    @property
    def sound(self):
        return self.sounds[self.sound_index]
        
    def note(self,
             note = 0,
             volume = 1.0,
             level = 1.0):
        sample = self.sample.clone()
        sample["note"] = note
        trigs = [SVSampleTrig(target = f"{self.namespace}MultiSynth",
                              sampler_mod = f"{self.namespace}Sampler",
                              sample = sample,
                              vel = volume * level),
                 SVModTrig(target = f"{self.namespace}Sound2Ctl/out_max",
                           value = self.sound.filter_freq),
                 SVModTrig(target = f"{self.namespace}ADSR/attack_ms",
                           value = self.sound.attack_ms),
                 SVModTrig(target = f"{self.namespace}ADSR/decay_ms",
                           value = self.sound.decay_ms),
                 SVModTrig(target = f"{self.namespace}ADSR/sustain_level",
                           value = self.sound.sustain_level),
                 SVModTrig(target = f"{self.namespace}ADSR/release_ms",
                           value = self.sound.release_ms)]
        if self.sound.sustain_term:
            trigs.append(SVNoteOffTrig(target = f"{self.namespace}MultiSynth",
                                       i = self.sound.sustain_term))
        return SVMachineTrigs(trigs = trigs)

    def modulation(self,
                   level = 1.0,
                   echo_delay = None,
                   echo_wet = None,
                   echo_feedback = None,
                   filter_resonance = None,
                   filter_roll_off = None):
        trigs = []
        if echo_delay:
            delay_level = int(level * controller_value(echo_delay))
            trigs.append(SVModTrig(target = f"{self.namespace}Echo/delay",
                                   value = delay_level))
        if echo_wet:
            wet_level = int(level * controller_value(echo_wet))
            trigs.append(SVModTrig(target = f"{self.namespace}Echo/wet",
                                   value = wet_level))
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
