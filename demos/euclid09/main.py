from sv.container import SVContainer
from sv.machines import SVSamplerMachine, SVMachineTrigs
from sv.trigs import SVSampleTrig, SVModTrig, controller_value

from demos import *

import argparse
import os
import random
import yaml

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

    def toggle_sample(self):
        self.sample_index = 1 - int(self.sample_index > 0)

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
            feedback_level = int(controller_value(echo_feedback))
            trigs.append(SVModTrig(target=f"{self.namespace}Echo/feedback",
                                   value=feedback_level))
        return SVMachineTrigs(trigs=trigs)

def Beat(self, n, rand, pattern, groove, temperature, density, **kwargs):
    for i in range(n):        
        volume = groove(rand = rand["vol"], i = i)
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
            
def parse_args(config = [("bank_src", str, "demos/pico-default.zip"),
                         ("bpm", int, 120),
                         ("n_ticks", int, 16),
                         ("n_patches", int, 16)]):
    parser = argparse.ArgumentParser(description="euclid09")
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
    if not args.bank_src.endswith(".zip"):
        raise RuntimeError("bank_src must be a zip file")
    return args

TrackConfig = [("kick", lambda x: "BD" in x, 0.5, 0.5),
               ("snare", lambda x: ("SD" in x or
                                    "TOM" in x or
                                    "HC" in x), 0.5, 0.25),
               ("hat", lambda x: ("RS" in x or
                                  # "CH" in x or
                                  "OH" in x or
                                  "BLIP" in x or
                                  "HH" in x), 0.5, 0.75)]

def spawn_patch(bank_samples, container, bpm,
                track_config = TrackConfig,
                beat_generator = Beat,
                echo_generator = GhostEcho):
    for name, filter_fn, temperature, density in track_config:
        track_samples = [sample for sample in bank_samples if filter_fn(sample)]
        selected_samples = [random.choice(track_samples) for i in range(2)]
        machine = Detroit09(container = container,
                            namespace = name,
                            colour = random_colour(),
                            samples = selected_samples)
        container.add_machine(machine)
        pattern = random_euclid_pattern()
        groove = random_perkons_groove()
        seeds = {key: random_seed() for key in "sample|fx|beat|vol".split("|")}
        machine.render(generator = beat_generator,
                       seeds = seeds,
                       env = {"groove": groove,
                              "pattern": pattern,
                              "density": density,
                              "temperature": temperature})
        machine.render(generator = echo_generator,
                       seeds = seeds,
                       env = {"bpm": args.bpm})
    
if __name__ == "__main__":
    try:
        args = parse_args()
        bank = SimpleZipBank(args.bank_src)
        container = SVContainer(bank = bank,
                                bpm = args.bpm,
                                n_ticks = args.n_ticks)
        bank_samples = bank.file_names
        for i in range(args.n_patches):
            colour = random_colour()
            container.spawn_patch(colour)
            spawn_patch(bank_samples = bank_samples,
                        container = container,
                        bpm = args.bpm)
            container.spawn_patch(colour)
        container.write_project("tmp/euclid09-demo.sunvox")                    
    except RuntimeError as error:
        print(f"ERROR: {error}")
