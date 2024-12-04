from sv.machines import SVMachine, SVMachineTrigs, load_yaml
from sv.trigs import SVNoteTrig, SVModTrig, controller_value

import rv
import rv.api

class TokyoMachineBase(SVMachine):

    Modules = load_yaml(__file__, "modules.yaml")
    
    def __init__(self, container, namespace, notes, sounds,
                 sound_index = 0,
                 echo_delay = 36,
                 echo_delay_unit = 3, # tick
                 echo_wet = 0,
                 echo_feedback = 0,
                 colour = [127, 127, 127],
                 **kwargs):
        super().__init__(container = container,
                         namespace = namespace,
                         colour = colour)
        self.defaults = {"Echo": {"wet": echo_wet,
                                  "feedback": echo_feedback,
                                  "delay": echo_delay,
                                  "delay_unit": echo_delay_unit}}
        self.notes = notes
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
        i = self.sounds[self.sound_index]
        return self.notes[i % len(self.notes)]

    def note(self,
             note = 0,
             volume = 1.0,
             level = 1.0):
        trigs = [SVNoteTrig(target = f"{self.namespace}Beat",
                            note = self.sound,                        
                            vel = volume * level)]
        return SVMachineTrigs(trigs = trigs)

    def modulation(self,                   
                   level = 1.0,
                   echo_wet = None,
                   echo_feedback = None):
        trigs = []
        if echo_wet:
            wet_level = int(level * controller_value(echo_wet))
            trigs.append(SVModTrig(target = f"{self.namespace}Echo/wet",
                                   value = wet_level))
        if echo_feedback:
            trigs.append(SVModTrig(target = f"{self.namespace}Echo/feedback",
                                   value = echo_feedback))
        return SVMachineTrigs(trigs = trigs)

class TokyoKick(TokyoMachineBase):

    def __init__(self, container, namespace, colour, sounds,
                 notes = [j + i * 12
                          for i in range(10)
                          for j in range(3)
                          if i not in []],
                 **kwargs):
        super().__init__(container = container,
                         namespace = namespace,                         
                         colour = colour,
                         notes = notes,
                         sounds = sounds,
                         **kwargs)

class TokyoSnare(TokyoMachineBase):

    def __init__(self, container, namespace, colour, sounds, 
                 notes = [j + i * 12
                          for i in range(10)
                          for j in range(7, 12)
                          if i not in []],
                 **kwargs):
        super().__init__(container = container,
                         namespace = namespace,                         
                         colour = colour,
                         notes = notes,
                         sounds = sounds,
                         **kwargs)

class TokyoHat(TokyoMachineBase):

    def __init__(self, container, namespace, colour, sounds,
                 notes = [j + i * 12
                          for i in range(10)
                          for j in range(3, 6)
                          if i not in [6]],
                 **kwargs):
        super().__init__(container = container,
                         namespace = namespace,                         
                         colour = colour,
                         notes = notes,
                         sounds = sounds,
                         **kwargs)
    
if __name__ == "__main__":
    pass
