import rv

class SVNoteOffTrig:

    def __init__(self, mod, i):
        self.mod = mod
        self.i = i

    @property
    def key(self):
        return self.mod
    
    def render(self,
               *args):
        return rv.note.Note(note = rv.note.NOTECMD.NOTE_OFF)
        
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
            if not isinstance(self.note, int):
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
            note_kwargs["vel"] = max(1, int(self.vel * self.Volume))
        return rv.note.Note(**note_kwargs)

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
        return rv.note.Note(module = mod_id,
                            ctl = ctrl_id,
                            val = value)

class SVPatch:

    def __init__(self, trigs, n_ticks):
        self.trigs = trigs
        self.n_ticks = n_ticks

    def tracks(self, mod_names):
        tracks = {mod_name: {} for mod_name in mod_names}
        for trig in self.trigs:
            tracks[trig.mod].setdefault(trig.key, [])
            tracks[trig.mod][trig.key].append(trig)
        # START TEMP CODE
        """
        tracks = {k:v for k, v in tracks.items()
                  if v != {}}
        """
        # END TEMP CODE
        return tracks

    def update_pool(self, mod_names, pool):
        for _, group in self.tracks(mod_names).items():
            for _, track in group.items():
                for trig in track:
                    if (hasattr(trig, "sample") and trig.sample):
                        pool.add(trig.sample)

    
if __name__ == "__main__":
    pass
