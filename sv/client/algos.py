import sv.utils.algos.euclid as euclid
import sv.utils.algos.perkons as perkons

import inspect
import random

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
