from sv.machines import SVMachineTrigs
from sv.trigs import SVModTrig, controller_value

class SVBeatsApi:
    
    def __init__(self, sounds, sound_index=0, **kwargs):
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
