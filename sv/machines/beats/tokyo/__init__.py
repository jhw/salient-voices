from sv.machines import SVMachine, SVMachineTrigs, load_yaml
from sv.trigs import SVNoteTrig, SVModTrig, controller_value

import rv
import rv.api

class TokyoMachineBase(SVMachine):

    Modules = load_yaml(__file__, "modules.yaml")
    
    def __init__(self, container, namespace, base_notes, notes,
                 note_index = 0,
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
        self.base_notes = base_notes
        self.notes = notes
        self.note_index = note_index

    def toggle_sound(self):
        self.note_index = 1 - int(self.note_index > 0)

    def increment_sound(self):
        self.note_index = (self.note_index + 1) % len(self.notes)

    def decrement_sound(self):
        self.note_index = (self.note_index - 1) % len(self.notes)
        
    def randomise_sound(self, rand):
        self.note_index = rand.choice(list(range(len(self.notes))))

    @property
    def base_note(self):
        i = self.notes[self.note_index]
        return self.base_notes[i % len(self.base_notes)]

    def note(self,
             note = 0,
             volume = 1.0,
             level = 1.0):
        trigs = [SVNoteTrig(target = f"{self.namespace}Beat",
                            note = self.base_note,                        
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

    def __init__(self, container, namespace, colour, notes,
                 base_notes = [j + i * 12
                          for i in range(10)
                          for j in range(3)],
                 **kwargs):
        super().__init__(container = container,
                         namespace = namespace,                         
                         colour = colour,
                         base_notes = base_notes,
                         notes = notes,
                         **kwargs)

class TokyoSnare(TokyoMachineBase):

    def __init__(self, container, namespace, colour, notes, 
                 base_notes = [j + i * 12
                          for i in range(10)
                          for j in range(7, 12)],
                 **kwargs):
        super().__init__(container = container,
                         namespace = namespace,                         
                         colour = colour,
                         base_notes = base_notes,
                         notes = notes,
                         **kwargs)

class TokyoHat(TokyoMachineBase):

    def __init__(self, container, namespace, colour, notes,
                 base_notes = [j + i * 12
                          for i in range(10)
                          for j in range(3, 6)],
                 **kwargs):
        super().__init__(container = container,
                         namespace = namespace,                         
                         colour = colour,
                         base_notes = base_notes,
                         notes = notes,
                         **kwargs)
    
if __name__ == "__main__":
    pass
