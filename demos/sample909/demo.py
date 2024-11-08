from sv.banks import SVBank, SVBanks
from sv.container import SVContainer
from sv.instruments.nine09.samples import Nine09
from sv.utils.banks import sync_banks, list_remote_keys, diff_keys

import sv.algos.euclid as euclid
import sv.algos.groove.perkons as perkons

import boto3
import inspect
import logging
import random
import sys
import yaml

PoolTerms = yaml.safe_load("""
kick: (kick)|(kik)|(kk)|(bd)
clap: (clap)|(clp)|(cp)|(hc)
hat: (oh)|( ch)|(open)|(closed)|(hh)|(hat)
""")

logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format="%(levelname)s: %(message)s")

def spawn_function(mod, fn, **kwargs):
    return getattr(eval(mod), fn)

def beat(self, n, rand, pattern, groove, sample_temperature, beat_density, dry_level, **kwargs):
    pattern_fn = spawn_function(**pattern)(**pattern["args"])
    groove_fn = spawn_function(**groove)
    for i in range(n):
        volume = groove_fn(rand = rand["vol"], i = i)
        if rand["samp"].random() < sample_temperature:
            self.toggle_sample()        
        if (pattern_fn(i) and 
            rand["beat"].random() < beat_density):
            trig_block = self.note(volume = volume,
                                   level = dry_level)            
            yield i, trig_block

def ghost_echo(self, n, rand, wet_level,
               sample_hold_levels = ["0000", "2000", "4000", "6000", "8000"],
               quantise = 4,
               **kwargs):
    for i in range(n):
        if 0 == i % quantise:            
            sample_hold_wet = rand["fx"].choice(sample_hold_levels)
            sample_hold_feedback = rand["fx"].choice(sample_hold_levels)
            trig_block = self.modulation(level = wet_level,
                                         echo_wet = sample_hold_wet,
                                         echo_feedback = sample_hold_feedback)
            yield i, trig_block

def random_pattern(fn):
    def wrapped(env, **kwargs):
        pattern_kwargs = {k:v for k, v in zip(["pulses", "steps"], random.choice(euclid.TidalPatterns)[:2])}
        env["pattern"] = {"mod": "euclid",
                          "fn": "bjorklund",
                          "args": pattern_kwargs}
        return fn(env = env, **kwargs)
    return wrapped

def random_groove(fn):
    groove_fns = [name for name, _ in inspect.getmembers(perkons, inspect.isfunction)]    
    def wrapped(env, **kwargs):
        env["groove"] = {"mod": "perkons",
                         "fn": random.choice(groove_fns)}
        return fn(env = env, **kwargs)
    return wrapped

@random_pattern
@random_groove
def spawn_track(container,
                pool,
                namespace,
                tag,
                generators,
                seeds,
                env):
    samples = pool.match(lambda sample: tag in sample.tags)
    random.shuffle(samples)
    nine09 = Nine09(container = container,
                    namespace = namespace,
                    samples = samples[:2]) # NB
    container.add_instrument(nine09)
    nine09.render(generator = generators["beat"],
                  seeds = seeds,
                  env = env)
    nine09.render(generator = generators["echo"],
                  seeds = seeds,
                  env = env)

def spawn_patch(container, pool, generators):
    container.spawn_patch()
    for tag, temp, density in [("kick", 0.5, 0.5),
                               ("clap", 0.25, 0.25),
                               ("hat", 0.75, 0.75)]:
        seeds = {key: int(random.random() * 1e8)
                 for key in "fx|vol|samp|beat".split("|")}
        spawn_track(container = container,
                    pool = pool,
                    tag = tag,
                    namespace = tag.lower().capitalize(),
                    generators = generators,
                    seeds = seeds,
                    env = {"dry_level": 1.0,
                           "wet_level": 1.0,
                           "sample_temperature": temp,
                           "beat_density": density})

if __name__ == "__main__":
    try:
        bank = SVBank.load_zip("demos/sample909/pico-default.zip")
        banks = SVBanks([bank])
        container = SVContainer(banks = banks,
                                bpm = 120,
                                n_ticks = 16)
        pool, _ = banks.spawn_pool(tag_mapping = PoolTerms)
        generators = {"beat": beat,
                      "echo": ghost_echo}
        for i in range(16):
            spawn_patch(container = container,
                        pool = pool,
                        generators = generators)
        container.write_project("tmp/demo-sample909.sunvox")
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
