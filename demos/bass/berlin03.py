from sv.client.algos import random_perkons_groove
from sv.client.banks import StaticZipBank
from sv.client.parse import parse_args

from sv.core.container import SVContainer
from sv.core.machines import SVSamplerMachine
from sv.core.trigs import SVMultiSynthSampleTrig, SVModTrig, SVNoteOffTrig

from demos import *

import random
import yaml

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
  class: sv.core.sampler.SVSlotSampler
  links:
    - Distortion
- name: Distortion
  class: rv.modules.distortion.Distortion
  defaults:
    power: 64
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
                 **kwargs):
        SVSamplerMachine.__init__(self, container=container,
                                  namespace=namespace,
                                  relative_note=relative_note,
                                  **kwargs)
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

ArgsConfig = yaml.safe_load("""
- name: bank_src
  type: str
  file: true
  default: packs/pico-vco-waveforms.zip
- name: bpm
  type: int
  default: 120
  min: 1
- name: n_ticks
  type: int
  default: 32
  min: 1
- name: n_patches
  type: int
  default: 16
  min: 1
""")

def main():
    try:
        args = parse_args(ArgsConfig)
        bank = StaticZipBank(args.bank_src)
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
        container.write_project("tmp/demos/berlin03.sunvox")                    
    except RuntimeError as error:
        print(f"ERROR: {error}")

if __name__ == "__main__":
    main()
