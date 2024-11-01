from sv.banks import SVBank, SVBanks
from sv.container import SVContainer
from sv.instruments.nine09.samples import Nine09
from sv.utils.banks import sync_banks, list_remote_keys, diff_keys

import sv.algos.euclid as euclid
import sv.algos.groove.perkons as perkons

import boto3
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

PerkonsGrooves = ['dynamic',
                  'humanise',
                  'pull',
                  'push',
                  'shifted_swing',
                  'swing']

def _sync_banks(s3, bucket_name):
    remote_keys = list_remote_keys(s3 = s3,
                                   bucket_name = bucket_name)
    diffed_keys = diff_keys(s3 = s3,
                            bucket_name = bucket_name,
                            keys = remote_keys)
    sync_banks(s3 = s3,
               bucket_name = bucket_name,
               keys = diffed_keys)

def beat(self, n, rand, env):
    pattern_kwargs = {k:v for k, v in zip(["pulses", "steps"], random.choice(euclid.TidalPatterns)[:2])}
    pattern = euclid.bjorklund(**pattern_kwargs)
    groove_fn = getattr(perkons, random.choice(PerkonsGrooves))
    for i in range(n):
        volume = groove_fn(rand = rand["vol"],
                           i = i)
        if rand["samp"].random() < env["sample_temperature"]:
            self.toggle_sample()
        if (pattern[i % len(pattern)] and
            rand["beat"].random() < env["beat_density"]):
            trig_block = self.note(note = 0,
                                   volume = volume)            
            yield i, trig_block

def ghost_echo(self, n, rand, env,
               sample_hold_levels = ["0000", "2000", "4000", "6000", "8000"],
               quantise = 4):
    for i in range(n):
        if 0 == i % quantise:            
            echo_wet_level = rand["fx"].choice(sample_hold_levels)
            echo_feedback_level = rand["fx"].choice(sample_hold_levels)
            trig_block = self.modulation(echo_wet = echo_wet_level,
                                         echo_feedback = echo_feedback_level)
            yield i, trig_block

def add_track(container,
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
        add_track(container = container,
                  pool = pool,
                  tag = tag,
                  namespace = tag.lower().capitalize(),
                  generators = generators,
                  seeds = seeds,
                  env = {"sample_temperature": temp,
                         "beat_density": density})
        
if __name__ == "__main__":
    try:
        """
        if len(sys.argv) < 2:
            raise RuntimeError("please enter bucket name")
        bucket_name = sys.argv[1]
        s3 = boto3.client("s3")
        _sync_banks(s3 = s3,
                    bucket_name = bucket_name)        
        """
        bank = SVBank.load_zip("dev/pico-default.zip")
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
        container.write_project("tmp/unique-modules-test.sunvox")
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
