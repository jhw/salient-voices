from sv.instruments import SVInstrumentBase, SVTrigBlock, load_yaml
from sv.model import SVNoteOffTrig, SVModTrig, SVSampleTrig

import rv
import rv.api

class SVMultiSynthSampleTrig(SVSampleTrig):

    def __init__(self, target,
                 i = 0,
                 sample = None,
                 sampler_mod = None,
                 vel = None,
                 fx_value = None):
        super().__init__(target = target,
                         i = i,
                         vel = vel,
                         fx_value = fx_value,
                         sample = sample)
        self.sampler_mod = sampler_mod

    def clone(self):
        return SVMultiSynthSampleTrig(target = self.target,
                                      i = self.i,
                                      sample = self.sample,
                                      sampler_mod = self.sampler_mod,
                                      vel = self.vel,
                                      fx_value = self.fx_value)
        
    def render(self, modules, *args):
        for mod in [self.mod,
                    self.sampler_mod]:
            if mod not in modules:
                raise RuntimeError("module %s not found" % mod)
        mod = modules[self.mod]
        sampler_mod = modules[self.sampler_mod]
        note = 1 + sampler_mod.index_of(self.sample)
        mod_id = 1 + mod.index
        note_kwargs = {
            "module": mod_id,
            "note": note
        }
        if self.has_vel:
            note_kwargs["vel"] = self.velocity
        if self.has_fx and self.fx_value:
            note_kwargs["pattern"] = self.fx
            note_kwargs["val"] = self.fx_value
        return rv.note.Note(**note_kwargs)


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
        cloned_sample = self.sample.clone()
        cloned_sample["note"] = note
        trigs = [SVMultiSynthSampleTrig(target = f"{self.namespace}MultiSynth",
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
