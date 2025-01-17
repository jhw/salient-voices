from demos import random_colour, random_seed

import argparse
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
  class: sv.sampler.SVSlotSampler
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

class Berlin03Sound:

    def __init__(self,
                 attack = "0008",
                 decay = "0018",
                 sustain_level = "0800",
                 sustain_term = None,
                 release = "0300",
                 filter_freq = "4000",
                 filter_resonance = "7000"):
        self.attack = attack
        self.decay = decay
        self.sustain_level = sustain_level
        self.sustain_term = sustain_term
        self.release = release
        self.filter_freq = filter_freq
        self.filter_resonance = filter_resonance

    def as_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}
    
class Berlin03Wave(Enum):
    
    SQR = "SQR"
    SAW = "SAW"
        
class Berlin03Machine(SVSamplerMachine):
    
    Modules = Modules
                      
    def __init__(self, container, namespace, wave, sounds,
                 sound_index=0,
                 relative_note=0,
                 echo_delay=36,
                 echo_delay_unit=3,  # tick
                 echo_wet=32,  # '1000'
                 echo_feedback=32,  # '1000'
                 colour=[127, 127, 127],
                 **kwargs):
        SVSamplerMachine.__init__(self, container=container,
                                   namespace=namespace,
                                   root=rv.note.NOTE.C5 + relative_note,
                                  colour=colour)
        self.sounds = sounds
        self.sound_index = sound_index
        self.sample = SVSample.parse(f"mikey303/303 VCO {wave.value}.wav")
        self.defaults = {"Echo": {"wet": echo_wet,
                                   "feedback": echo_feedback,
                                   "delay": echo_delay,
                                   "delay_unit": echo_delay_unit}}

    def note(self,
             note=0,
             volume=1.0):
        sample = self.sample.clone()
        sample.note = note
        trigs = [
            SVSampleTrig(target=f"{self.namespace}MultiSynth",
                         sampler_mod=f"{self.namespace}Sampler",
                         sample=sample,
                         vel=volume),
            SVModTrig(target=f"{self.namespace}Sound2Ctl/out_max",
                      value=self.sound.filter_freq),
            SVModTrig(target=f"{self.namespace}Filter/resonance",
                      value=self.sound.filter_resonance),
            SVModTrig(target=f"{self.namespace}ADSR/attack",
                      value=self.sound.attack),
            SVModTrig(target=f"{self.namespace}ADSR/decay",
                      value=self.sound.decay),
            SVModTrig(target=f"{self.namespace}ADSR/sustain_level",
                      value=self.sound.sustain_level),
            SVModTrig(target=f"{self.namespace}ADSR/release",
                      value=self.sound.release)
        ]
        if self.sound.sustain_term:
            trigs.append(SVNoteOffTrig(target=f"{self.namespace}MultiSynth",
                                       i=self.sound.sustain_term))
        return SVMachineTrigs(trigs=trigs)

def BassLine(self, n, rand, groove, temperature,
             root_offset = -4,
             offsets = [0, 0, 0, -2],
             note_density = 0.5,
             quantise = 1,
             **kwargs):
    i = 0
    while True:
        if rand["sound"].random() < temperature:
            self.randomise_sound(rand["sound"])
        note = root_offset + rand["note"].choice(offsets)
        volume = groove(rand = rand["vol"], i = i)
        if (rand["seq"].random() < note_density and
              0 == i % quantise:
            block =  self.note(note = note,
                               volume = volume)
            yield i, block
            i += self.sound.sustain_term # NB
        i += 1
        if i >= n:
            break

def random_sounds(n,
                  terms = [0.5, 0.5, 0.5, 1, 2],
                  frequencies = ["2000", "3000", "3000", "3000", "5000"],
                  resonances = ["6000", "6800", "7000", "7800"]):
    resonance = random.choice(resonances)
    sounds = []
    for i in range(n):
        sound = Berlin03Sound(sustain_term = int(random.choice(terms)),
                              filter_freq = random.choice(frequencies),
                              filter_resonance = resonance)
        sounds.append(sound)
    return sounds

def parse_args(config = [("bank_src", str, "demos/berlin03/mikey303.zip"),
                         ("bpm", int, 240),
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

if __name__ == "__main__":
    try:
        args = parse_args()
        bank = Bank(args.bank_src)
        container = SVContainer(bank = bank,
                                bpm = args.bpm,
                                n_ticks = args.n_ticks)
    except RuntimeError as error:
        print(f"ERROR: {error}")
