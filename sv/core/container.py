from sv.core.project import SVProject

import json
import os

class SVTrigPatch:
    
    def __init__(self, n_ticks, colour, trigs = []):
        self.trigs = trigs
        self.n_ticks = n_ticks
        self.colour = colour

    def add_trigs(self, trigs):
        self.trigs += trigs    
        
    def trig_groups(self, mod_names):
        groups = {mod_name: {} for mod_name in mod_names}
        for trig in self.trigs:
            if trig.mod in mod_names:
                groups[trig.mod].setdefault(trig.key, [])
                groups[trig.mod][trig.key].append(trig)
        return groups
        
class SVContainer:

    def __init__(self,
                 bpm,
                 n_ticks,
                 bank = None):
        self.bank = bank
        self.bpm = bpm
        self.n_ticks = n_ticks
        self.machines = []
        self.patches = []

    def spawn_patch(self, colour = [128, 128, 128]):
        self.patches.append(SVTrigPatch(n_ticks = self.n_ticks,
                                        trigs = [],
                                        colour = colour)) # NB force reset

    def add_machine(self, machine):
        self.machines.append(machine)

    """
    - note that this will overwrite/flatten modules of the same name, hence the need for @validate_namespaces
    - one consequence of this is that colours get flattened; assuming they are randomly chosen then the colour of the modules in the machine will be whatever the colour of the last specified one is
    """
        
    @property
    def flattened_modules(self):
        modules = {}
        for machine in self.machines:        
            modules.update({mod["name"]:mod for mod in machine.modules})
        return list(modules.values())

    def add_trigs(self, trigs):
        self.patches[-1].add_trigs(trigs)

    def validate_namespaces(fn):
        def wrapped(self):
            configs = {}
            for machine in self.machines:
                configs.setdefault(machine.namespace, set())
                struct = {"modules": machine.Modules,
                          "class": str(machine.__class__)}
                configs[machine.namespace].add(json.dumps(struct))
            for k, v in configs.items():
                if len(v) != 1:
                    raise RuntimeError(f"container namespace {k} contains multiple machine confgurations")
            return fn(self)
        return wrapped
        
    @validate_namespaces
    def render_project(self):
        return SVProject().render_project(patches = self.patches,
                                          modules = self.flattened_modules,
                                          bank = self.bank,
                                          bpm = self.bpm)

    def write_project(self, filename):
        path_to_filename = "/".join(filename.split("/")[:-1])
        if (path_to_filename != ""  and
            not os.path.exists(path_to_filename)):
            os.makedirs(path_to_filename)
        project = self.render_project()
        with open(filename, 'wb') as f:            
            project.write_to(f)
              
if __name__ == "__main__":
    pass
