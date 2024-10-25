from sv.instruments import InstrumentBase, SVTrigBlock

import yaml

FXModules = yaml.safe_load("""
- name: Echo
  class: rv.modules.echo.Echo
  defaults:
    dry: 256
    wet: 256
    delay: 36
    delay_unit: 3 # tick
  links:
    - Output
""")

class Nine09(InstrumentBase):

    Modules = []
    
    def __init__(self, container, namespace, machine_config):
        self.defaults = {}
        for machine_conf in machine_config:
            mod_name = f"{machine_conf['tag'].capitalize()}Sampler"            
            mod = {"name": mod_name,
                   "class": "sv.sample.SVSlotSampler",
                   "links": ["Echo"]}
            self.Modules.append(mod)
        self.Modules += FXModules

    def note(self):
        trigs = []
        return SVTrigBlock(trigs = trigs)

    def modulation(self):
        trigs = []
        return SVTrigBlock(trigs = trigs)
    
if __name__ == "__main__":
    pass
