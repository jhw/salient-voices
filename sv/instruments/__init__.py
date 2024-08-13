from random import Random

import copy
import yaml

def load_yaml(base_path, file_name):
    return yaml.safe_load(open("/".join(base_path.split("/")[:-1] + [file_name])).read())

class InstrumentBase:

    def __init__(self, container, namespace):
        self.container = container
        self.namespace = namespace
        self.defaults = {}

    def play(self, generator, seeds):
        rand = {key: Random(seed) for key, seed in seeds.items()}
        for trigs in generator(self,
                               rand = rand,
                               n = self.container.n_ticks):
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
        return modules
        
if __name__ == "__main__":
    pass
