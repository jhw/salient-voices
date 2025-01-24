import sv.client.algos.euclid as euclid
import sv.client.algos.perkons as perkons

import inspect
import random

### general

def random_seed():
    return int(random.random() * 1e8)

def random_colour(offset = 64,
                  contrast = 128,
                  n = 256):
    for i in range(n):
        color = [int(offset + random.random() * (255 - offset))
                 for i in range(3)]
        if (max(color) - min(color)) > contrast:
            return color
    raise RuntimeError("couldn't find suitable random colour")

### algo generators

def spawn_function(mod, fn, **kwargs):
    return getattr(eval(mod), fn)

def _random_euclid_pattern():
    pattern_kwargs = {k:v for k, v in zip(["pulses", "steps"],
                                          random.choice(euclid.TidalPatterns)[:2])}
    return {"mod": "euclid",
            "fn": "bjorklund",
            "args": pattern_kwargs}

def random_euclid_pattern():
    pattern = _random_euclid_pattern()
    return spawn_function(**pattern)(**pattern["args"])

def _random_perkons_groove():
    groove_fns = [name for name, _ in inspect.getmembers(perkons, inspect.isfunction)]    
    return {"mod": "perkons",
            "fn": random.choice(groove_fns)}

def random_perkons_groove():
    groove = _random_perkons_groove()
    return spawn_function(**groove)

if __name__ == "__main__":
    pass
