from sv.machines import SVSamplerMachine, SVMachineTrigs, SVBeatsApi
from sv.trigs import SVSampleTrig

import rv
import rv.api
import yaml

Modules = yaml.safe_load("""
- name: Beat
  class: sv.sampler.SVSlotSampler
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

class Detroit(SVSamplerMachine, SVBeatsApi):

    Modules = Modules

    def __init__(self, container, namespace, sounds,
                 sound_index=0,
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
        SVBeatsApi.__init__(self,
                            sounds=sounds,
                            sound_index=sound_index)
        self.defaults = {"Echo": {"wet": echo_wet,
                                   "feedback": echo_feedback,
                                   "delay": echo_delay,
                                   "delay_unit": echo_delay_unit}}

    def note(self,
             note=0,
             volume=1.0,
             level=1.0):
        sample = self.sound.clone()
        sample["note"] = note
        trigs = [SVSampleTrig(target=f"{self.namespace}Beat",
                              sample=sample,
                              vel=volume * level)]
        return SVMachineTrigs(trigs=trigs)

if __name__ == "__main__":
    pass
