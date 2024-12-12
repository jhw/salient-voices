from sv.project import SVModule
from sv.trigs import SVModTrig, controller_value

from random import Random

import copy
import rv

class SVMachineTrigs:

    def __init__(self, trigs):
        self.trigs = trigs
                 
    def render(self, i):
        trigs = []
        for trig in self.trigs:
            trig.set_position(i)
            trigs.append(trig)
        return trigs
        
class SVMachine:

    def __init__(self, container, namespace, colour):
        self.container = container
        self.namespace = namespace.lower().capitalize()
        self.colour = colour
        self.defaults = {}

    def render(self, generator,
               seeds = {},
               env = {}):
        rand = {key: Random(value)
                 for key, value in seeds.items()}
        for i, trig_block in generator(self,
                                       rand = rand,
                                       n = self.container.tpb_adjusted_n_ticks,
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
            mod["colour"] = self.colour
        return modules

class SVSamplerMachine(SVMachine):

    def __init__(self, container, namespace, colour, root, cutoff = 1e8):
        super().__init__(container = container,
                         namespace = namespace,
                         colour = colour)
        self.root = root
        self.cutoff = cutoff

    @property
    def modules(self, attrs = ["root", "cutoff"]):
        modules = super().modules
        for mod in modules:
            if SVModule(mod).is_sampler:
                for attr in attrs:
                    mod[attr] = getattr(self, attr)
        return modules

class SVBeatsApi:
    
    def __init__(self, sounds, sound_index=0, **kwargs):
        self.sounds = sounds
        self.sound_index = sound_index

    def toggle_sound(self):
        self.sound_index = 1 - int(self.sound_index > 0)

    def increment_sound(self):
        self.sound_index = (self.sound_index + 1) % len(self.sounds)

    def decrement_sound(self):
        self.sound_index = (self.sound_index - 1) % len(self.sounds)

    def randomise_sound(self, rand):
        self.sound_index = rand.choice(list(range(len(self.sounds))))

    @property
    def sound(self):
        return self.sounds[self.sound_index]

    def modulation(self,
                   level=1.0,
                   echo_delay=None,
                   echo_wet=None,
                   echo_feedback=None):
        trigs = []
        if echo_delay:
            delay_level = int(level * controller_value(echo_delay))
            trigs.append(SVModTrig(target=f"{self.namespace}Echo/delay",
                                   value=delay_level))
        if echo_wet:
            wet_level = int(level * controller_value(echo_wet))
            trigs.append(SVModTrig(target=f"{self.namespace}Echo/wet",
                                   value=wet_level))
        if echo_feedback:
            trigs.append(SVModTrig(target=f"{self.namespace}Echo/feedback",
                                   value=echo_feedback))
        return SVMachineTrigs(trigs=trigs)


    
if __name__ == "__main__":
    pass
