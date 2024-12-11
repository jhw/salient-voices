from sv.machines import SVSamplerMachine, SVMachineTrigs, SVBeatsApi
from sv.sounds import SVSample
from sv.trigs import SVNoteOffTrig, SVModTrig, SVSampleTrig

from enum import Enum

import rv
import rv.api
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
    - Distortion
- name: Distortion
  class: rv.modules.distortion.Distortion
  defaults:
    power: 0
  links:
    - Echo
- name: Echo
  class: rv.modules.echo.Echo
  links:
    - Reverb
- name: Reverb
  class: rv.modules.reverb.Reverb
  defaults:
    wet: 0
  links:
    - Output

""")

class BerlinSound:

    def __init__(self,
                 attack_ms = "0008",
                 decay_ms = "0018",
                 sustain_level = "0800",
                 sustain_term = None,
                 release_ms = "0300",
                 filter_freq = "4000"):
        self.attack_ms = attack_ms
        self.decay_ms = decay_ms
        self.sustain_level = sustain_level
        self.sustain_term = sustain_term
        self.release_ms = release_ms
        self.filter_freq = filter_freq

class Berlin(SVSamplerMachine, SVBeatsApi):

    class Wave(Enum):
        
        SQR = "SQR"
        SAW = "SAW"
    
    Modules = Modules

    def __init__(self, container, namespace, wave, sounds,
                 sound_index=0,
                 relative_note=0,
                 filter_resonance=1300,
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
        SVBeatsApi.__init__(self, sounds=sounds, sound_index=sound_index)
        self.sample = SVSample.parse(f"mikey303/303 VCO {wave.value}.wav")
        self.defaults = {"Filter": {"resonance": filter_resonance},
                         "Echo": {"wet": echo_wet,
                                   "feedback": echo_feedback,
                                   "delay": echo_delay,
                                   "delay_unit": echo_delay_unit}}

    def note(self, note=0, volume=1.0, level=1.0):
        sample = self.sample.clone()
        sample["note"] = note
        trigs = [
            SVSampleTrig(target=f"{self.namespace}MultiSynth",
                         sampler_mod=f"{self.namespace}Sampler",
                         sample=sample,
                         vel=volume * level),
            SVModTrig(target=f"{self.namespace}Sound2Ctl/out_max",
                      value=self.sound.filter_freq),
            SVModTrig(target=f"{self.namespace}ADSR/attack_ms",
                      value=self.sound.attack_ms),
            SVModTrig(target=f"{self.namespace}ADSR/decay_ms",
                      value=self.sound.decay_ms),
            SVModTrig(target=f"{self.namespace}ADSR/sustain_level",
                      value=self.sound.sustain_level),
            SVModTrig(target=f"{self.namespace}ADSR/release_ms",
                      value=self.sound.release_ms)
        ]
        if self.sound.sustain_term:
            trigs.append(SVNoteOffTrig(target=f"{self.namespace}MultiSynth",
                                       i=self.sound.sustain_term))
        return SVMachineTrigs(trigs=trigs)

    def modulation(self,
                   level=1.0,
                   echo_delay=None,
                   echo_wet=None,
                   echo_feedback=None,
                   filter_resonance=None,
                   filter_roll_off=None):
        trigs = super().modulation(level=level,
                                   echo_delay=echo_delay,
                                   echo_wet=echo_wet,
                                   echo_feedback=echo_feedback)
        if filter_resonance:
            trigs.append(SVModTrig(target=f"{self.namespace}Filter/resonance",
                                   value=filter_resonance))
        if filter_roll_off:
            trigs.append(SVModTrig(target=f"{self.namespace}Filter/roll_off",
                                   value=filter_roll_off))
        return SVMachineTrigs(trigs=trigs)
    
if __name__ == "__main__":
    pass
