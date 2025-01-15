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

from sv.machines import SVSamplerMachine, SVMachineTrigs
from sv.trigs import SVSampleTrig, SVModTrig, controller_value

import rv
import rv.api
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

class BeatsApi:
    
    def __init__(self,
                 samples,
                 sample_index = 0,
                 pitches = [0],
                 pitch_index = 0,
                 cutoffs = [500],
                 cutoff_index = 0,
                 **kwargs):
        self.samples = samples
        self.sample_index = sample_index
        self.pitches = pitches
        self.pitch_index = pitch_index
        self.cutoffs = cutoffs
        self.cutoff_index = cutoff_index

    # sample
        
    def toggle_sample(self):
        self.sample_index = 1 - int(self.sample_index > 0)

    @property
    def sample(self):
        return self.samples[self.sample_index]

    # pitch

    @property
    def pitch(self):
        return self.pitches[self.pitch_index]

    # cutoff

    @property
    def cutoff(self):
        return self.cutoffs[self.cutoff_index]

class Sampler(SVSamplerMachine, BeatsApi):

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
        BeatsApi.__init__(self,
                          samples=samples,
                          sample_index=sample_index)
        self.defaults = {"Echo": {"wet": echo_wet,
                                  "feedback": echo_feedback,
                                  "delay": echo_delay,
                                  "delay_unit": echo_delay_unit}}

    def note(self,
             volume=1.0):
        trigs = [SVSampleTrig(target=f"{self.namespace}Beat",
                              sample=self.sample,
                              cutoff=self.cutoff,
                              pitch=self.pitch,
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
            feedback_level = int(controller_value(echo_feedback))
            trigs.append(SVModTrig(target=f"{self.namespace}Echo/feedback",
                                   value=feedback_level))
        return SVMachineTrigs(trigs=trigs)

def Beat(self, n, rand, pattern, groove, temperature, density, **kwargs):
    for i in range(n):
        volume = groove(rand = rand["volume"], i = i)
        if rand["sample"].random() < temperature:
            self.toggle_sample()        
        if (pattern(i) and 
            rand["beat"].random() < density):
            trig_block = self.note(volume = volume)
            yield i, trig_block

def GhostEcho(self, n, rand, bpm,
              wet_levels = ["0000", "2000", "4000", "6000"],
              feedback_levels = ["0000", "2000", "4000", "6000"],
              quantise = 4,
              **kwargs):
    for i in range(n):
        if 0 == i % quantise:
            wet_level = rand["fx"].choice(wet_levels)
            feedback_level = rand["fx"].choice(feedback_levels)
            delay_value = hex(int(128 * bpm  * 3 / 10))
            trig_block = self.modulation(echo_delay = delay_value,
                                         echo_wet = wet_level,
                                         echo_feedback = feedback_level)
            yield i, trig_block
            
class Bank(dict):

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

def parse_args(config = [("archive_src", str, "demos/euclid09/pico-default.zip"),
                         ("temperature", int, 0.5),
                         ("density", float, 0.5),
                         ("bpm", int, 120),
                         ("n_ticks", int, 16),
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
    return args

if __name__ == "__main__":
    try:
        args = parse_args()
        bank = Euclid09Archive(args.archive_src)
        container = SVContainer(bank = bank,
                                bpm = args.bpm,
                                n_ticks = args.n_ticks)
        samples = []
        sampler = Sampler(container = container,
                          namespace = "wol",
                          colour = random_colour(),
                          samples = samples)
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
