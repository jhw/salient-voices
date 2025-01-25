from sv.client.algos import random_perkons_groove, random_euclid_pattern
from sv.client.banks import StaticZipBank
from sv.client.colours import Colours
from sv.client.model import Project, Patch, TrackBase
from sv.client.parse import parse_args

from sv.machines import SVSamplerMachine
from sv.trigs import SVSampleTrig, SVModTrig, controller_value

from demos import *

import random
import yaml

Modules = yaml.safe_load("""
- name: Beat
  class: sv.sampler.SVSlotSampler
  links:
    - Echo
- name: Echo
  class: rv.modules.echo.Echo
  links:
    - Output
""")

class BeatMachine(SVSamplerMachine):

    Modules = Modules

    def __init__(self, container, namespace, samples,
                 sample_index=0,
                 relative_note=0,
                 echo_delay=36,
                 echo_delay_unit=3,  # tick
                 echo_wet=0,
                 echo_feedback=0,
                 **kwargs):
        SVSamplerMachine.__init__(self,
                                  container=container,
                                  namespace=namespace,
                                  relative_note=relative_note,
                                  **kwargs)
        self.samples = samples
        self.sample_index = sample_index
        self.defaults = {"Echo": {"wet": echo_wet,
                                  "feedback": echo_feedback,
                                  "delay": echo_delay,
                                  "delay_unit": echo_delay_unit}}

    def toggle_sample(self):
        self.sample_index = 1 - int(self.sample_index > 0)

    @property
    def sample(self):
        return self.samples[self.sample_index]
        
    def note(self, i,
             volume=1.0):
        return [SVSampleTrig(target=f"{self.namespace}Beat",
                             i=i,
                             sample=self.sample,
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

class Track(TrackBase):

    def __init__(self, name, machine, pattern, groove, seeds, temperature, density, samples, muted = False):
        super().__init__(name = name,
                         machine = machine,
                         seeds = seeds,
                         muted = muted)
        self.pattern = pattern
        self.groove = groove
        self.temperature = temperature
        self.density = density
        self.samples = samples

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
            "samples": self.samples
        }
    
def Beat(self, n, rand, pattern, groove, temperature, density, **kwargs):
    for i in range(n):        
        volume = groove(rand = rand["vol"], i = i)
        if rand["sample"].random() < temperature:
            self.toggle_sample()        
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

TrackConfig = [
    {
        "name": "kick",
        "machine": "demos.beats.euclid09.BeatMachine",
        "temperature": 0.5,
        "density": 0.5,
        "filter_fn": lambda x: "BD" in x
    },
    {
        "name": "snare",
        "machine": "demos.beats.euclid09.BeatMachine",
        "temperature": 0.5,
        "density": 0.25,
        "filter_fn": lambda x: ("SD" in x or
                                "TOM" in x or
                                "HC" in x),
    },
    {
        "name": "hat",
        "machine": "demos.beats.euclid09.BeatMachine",
        "temperature": 0.5,
        "density": 0.75,
        "filter_fn": lambda x: ("RS" in x or
                                # "CH" in x or
                                "OH" in x or
                                "BLIP" in x or
                                "HH" in x)
    }
]

ArgsConfig = yaml.safe_load("""
- name: bank_src
  type: str
  file: true
  default: demos/packs/pico-default.zip
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
        
def main(args_config = ArgsConfig,
         tracks = TrackConfig,
         generators = [Beat, GhostEcho]):
    try:
        args = parse_args(args_config)
        bank = StaticZipBank(args.bank_src)
        all_samples = bank.file_names
        project = Project()
        for i in range(args.n_patches):
            patch = Patch()
            for _track in tracks:
                track_samples = [sample for sample in all_samples
                                 if _track["filter_fn"](sample)]
                selected_samples = [random.choice(track_samples) for i in range(2)]
                seeds = {key: random_seed() for key in "sample|fx|beat|vol".split("|")}
                track = Track(name = _track["name"],
                              machine = _track["machine"],
                              groove = random_perkons_groove(),
                              pattern = random_euclid_pattern(),
                              seeds = seeds,
                              temperature = _track["temperature"],
                              density = _track["density"],
                              samples = selected_samples)
                patch.tracks.append(track)
            project.patches.append(patch)
        colours = Colours.randomise(tracks = tracks,
                                    patches = project.patches)
        container = project.render(bank = bank,
                                   generators = generators,
                                   colours = colours,
                                   bpm = args.bpm,
                                   n_ticks = args.n_ticks)
        container.write_project("tmp/euclid09-demo.sunvox")                    
    except RuntimeError as error:
        print(f"ERROR: {error}")

if __name__ == "__main__":
    main()
