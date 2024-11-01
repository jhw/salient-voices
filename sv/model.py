from sv.sampler import SVSlotSampler, SVChromaticSampler

import rv

def parse_value(value):
    if isinstance(value, str):
        try:
            return int(value, 16)
        except ValueError:
            raise RuntimeError(f"couldn't parse FX value {value} as hex string")
    elif isinstance(value, int):
        return value
    else:
        raise RuntimeError(f"FX value of {value} found; must be int or hex string")

class SVTrigBase:

    def __init__(self, target, i):
        self.target = target
        self.i = i

    def increment(self, i):
        self.i += i
        
class SVNoteTrig(SVTrigBase):

    Volume = 128
    
    def __init__(self, target,
                 i = 0,
                 sample = None,
                 sample_mod = None,
                 note = None,
                 vel = None,
                 value = None):
        super().__init__(target = target,
                         i = i)
        self.sample = sample
        self.sample_mod = sample_mod
        self.note = note
        self.vel = vel
        self.value = value

    def clone(self):
        return SVNoteTrig(target = self.target,
                          i = self.i,
                          sample = self.sample,
                          sample_mod = self.sample_mod,
                          note = self.note,
                          vel = self.vel)

    @property
    def mod(self):
        return self.target.split("/")[0]

    @property
    def has_fx(self):
        return len(self.target.split("/")) > 1
    
    @property
    def fx(self):
        return int(self.target.split("/")[1])
    
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
        mod_id = 1 + mod.index
        note_kwargs = {
            "module": mod_id,
            "note": note
        }
        if self.vel:
            note_kwargs["vel"] = max(1, int(self.vel * self.Volume))
        if self.has_fx and self.value:
            note_kwargs["pattern"] = self.fx
            note_kwargs["val"] = self.value
        return rv.note.Note(**note_kwargs)

class SVNoteOffTrig(SVTrigBase):

    def __init__(self, target, i = 0):
        super().__init__(target = target,
                         i = i)
    
    def clone(self):
        return SVNoteOffTrig(target = self.target,
                             i = self.i)

    @property
    def mod(self):
        return self.target.split("/")[0]

    @property
    def key(self):
        return self.mod
    
    def render(self, *args):
        return rv.note.Note(note = rv.note.NOTECMD.NOTE_OFF)

class SVFXTrig(SVTrigBase):

    def __init__(self, target, value, i = 0):
        super().__init__(target = target,
                         i = i)
        self.value = value

    def clone(self):
        return SVFXTrig(target = self.target,
                        value = self.value,
                        i = self.i)

    @property
    def mod(self):
        return self.target.split("/")[0]

    @property
    def fx(self):
        return int(self.target.split("/")[1])

    @property
    def key(self):
        return self.target
    
    def render(self, modules, *args):
        if self.mod not in modules:
            raise RuntimeError("module %s not found" % self.mod)
        mod = modules[self.mod]
        mod_id = 1 + mod.index
        value = parse_value(self.value)
        return rv.note.Note(module = mod_id,
                            pattern = self.fx,
                            val = value)
    
class SVModTrig(SVTrigBase):

    CtrlMult = 256

    def __init__(self, target, value, i = 0):
        super().__init__(target = target,
                         i = i)
        self.value = value

    def clone(self):
        return SVModTrig(target = self.target,
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
        mod_id = 1 + mod.index
        if self.ctrl not in controller:
            raise RuntimeError("controller %s not found in module %s" % (self.ctrl,
                                                                         self.mod))
        ctrl_id = self.CtrlMult*controller[self.ctrl]
        value = parse_value(self.value)
        return rv.note.Note(module = mod_id,
                            ctl = ctrl_id,
                            val = value)

class SVTrigPatch:
    
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
