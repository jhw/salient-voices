from sv.core.trigs import SVModTrig, controller_value

import random

### random helpers

def random_seed():
    return int(random.random() * 1e8)

def unpack_string_list(fn):
    def wrapped(keys):
        return fn(keys.split("|") if isinstance(keys, str) else keys)
    return wrapped

@unpack_string_list
def random_seeds(keys):    
    return {key: random_seed() for key in keys}

def random_colour(offset = 64,
                  contrast = 128,
                  n = 256):
    for i in range(n):
        color = [int(offset + random.random() * (255 - offset))
                 for i in range(3)]
        if (max(color) - min(color)) > contrast:
            return color
    raise RuntimeError("couldn't find suitable random colour")

### machines

class GhostEchoMachine:

    def modulation(self,
                   i, 
                   echo_wet=None,
                   echo_feedback=None):
        trigs = []
        if echo_wet:
            wet_level = int(controller_value(echo_wet))
            trigs.append(SVModTrig(target=f"{self.namespace}Echo/wet",
                                   i=i,
                                   value=wet_level))
        if echo_feedback:
            feedback_level = int(controller_value(echo_feedback))
            trigs.append(SVModTrig(target=f"{self.namespace}Echo/feedback",
                                   i=i,
                                   value=feedback_level))
        return trigs

### test helpers
    
def flatten_trigs(patches):
    trigs = []
    for patch in patches:
        trigs += patch.trigs
    return trigs

if __name__ == "__main__":
    pass
