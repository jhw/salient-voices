from sv.container import SVContainer
from sv.machines import SVSamplerMachine, SVMachineTrigs
from sv.trigs import SVSampleTrig, SVModTrig, controller_value

import argparse
import io
import json
import os
import random
import yaml
import zipfile

import rv

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

class Sampler(SVSamplerMachine):

    Modules = Modules

    def __init__(self, container, namespace, samples, sample_mapping,
                 sample_i = 0,
                 sample_j = 0,
                 relative_note=0,
                 echo_delay=36,
                 echo_delay_unit=3,  # tick
                 echo_wet=0,
                 echo_feedback=0,
                 colour=[127, 127, 127],
                 **kwargs):
        SVSamplerMachine.__init__(self,
                                  container=container,
                                  namespace=namespace,
                                  root=rv.note.NOTE.C5 + relative_note,
                                  colour=colour)
        self.samples = samples
        self.sample_mapping = sample_mapping
        self.sample_i = sample_i
        self.sample_j = sample_j
        self.defaults = {"Echo": {"wet": echo_wet,
                                  "feedback": echo_feedback,
                                  "delay": echo_delay,
                                  "delay_unit": echo_delay_unit}}

    def randomise_sample_group(self, rand):
        self.sample_i = rand.choice(range(len(self.sample_mapping)))

    def randomise_sample_index(self, rand):
        self.sample_j = rand.choice(range(len(self.sample_mapping[self.sample_i])))
        
    @property
    def sample_index(self):
        return self.sample_mapping[self.sample_i][self.sample_j]
        
    @property
    def sample(self):
        return self.samples[self.sample_index]

    def note(self,
             volume=1.0):
        trigs = [SVSampleTrig(target=f"{self.namespace}Beat",
                              sample=self.sample,
                              vel=volume)]
        return SVMachineTrigs(trigs=trigs)

    def modulation(self,
                   echo_delay=None,
                   echo_wet=None,
                   echo_feedback=None):
        trigs = []
        if echo_delay:
            delay_level = int(controller_value(echo_delay))
            trigs.append(SVModTrig(target=f"{self.namespace}Echo/delay",
                                   value=delay_level))
        if echo_wet:
            wet_level = int(controller_value(echo_wet))
            trigs.append(SVModTrig(target=f"{self.namespace}Echo/wet",
                                   value=wet_level))
        if echo_feedback:
            trigs.append(SVModTrig(target=f"{self.namespace}Echo/feedback",
                                   value=echo_feedback))
        return SVMachineTrigs(trigs=trigs)

def Beat(self, n, rand, groove_fn, quantise, density,
         **kwargs):
    self.randomise_sample_group(rand["sample"])
    for i in range(n):
        volume = groove_fn(i = i,
                           rand = rand["vol"])
        if (0 == i % quantise and
            rand["trig"].random() < density):
            self.randomise_sample_index(rand["sample"])
            trig_block = self.note(volume = volume)
            yield i, trig_block

def GhostEcho(self, n, rand, bpm,
              quantise = 4,
              sample_hold_levels = ["0000", "2000", "4000", "6000", "8000"],
              **kwargs):
    for i in range(n):
        if 0 == i % quantise:
            wet_level = rand["fx"].choice(sample_hold_levels)
            feedback_level = rand["fx"].choice(sample_hold_levels)
            delay_value = hex(int(128 * bpm * 3 / 10))
            trig_block = self.modulation(echo_delay = delay_value,
                                         echo_wet = wet_level,
                                         echo_feedback = feedback_level)
            yield i, trig_block

class ZipBankBase(dict):

    @staticmethod
    def load_zip(zip_path):
        zip_buffer = io.BytesIO()
        with open(zip_path, 'rb') as f:
            zip_buffer.write(f.read())
        zip_buffer.seek(0)
        return Bank(zip_buffer=zip_buffer)

    def __init__(self, zip_buffer):
        self.zip_buffer = zip_buffer

    @property
    def zip_file(self):
        return zipfile.ZipFile(self.zip_buffer, 'r')

    @property
    def file_names(self):
        return self.zip_file.namelist()

    def get_wav(self, file_name):
        if file_name not in self.file_names:
            raise RuntimeError(f"path {file_name} not found in bank")
        with self.zip_file.open(file_name, 'r') as file_entry:
            file_content = file_entry.read()
        return io.BytesIO(file_content)

"""
resampler assumes a particular output structure available from Euclid09, including metadata and slices of different duration
"""
    
class Euclid09Archive(ZipBankBase):

    def __init__(self, zip_buffer):
        ZipBankBase.__init__(self, zip_buffer)

    @property
    def project_metadata(self):
        if "meta.json" not in self.file_names:
            raise RuntimeError("project metadata not found")
        with self.zip_file.open("meta.json", 'r') as file_entry:
            file_content = file_entry.read()
        return json.loads(file_content)["project"]

    def slice_files(self, n_ticks, quantise):
        n = int(n_ticks / quantise)
        files = [file_name for file_name in self.file_names
                 if file_name.startswith(f"audio/sliced/{n:04}")]
        if files == []:
            raise RuntimeError("no slice files found")
        return files
    
def perkons_humanise(i, rand, **kwargs):
    return max(0.85, min(1.0, 0.9 + rand.uniform(-0.05, 0.05)))
    
def random_colour(offset = 64,
                  contrast = 128,
                  n = 256):
    for i in range(n):
        color = [int(offset + random.random() * (255 - offset))
                 for i in range(3)]
        if (max(color) - min(color)) > contrast:
            return color
    raise RuntimeError("couldn't find suitable random colour")

def random_seed():
    return int(random.random() * 1e8)

def add_patch(container, sampler, quantise, density, groove_fn, bpm):
    container.spawn_patch(colour = random_colour())
    seeds = {key: random_seed() for key in "sample|fx|trig|vol".split("|")}
    sampler.render(generator = Beat,
                   seeds = seeds,
                   env = {"groove_fn": groove_fn,
                          "quantise": quantise,
                          "density": density})
    sampler.render(generator = GhostEcho,
                   seeds = seeds,
                   env = {"bpm": bpm})

def init_sample_groups(n_samples, n_groups, group_sz):
    index = list(range(n_samples))
    return [[random.choice(index) for _ in range(group_sz)] for _ in range(n_groups)]

def parse_args(config = [("archive_src", str, None),
                         ("n_groups", int, 64),
                         ("group_sz", int, 4),
                         ("density", float, 0.5),
                         ("quantise", int, 2),
                         ("n_patches", int, 16)]):
    parser = argparse.ArgumentParser(description="whatevs")
    for attr, type, default in config:
        kwargs = {"type": type}
        if default:
            kwargs["default"] = default
        parser.add_argument(f"--{attr}", **kwargs)
    args, errors = parser.parse_args(), []
    for attr, _, _ in config:
        if getattr(args, attr) == None:
            errors.append(attr)
    if errors != []:
        raise RuntimeError(f"please supply {', '.join(errors)}")
    if not args.archive_src.endswith(".zip"):
        raise RuntimeError("archive_src must be a zip file")
    return args

if __name__ == "__main__":
    try:
        args = parse_args()
        bank = Euclid09Archive(args.archive_src)
        meta = bank.project_metadata
        container = SVContainer(bank = bank,
                                bpm = meta["bpm"],
                                n_ticks = meta["n_ticks"])
        samples = bank.slice_files(n_ticks = meta["n_ticks"],
                                   quantise = args.quantise)
        sample_mapping = init_sample_groups(n_samples = len(samples),
                                            n_groups = args.n_groups,
                                            group_sz = args.group_sz)
        sampler = Sampler(container = container,
                          namespace = "wol",
                          colour = random_colour(),
                          samples = samples,
                          sample_mapping = sample_mapping)
        container.add_machine(sampler)
        for i in range(args.n_patches):
            add_patch(container = container,
                      sampler = sampler,
                      groove_fn = perkons_humanise,
                      quantise = args.quantise,
                      density = args.density,
                      bpm = meta["bpm"])
        container.write_project("tmp/resampler-demo.sunvox")
    except RuntimeError as error:
        print(f"ERROR: {error}")
