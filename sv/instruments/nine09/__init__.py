from sv.instruments import InstrumentBase, SVTrigBlock, load_yaml

class Nine09(InstrumentBase):

    Modules = load_yaml(__file__, "modules.yaml")
    
    def __init__(self, container, namespace):
        self.defaults = {}

    def note(self):
        trigs = []
        return SVTrigBlock(trigs = trigs)

    def modulation(self):
        trigs = []
        return SVTrigBlock(trigs = trigs)
    
if __name__ == "__main__":
    pass
