from sv.model import SVTrigPatch
from sv.project import SVProject

class SVContainer:

    def __init__(self,
                 banks = [],
                 bpm = 120,
                 n_ticks = 16,
                 wash = False,
                 breaks = False):
        self.banks = banks
        self.bpm = bpm
        self.n_ticks = n_ticks
        self.wash = wash
        self.breaks = breaks
        self.instruments = []
        self.patches = []
        self.spawn_patch()

    def spawn_patch(self):
        self.patches.append(SVTrigPatch(n_ticks = self.n_ticks))

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
         return SVProject().render_project(patches = self.patches,
                                           modules = self.modules,
                                           banks = self.banks,
                                           bpm = self.bpm,
                                           wash = self.wash,
                                           breaks = self.breaks)
        
if __name__ == "__main__":
    pass
