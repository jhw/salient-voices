from sv.container import SVContainer
from sv.machines import SVSamplerMachine
from sv.trigs import SVMultiSynthSampleTrig, SVModTrig, SVNoteOffTrig, controller_value

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
    - Distortion
- name: Distortion
  class: rv.modules.distortion.Distortion
  defaults:
    power: 128
  links:
    - Filter
- name: Filter
  class: rv.modules.filter.Filter
  defaults:
    freq: 0
    roll_off: 3 # no idea but seems to allow resonance to be higher without pinking distortion
  links:
    - Echo
- name: Echo
  class: rv.modules.echo.Echo
  links:
    - Output
""")

class BassSound:

    def __init__(self, sample,
                 attack = "0008",
                 decay = "0018",
                 sustain = "0800",
                 release = "0300",
                 filter_freq = "4000",
                 filter_resonance = "7000"):
        self.sample = sample
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release
        self.filter_freq = filter_freq
        self.filter_resonance = filter_resonance

SlideToFX = "0003"
        
class BassMachine(SVSamplerMachine):
    
    Modules = Modules
    
    def __init__(self, container, namespace, sound,
                 relative_note=-6,
                 echo_delay=36,
                 echo_delay_unit=3,  # tick
                 echo_wet=32,
                 echo_feedback=32,
                 colour=[127, 127, 127],
                 **kwargs):
        SVSamplerMachine.__init__(self, container=container,
                                  namespace=namespace,
                                  root=rv.note.NOTE.C5 + relative_note,
                                  colour=colour)
        self.sound = sound
        self.defaults = {"Echo": {"wet": echo_wet,
                                  "feedback": echo_feedback,
                                  "delay": echo_delay,
                                  "delay_unit": echo_delay_unit}}

    def note_on(self, i,
                pitch=0,
                volume=1.0,
                slide_to=False,
                slide_level="0080"):
        trigs = []
        # note
        sample = f"{self.sound.sample}?pitch={pitch}"
        fx = f"{SlideToFX}/{slide_level}" if slide_to else None
        note = SVMultiSynthSampleTrig(target=f"{self.namespace}MultiSynth",
                                      i=i,
                                      sampler_mod=f"{self.namespace}Sampler",
                                      sample=sample,
                                      vel=volume,
                                      fx=fx)
        trigs.append(note)
        # envelope
        envelope = [
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
                      value=self.sound.sustain),
            SVModTrig(target=f"{self.namespace}ADSR/release",
                      i=i,
                      value=self.sound.release)
        ]
        trigs += envelope
        return trigs

    def note_off(self, i):
        return [SVNoteOffTrig(target=f"{self.namespace}MultiSynth",
                              i=i)]
    
def Bassline(self, n, rand, groove, scale, **kwargs):
    last = None
    for i in range(n):
        pitch = rand["note"].choice(scale)
        volume = groove(rand = rand["vol"],
                        i = i)
        def note_on(self):
            slide_to = (last != None and
                        last[1] != pitch)
            return self.note_on(pitch = pitch,
                                volume = volume,
                                i = i,
                                slide_to = slide_to)
        def note_off(self):
            return self.note_off(i = i)
        if i == 0:
            yield note_on(self)
            last = (i, pitch)
        elif i == n-1:
            if last != None:
                yield note_off(self)
                last = None
        else:
            q = rand["note"].choice(range(3))
            if q == 0:
                yield note_on(self)
                last = (i, pitch)
            elif q == 1:
                if last != None:
                    yield note_off(self)
                    last = None
            else:
                pass
        
def parse_args(config = [("bank_src", str, "demos/packs/erica-pico-vco-waveforms-32.zip"),
                         ("bpm", int, 120),
                         ("n_ticks", int, 32),
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

"""
https://github.com/vitling/acid-banger/blob/main/src/pattern.ts
"""

Vitling303Scales = [[0, 0, 12, 24, 27],
                    [0, 0, 0, 12, 10, 19, 26, 27],
                    [0, 1, 7, 10, 12, 13],
                    [0], 
                    [0, 0, 0, 12],
                    [0, 0, 12, 14, 15, 19],
                    [0, 0, 0, 0, 12, 13, 16, 19, 22, 24, 25],
                    [0, 0, 0, 7, 12, 15, 17, 20, 24]]


WolScales = [[0],
             [0, 0, 0, 12],
             [0, 0, 10, 12],
             [0, 0, 0, -2, 12]]

if __name__ == "__main__":
    try:
        args = parse_args()
        bank = SimpleZipBank(args.bank_src)
        container = SVContainer(bank = bank,
                                bpm = args.bpm,
                                n_ticks = args.n_ticks)
        for i in range(args.n_patches):
            container.spawn_patch(colour = random_colour())
            sample = random.choice(bank.file_names)
            attack = random.choice(["0008"])
            decay = random.choice(["0018"])
            sustain = random.choice(["0800"])
            release = random.choice(["0300"])
            filter_freq = random.choice(["6000", "8000", "a000"])
            filter_resonance = random.choice(["7000"])
            sound = BassSound(sample = sample,
                                attack = attack,
                                decay = decay,
                                sustain = sustain,
                                release = release,                                
                                filter_freq = filter_freq,
                                filter_resonance = filter_resonance)
            machine = BassMachine(container = container,
                                  namespace = "303",
                                  sound = sound,
                                  colour = random_colour())
            container.add_machine(machine)
            seeds = {key: int(random.random() * 1e8)
                     for key in "note|vol".split("|")}
            groove = random_perkons_groove()
            # scale = [i for i in random.choice(Vitling303Scales) if i <= 12]
            scale = random.choice(WolScales)
            env = {"groove": groove,
                   "scale": scale}
            machine.render(generator = Bassline,
                           seeds = seeds,
                           env = env)
        container.write_project("tmp/berlin03-demo.sunvox")                    
    except RuntimeError as error:
        print(f"ERROR: {error}")
