from sv.machines import SVMachineBase

class SVBeatsMachine(SVMachineBase):

    def __init__(self, container, namespace, **kwargs):
        super().__init__(container = container,
                         namespace = namespace,
                         **kwargs)

    def toggle_sound(self):
        pass

    def increment_sound(self):
        pass

    def decrement_sound(self):
        pass
                
    def randomise_sound(self, rand):
        pass

if __name__ == "__main__":
    pass
