from sv.client.algos import random_perkons_groove
from sv.client.banks import StaticZipBank
from sv.client.banks.slicer import SlicerBank
from sv.client.cli import parse_args
from sv.client.colours import Colours
from sv.client.model import Project, Patch, TrackBase

from sv.core.machines import SVSamplerMachine
from sv.core.trigs import SVSampleTrig

from demos import *

import io
import json
import random
import re
import yaml

Modules = yaml.safe_load("""
- name: Beat
  class: sv.core.sampler.SVSlotSampler
  links:
    - Echo
- name: Echo
  class: rv.modules.echo.Echo
  links:
    - Output
""")

class SliceMachine(SVSamplerMachine, GhostEchoMachine):

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
        GhostEchoMachine.__init__(self)
        self.samples = samples
        self.sample_index = sample_index
        self.defaults = {"Echo": {"wet": echo_wet,
                                  "feedback": echo_feedback,
                                  "delay": echo_delay,
                                  "delay_unit": echo_delay_unit}}

    def randomise_sample(self, rand):
        self.sample_index = rand.choice(range(len(self.samples)))
        
    @property
    def sample(self):
        return self.samples[self.sample_index]

    def note(self, i,
             volume=1.0):
        return [SVSampleTrig(target=f"{self.namespace}Beat",
                             i=i,
                             sample=self.sample,
                             vel=volume)]

class Track(TrackBase):

    def __init__(self, name, machine, groove, seeds, beat_quantise, echo_quantise, density, samples, muted = False):
        super().__init__(name = name,
                         machine = machine,
                         seeds = seeds,
                         muted = muted)
        self.groove = groove
        self.density = density
        self.beat_quantise = beat_quantise
        self.echo_quantise = echo_quantise
        self.samples = samples

    @property
    def env(self):
        return {
            "density": self.density,
            "beat_quantise": self.beat_quantise,
            "echo_quantise": self.echo_quantise,
            "groove": self.groove
        }

    @property
    def machine_kwargs(self):
        return {
            "samples": self.samples
        }

def Beat(self, n, rand, groove, beat_quantise, density,
         **kwargs):
    for i in range(n):
        volume = groove(i = i,
                        rand = rand["vol"])
        if (0 == i % beat_quantise and
            rand["trig"].random() < density):
            self.randomise_sample(rand["sample"])
            yield self.note(volume = volume, i = i)

def GhostEcho(self, n, rand, echo_quantise,
              sample_hold_levels = ["0000", "2000", "4000", "6000", "8000"],
              **kwargs):
    for i in range(n):
        if 0 == i % echo_quantise:
            wet_level = rand["fx"].choice(sample_hold_levels)
            feedback_level = rand["fx"].choice(sample_hold_levels)
            yield self.modulation(i = i,
                                  echo_wet = wet_level,
                                  echo_feedback = feedback_level)
                    
class Euclid09Archive:

    def __init__(self, bank):
        self.bank = bank

    @property
    def project_metadata(self):
        if "meta.json" not in self.bank.file_names:
            raise RuntimeError("project metadata not found")
        with self.bank.zip_file.open("meta.json", 'r') as file_entry:
            file_content = file_entry.read()
        return json.loads(file_content)["project"]
    
    @property
    def patch_audio(self):
        file_names = [file_name for file_name in self.bank.file_names
                      if re.search("\.wav$", file_name) != None]
        if file_names == []:
            raise RuntimeError("patch audio file not found")
        file_name = file_names[0]
        with self.bank.zip_file.open(file_name, 'r') as file_entry:
            file_content = file_entry.read()
        return io.BytesIO(file_content)

ArgsConfig = yaml.safe_load("""
- name: zip_src
  type: str
  file: true
  default: demos/resampler/sample-archive.zip
- name: group_sz
  type: int
  default: 4
  min: 1
- name: density
  type: float
  default: 0.5
  min: 0
  max: 1
- name: beat_quantise
  type: int
  default: 2
  options: [1, 2, 4, 8, 16]
- name: echo_quantise
  type: int
  default: 4
  options: [1, 2, 4, 8, 16]
- name: n_patches
  type: int
  default: 16
  min: 1
""")
    
def main(args_config = ArgsConfig,
         _track = {"name": "wol",
                   "machine": "demos.resampler.SliceMachine"},
         generators = [Beat, GhostEcho]):
    try:
        args = parse_args(args_config)
        archive = Euclid09Archive(StaticZipBank(args.zip_src))
        meta, src_wav_io = archive.project_metadata, archive.patch_audio
        bank = SlicerBank(n_patches = meta["n_patches"],
                          n_ticks = meta["n_ticks"],
                          wav_io = src_wav_io)
        all_slices = bank.list_slices(n_ticks = meta["n_ticks"],
                                       quantise = args.beat_quantise)
        project = Project()
        for i in range(args.n_patches):
            patch = Patch()
            slices = [random.choice(all_slices) for i in range(args.group_sz)]
            track = Track(name = _track["name"],
                          machine = _track["machine"],
                          groove = random_perkons_groove(),
                          seeds = random_seeds("sample|fx|trig|vol"),
                          beat_quantise = args.beat_quantise,
                          echo_quantise = args.echo_quantise,
                          density = args.density,
                          samples = slices)
            patch.tracks.append(track)
            project.patches.append(patch)
        colours = Colours.randomise(tracks = [_track],
                                    patches = project.patches)
        container = project.render(bank = bank,
                                   generators = generators,
                                   colours = colours,
                                   bpm = meta["bpm"],
                                   n_ticks = meta["n_ticks"])
        container.write_project("tmp/demos/resampler.sunvox")
    except RuntimeError as error:
        print(f"ERROR: {error}")

if __name__ == "__main__":
    main()
