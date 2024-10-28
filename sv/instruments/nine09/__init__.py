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
    
    def __init__(self, container, namespace, channel_names):
        super().__init__(container = container,
                         namespace = namespace)
        self.defaults = {}
        for channel_name in channel_names:
            mod = {"name": channel_name,
                   "class": "sv.sample.SVSlotSampler",
                   "links": ["Echo"]}
            self.Modules.append(mod)
        self.Modules += FXModules

    """
    trigs = [SVNoteTrig(target = f"{self.namespace}MultiSynth",
                        sample_mod = f"{self.namespace}Sampler",
                        sample = self.sample,
                        note = note),
    """
        
    def note(self):
        trigs = []
        return SVTrigBlock(trigs = trigs)

    def modulation(self):
        trigs = []
        return SVTrigBlock(trigs = trigs)
    
if __name__ == "__main__":
    pass
