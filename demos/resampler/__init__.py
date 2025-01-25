from sv.client.algos import random_perkons_groove
from sv.client.banks import StaticZipBank
from sv.client.banks.slicer import SlicerBank
from sv.client.parse import parse_args

from sv.container import SVContainer
from sv.machines import SVSamplerMachine
from sv.trigs import SVSampleTrig, SVModTrig, controller_value

from demos import *

import io
import json
import random
import re
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

class SliceMachine(SVSamplerMachine):

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

    def modulation(self, i,
                   echo_wet=None,
                   echo_feedback=None):
        trigs = []
        if echo_wet:
            wet_level = int(controller_value(echo_wet))
            trigs.append(SVModTrig(target=f"{self.namespace}Echo/wet",
                                   i=i,
                                   value=wet_level))
        if echo_feedback:
            trigs.append(SVModTrig(target=f"{self.namespace}Echo/feedback",
                                   i=i,
                                   value=echo_feedback))
        return trigs

def Beat(self, n, rand, groove, quantise, density,
         **kwargs):
    for i in range(n):
        volume = groove(i = i,
                        rand = rand["vol"])
        if (0 == i % quantise and
            rand["trig"].random() < density):
            self.randomise_sample(rand["sample"])
            yield self.note(volume = volume, i = i)

def GhostEcho(self, n, rand,
              quantise = 4,
              sample_hold_levels = ["0000", "2000", "4000", "6000", "8000"],
              **kwargs):
    for i in range(n):
        if 0 == i % quantise:
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
- name: quantise
  type: int
  default: 2
  options: [1, 2, 4, 8, 16]
- name: n_patches
  type: int
  default: 16
  min: 1
""")
    
def main():
    try:
        args = parse_args(ArgsConfig)
        archive = Euclid09Archive(StaticZipBank(args.zip_src))
        meta, src_wav_io = archive.project_metadata, archive.patch_audio
        bank = SlicerBank(n_patches = meta["n_patches"],
                          n_ticks = meta["n_ticks"],
                          wav_io = src_wav_io)
        container = SVContainer(bank = bank,
                                bpm = meta["bpm"],
                                n_ticks = meta["n_ticks"])
        all_samples = bank.list_slices(n_ticks = meta["n_ticks"],
                                       quantise = args.quantise)
        for i in range(args.n_patches):
            container.spawn_patch(colour = random_colour())
            samples = [random.choice(all_samples) for i in range(args.group_sz)]
            machine = SliceMachine(container = container,
                                   namespace = "wol",
                                   colour = random_colour(),
                                   samples = samples)
            container.add_machine(machine)
            groove = random_perkons_groove()
            seeds = {key: random_seed() for key in "sample|fx|trig|vol".split("|")}
            machine.render(generator = Beat,
                           seeds = seeds,
                           env = {"groove": groove,
                                  "quantise": args.quantise,
                                  "density": args.density})
            machine.render(generator = GhostEcho,
                           seeds = seeds)
        container.write_project("tmp/demos/resampler.sunvox")
    except RuntimeError as error:
        print(f"ERROR: {error}")

if __name__ == "__main__":
    main()
