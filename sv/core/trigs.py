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

class SVNoteTrig(SVTrigBase):

    Volume = 128
        
    def __init__(self, target,
                 i = 0,
                 note = None,
                 vel = None,
                 fx = None,
                 **kwargs):
        super().__init__(target = target,
                         i = i)
        self.note = note
        self.vel = vel
        self.fx = fx

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
    def key(self):
        return self.mod

    @property
    def fx_pattern(self):
        return controller_value(self.fx.split("/")[0])

    @property
    def fx_value(self):
        return controller_value(self.fx.split("/")[1])

    def resolve_note(self, _):
        return self.note

    def render(self, modules, *args):
        mod = modules[self.mod]        
        mod_id = 1 + mod.index
        note = self.resolve_note(modules)
        note_kwargs = {
            "module": mod_id,
            "note": note
        }
        if self.has_vel:
            note_kwargs["vel"] = self.velocity
        if self.fx:
            note_kwargs["ctl"] = self.fx_pattern
            note_kwargs["val"] = self.fx_value
        return rv.note.Note(**note_kwargs)
    
class SVSampleTrig(SVNoteTrig):

    def __init__(self, target, sample,
                 **kwargs):
        super().__init__(target = target,
                         **kwargs)
        self.sample = sample
    
    def resolve_sampler_mod(self, modules):
        return modules[self.mod]
        
    def resolve_note(self, modules):
        mod = self.resolve_sampler_mod(modules)
        note = 1 + mod.index_of(self.sample)
        return note
    
class SVMultiSynthSampleTrig(SVSampleTrig):

    def __init__(self, target, sample, sampler_mod, **kwargs):
        super().__init__(target = target,
                         sample = sample,
                         **kwargs)
        self.sampler_mod = sampler_mod

    def resolve_sampler_mod(self, modules):
        return modules[self.sampler_mod]
            
class SVModTrig(SVTrigBase):

    CtrlMult = 256

    def __init__(self, target, value, **kwargs):
        super().__init__(target = target, **kwargs)            
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

class SVNoteOffTrig(SVTrigBase):

    def __init__(self, target, **kwargs):
        super().__init__(target = target, **kwargs)
    
    @property
    def mod(self):
        return self.target.split("/")[0]

    @property
    def key(self):
        return self.mod
    
    def render(self, *args):
        return rv.note.Note(note = rv.note.NOTECMD.NOTE_OFF)
    
if __name__ == "__main__":
    pass
