from sv.model import SVTrigPatch
from sv.project import SVProject

import os

class SVContainerPatch:

    def __init__(self, n_ticks):
        self.trig_patch = SVTrigPatch(n_ticks = n_ticks)

    def add_trigs(self, trigs):
        self.trig_patch.add_trigs(trigs)

class SVContainerPatches(list):

    def __init__(self, patches = []):
        list.__init__(self, patches)

    def spawn_patch(self, n_ticks):
        self.append(SVContainerPatch(n_ticks = n_ticks))

class SVInstruments(list):

    def __init__(self, instruments = []):
        list.__init__(self, instruments)
        
class SVContainer:

    def __init__(self,
                 banks = [],
                 bpm = 120,
                 n_ticks = 16):
        self.banks = banks
        self.bpm = bpm
        self.n_ticks = n_ticks
        self.instruments = SVInstruments()
        self.patches = SVContainerPatches()

    def spawn_patch(self):
        self.patches.spawn_patch(self.n_ticks)

    def add_instrument(self, instrument):
        self.instruments.append(instrument)

    @property
    def modules(self):
        modules = []
        for instrument in self.instruments:
            modules += instrument.modules
        return modules

    def add_trigs(self, trigs):
        self.patches[-1].add_trigs(trigs)

    def render_project(self):
        patches = [patch.trig_patch for patch in self.patches]
        return SVProject().render_project(patches = patches,
                                          modules = self.modules,
                                          banks = self.banks,
                                          bpm = self.bpm)

    def write_project(self, filename):
        path_to_filename = "/".join(filename.split("/")[:-1])
        if not os.path.exists(path_to_filename):
            os.makedirs(path_to_filename)
        project = self.render_project()
        with open(filename, 'wb') as f:            
            project.write_to(f)
              
if __name__ == "__main__":
    pass
