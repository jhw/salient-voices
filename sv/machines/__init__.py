from random import Random

import copy
import yaml

def load_yaml(base_path, file_name):
    return yaml.safe_load(open("/".join(base_path.split("/")[:-1] + [file_name])).read())

class SVTrigBlock:

    def __init__(self, trigs):
        self.trigs = trigs
                 
    def render(self, i):
        trigs = []
        for trig in self.trigs:
            trig.increment(i)
            trigs.append(trig)
        return trigs
        
class SVMachine:

    def __init__(self, container, namespace, root = None):
        self.container = container
        self.namespace = namespace.lower().capitalize()
        self.root = root
        self.defaults = {}

    def render(self, generator,
               seeds = {},
               env = {}):
        rand = {key: Random(value)
                 for key, value in seeds.items()}
        for i, trig_block in generator(self,
                                       rand = rand,
                                       n = self.container.n_ticks,
                                       **env):
            trigs = trig_block.render(i)
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
            if self.root:
                mod["root"] = self.root
        return modules
        
if __name__ == "__main__":
    pass
