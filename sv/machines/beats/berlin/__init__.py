from sv.machines import SVSamplerMachine, SVMachineTrigs
from sv.machines.beats import SVBeatsApi
from sv.sounds import SVSample
from sv.trigs import SVNoteOffTrig, SVModTrig, SVSampleTrig, SVFXTrig

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
    - Echo
- name: Echo
  class: rv.modules.echo.Echo
  links:
    - Output
""")

class BerlinSound:

    def __init__(self,
                 attack = "0008",
                 decay = "0018",
                 sustain_level = "0800",
                 sustain_term = None,
                 release = "0300",
                 filter_freq = "4000",
                 filter_resonance = "7000",
                 slide_up = None,
                 slide_down = None):
        self.attack = attack
        self.decay = decay
        self.sustain_level = sustain_level
        self.sustain_term = sustain_term
        self.release = release
        self.filter_freq = filter_freq
        self.filter_resonance = filter_resonance
        self.slide_up = slide_up
        self.slide_down = slide_down

    def as_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}

class BerlinWave(Enum):
            
    SQR = "SQR"
    SAW = "SAW"
        
class BerlinMachine(SVSamplerMachine, SVBeatsApi):
    
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
        SVBeatsApi.__init__(self, sounds=sounds, sound_index=sound_index)
        self.sample = SVSample.parse(f"mikey303/303 VCO {wave.value}.wav")
        self.defaults = {"Echo": {"wet": echo_wet,
                                   "feedback": echo_feedback,
                                   "delay": echo_delay,
                                   "delay_unit": echo_delay_unit}}

    def note(self, note=0, volume=1.0, level=1.0):
        sample = self.sample.clone()
        sample.note = note
        trigs = [
            SVSampleTrig(target=f"{self.namespace}MultiSynth",
                         sampler_mod=f"{self.namespace}Sampler",
                         sample=sample,
                         vel=volume * level),
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
            if self.sound.slide_up != None:
                for i in range(self.sound.sustain_term):
                    pass
            elif self.sound.slide_down != None:
                for i in range(self.sound.sustain_term):
                    pass
            trigs.append(SVNoteOffTrig(target=f"{self.namespace}MultiSynth",
                                       i=self.sound.sustain_term))
        return SVMachineTrigs(trigs=trigs)
    
if __name__ == "__main__":
    pass
