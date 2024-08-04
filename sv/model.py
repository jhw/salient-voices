from core import load_class

class SVNoteTrig:

    Volume = 128
    
    def __init__(self, mod, i,
                 sample = None,
                 note = None,
                 vel = 1):
        self.mod = mod
        self.i = i
        self.sample = sample
        self.note = note
        self.vel = vel        

    @property
    def key(self):
        return self.mod
        
    def render(self,
               modules,
               *args):
        if self.mod not in modules:
            raise RuntimeError("mod %s not found" % self.mod)
        mod = modules[self.mod]
        mod_id = 1+mod.index # NB 1+
        note = 1+(mod.lookup(self.sample) if self.sample else self.note)
        vel = max(1, int(self.vel*self.Volume))
        from rv.note import Note
        return Note(module = mod_id,
                    note = note,
                    vel = vel)

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
            raise RuntimeError("mod %s not found" % self.mod)
        mod, controller = modules[self.mod], controllers[self.mod]
        mod_id = 1+mod.index # NB 1+
        if self.ctrl not in controller:
            raise RuntimeError("ctrl %s not found in mod %s" % (self.ctrl,
                                                                self.mod))
        ctrl_id = self.CtrlMult*controller[self.ctrl]
        from rv.note import Note
        return Note(module = mod_id,
                    ctl = ctrl_id,
                    val = self.value)

class SVTracks(dict):

    def __init__(self, n_ticks, item = {}):
        dict.__init__(self)
        self.n_ticks = n_ticks

class SVMachines(list):
    
    @classmethod
    def randomise(self,
                  machines,
                  **kwargs):
        return SVMachines([load_class(machine["class"]).randomise(machine = machine,
                                                                  **kwargs)
                           for machine in machines])
    
    def __init__(self, machines):
        list.__init__(self, [load_class(machine["class"])(machine = machine)
                             for machine in machines])
        
    def clone(self):
        return SVMachines([machine.clone()
                           for machine in self])
    
class SVPatch(dict):
    
    @classmethod
    def randomise(self, machines, **kwargs):
        return SVPatch(machines = SVMachines.randomise(machines = machines,
                                                       **kwargs))
        
    def __init__(self,
                 machines):
        dict.__init__(self, {"machines": SVMachines(machines)})
        
    def clone(self):
        return SVPatch(machines = self["machines"].clone())

    def render(self,
               n_ticks,
               density,
               temperature,
               mutes = []):
        tracks = SVTracks(n_ticks = n_ticks)
        for machine in self["machines"]:
            volume = 1 if machine["name"] not in mutes else 0
            for trig in machine.render(n_ticks = n_ticks,
                                       density = density,
                                       temperature = temperature,
                                       volume = volume):
                tracks.setdefault(trig.key, [])
                tracks[trig.key].append(trig)
        return tracks
        
if __name__ == "__main__":
    pass
