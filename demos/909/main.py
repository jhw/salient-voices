from sv.algos.euclid import bjorklund, TidalPatterns
from sv.algos.groove import wolgroove
from sv.banks import SVBank, SVBanks
from sv.container import SVContainer
from sv.instruments.nine09 import Nine09

import os
import random
import re
import yaml

PoolMappingTerms = yaml.safe_load("""
kick: (kick)|(kik)|(kk)|(bd)
clap: (clap)|(clp)|(cp)|(hc)
hat: (oh)|( ch)|(open)|(closed)|(hh)|(hat)
""")

def random_pattern(rand, patterns = [pattern for pattern in TidalPatterns
                                     if (pattern[0] / pattern[1]) < 0.5]):
    pulses, steps = rand["pat"].choice(patterns)[:2] # because some of Tidal euclid rhythms have 3 parameters
    return bjorklund(pulses = pulses,
                     steps = steps)

def beat(self, n, rand,
         sample_temperature = 0.5):
    pattern = random_pattern(rand)
    for i in range(n):
        if pattern[i % len(pattern)]:
            volume = wolgroove(rand = rand["vol"],
                               i = i)
            if rand["samp"].random() < sample_temperature:
                self.toggle_sample()
            trig_block = self.note(note = 0,
                                   volume = volume)            
            yield i, trig_block

def ghost_echo(self, n, rand,
               sample_hold_levels = ["0000", "2000", "4000", "6000", "8000"],
               quantise = 4):
    for i in range(n):
        if 0 == i % quantise:            
            echo_wet_level = rand["fx"].choice(sample_hold_levels)
            echo_feedback_level = rand["fx"].choice(sample_hold_levels)
            trig_block = self.modulation(echo_wet = echo_wet_level,
                                         echo_feedback = echo_feedback_level)
            yield i, trig_block
                            
if __name__ == "__main__":
    try:        
        bank = SVBank.load_zip_file("demos/909/pico-default.zip")
        container = SVContainer(banks = [bank],
                                bpm = 120,
                                n_ticks = 16)
        pool, _ = SVBanks([bank]).spawn_pool(tag_mapping = PoolMappingTerms)
        samples = pool.filter_by_tag("hat")
        random.shuffle(samples)
        nine09 = Nine09(container = container,
                        namespace = "909",
                        samples = samples[:2]) # sample, alt sample
        container.add_instrument(nine09)
        container.spawn_patch()
        seeds = {key: int(random.random() * 1e8)
                 for key in "fx|vol|pat|samp".split("|")}
        nine09.play(generator = beat,
                    seeds = seeds)        
        nine09.play(generator = ghost_echo,
                    seeds = seeds)        
        project = container.render_project()
        if not os.path.exists("tmp"):
            os.mkdir("tmp")
        with open("tmp/demo-909.sunvox", 'wb') as f:
            project.write_to(f)
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
