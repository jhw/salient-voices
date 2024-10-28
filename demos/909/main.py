from sv.banks import SVBank, SVBanks
from sv.container import SVContainer
from sv.instruments.nine09 import Nine09
from random import Random

import os
import random
import re
import yaml

PoolMappingTerms = yaml.safe_load("""
kick: (kick)|(kik)|(kk)|(bd)
clap: (clap)|(clp)|(cp)|(hc)
hat: (oh)|( ch)|(open)|(closed)|(hh)|(hat)
""")

if __name__ == "__main__":
    try:        
        # initialise container
        bank = SVBank.load_zip_file("demos/909/pico-default.zip")
        pool, _ = SVBanks([bank]).spawn_pool(tag_mapping = PoolMappingTerms)
        container = SVContainer(banks = [bank],
                                bpm = 120,
                                n_ticks = 16)
        nine09 = Nine09(container = container,
                        namespace = "909",
                        samples = [])
        container.add_instrument(nine09)
        print(container)
        """
        # play machine
        rand = {key: Random(int(random.random() * 1e8))
                 for key in "sample|trig|pattern|volume|level".split("|")}
        nine09.play(generator = machine,
                    rand = rand)        
        # render project
        project = container.render_project()
        if not os.path.exists("tmp"):
            os.mkdir("tmp")
        with open("tmp/demo-909.sunvox", 'wb') as f:
            project.write_to(f)
        """
    except RuntimeError as error:
        print ("ERROR: %s" % str(error))
