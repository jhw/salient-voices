from sv.machines import SVMachineBase

class SVBassMachine(SVMachineBase):

    def __init__(self, container, namespace, **kwargs):
        super().__init__(container = container,
                         namespace = namespace,
                         **kwargs)

if __name__ == "__main__":
    pass
