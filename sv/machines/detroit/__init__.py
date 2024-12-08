from sv.machines import SVSamplerMachine, SVMachineTrigs, load_yaml
from sv.trigs import SVSampleTrig, SVModTrig, controller_value

import rv
import rv.api

class Detroit(SVSamplerMachine):

    Modules = load_yaml(__file__, "modules.yaml")
    
    def __init__(self, container, namespace, sounds,
                 sound_index = 0,
                 relative_note = 0,
                 echo_delay = 36,
                 echo_delay_unit = 3, # tick
                 echo_wet = 0,
                 echo_feedback = 0,
                 colour = [127, 127, 127],
                 **kwargs):
        super().__init__(container = container,
                         namespace = namespace,
                         root = rv.note.NOTE.C5 + relative_note,
                         colour = colour)
        self.defaults = {"Echo": {"wet": echo_wet,
                                  "feedback": echo_feedback,
                                  "delay": echo_delay,
                                  "delay_unit": echo_delay_unit}}
        self.sounds = sounds
        self.sound_index = sound_index

    def toggle_sound(self):
        self.sound_index = 1 - int(self.sound_index > 0)

    def increment_sound(self):
        self.sound_index = (self.sound_index + 1) % len(self.sounds)

    def decrement_sound(self):
        self.sound_index = (self.sound_index - 1) % len(self.sounds)
        
    def randomise_sound(self, rand):
        self.sound_index = rand.choice(list(range(len(self.sounds))))
        
    @property
    def sound(self):
        return self.sounds[self.sound_index]
        
    def note(self,
             note = 0,
             volume = 1.0,
             level = 1.0):
        sample = self.sound.clone()
        sample["note"] = note
        trigs = [SVSampleTrig(target = f"{self.namespace}Beat",
                                  sample = sample,
                                  vel = volume * level)]
        return SVMachineTrigs(trigs = trigs)

    def modulation(self,                   
                   level = 1.0,
                   echo_delay = None,
                   echo_wet = None,
                   echo_feedback = None):
        trigs = []
        if echo_delay:
            delay_level = int(level * controller_value(echo_delay))
            trigs.append(SVModTrig(target = f"{self.namespace}Echo/delay",
                                   value = delay_level))
        if echo_wet:
            wet_level = int(level * controller_value(echo_wet))
            trigs.append(SVModTrig(target = f"{self.namespace}Echo/wet",
                                   value = wet_level))
        if echo_feedback:
            trigs.append(SVModTrig(target = f"{self.namespace}Echo/feedback",
                                   value = echo_feedback))
        return SVMachineTrigs(trigs = trigs)
    
if __name__ == "__main__":
    pass
