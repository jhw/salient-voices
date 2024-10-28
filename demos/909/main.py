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

def beat(self, n, rand,
         quantise = 4):
    for i in range(n):
        if 0 == i % quantise:
             trig_block = self.note(note = 0,
                                    sample_index = 0)
             yield trig_block.render(i = i)

def ghost_echo(self, n, rand,
               sample_hold_levels = ["0000", "2000", "4000", "6000", "8000"],
               quantise = 4):
    for i in range(n):
        if 0 == i % quantise:            
            echo_wet_level = rand["fx"].choice(sample_hold_levels)
            echo_feedback_level = rand["fx"].choice(sample_hold_levels)
            trig_block = self.modulation(echo_wet = echo_wet_level,
                                         echo_feedback = echo_feedback_level)
            yield trig_block.render(i = i)
                            
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
                        samples = samples[:4])
        container.add_instrument(nine09)
        seeds = {key: int(random.random() * 1e8)
                 for key in "fx".split("|")}
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
