from sv.container import SVContainer
from sv.machines import SVMachine
from sv.trigs import SVNoteTrig, SVModTrig, controller_value
from sv.utils.cli.parse import parse_args

from demos import *

import random
import yaml

Modules = yaml.safe_load("""
- name: Beat
  class: rv.modules.drumsynth.DrumSynth
  links:
    - Echo
- name: Echo
  class: rv.modules.echo.Echo
  links:
    - Output
""")

class BeatMachine(SVMachine):

    Modules = Modules

    def __init__(self, container, namespace, notes,
                 note_index=0,
                 echo_delay=36,
                 echo_delay_unit=3,  # tick
                 echo_wet=0,
                 echo_feedback=0,
                 **kwargs):
        SVMachine.__init__(self,
                           container=container,
                           namespace=namespace,
                           **kwargs)
        self.notes = notes
        self.note_index = note_index
        self.defaults = {"Echo": {"wet": echo_wet,
                                  "feedback": echo_feedback,
                                  "delay": echo_delay,
                                  "delay_unit": echo_delay_unit}}

    def toggle_note(self):
        self.note_index = 1 - int(self.note_index > 0)

    def note(self, i,
             volume=1.0):
        note = self.notes[self.note_index]
        return [SVNoteTrig(target=f"{self.namespace}Beat",
                           i=i,
                           note=self.note,
                           vel=volume)]

    def modulation(self,
                   i, 
                   echo_wet=None,
                   echo_feedback=None):
        trigs = []
        if echo_wet:
            wet_level = int(controller_value(echo_wet))
            trigs.append(SVModTrig(target=f"{self.namespace}Echo/wet",
                                   i=i,
                                   value=wet_level))
        if echo_feedback:
            feedback_level = int(controller_value(echo_feedback))
            trigs.append(SVModTrig(target=f"{self.namespace}Echo/feedback",
                                   i=i,
                                   value=feedback_level))
        return trigs

def Beat(self, n, rand, pattern, groove, temperature, density, **kwargs):
    for i in range(n):        
        volume = groove(rand = rand["vol"], i = i)
        if rand["note"].random() < temperature:
            self.toggle_note()        
        if (pattern(i) and 
            rand["beat"].random() < density):
            yield self.note(volume = volume,
                            i = i)

def GhostEcho(self, n, rand,
              wet_levels = ["0000", "2000", "4000", "6000"],
              feedback_levels = ["0000", "2000", "4000", "6000"],
              quantise = 4,
              **kwargs):
    for i in range(n):
        if 0 == i % quantise:
            wet_level = rand["fx"].choice(wet_levels)
            feedback_level = rand["fx"].choice(feedback_levels)
            yield self.modulation(i = i,
                                  echo_wet = wet_level,
                                  echo_feedback = feedback_level)

TrackConfig = [("kick", lambda x: "BD" in x, 0.5, 0.5),
               ("snare", lambda x: ("SD" in x or
                                    "TOM" in x or
                                    "HC" in x), 0.5, 0.25),
               ("hat", lambda x: ("RS" in x or
                                  # "CH" in x or
                                  "OH" in x or
                                  "BLIP" in x or
                                  "HH" in x), 0.5, 0.75)]

def spawn_patch(notes, container,
                track_config = TrackConfig,
                beat_generator = Beat,
                echo_generator = GhostEcho):
    for name, filter_fn, temperature, density in track_config:
        track_notes = [note for note in notes if filter_fn(note)]
        selected_notes = [random.choice(track_notes) for i in range(2)]
        machine = BeatMachine(container = container,
                              namespace = name,
                              colour = random_colour(),
                              notes = selected_notes)
        container.add_machine(machine)
        pattern = random_euclid_pattern()
        groove = random_perkons_groove()
        seeds = {key: random_seed() for key in "note|fx|beat|vol".split("|")}
        machine.render(generator = beat_generator,
                       seeds = seeds,
                       env = {"groove": groove,
                              "pattern": pattern,
                              "density": density,
                              "temperature": temperature})
        machine.render(generator = echo_generator,
                       seeds = seeds)

ArgsConfig = yaml.safe_load("""
- name: bpm
  type: int
  default: 120
  min: 1
- name: n_ticks
  type: int
  default: 16
  min: 1
- name: n_patches
  type: int
  default: 16
  min: 1
""")
        
if __name__ == "__main__":
    try:
        args = parse_args(ArgsConfig)
        container = SVContainer(bpm = args.bpm,
                                n_ticks = args.n_ticks)
        notes = list(range(120))
        for i in range(args.n_patches):
            colour = random_colour()
            container.spawn_patch(colour)
            spawn_patch(notes = notes,
                        container = container)
            # container.spawn_patch(colour)
        container.write_project("tmp/euclid09-demo.sunvox")                    
    except RuntimeError as error:
        print(f"ERROR: {error}")
