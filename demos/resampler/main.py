from sv.container import SVContainer
from sv.machines import SVSamplerMachine, SVMachineTrigs
from sv.trigs import SVSampleTrig, SVModTrig, controller_value

import demos.algos.perkons as perkons

from demos import random_seed, random_colour, random_perkons_groove

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

class Detroit09(SVSamplerMachine):

    Modules = Modules

    def __init__(self, container, namespace, samples,
                 sample_index=0,
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
    for i in range(n):
        volume = groove_fn(i = i,
                           rand = rand["vol"])
        if (0 == i % quantise and
            rand["trig"].random() < density):
            self.randomise_sample(rand["sample"])
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

def spawn_function(mod, fn, **kwargs):
    return getattr(eval(mod), fn)
    
def add_patch(container, machine, quantise, density, groove, bpm):
    container.spawn_patch(colour = random_colour())
    seeds = {key: random_seed() for key in "sample|fx|trig|vol".split("|")}
    groove_fn = spawn_function(**groove)
    machine.render(generator = Beat,
                   seeds = seeds,
                   env = {"groove_fn": groove_fn,
                          "quantise": quantise,
                          "density": density})
    machine.render(generator = GhostEcho,
                   seeds = seeds,
                   env = {"bpm": bpm})

def parse_args(config = [("archive_src", str, "demos/resampler/sample-archive.zip"),
                         ("group_sz", int, 4),
                         ("density", float, 0.5),
                         ("quantise", int, 2), # <-- don't change this as sample-archive.zip currently only includes slices for quantise == 2
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
        all_samples = bank.slice_files(n_ticks = meta["n_ticks"],
                                       quantise = args.quantise)
        for i in range(args.n_patches):
            samples = [random.choice(all_samples) for i in range(args.group_sz)]
            machine = Detroit09(container = container,
                                namespace = "wol",
                                colour = random_colour(),
                                samples = samples)
            container.add_machine(machine)
            groove = random_perkons_groove()
            add_patch(container = container,
                      machine = machine,
                      groove = groove,
                      quantise = args.quantise,
                      density = args.density,
                      bpm = meta["bpm"])
        container.write_project("tmp/resampler-demo.sunvox")
    except RuntimeError as error:
        print(f"ERROR: {error}")
