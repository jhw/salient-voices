from sv.client.algos import random_perkons_groove, random_euclid_pattern
from sv.client.colours import Colours
from sv.client.model import Project, Patch, TrackBase
from sv.client.parse import parse_args

from sv.container import SVContainer
from sv.machines import SVMachine
from sv.trigs import SVNoteTrig, SVModTrig, controller_value

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

    @property
    def _note(self):
        return self.notes[self.note_index]

    """
    because some bass notes are on the loud side
    """
    
    def mix_level(self, i):
        if i in [85, 86, 87, 88]:
            return 0.7
        elif i in [37, 38, 39, 40, 49, 50, 51, 52]:
            return 0.85
        else:
            return 1.0
        
    def note(self, i,
             volume=1.0):
        note = self._note
        level = self.mix_level(note)
        return [SVNoteTrig(target = f"{self.namespace}Beat",
                           i = i,
                           note = note,
                           vel = volume * level)]

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

class Track(TrackBase):

    def __init__(self, name, machine, pattern, groove, seeds, temperature, density, notes, muted = False):
        super().__init__(name = name,
                         machine = machine,
                         seeds = seeds,
                         muted = muted)
        self.pattern = pattern
        self.groove = groove
        self.temperature = temperature
        self.density = density
        self.notes = notes

    @property
    def env(self):
        return {
            "temperature": self.temperature,
            "density": self.density,
            "pattern": self.pattern,
            "groove": self.groove
        }

    @property
    def machine_kwargs(self):
        return {
            "notes": self.notes
        }    
    
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

"""
No snare as SVDrum snare sounds are lame
"""
            
TrackConfig = [
    {
        "name": "kick",
        "machine": "demos.beats.tokyo09.BeatMachine",
        "temperature": 0.5,
        "density": 0.5,
        "filter_fn": lambda i:((i % 12) < 4 and
                               int(i / 12) not in [1, 9])
    },
    {
        "name": "hat",
        "machine": "demos.beats.tokyo09.BeatMachine",
        "temperature": 0.5,
        "density": 0.75,
        "filter_fn": lambda i: ((i % 12) > 4 and
                                (i % 12) < 7 and
                                int(i / 12) not in [6])
    }
]

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

def main(notes = list(range(120)),
         args_config = ArgsConfig,
         tracks = TrackConfig,
         generators = [Beat, GhostEcho]):
    try:
        args = parse_args(args_config)
        project = Project()
        for i in range(args.n_patches):
            patch = Patch()
            for _track in tracks:
                track_notes = [note for note in notes
                               if _track["filter_fn"](note)]
                selected_notes = [random.choice(track_notes) for i in range(2)]
                track = Track(name = _track["name"],
                              machine = _track["machine"],
                              groove = random_perkons_groove(),
                              pattern = random_euclid_pattern(),
                              seeds = random_seeds("note|fx|beat|vol"),
                              notes = selected_notes,
                              temperature = _track["temperature"],
                              density = _track["density"])
                patch.tracks.append(track)
            project.patches.append(patch)
        colours = Colours.randomise(tracks = tracks,
                                    patches = project.patches)
        container = project.render(generators = generators,
                                   colours = colours,
                                   bpm = args.bpm,
                                   n_ticks = args.n_ticks)
        container.write_project("tmp/tokyo09-demo.sunvox")                    
    except RuntimeError as error:
        print(f"ERROR: {error}")

if __name__ == "__main__":
    main()
