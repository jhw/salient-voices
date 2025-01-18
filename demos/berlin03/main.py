from sv.container import SVContainer
from sv.machines import SVSamplerMachine
from sv.trigs import SVSampleTrig, SVModTrig, SVNoteOffTrig, controller_value

from enum import Enum

from demos import *

import argparse
import random
import yaml

import rv

Modules = yaml.safe_load("""
- name: MultiSynth
  class: rv.modules.multisynth.MultiSynth
  links:
    - ADSR
    - Sampler
- name: ADSR
  class: rv.modules.adsr.Adsr
  links:
    - Sound2Ctl
- name: Sound2Ctl
  class: rv.modules.sound2ctl.Sound2Ctl
  defaults:
    out_controller: 2
  links:
    - Filter
- name: Sampler
  class: sv.sampler.SVSlotSampler
  links:
    - Filter
- name: Filter
  class: rv.modules.filter.Filter
  defaults:
    freq: 0
    roll_off: 3 # no idea but seems to allow resonance to be higher without pinking distortion
  links:
    - Output
""")

class BerlinSampleTrig(SVSampleTrig):

    def __init__(self, target, sample, sampler_mod, **kwargs):
        super().__init__(target = target,
                         sample = sample,
                         **kwargs)
        self.sampler_mod = sampler_mod
        
    def resolve_sampler(self):
        return self.sampler_mod if self.sampler_mod else self.mod
    
    def resolve_sampler_note(self, modules):
        sampler_mod = modules[self.sampler_mod if self.sampler_mod else self.mod]
        note = 1 + sampler_mod.index_of(self.sample)
        return note
    
    def render(self, modules, *args):
        mod = modules[self.mod]        
        mod_id = 1 + mod.index
        # note = 1 + mod.index_of(self.sample_string)
        note = self.resolve_sampler_note(modules)
        note_kwargs = {
            "module": mod_id,
            "note": note
        }
        if self.has_vel:
            note_kwargs["vel"] = self.velocity
        if self.has_fx and self.fx_value:
            note_kwargs["pattern"] = self.fx
            note_kwargs["val"] = self.fx_value
        return rv.note.Note(**note_kwargs)

class BerlinSound:

    def __init__(self, sample,
                 attack = "0008",
                 decay = "0018",
                 sustain_level = "0800",
                 release = "0300",
                 filter_freq = "4000",
                 filter_resonance = "7000"):
        self.sample = sample
        self.attack = attack
        self.decay = decay
        self.sustain_level = sustain_level
        self.release = release
        self.filter_freq = filter_freq
        self.filter_resonance = filter_resonance
        
class BerlinMachine(SVSamplerMachine):
    
    Modules = Modules
    
    def __init__(self, container, namespace, sound,
                 relative_note=-6,
                 colour=[127, 127, 127],
                 **kwargs):
        SVSamplerMachine.__init__(self, container=container,
                                  namespace=namespace,
                                  root=rv.note.NOTE.C5 + relative_note,
                                  colour=colour)
        self.sound = sound
        self.defaults = {}

    def note_on(self, i,
                pitch=0,
                volume=1.0):
        sample = f"{self.sound.sample}?pitch={pitch}"
        return [
            BerlinSampleTrig(target=f"{self.namespace}MultiSynth",                             
                             i=i,
                             sampler_mod=f"{self.namespace}Sampler",
                             sample=sample,
                             vel=volume),
            SVModTrig(target=f"{self.namespace}Sound2Ctl/out_max",
                      i=i,
                      value=self.sound.filter_freq),
            SVModTrig(target=f"{self.namespace}Filter/resonance",
                      i=i,
                      value=self.sound.filter_resonance),
            SVModTrig(target=f"{self.namespace}ADSR/attack",
                      i=i,
                      value=self.sound.attack),
            SVModTrig(target=f"{self.namespace}ADSR/decay",
                      i=i,
                      value=self.sound.decay),
            SVModTrig(target=f"{self.namespace}ADSR/sustain_level",
                      i=i,
                      value=self.sound.sustain_level),
            SVModTrig(target=f"{self.namespace}ADSR/release",
                      i=i,
                      value=self.sound.release)
        ]
    
    def note_off(self, i):
        return [SVNoteOffTrig(target=f"{self.namespace}MultiSynth",
                              i=i)]
    
def BassLine(self, n, rand, groove, **kwargs):
    last = None
    for i in range(n):
        pitch = rand["note"].choice([0, 12])
        volume = groove(rand = rand["vol"],
                        i = i)
        def note_on(self):
            return self.note_on(pitch = pitch,
                                volume = volume,
                                i = i)
        def note_off(self):
            return self.note_off(i = i)
        if i == 0:
            yield note_on(self)
            last = (i, pitch)
        elif (i == n-1 and last != None):
            yield note_off(self)
            last = None
        else:
            q = rand["note"].choice(range(3))
            if q == 0:
                yield note_on(self)
                last = (i, pitch)
            elif (q == 1 and last != None):
                yield note_off(self)
                last = None
            else:
                pass
        
def parse_args(config = [("bank_src", str, "demos/berlin03/mikey303.zip"),
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
    if not args.bank_src.endswith(".zip"):
        raise RuntimeError("bank_src must be a zip file")
    return args

if __name__ == "__main__":
    try:
        args = parse_args()
        bank = SimpleZipBank(args.bank_src)
        container = SVContainer(bank = bank,
                                bpm = args.bpm,
                                n_ticks = args.n_ticks)
        for i in range(args.n_patches):
            container.spawn_patch(colour = random_colour())
            sound = BerlinSound(sample =  random.choice(bank.file_names),
                                filter_freq = random.choice(["2000", "4000", "6000"]),
                                filter_resonance = random.choice(["6000", "6800", "7000"]))
            machine = BerlinMachine(container = container,
                                    namespace = "303",
                                    sound = sound,
                                    colour = random_colour())
            container.add_machine(machine)
            seeds = {key: int(random.random() * 1e8)
                     for key in "note|vol".split("|")}
            groove = random_perkons_groove()
            env = {"groove": groove}
            machine.render(generator = BassLine,
                           seeds = seeds,
                           env = env)
        container.write_project("tmp/berlin03-demo.sunvox")                    
    except RuntimeError as error:
        print(f"ERROR: {error}")
