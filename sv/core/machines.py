from sv.core.project import SVModule

from random import Random

import copy

import rv

class SVMachine:

    Modules = []
    
    def __init__(self, container, namespace, colour = [127, 127, 127]):
        self.container = container
        self.namespace = namespace.lower().capitalize()
        self.colour = colour
        self.defaults = {}

    def render(self, generator,
               seeds = {},
               env = {}):
        rand = {key: Random(value)
                 for key, value in seeds.items()}
        for trigs in generator(self,
                            rand = rand,
                               n = self.container.n_ticks,
                               **env):
            self.container.add_trigs(trigs)

    @property
    def modules(self):
        modules = copy.deepcopy(self.Modules)
        for mod in modules:
            mod_name = mod["name"]
            if mod_name in self.defaults:
                defaults = self.defaults[mod_name]
                mod.setdefault("defaults", {})
                mod["defaults"].update(defaults)
            if "links" in mod:
                for i, link_name in enumerate(mod["links"]):
                    if link_name != "Output":
                        mod["links"][i] = f"{self.namespace}{link_name}"
            mod["name"] = f"{self.namespace}{mod_name}"
            mod["colour"] = self.colour
        return modules

class SVSamplerMachine(SVMachine):

    def __init__(self, container, namespace, colour,
                 root_note = rv.note.NOTE.C5,
                 relative_note = 0):
        super().__init__(container = container,
                         namespace = namespace,
                         colour = colour)
        self.root_note = root_note
        self.relative_note = relative_note

    @property
    def root(self):
        return self.root_note + self.relative_note

    @property
    def modules(self, attrs = ["root"]):
        modules = super().modules
        for mod in modules:
            if SVModule(mod).is_sampler:
                for attr in attrs:
                    mod[attr] = getattr(self, attr)
        return modules
    
if __name__ == "__main__":
    pass
