from sv.instruments import InstrumentBase, SVTrigBlock, load_yaml
from sv.model import SVNoteTrig, SVNoteOffTrig, SVModTrig

class Nine09(InstrumentBase):

    Modules = load_yaml(__file__, "modules.yaml")
    
    def __init__(self, container, namespace, samples,
                 echo_delay = 192):
        super().__init__(container = container,
                         namespace = namespace)
        self.samples = samples
        self.defaults = {"Echo": {"delay": echo_delay}}

    def note(self):
        trigs = []
        return SVTrigBlock(trigs = trigs)

    def modulation(self,
                   echo_wet = None,
                   echo_feedback = None):
        trigs = []
        if echo_wet:
            trigs.append(SVModTrig(target = f"{self.namespace}Echo/wet",
                                   value = echo_wet))
        if echo_feedback:
            trigs.append(SVModTrig(target = f"{self.namespace}Echo/feedback",
                                   value = echo_feedback))
        return SVTrigBlock(trigs = trigs)
    
if __name__ == "__main__":
    pass
