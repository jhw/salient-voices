# from rv.note import Note, NOTECMD

"""
^^^ leads to some weird circular import error
"""

class SVNoteOffTrig:

    def __init__(self, mod, i):
        self.mod = mod
        self.i = i

    @property
    def key(self):
        return self.mod
    
    def render(self,
               *args):
        from rv.note import Note, NOTECMD
        return Note(note = NOTECMD.NOTE_OFF)
        
class SVNoteTrig:

    Volume = 128
    
    def __init__(self, mod, i,
                 sample = None,
                 sample_mod = None,
                 note = None,
                 vel = None):
        self.mod = mod
        self.i = i
        self.sample = sample
        self.sample_mod = sample_mod
        self.note = note
        self.vel = vel        

    @property
    def key(self):
        return self.mod
        
    def render(self,
               modules,
               *args):
        if self.mod not in modules:
            raise RuntimeError("module %s not found" % self.mod)
        if self.sample_mod and self.sample_mod not in modules:
            raise RuntimeError("module %s not found" % self.sample_mod)
        mod = modules[self.mod]
        sample_mod = modules[self.sample_mod] if self.sample_mod else mod
        if self.note:
            if not isinstance(note, int):
                raise RuntimeError(f"note with value {self.note} found; note must be an int")
            note = self.note
        elif self.sample:
            note = 1 + sample_mod.lookup(self.sample)
        else:
            raise RuntimeError("either sample or note must be defined")
        mod_id = 1 + mod.index # NB 1+
        note_kwargs = {
            "module": mod_id,
            "note": note
        }
        if self.vel:
            if not isinstance(self.vel, int):
                raise RuntimeError("velocity of value {self.vel} found; velocity must be an int")
            note_kwargs["vel"] = max(1, int(self.vel * self.Volume))
        from rv.note import Note
        return Note(**note_kwargs)

class SVFXTrig:

    CtrlMult = 256

    def __init__(self, target, value, i):
        self.target = target
        self.value = value
        self.i = i

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
               controllers):
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
        from rv.note import Note
        return Note(module = mod_id,
                    ctl = ctrl_id,
                    val = value)

class SVPatch:

    def __init__(self, trigs, n_ticks):
        self.trigs = trigs
        self.n_ticks = n_ticks

    @property
    def tracks(self):
        tracks = {}
        for trig in self.trigs:
            tracks.setdefault(trig.key, [])
            tracks[trig.key].append(trig)
        return list(tracks.values())
            
if __name__ == "__main__":
    pass
