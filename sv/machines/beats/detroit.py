from sv.machines import SVSamplerMachine, SVMachineTrigs
from sv.machines.beats import SVBeatsApi
from sv.trigs import SVSampleTrig

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

class DetroitMachine(SVSamplerMachine, SVBeatsApi):

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
        SVBeatsApi.__init__(self,
                            samples=samples,
                            sample_index=sample_index)
        self.defaults = {"Echo": {"wet": echo_wet,
                                   "feedback": echo_feedback,
                                   "delay": echo_delay,
                                   "delay_unit": echo_delay_unit}}

    def note(self,
             volume=1.0,
             level=1.0):
        trigs = [SVSampleTrig(target=f"{self.namespace}Beat",
                              sample=self.sample,
                              cutoff=self.cutoff,
                              pitch=self.pitch,
                              vel=volume * level)]
        return SVMachineTrigs(trigs=trigs)

if __name__ == "__main__":
    pass
