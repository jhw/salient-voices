from sv.model import SVNoteTrigBase

import rv

class SVChromaticSampleTrig(SVNoteTrigBase):

    def __init__(self, target,
                 i = 0,
                 sample = None,
                 sample_mod = None,
                 note = None,
                 vel = None,
                 fx_value = None):
        super().__init__(target = target,
                         i = i,
                         vel = vel,
                         fx_value = fx_value)
        self.sample = sample
        self.sample_mod = sample_mod
        self.note = note

    def clone(self):
        return SVChromaticSampleTrig(target = self.target,
                                     i = self.i,
                                     sample = self.sample,
                                     sample_mod = self.sample_mod,
                                     note = self.note,
                                     vel = self.vel,
                                     fx_value = self.fx_value)
        
    def render(self, modules, *args):
        if self.mod not in modules:
            raise RuntimeError("module %s not found" % self.mod)
        if self.sample_mod and self.sample_mod not in modules:
            raise RuntimeError("module %s not found" % self.sample_mod)
        mod = modules[self.mod]
        sample_mod = modules[self.sample_mod] if self.sample_mod else mod
        root_note = 1 + sample_mod.index_of(self.sample)
        offset = self.note
        note = root_note + offset
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

    
