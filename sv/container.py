from sv.project import SVProject

import os

class SVTrigPatch:
    
    def __init__(self, n_ticks, trigs = [], colour = [128, 128, 128]):
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
                 banks = [],
                 bpm = 120,
                 n_ticks = 16):
        self.banks = banks
        self.bpm = bpm
        self.n_ticks = n_ticks
        self.machines = []
        self.patches = []

    def spawn_patch(self):
        self.patches.append(SVTrigPatch(n_ticks = self.n_ticks,
                                        trigs = [])) # NB force reset

    def add_machine(self, machine):
        self.machines.append(machine)

    @property
    def modules(self):
        modules = {}
        for machine in self.machines:            
            modules.update({mod["name"]:mod for mod in machine.modules})
        return list(modules.values())

    def add_trigs(self, trigs):
        self.patches[-1].add_trigs(trigs)

    def render_project(self):
        return SVProject().render_project(patches = self.patches,
                                          modules = self.modules,
                                          banks = self.banks,
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
