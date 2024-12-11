from sv.machines import SVSamplerMachine, SVMachineTrigs, SVBeatsApi, load_yaml
from sv.trigs import SVSampleTrig, SVModTrig, controller_value

import rv
import rv.api

class Detroit(SVSamplerMachine, SVBeatsApi):

    Modules = load_yaml(__file__, "modules.yaml")

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

    def modulation(self,
                   level=1.0,
                   echo_delay=None,
                   echo_wet=None,
                   echo_feedback=None):
        trigs = []
        if echo_delay:
            delay_level = int(level * controller_value(echo_delay))
            trigs.append(SVModTrig(target=f"{self.namespace}Echo/delay",
                                   value=delay_level))
        if echo_wet:
            wet_level = int(level * controller_value(echo_wet))
            trigs.append(SVModTrig(target=f"{self.namespace}Echo/wet",
                                   value=wet_level))
        if echo_feedback:
            trigs.append(SVModTrig(target=f"{self.namespace}Echo/feedback",
                                   value=echo_feedback))
        return SVMachineTrigs(trigs=trigs)

if __name__ == "__main__":
    pass
