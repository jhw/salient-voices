import rv

def hex_value(value):
    try:
        return int(value, 16)
    except ValueError:
        raise RuntimeError(f"couldn't parse {value} as hex")

def controller_value(value):
    if isinstance(value, str):
        return hex_value(value)
    elif isinstance(value, int):
        return value
    else:
        raise RuntimeError(f"controller_value supports int and hex string only [{value}]")
    
class SVTrigBase:

    def __init__(self, target, i):
        self.target = target
        self.i = i

    def set_position(self, i):
        self.i += i

class SVNoteTrigBase(SVTrigBase):

    Volume = 128
        
    def __init__(self, target,
                 i = 0,
                 vel = None,
                 fx_value = None):
        super().__init__(target = target,
                         i = i)
        self.vel = vel
        self.fx_value = fx_value

    @property
    def mod(self):
        return self.target.split("/")[0]

    """
    - NB explicit None check; a vel of 0 should still register as a vel
    """
    
    @property
    def has_vel(self):
        return self.vel != None

    """
    - NB a zero will be rendered by RV as a null which will be rendered by Sunvox as "volume missing; use default value"
    """

    @property
    def velocity(self):        
        return max(1, int(self.vel * self.Volume))
    
    @property
    def has_fx(self):
        return len(self.target.split("/")) > 1
    
    @property
    def fx(self):
        return int(self.target.split("/")[1])
    
    @property
    def key(self):
        return self.mod
        
class SVNoteTrig(SVNoteTrigBase):

    def __init__(self, target,
                 i = 0,
                 note = None,
                 vel = None,
                 fx_value = None):
        super().__init__(target = target,
                         i = i,
                         vel = vel,
                         fx_value = fx_value)
        self.note = note

    def render(self, modules, *args):
        mod = modules[self.mod]
        note = self.note
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

class SVSampleTrig(SVNoteTrigBase):

    def __init__(self, target, sample,
                 sampler_mod = None,
                 i = 0,
                 vel = None,
                 fx_value = None):
        super().__init__(target = target,
                         i = i,
                         vel = vel,
                         fx_value = fx_value)
        self.sample = sample
        self.sampler_mod = sampler_mod

    def resolve_sampler(self):
        return self.sampler_mod if self.sampler_mod else self.mod

    def resolve_sampler_note(self, modules):
        sampler_mod = modules[self.sampler_mod if self.sampler_mod else self.mod]
        note = 1 + sampler_mod.index_of(self.sample)
        return note
    
    def render(self, modules, *args):
        mod = modules[self.mod]        
        mod_id = 1 + mod.index
        note = self.resolve_sampler_note(modules)
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
        
class SVNoteOffTrig(SVTrigBase):

    def __init__(self, target, i = 0):
        super().__init__(target = target,
                         i = i)
    
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
        mod = modules[self.mod]
        mod_id = 1 + mod.index
        value = controller_value(self.value)
        return rv.note.Note(module = mod_id,
                            pattern = self.fx,
                            val = value)
    
class SVModTrig(SVTrigBase):

    CtrlMult = 256

    def __init__(self, target, value, i = 0):
        super().__init__(target = target,
                         i = i)
        self.value = value

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
        mod, controller = modules[self.mod], controllers[self.mod]
        mod_id = 1 + mod.index
        ctrl_id = self.CtrlMult * controller[self.ctrl]
        value = controller_value(self.value)
        return rv.note.Note(module = mod_id,
                            ctl = ctrl_id,
                            val = value)

if __name__ == "__main__":
    pass
