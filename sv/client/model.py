from sv.client.colours import Colour
from sv.core.container import SVContainer
from sv.core.project import load_class

import sv # so machine classes can be dynamically accessed

DefaultColour = Colour([127, 127, 127])

class SequenceBase:

    def __init__(self, name, machine, seeds, muted = False):
        self.name = name
        self.machine = machine
        self.seeds = seeds
        self.muted = muted    
    
    def render(self, container, generators, colour):
        machine_class = load_class(self.machine)
        machine = machine_class(
            container=container,
            namespace=self.name.capitalize(),
            colour=colour,
            **self.machine_kwargs
        )
        container.add_machine(machine)
        for generator in generators:
            machine.render(generator=generator,
                           seeds=self.seeds,
                           env=self.env)

class Sequences(list):

    def __init__(self, sequences = None):
        list.__init__(self, sequences if sequences else [])

    def clone(self):
        return Sequences([sequence.clone() for sequence in self])

    def render(self, container, generators, colours,
               default_colour = DefaultColour):
        for sequence in self:
            if not sequence.muted:
                colour = colours[sequence.name] if sequence.name in colours else default_colour
                sequence.render(container = container,
                             generators = generators,
                             colour = colour)

    def mute(self, mute_fn):        
        for sequence in self:
            sequence.muted = mute_fn(sequence)            
                
class Patch:
    
    def __init__(self, sequences = None, frozen = False):
        self.sequences = sequences if sequences else Sequences()
        self.frozen = frozen

    def clone(self):
        return Patch(sequences = self.sequences.clone(),
                     frozen = self.frozen)

    def render(self, container, generators, machine_colours):
        self.sequences.render(container = container,
                           generators = generators,
                           colours = machine_colours)

    def mute(self, mute_fn):
        self.sequences.mute(mute_fn)
        
class Patches(list):
    
    def __init__(self, patches = None):
        list.__init__(self, patches if patches else [])

    def clone(self):
        return Patches([patch.clone() for patch in self])
        
    def render(self, container, generators, colours, firewall,
               default_colour = DefaultColour):
        for i, patch in enumerate(self):
            machine_colours = colours["machines"] if "machines" in colours else {}
            patch_colour = colours["patches"][i] if "patches" in colours else default_colour
            container.spawn_patch(patch_colour)
            patch.render(container = container,
                         generators = generators,
                         machine_colours = machine_colours)
            if firewall:
                container.spawn_patch(patch_colour)

    def mute(self, mute_fn):
        for patch in self:
            patch.mute(mute_fn)
                
    def freeze(self, n):
        for i, patch in enumerate(self):
            patch.frozen = i < n            
    
class Project:
    
    def __init__(self, patches = None):
        self.patches = patches if patches else Patches()
        
    def render(self, generators, bpm, n_ticks,
               bank = None,
               firewall = False,
               colours = {}):
        container = SVContainer(bank = bank,
                                bpm = bpm,
                                n_ticks = n_ticks)
        self.patches.render(container = container,
                            generators = generators,
                            colours = colours,
                            firewall = firewall)
        return container

    def mute(self, mute_fn):
        self.patches.mute(mute_fn)
                
    def freeze(self, n):
        self.patches.freeze(n)
        
    def clone(self):
        return Project(patches = self.patches.clone())

if __name__ == "__main__":
    pass
