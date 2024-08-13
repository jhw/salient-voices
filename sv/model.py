from sv.sampler import SVSlotSampler, SVChromaticSampler

import rv

class SVTrigBase:

    def __init__(self, i):
        self.i = i

    def increment(self, i):
        self.i += i

class SVNoteOffTrig(SVTrigBase):

    def __init__(self, mod, i = 0):
        super().__init__(i = i)
        self.mod = mod

    def clone(self):
        return SVNoteOffTrig(mod = self.mod,
                             i = self.i)

    @property
    def key(self):
        return self.mod
    
    def render(self, *args):
        return rv.note.Note(note = rv.note.NOTECMD.NOTE_OFF)
        
class SVNoteTrig(SVTrigBase):

    Volume = 128
    
    def __init__(self, mod,
                 i = 0,
                 sample = None,
                 sample_mod = None,
                 note = None,
                 vel = None):
        super().__init__(i = i)
        self.mod = mod
        self.sample = sample
        self.sample_mod = sample_mod
        self.note = note
        self.vel = vel        

    def clone(self):
        return SVNoteTrig(mod = self.mod,
                          i = self.i,
                          sample = self.sample,
                          sample_mod = self.sample_mod,
                          note = self.note,
                          vel = self.vel)
    
    @property
    def key(self):
        return self.mod
        
    def render(self, modules, *args):
        if self.mod not in modules:
            raise RuntimeError("module %s not found" % self.mod)
        if self.sample_mod and self.sample_mod not in modules:
            raise RuntimeError("module %s not found" % self.sample_mod)
        mod = modules[self.mod]
        sample_mod = modules[self.sample_mod] if self.sample_mod else mod
        if isinstance(sample_mod, SVSlotSampler):
            note = 1 + sample_mod.index_of(self.sample)
        elif isinstance(sample_mod, SVChromaticSampler):
            root_note = 1 + sample_mod.index_of(self.sample)
            offset = self.note
            note = root_note + offset
        else:
            note = self.note
        mod_id = 1 + mod.index # NB 1+
        note_kwargs = {
            "module": mod_id,
            "note": note
        }
        if self.vel:
            note_kwargs["vel"] = max(1, int(self.vel * self.Volume))
        return rv.note.Note(**note_kwargs)

class SVFXTrig(SVTrigBase):

    CtrlMult = 256

    def __init__(self, target, value, i = 0):
        super().__init__(i = i)
        self.target = target
        self.value = value

    def clone(self):
        return SVFXTrig(target = self.target,
                        value = self.value,
                        i = self.i)
    
    @property
    def mod(self):
        return self.target.split("/")[0]

    @property
    def ctrl(self):
        return self.target.split("/")[1]

    @property
    def key(self):
        return self.target
        
    def render(self,
               modules,
               controllers,
               *args):
        if (self.mod not in modules or
            self.mod not in controllers):
            raise RuntimeError("module %s not found" % self.mod)
        mod, controller = modules[self.mod], controllers[self.mod]
        mod_id = 1 + mod.index # NB 1+
        if self.ctrl not in controller:
            raise RuntimeError("controller %s not found in module %s" % (self.ctrl,
                                                                         self.mod))
        ctrl_id = self.CtrlMult*controller[self.ctrl]
        if isinstance(self.value, str):
            try:
                value = int(self.value, 16)
            except ValueError:
                raise RuntimeError(f"couldn't parse {self.value} as hex string")
        elif isinstance(self.value, int):
            value = self.value
        else:
            raise RuntimeError(f"fx value of {self.value} found; must be int or hex string")
        return rv.note.Note(module = mod_id,
                            ctl = ctrl_id,
                            val = value)

class SVPatch:

    def __init__(self, n_ticks, trigs = []):
        self.trigs = trigs
        self.n_ticks = n_ticks

    def add_trigs(self, trigs):
        self.trigs += trigs
        
    def trig_groups(self, mod_names):
        groups = {mod_name: {} for mod_name in mod_names}
        for trig in self.trigs:
            if trig.mod not in groups:
                raise RuntimeError(f"trig mod {trig.mod} not found in modules")
            groups[trig.mod].setdefault(trig.key, [])
            groups[trig.mod][trig.key].append(trig)
        return groups

    def populate_pool(self, mod_names, pool):
        for group in self.trig_groups(mod_names).values():
            for trigs in group.values():
                for trig in trigs:
                    if (hasattr(trig, "sample") and trig.sample):
                        pool.add(trig.sample)

    
if __name__ == "__main__":
    pass
