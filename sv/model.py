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
        from rv.note import Note
        return Note(module = mod_id,
                    ctl = ctrl_id,
                    val = self.value)

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
