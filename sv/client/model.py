from sv.container import SVContainer
from sv.project import load_class
from sv.client.colours import Colour

import sv # so machine classes can be dynamically accessed

DefaultColour = Colour([127, 127, 127])

class TrackBase:

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

class Tracks(list):

    def __init__(self, tracks = None):
        list.__init__(self, tracks if tracks else [])

    def clone(self):
        return Tracks([track.clone() for track in self])

    def render(self, container, generators, colours,
               default_colour = DefaultColour):
        for track in self:
            if not track.muted:
                colour = colours[track.name] if track.name in colours else default_colour
                track.render(container = container,
                             generators = generators,
                             colour = colour)
                
class Patch:
    
    def __init__(self, tracks, frozen = False):
        self.tracks = tracks
        self.frozen = frozen

    def clone(self):
        return Patch(tracks = self.tracks.clone(),
                     frozen = self.frozen)

    def render(self, container, generators, machine_colours):
        self.tracks.render(container = container,
                           generators = generators,
                           colours = machine_colours)
        
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

    def freeze(self, n):
        for i, patch in enumerate(self):
            patch.frozen = i < n            
    
class Project:
    
    def __init__(self, patches = None):
        self.patches = patches if patches else Patches()
        
    def render(self, bank, generators, bpm, n_ticks,
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

    def freeze_patches(self, n):
        self.patches.freeze(n)
        
    def clone(self):
        return Project(patches = self.patches.clone())

if __name__ == "__main__":
    pass
