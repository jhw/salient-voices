import inspect
import random

import demos.algos.euclid as euclid
import demos.algos.perkons as perkons

def random_colour(offset = 64,
                  contrast = 128,
                  n = 256):
    for i in range(n):
        color = [int(offset + random.random() * (255 - offset))
                 for i in range(3)]
        if (max(color) - min(color)) > contrast:
            return color
    raise RuntimeError("couldn't find suitable random colour")

def random_seed():
    return int(random.random() * 1e8)

def random_euclid_pattern():
    pattern_kwargs = {k:v for k, v in zip(["pulses", "steps"],
                                          random.choice(euclid.TidalPatterns)[:2])}
    return {"mod": "euclid",
            "fn": "bjorklund",
            "args": pattern_kwargs}

def random_perkons_groove():
    groove_fns = [name for name, _ in inspect.getmembers(perkons, inspect.isfunction)]    
    return {"mod": "perkons",
            "fn": random.choice(groove_fns)}

if __name__ == "__main__":
    pass
